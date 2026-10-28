"""Replay 17Lands drafts through DraftAdvisor and score its picks.

For a sample of drafts from a 17Lands public draft dump, each pick is shown to
the advisor (with the pool and lane signals the app would have at that point),
and its ranking is compared with the card the drafter actually took. Simple
baselines (highest GIH WR, lowest ATA) are scored on the same picks.

    python Tools/AdvisorReplay/advisor_replay.py run \
        --dump draft_data_public.FRA.PremierDraft.csv.gz \
        --dataset FRA_PremierDraft_All_Data.json.gz \
        --drafts 500 --variant baseline --variant arch-overall-pick \
        --out results/FRA.json

    python Tools/AdvisorReplay/advisor_replay.py summarize results/*.json

Card ratings come from the whole format, including the replayed drafts, so the
numbers compare methods with each other; they are not out-of-sample accuracy.
"""

import argparse
import contextlib
import csv
import gzip
import hashlib
import heapq
import json
import logging
import math
import os
import sys
import tempfile
import time
from collections import defaultdict
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import constants  # noqa: E402
from src.advisor import deck_builder  # noqa: E402
from src.advisor.engine import DraftAdvisor  # noqa: E402
from src.dataset import Dataset  # noqa: E402
from src.set_metrics import SetMetrics  # noqa: E402
from src.signals import SignalCalculator  # noqa: E402

# A drafter counts as strong with a 60%+ game win rate over 50+ games.
STRONG_WIN_RATE = 0.6
STRONG_MIN_GAMES = 50


# --- Engine variants -------------------------------------------------------


def _fast_stack_cards(cards):
    """stack_cards without the deepcopy; the deck builders only change "count"."""
    stacked = {}
    for c in cards:
        name = c.get(constants.DATA_FIELD_NAME, "Unknown")
        if name not in stacked:
            stacked[name] = dict(c)
            stacked[name]["count"] = 1
        else:
            stacked[name]["count"] += 1
    return list(stacked.values())


@contextlib.contextmanager
def _baseline(dataset):
    yield


@contextlib.contextmanager
def _arch_overall_pick(dataset):
    """Weight the archetype by overall pick, not the pick within the pack."""
    original = DraftAdvisor._calculate_weighted_score

    def patched(self, card, pick_number):
        return original(self, card, len(self.pool) + 1)

    with mock.patch.object(DraftAdvisor, "_calculate_weighted_score", patched):
        yield


# Color combos with at least this share of the set's games count as archetypes.
ARCHETYPE_MIN_SHARE = 0.03


def archetype_shares(dataset):
    """{two- or three-color key: share of games} for the set's real archetypes.

    Uses the per-deck-color sample counts in the card ratings, so a set like
    TDM yields its five clans (plus WR) and a two-color set yields its pairs.
    """
    totals = defaultdict(int)
    for card in dataset.get_card_ratings().values():
        for key, stats in card.get(constants.DATA_FIELD_DECK_COLORS, {}).items():
            totals[key] += stats.get("samples", 0) or 0
    games = totals.pop(constants.FILTER_OPTION_ALL_DECKS, 0) or 1
    return {
        k: n / games
        for k, n in totals.items()
        if len(k) in (2, 3) and n / games >= ARCHETYPE_MIN_SHARE
    }


def pick_lane(main_colors, color_counts, shares):
    """The archetype containing the top two colors that best fits the pool.

    Each candidate scores its share of games times, for each color beyond the
    top two, how committed the pool is to it relative to the second color
    (floored at 0.1). Returns (lane, candidates best first), or (None, []).
    """
    if len(main_colors) < 2:
        return None, []
    top2 = set(main_colors[:2])
    second = max(1, color_counts.get(main_colors[1], 0))
    scored = []
    for key, share in shares.items():
        if not top2 <= set(key):
            continue
        score = share
        for extra in set(key) - top2:
            score *= max(0.1, min(1.0, color_counts.get(extra, 0) / second))
        scored.append((score, key))
    scored.sort(reverse=True)
    return (scored[0][1] if scored else None), [k for _, k in scored]


_SHARES = {}  # id(dataset) -> archetype_shares, so each pick doesn't recount


@contextlib.contextmanager
def _arch_lane(dataset, soft=False):
    """Make the lane a frequent archetype (e.g. a TDM clan), not the top two colors.

    The lane sets the archetype used for card win rates and which colors count
    as castable. With soft, a card that fits another archetype containing the
    top two colors is penalized less (0.7) than a true off-color card.
    """
    shares = _SHARES.get(id(dataset))
    if shares is None:
        shares = _SHARES[id(dataset)] = archetype_shares(dataset)
    init = DraftAdvisor.__init__
    castability = DraftAdvisor._calculate_castability_v5

    def patched_init(self, *args, **kwargs):
        init(self, *args, **kwargs)
        self.lane, self.lane_options = pick_lane(
            self.main_colors, self.color_counts, shares
        )
        if self.lane:
            self.main_archetype = self.lane
            self.main_colors = sorted(
                self.lane, key=lambda c: -self.color_counts.get(c, 0)
            )
            self.active_colors = self.main_colors

    def patched_castability(self, card, pack, pick, z_score):
        if not self.lane:
            return castability(self, card, pack, pick, z_score)
        colors = set(card.get("colors", []))
        if colors <= set(self.lane):
            return 1.0, ""
        mult, reason = castability(self, card, pack, pick, z_score)
        if soft and mult < 0.7 and any(colors <= set(k) for k in self.lane_options):
            return 0.7, "Other Archetype In Lane"
        return mult, reason

    with mock.patch.object(DraftAdvisor, "__init__", patched_init), mock.patch.object(
        DraftAdvisor, "_calculate_castability_v5", patched_castability
    ):
        yield


VARIANTS = {
    "baseline": _baseline,
    "arch-overall-pick": _arch_overall_pick,
    "arch-lane": _arch_lane,
    "arch-lane-soft": lambda dataset: _arch_lane(dataset, soft=True),
}


# --- ATA blends ------------------------------------------------------------

# Each blend reranks a variant's advice by
#     (1 - w) * z(advisor score) + w * z(-ATA),
# with z-scores taken over the pack and w = f(pack, pick in pack, overall pick).
# They only re-sort the advice, so they cost almost nothing to score.
BLENDS = {
    "ata30": lambda pk, pi, overall: 0.3,
    "ata50": lambda pk, pi, overall: 0.5,
    "ata70": lambda pk, pi, overall: 0.7,
    "ata70-exp4": lambda pk, pi, overall: 0.7 * math.exp(-(pi - 1) / 4),
    "ata70-exp8": lambda pk, pi, overall: 0.7 * math.exp(-(pi - 1) / 8),
    "ata90-exp8": lambda pk, pi, overall: 0.9 * math.exp(-(pi - 1) / 8),
    "ata70-exp4-floor30": lambda pk, pi, overall: 0.3 + 0.4 * math.exp(-(pi - 1) / 4),
    "ata-overall-linear": lambda pk, pi, overall: 0.8
    * max(0.0, 1 - (overall - 1) / 44),
    "ata-first4": lambda pk, pi, overall: 1.0 if pi <= 4 else 0.0,
    "ata-first4-pack1": lambda pk, pi, overall: 1.0 if pk == 1 and pi <= 4 else 0.0,
    "ata-rising": lambda pk, pi, overall: 0.2 + 0.5 * min(1.0, (pi - 1) / 13),
}

# Cards with no ATA sort as if taken at the end of a pack.
MISSING_ATA = 15.0


def _zscores(values):
    mean = sum(values) / len(values)
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)) or 1.0
    return [(v - mean) / sd for v in values]


def blend_order(recs, pack, weight):
    """Names from recs, reordered by the advisor/ATA blend with ATA weight."""
    scores = {}
    for r in recs:
        scores.setdefault(r.card_name, r.contextual_score)
    ata = {
        c[constants.DATA_FIELD_NAME]: _stat(c, constants.DATA_FIELD_ATA) for c in pack
    }
    names = list(scores)
    z_adv = _zscores([scores[n] for n in names])
    z_ata = _zscores([-(ata.get(n) or MISSING_ATA) for n in names])
    blended = {n: (1 - weight) * a + weight * t for n, a, t in zip(names, z_adv, z_ata)}
    # sorted is stable, so ties keep the advisor's order.
    return sorted(names, key=lambda n: -blended[n])


# --- Reading the dump ------------------------------------------------------


def _open_text(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", newline="", encoding="utf-8")
    return open(path, "r", newline="", encoding="utf-8")


def _draft_hash(draft_id):
    return int(hashlib.md5(draft_id.encode("utf-8")).hexdigest()[:15], 16)


def _float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def sample_drafts(path, n_drafts, shard=0, num_shards=1):
    """Pick n_drafts drafts uniformly at random (by hashed draft_id).

    Returns {draft_id: draft}, where a draft has "strong" and a list of
    "picks" (pack, pick, picked name, pack names, pool names), in dump order.
    """
    with _open_text(path) as f:
        reader = csv.reader(f)
        header = next(reader)
        col = {c: i for i, c in enumerate(header)}
        pack_cols = [
            (i, c[len("pack_card_") :])
            for i, c in enumerate(header)
            if c.startswith("pack_card_")
        ]
        pool_cols = [
            (i, c[len("pool_") :])
            for i, c in enumerate(header)
            if c.startswith("pool_")
        ]
        i_id, i_pack, i_pick, i_name = (
            col["draft_id"],
            col["pack_number"],
            col["pick_number"],
            col["pick"],
        )
        i_wr = col.get("user_game_win_rate_bucket")
        i_games = col.get("user_n_games_bucket")

        # Bottom-k by hash: a max-heap of (-priority, draft_id) for kept drafts.
        heap, drafts = [], {}
        current_id, keep = None, False
        for row in reader:
            draft_id = row[i_id]
            if draft_id != current_id:
                current_id = draft_id
                h = _draft_hash(draft_id)
                keep = h % num_shards == shard
                if keep:
                    priority = h // num_shards
                    if draft_id in drafts:
                        pass
                    elif len(heap) < n_drafts:
                        heapq.heappush(heap, (-priority, draft_id))
                    elif priority < -heap[0][0]:
                        _, dropped = heapq.heappushpop(heap, (-priority, draft_id))
                        drafts.pop(dropped, None)
                    else:
                        keep = False
                if keep and draft_id not in drafts:
                    strong = (
                        i_wr is not None
                        and _float(row[i_wr]) >= STRONG_WIN_RATE
                        and _float(row[i_games]) >= STRONG_MIN_GAMES
                    )
                    drafts[draft_id] = {"strong": strong, "picks": []}
            if not keep:
                continue
            drafts[draft_id]["picks"].append(
                (
                    int(row[i_pack]),
                    int(row[i_pick]),
                    row[i_name],
                    [
                        n
                        for i, n in pack_cols
                        if row[i] not in ("", "0")
                        for _ in range(int(row[i]))
                    ],
                    [
                        n
                        for i, n in pool_cols
                        if row[i] not in ("", "0")
                        for _ in range(int(row[i]))
                    ],
                )
            )
    return drafts


# --- Replaying -------------------------------------------------------------


def load_dataset(path):
    """Open an app dataset (.json or .json.gz)."""
    dataset = Dataset()
    if path.endswith(".gz"):
        # Dataset.open_file reads plain JSON only.
        with tempfile.TemporaryDirectory() as tmp:
            plain = os.path.join(tmp, os.path.basename(path)[: -len(".gz")])
            with gzip.open(path, "rb") as src, open(plain, "wb") as dst:
                dst.write(src.read())
            result = dataset.open_file(plain)
    else:
        result = dataset.open_file(path)
    if not dataset.get_card_ratings():
        raise SystemExit(f"Could not load dataset {path}: {result}")
    return dataset


class NameResolver:
    """Map dump names (front faces only) to dataset card dicts."""

    def __init__(self, dataset):
        self.dataset = dataset
        self.front = {}
        for card in dataset.get_card_ratings().values():
            name = card.get(constants.DATA_FIELD_NAME, "")
            if " // " in name:
                self.front.setdefault(name.split(" // ")[0], name)
        self.missing = defaultdict(int)

    def cards(self, names):
        out = []
        for n in names:
            found = self.dataset.get_data_by_name([self.front.get(n, n)])
            if found:
                out.append(found[0])
            else:
                self.missing[n] += 1
        return out


def _rank_of(order, target):
    """0-based rank of target among the unique names in order."""
    seen = []
    for name in order:
        if name not in seen:
            seen.append(name)
        if name == target:
            return len(seen) - 1
    return None


def _stat(card, field):
    return _float(
        card.get(constants.DATA_FIELD_DECK_COLORS, {})
        .get(constants.FILTER_OPTION_ALL_DECKS, {})
        .get(field, 0.0)
    )


def baseline_orders(pack):
    by_gihwr = sorted(pack, key=lambda c: -_stat(c, constants.DATA_FIELD_GIHWR))
    by_ata = sorted(
        pack,
        key=lambda c: _stat(c, constants.DATA_FIELD_ATA) or float("inf"),
    )
    return {
        "gihwr": [c[constants.DATA_FIELD_NAME] for c in by_gihwr],
        "ata": [c[constants.DATA_FIELD_NAME] for c in by_ata],
    }


def _slices(pack_no, pick_no):
    """Buckets each pick is reported under (1-indexed pack and pick)."""
    phase = "picks 1-4" if pick_no <= 4 else "picks 5-8" if pick_no <= 8 else "picks 9+"
    return ["all", f"pack {pack_no}", phase]


class Tally:
    def __init__(self):
        self.data = defaultdict(lambda: {"n": 0, "top1": 0, "top3": 0, "rank": 0})

    def add(self, method, group, slices, rank):
        for s in slices:
            d = self.data[f"{method}|{group}|{s}"]
            d["n"] += 1
            d["top1"] += rank == 0
            d["top3"] += rank < 3
            d["rank"] += rank


def replay(drafts, dataset, variants, progress_every=0, fast=True, blends=()):
    """Score each variant and the baselines on every pick of every draft.

    Each name in blends is also scored on top of every variant, as
    "<variant>+<blend>".
    """
    patch = (
        mock.patch.object(deck_builder, "stack_cards", _fast_stack_cards)
        if fast
        else contextlib.nullcontext()
    )
    with patch:
        return _replay(drafts, dataset, variants, progress_every, blends)


def _replay(drafts, dataset, variants, progress_every, blends):
    metrics = SetMetrics(dataset)
    resolver = NameResolver(dataset)
    sig_calc = SignalCalculator(metrics)
    tally = Tally()
    skipped = defaultdict(int)
    start = time.time()

    for n, (draft_id, draft) in enumerate(sorted(drafts.items()), 1):
        groups = ["all"] + (["strong"] if draft["strong"] else [])
        history = []
        for pack_no, pick_no, picked, pack_names, pool_names in draft["picks"]:
            pk, pi = pack_no + 1, pick_no + 1
            pack = resolver.cards(pack_names)
            pool = resolver.cards(pool_names)
            history.append((pk, pi, pack))

            target = resolver.cards([picked])
            if not target:
                skipped["pick not in dataset"] += 1
                continue
            target = target[0][constants.DATA_FIELD_NAME]
            if len({c[constants.DATA_FIELD_NAME] for c in pack}) < 2:
                skipped["fewer than 2 distinct cards"] += 1
                continue

            # Same signals as AppController: every pack seen so far, minus pack 2.
            scores = {c: 0.0 for c in constants.CARD_COLORS}
            for h_pk, h_pi, h_pack in history:
                if h_pk == 2:
                    continue
                for c, v in sig_calc.calculate_pack_signals(h_pack, h_pi).items():
                    scores[c] += v

            slices = _slices(pk, pi)
            for name in variants:
                with VARIANTS[name](dataset):
                    recs = DraftAdvisor(metrics, pool, signals=scores).evaluate_pack(
                        pack, pi, current_pack=pk
                    )
                rank = _rank_of([r.card_name for r in recs], target)
                if rank is None:
                    skipped[f"{name}: pick missing from advice"] += 1
                    continue
                for g in groups:
                    tally.add(name, g, slices, rank)
                for b in blends:
                    weight = BLENDS[b](pk, pi, len(pool) + 1)
                    rank = _rank_of(blend_order(recs, pack, weight), target)
                    for g in groups:
                        tally.add(f"{name}+{b}", g, slices, rank)
            for name, order in baseline_orders(pack).items():
                rank = _rank_of(order, target)
                for g in groups:
                    tally.add(name, g, slices, rank)

        if progress_every and n % progress_every == 0:
            print(
                f"{n}/{len(drafts)} drafts, {time.time() - start:.0f}s",
                file=sys.stderr,
                flush=True,
            )

    return {
        "drafts": len(drafts),
        "strong_drafts": sum(d["strong"] for d in drafts.values()),
        "seconds": round(time.time() - start, 1),
        "skipped": dict(skipped),
        "unmatched_names": dict(
            sorted(resolver.missing.items(), key=lambda x: -x[1])[:20]
        ),
        "tally": dict(tally.data),
    }


# --- Reporting -------------------------------------------------------------


def merge(results):
    total = {"drafts": 0, "strong_drafts": 0, "tally": {}}
    for r in results:
        total["drafts"] += r["drafts"]
        total["strong_drafts"] += r["strong_drafts"]
        for key, d in r["tally"].items():
            t = total["tally"].setdefault(
                key, {"n": 0, "top1": 0, "top3": 0, "rank": 0}
            )
            for k in t:
                t[k] += d[k]
    return total


def format_table(result, sets=None):
    """Markdown table: one row per method, columns per group and slice."""
    tally = result["tally"]
    methods = sorted({k.split("|")[0] for k in tally}, key=_method_order)
    columns = [
        ("all", "all"),
        ("strong", "all"),
        ("strong", "pack 1"),
        ("strong", "pack 2"),
        ("strong", "pack 3"),
        ("strong", "picks 1-4"),
        ("strong", "picks 5-8"),
        ("strong", "picks 9+"),
    ]
    title = f"{', '.join(sets)}: " if sets else ""
    lines = [
        f"{title}{result['drafts']} drafts ({result['strong_drafts']} by strong drafters). "
        "Cells are top-1 % / top-3 % / mean rank of the card actually taken.",
        "",
        "| method | " + " | ".join(f"{g} {s}" for g, s in columns) + " |",
        "|---|" + "---|" * len(columns),
    ]
    for m in methods:
        cells = []
        for g, s in columns:
            d = tally.get(f"{m}|{g}|{s}")
            if not d or not d["n"]:
                cells.append("–")
                continue
            cells.append(
                f"{100 * d['top1'] / d['n']:.1f} / {100 * d['top3'] / d['n']:.1f} / "
                f"{d['rank'] / d['n']:.2f}"
            )
        lines.append(f"| {m} | " + " | ".join(cells) + " |")
    n = tally.get(f"{methods[0]}|all|all", {}).get("n", 0) if methods else 0
    lines += ["", f"{n} picks scored."]
    return "\n".join(lines)


def _method_order(m):
    """Variants in VARIANTS order, each followed by its blends, then baselines."""
    order = list(VARIANTS) + ["gihwr", "ata"]
    base, _, blend = m.partition("+")
    i = order.index(base) if base in order else len(order)
    j = list(BLENDS).index(blend) + 1 if blend in BLENDS else 0
    return (i, j, m)


# --- CLI -------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Replay a sample of drafts from one dump.")
    run.add_argument("--dump", required=True, help="17Lands draft_data_public CSV(.gz)")
    run.add_argument(
        "--dataset", required=True, help="App dataset JSON(.gz) for the set"
    )
    run.add_argument("--drafts", type=int, default=200)
    run.add_argument("--shard", type=int, default=0)
    run.add_argument("--num-shards", type=int, default=1)
    run.add_argument(
        "--variant",
        action="append",
        choices=sorted(VARIANTS),
        help="Engine variant to score (repeatable). Default: baseline.",
    )
    run.add_argument(
        "--blend",
        action="append",
        choices=list(BLENDS),
        default=[],
        help="ATA blend to score on top of each variant (repeatable).",
    )
    run.add_argument("--out", help="Write results JSON here")
    run.add_argument("--progress", type=int, default=25, help="Report every N drafts")

    summ = sub.add_parser("summarize", help="Merge result files into a table.")
    summ.add_argument("results", nargs="+")
    summ.add_argument("--per-set", action="store_true", help="Also print each set")

    args = parser.parse_args(argv)
    logging.disable(logging.WARNING)

    if args.command == "run":
        variants = args.variant or ["baseline"]
        t = time.time()
        drafts = sample_drafts(args.dump, args.drafts, args.shard, args.num_shards)
        print(
            f"Sampled {len(drafts)} drafts in {time.time() - t:.0f}s", file=sys.stderr
        )
        result = replay(
            drafts,
            load_dataset(args.dataset),
            variants,
            args.progress,
            blends=args.blend,
        )
        result["dump"] = os.path.basename(args.dump)
        result["variants"] = variants
        result["blends"] = args.blend
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=1)
        print(format_table(result, [_set_code(result["dump"])]))
        if result["skipped"]:
            print(f"\nSkipped: {result['skipped']}")
        if result["unmatched_names"]:
            print(f"Names not in dataset: {result['unmatched_names']}")
    else:
        results = []
        for path in args.results:
            with open(path, encoding="utf-8") as f:
                results.append(json.load(f))
        by_set = defaultdict(list)
        for r in results:
            by_set[_set_code(r.get("dump", ""))].append(r)
        if args.per_set and len(by_set) > 1:
            for code, rs in sorted(by_set.items()):
                print(format_table(merge(rs), [code]) + "\n")
        print(format_table(merge(results), sorted(by_set)))


def _set_code(dump_name):
    """draft_data_public.FRA.PremierDraft.csv.gz -> FRA"""
    parts = dump_name.split(".")
    return parts[1] if len(parts) > 2 else dump_name or "?"


if __name__ == "__main__":
    main()
