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
def _baseline():
    yield


@contextlib.contextmanager
def _arch_overall_pick():
    """Weight the archetype by overall pick, not the pick within the pack."""
    original = DraftAdvisor._calculate_weighted_score

    def patched(self, card, pick_number):
        return original(self, card, len(self.pool) + 1)

    with mock.patch.object(DraftAdvisor, "_calculate_weighted_score", patched):
        yield


VARIANTS = {
    "baseline": _baseline,
    "arch-overall-pick": _arch_overall_pick,
}


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


def replay(drafts, dataset, variants, progress_every=0, fast=True):
    """Score each variant and the baselines on every pick of every draft."""
    patch = (
        mock.patch.object(deck_builder, "stack_cards", _fast_stack_cards)
        if fast
        else contextlib.nullcontext()
    )
    with patch:
        return _replay(drafts, dataset, variants, progress_every)


def _replay(drafts, dataset, variants, progress_every):
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
                with VARIANTS[name]():
                    recs = DraftAdvisor(metrics, pool, signals=scores).evaluate_pack(
                        pack, pi, current_pack=pk
                    )
                rank = _rank_of([r.card_name for r in recs], target)
                if rank is None:
                    skipped[f"{name}: pick missing from advice"] += 1
                    continue
                for g in groups:
                    tally.add(name, g, slices, rank)
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
    order = list(VARIANTS) + ["gihwr", "ata"]
    return order.index(m) if m in order else len(order)


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
        result = replay(drafts, load_dataset(args.dataset), variants, args.progress)
        result["dump"] = os.path.basename(args.dump)
        result["variants"] = variants
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
