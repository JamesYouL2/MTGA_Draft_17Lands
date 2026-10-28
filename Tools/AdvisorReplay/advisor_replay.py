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
import itertools
import json
import logging
import math
import os
import re
import sys
import tempfile
import time
from collections import defaultdict
from unittest import mock

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import constants  # noqa: E402
from src.advisor import deck_builder, deck_scorer  # noqa: E402
from src.advisor.deck_scorer import (  # noqa: E402
    holistic_score_parts,
    identify_top_pairs,
)
from src.advisor.engine import DraftAdvisor  # noqa: E402
from src.dataset import Dataset  # noqa: E402
from src.set_metrics import SetMetrics  # noqa: E402
from src.signals import SignalCalculator  # noqa: E402
from src.utils import normalize_color_string  # noqa: E402

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


def _cached(what, dataset, fn):
    """fn(dataset), computed once per dataset so each pick doesn't recount."""
    cache = dataset.__dict__.setdefault("_replay_cache", {})
    if what not in cache:
        cache[what] = fn(dataset)
    return cache[what]


@contextlib.contextmanager
def _lane_variant(choose, soft=False):
    """Replace the "top two colors" lane with choose(advisor) -> (lane, options).

    The lane sets the archetype used for card win rates and which colors count
    as castable. With soft, a card that fits one of the options is penalized
    less (0.7) than a true off-color card.
    """
    init = DraftAdvisor.__init__
    castability = DraftAdvisor._calculate_castability_v5

    def patched_init(self, *args, **kwargs):
        init(self, *args, **kwargs)
        self.lane, self.lane_options = choose(self)
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


def _arch_lane(dataset, soft=False):
    """Make the lane a frequent archetype (e.g. a TDM clan), not the top two colors.

    With soft, a card that fits another archetype containing the top two colors
    is penalized less (0.7) than a true off-color card.
    """
    shares = _cached("shares", dataset, archetype_shares)
    return _lane_variant(
        lambda adv: pick_lane(adv.main_colors, adv.color_counts, shares), soft
    )


# --- Deck-score refit ------------------------------------------------------

# Deck-score adjustments rescaled to what each was worth in wins per point,
# relative to the power from card ratings, in the pooled `pools` run over all
# ten sets (aggro 0.33, two colors 1.44, evasion 0.13 times power). These were
# fit on the same sets the replay uses, so they are not a held-out test.
REFIT_ADJUSTMENTS = {"aggro": 1.5, "two_colors": 4.0, "evasion": -1.0}

# Games of prior pulling an archetype win rate toward the overall one, as in
# Draft Omen: (wins + K * average) / (games + K).
SHRINK_GAMES = 500


@contextlib.contextmanager
def _deck_refit(dataset):
    """Reweight the deck score's aggro, two-color and evasion adjustments."""
    original = deck_scorer.holistic_score_parts

    def patched(*args, **kwargs):
        parts = original(*args, **kwargs)
        if parts is None:
            return None
        power, adjustments = parts
        return power, [
            (key, REFIT_ADJUSTMENTS.get(key, delta), note)
            for key, delta, note in adjustments
        ]

    with mock.patch.object(deck_scorer, "holistic_score_parts", patched):
        yield


def shrunk_card_rating(original, k=SHRINK_GAMES):
    """get_card_rating with the archetype weight 0.7 scaled by n / (n + k).

    n is the card's game-in-hand samples in the archetype, so a card rarely
    played in that pair leans on its overall GIH WR instead.
    """

    def patched(card, colors, metrics=None, tier_data=None):
        rating = original(card, colors, metrics, tier_data)
        stats = card.get(constants.DATA_FIELD_DECK_COLORS, {})
        overall = _float(stats.get(constants.FILTER_OPTION_ALL_DECKS, {}).get("gihwr"))
        arch = stats.get(normalize_color_string("".join(colors[:2])), {})
        arch_wr = _float(arch.get("gihwr"))
        if not (arch_wr > 30.0 and overall > 30.0):
            return rating
        n = _float(arch.get("samples"))
        weight = 0.7 * n / (n + k)
        return weight * arch_wr + (1 - weight) * overall

    return patched


@contextlib.contextmanager
def _arch_shrink(dataset):
    """Shrink the deck score's archetype card ratings by sample size."""
    patched = shrunk_card_rating(deck_scorer.get_card_rating)
    with mock.patch.object(deck_scorer, "get_card_rating", patched), mock.patch.object(
        deck_builder, "get_card_rating", patched
    ):
        yield


# --- Draft Omen ideas ------------------------------------------------------

# Color commitment: every color is open for picks 1-5; multipliers ramp in
# from pick 6 and are fully on from pick 16.
COMMIT_OPEN, COMMIT_LOCKED = 5, 16
ON_COLOR, OFF_COLOR = 1.15, 0.75
SPLASH_WITH_FIXING, SPLASH = 0.95, 0.85
FIXER = 1.05


def commitment(overall_pick):
    """0 while colors are open, rising to 1 once the drafter is locked in."""
    ramp = (overall_pick - COMMIT_OPEN) / (COMMIT_LOCKED - COMMIT_OPEN)
    return min(1.0, max(0.0, ramp))


def off_lane_pips(card, lane):
    """Colored pips in the card's cost that the lane can't pay (hybrid counts as payable)."""
    cost = card.get("mana_cost", "")
    if not cost:
        return sum(1 for c in card.get("colors", []) if c not in lane)
    off = 0
    for pip in re.findall(r"\{(.*?)\}", cost):
        options = [c for c in pip.split("/") if c in "WUBRG"]
        if options and not any(o in lane for o in options):
            off += 1
    return off


@contextlib.contextmanager
def _do_commit(dataset):
    """Draft Omen's soft color multipliers in place of the castability penalty.

    The engine's own penalty drops off-color cards to 0.01-0.05 from pack 2.
    Here a locked-in drafter gets 1.15 on color, 0.95 / 0.85 for a one-pip
    splash with / without a source for it, and 0.75 otherwise; fixing gets
    1.05. Each multiplier is scaled by commitment(overall pick).
    """

    def patched(self, card, pack, pick, z_score):
        lane = getattr(self, "lane", None) or self.main_colors[:2]
        if len(lane) < 2:
            return 1.0, ""
        colors = card.get("colors", [])
        off = off_lane_pips(card, lane)
        if off == 0:
            target, reason = (ON_COLOR if colors else 1.0), ""
        elif off == 1:
            splash = [c for c in colors if c not in lane]
            fixed = bool(splash) and all(self.fixing_map.get(c, 0) > 0 for c in splash)
            target = SPLASH_WITH_FIXING if fixed else SPLASH
            reason = "Splashable" if fixed else "Splash"
        else:
            target, reason = OFF_COLOR, "Off-Color"
        types = card.get("types", [])
        if "fixing_ramp" in card.get("tags", []) or (
            "Land" in types and len(colors) > 1
        ):
            target *= FIXER
        t = commitment(len(self.pool) + 1)
        return 1.0 + (target - 1.0) * t, (reason if t > 0 else "")

    with mock.patch.object(DraftAdvisor, "_calculate_castability_v5", patched):
        yield


# Three-color gate: triads are considered only in sets where three-color decks
# are at least this share of games, and only when each of the triad's colors
# is at least this share of the pool's colored cards.
THREE_COLOR_MIN_SHARE = 0.10
TRIAD_COLOR_MIN_WEIGHT = 0.20


def archetype_win_rates(dataset, k=SHRINK_GAMES):
    """{two- or three-color key: (share of games, shrunk win rate)}.

    Win rates come from the dataset's color ratings and are shrunk toward the
    share-weighted average by (wins + k * avg) / (games + k), with each
    archetype's games estimated from its share of the set's games.
    """
    totals = defaultdict(int)
    for card in dataset.get_card_ratings().values():
        for key, stats in card.get(constants.DATA_FIELD_DECK_COLORS, {}).items():
            totals[key] += stats.get("samples", 0) or 0
    all_samples = totals.pop(constants.FILTER_OPTION_ALL_DECKS, 0) or 1
    rates = dataset.get_color_ratings()
    meta = (getattr(dataset, "_dataset", None) or {}).get("meta", {})
    games = meta.get("game_count") or 0
    raw = {
        key: (n / all_samples, _float(rates.get(key)))
        for key, n in totals.items()
        if len(key) in (2, 3) and n > 0 and _float(rates.get(key)) > 0
    }
    weight = sum(share for share, _ in raw.values()) or 1.0
    avg = sum(share * wr for share, wr in raw.values()) / weight
    out = {}
    for key, (share, wr) in raw.items():
        n = share * games
        out[key] = (share, (n * wr + k * avg) / (n + k) if games else wr)
    return out


def gate_lane(main_colors, color_counts, archetypes):
    """The top two colors, or a triad with them that clears Draft Omen's gate.

    Returns (lane, [lane]) or (None, []) without two main colors.
    """
    if len(main_colors) < 2:
        return None, []
    pair = normalize_color_string("".join(main_colors[:2]))
    lane = pair
    triads = sum(share for key, (share, _) in archetypes.items() if len(key) == 3)
    if triads >= THREE_COLOR_MIN_SHARE and pair in archetypes:
        total = sum(color_counts.values()) or 1
        best = archetypes[pair][1]
        for key, (_, wr) in archetypes.items():
            if (
                len(key) == 3
                and set(pair) < set(key)
                and wr > best
                and all(
                    color_counts.get(c, 0) / total >= TRIAD_COLOR_MIN_WEIGHT
                    for c in key
                )
            ):
                lane, best = key, wr
    return lane, [lane]


def _do_gate(dataset):
    """Play a triad only when Draft Omen's three-color gate allows it."""
    archetypes = _cached("archetypes", dataset, archetype_win_rates)
    return _lane_variant(
        lambda adv: gate_lane(adv.main_colors, adv.color_counts, archetypes)
    )


# Cards within this many points of the top score count as a close pick.
CLOSE_PICK_POINTS = 3.0


def tiebreak(recs, pack, archetype):
    """Reorder close picks at the top by their win rate in the archetype.

    Cards within CLOSE_PICK_POINTS of the top score are re-sorted by GIH WR in
    the archetype (overall GIH WR without one) and placed just above the
    old top score, 0.01 apart, so the rest of the order is unchanged.
    """
    if not recs or recs[0].contextual_score <= 0:
        return recs
    top = recs[0].contextual_score
    close = [r for r in recs if r.contextual_score >= top - CLOSE_PICK_POINTS]
    if len(close) < 2:
        return recs
    cards = {c[constants.DATA_FIELD_NAME]: c for c in pack}

    def pair_wr(r):
        stats = cards.get(r.card_name, {}).get(constants.DATA_FIELD_DECK_COLORS, {})
        return _float(stats.get(archetype, {}).get("gihwr")) or r.base_win_rate

    close.sort(key=pair_wr, reverse=True)
    n = len(close)
    head = [
        r.model_copy(update={"contextual_score": round(top + 0.01 * (n - i), 2)})
        for i, r in enumerate(close)
    ]
    return head + recs[n:]


@contextlib.contextmanager
def _do_tiebreak(dataset):
    """Break close picks by the card's win rate in the drafter's pair."""
    evaluate = DraftAdvisor.evaluate_pack

    def patched(self, pack_cards, current_pick, current_pack=1):
        recs = evaluate(self, pack_cards, current_pick, current_pack)
        if len(self.main_colors) < 2:
            return recs
        return tiebreak(recs, pack_cards, self.main_archetype)

    with mock.patch.object(DraftAdvisor, "evaluate_pack", patched):
        yield


# --- Ablations ---------------------------------------------------------------

# Each switches off one piece of evaluate_pack by making its method return a
# neutral value, to see what the piece is worth: (method, neutral return).
ABLATIONS = {
    "no-bomb": ("_bomb_bonus", (0.0, 1.0)),
    "no-late-signal": ("_late_signal_bonus", (0.0, "")),
    "no-synergy": ("_archetype_synergy", (0.0, "")),
    "no-lane-mult": ("_lane_multiplier", 1.0),
    "no-vor": ("_vor_bonus", (0.0, ())),
    "no-castability": ("_calculate_castability_v5", (1.0, "")),
    "no-composition": ("_calculate_composition_bonus", (1.0, "")),
    "no-deck-improvement": ("_get_fast_best_deck_score", 0.0),
    "no-wheel": ("_check_relative_wheel", (1.0, "", 0.0)),
}


def _ablation(method, neutral):
    @contextlib.contextmanager
    def variant(dataset):
        with mock.patch.object(DraftAdvisor, method, lambda self, *a, **k: neutral):
            yield

    return variant


@contextlib.contextmanager
def _no_signal_tiebreak(dataset):
    """Drop the lane signals, which only feed the 1.05 signal tie-breaker."""
    init = DraftAdvisor.__init__

    def patched(self, *args, **kwargs):
        init(self, *args, **kwargs)
        self.signals = {}

    with mock.patch.object(DraftAdvisor, "__init__", patched):
        yield


def _combine(*names):
    """A variant that applies several others, in order."""

    @contextlib.contextmanager
    def combined(dataset):
        with contextlib.ExitStack() as stack:
            for name in names:
                stack.enter_context(VARIANTS[name](dataset))
            yield

    return combined


VARIANTS = {
    "baseline": _baseline,
    "arch-overall-pick": _arch_overall_pick,
    "arch-lane": _arch_lane,
    "arch-lane-soft": lambda dataset: _arch_lane(dataset, soft=True),
    "deck-refit": _deck_refit,
    "arch-shrink": _arch_shrink,
    "deck-refit-shrink": _combine("deck-refit", "arch-shrink"),
    "do-commit": _do_commit,
    "do-gate": _do_gate,
    "do-tiebreak": _do_tiebreak,
    # The gate goes first so the commitment multipliers use its lane.
    "do-all": _combine("do-gate", "do-commit", "do-tiebreak"),
}
VARIANTS |= {name: _ablation(*spec) for name, spec in ABLATIONS.items()}
VARIANTS["no-signal-tiebreak"] = _no_signal_tiebreak


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


def advisor_scores(recs):
    """{name: contextual score}, in the advisor's order (best first)."""
    scores = {}
    for r in recs:
        scores.setdefault(r.card_name, r.contextual_score)
    return scores


def blend_scores(recs, pack, weight):
    """{name: blended score} for the advisor/ATA blend with ATA weight."""
    scores = advisor_scores(recs)
    ata = {
        c[constants.DATA_FIELD_NAME]: _stat(c, constants.DATA_FIELD_ATA) for c in pack
    }
    names = list(scores)
    z_adv = _zscores([scores[n] for n in names])
    z_ata = _zscores([-(ata.get(n) or MISSING_ATA) for n in names])
    return {n: (1 - weight) * a + weight * t for n, a, t in zip(names, z_adv, z_ata)}


def blend_order(recs, pack, weight):
    """Names from recs, reordered by the advisor/ATA blend with ATA weight."""
    return _order(blend_scores(recs, pack, weight))


def _order(scores):
    """Names by score, best first; sorted is stable, so ties keep dict order."""
    return sorted(scores, key=lambda n: -scores[n])


def regret(scores, target):
    """How far below the method's top card the taken card scores, in pack SDs."""
    names = list(scores)
    z = dict(zip(names, _zscores([scores[n] for n in names])))
    return max(z.values()) - z[target]


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


def sample_drafts(path, n_drafts, shard=0, num_shards=1, final_only=False):
    """Pick n_drafts drafts uniformly at random (by hashed draft_id).

    Returns {draft_id: draft}, where a draft has "strong", its event result
    ("wins", "losses"), the drafter's "skill" (game win rate bucket) and
    "games" (games bucket), each None if missing, and a list of "picks"
    (pack, pick, picked name, pack names, pool names), in dump order. With
    final_only, "picks" stays empty and "final" holds the names in the final
    pool instead, which needs far less memory.
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
        i_wins = col.get("event_match_wins")
        i_losses = col.get("event_match_losses")

        def field(row, i):
            return _float(row[i], None) if i is not None else None

        def names(row, cols):
            return [
                n
                for i, n in cols
                if row[i] not in ("", "0")
                for _ in range(int(row[i]))
            ]

        # With final_only, the latest row of the draft being read: its pool
        # plus its pick is the final pool.
        last = None

        def finish():
            if last is not None and last[0] in drafts:
                drafts[last[0]]["final"] = names(last[2], pool_cols) + [last[2][i_name]]

        # Bottom-k by hash: a max-heap of (-priority, draft_id) for kept drafts.
        heap, drafts = [], {}
        current_id, keep = None, False
        for row in reader:
            draft_id = row[i_id]
            if draft_id != current_id:
                finish()
                last = None
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
                    drafts[draft_id] = {
                        "strong": strong,
                        "wins": field(row, i_wins),
                        "losses": field(row, i_losses),
                        "skill": field(row, i_wr),
                        "games": field(row, i_games),
                        "picks": [],
                    }
            if not keep:
                continue
            pack_no, pick_no = int(row[i_pack]), int(row[i_pick])
            if final_only:
                if last is None or (pack_no, pick_no) >= last[1]:
                    last = (draft_id, (pack_no, pick_no), row)
                continue
            drafts[draft_id]["picks"].append(
                (
                    pack_no,
                    pick_no,
                    row[i_name],
                    names(row, pack_cols),
                    names(row, pool_cols),
                )
            )
        finish()
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


def baseline_scores(pack):
    """{method: {name: score}} for the baselines, higher is better."""
    gihwr, ata = {}, {}
    for c in pack:
        name = c[constants.DATA_FIELD_NAME]
        gihwr[name] = _stat(c, constants.DATA_FIELD_GIHWR)
        ata[name] = -(_stat(c, constants.DATA_FIELD_ATA) or MISSING_ATA)
    return {"gihwr": gihwr, "ata": ata}


def _slices(pack_no, pick_no):
    """Buckets each pick is reported under (1-indexed pack and pick)."""
    phase = "picks 1-4" if pick_no <= 4 else "picks 5-8" if pick_no <= 8 else "picks 9+"
    return ["all", f"pack {pack_no}", phase]


DECK_SIZE = 23


# Adjustments calculate_holistic_score can add to the power from card ratings.
DECK_PARTS = (
    "curve",
    "aggro",
    "two_colors",
    "tribal",
    "domain",
    "greedy_mana",
    "evasion",
    "incomplete",
)


def pool_features(pool, metrics):
    """How strong a final pool is, by the advisor and by simpler yardsticks.

    Returns None for pools short of a deck. Otherwise a dict with the
    advisor's best-deck score ("deck_score") and its pieces ("power" from card
    ratings plus each of DECK_PARTS), the best deck's color count ("colors")
    and mean GIH WR over all decks ("deck_gihwr"), and "pool_gihwr": the mean
    GIH WR of the best 23 cards castable in one color pair (missing slots
    count as 0).
    """
    if len(pool) < DECK_SIZE:
        return None
    score, deck, colors = DraftAdvisor(metrics, pool)._get_fast_best_deck(
        pool, identify_top_pairs(pool, metrics)
    )
    features = {
        "deck_score": score,
        "power": None,
        "colors": None,
        "deck_gihwr": None,
    } | {k: 0.0 for k in DECK_PARTS}
    parts = holistic_score_parts(deck, colors, len(pool), metrics) if deck else None
    if parts:
        power, adjustments = parts
        features["power"] = power
        for key, delta, _ in adjustments:
            features[key] += delta
        features["colors"] = len(colors) if colors != ["All Decks"] else 5
        rates = [
            _stat(c, constants.DATA_FIELD_GIHWR)
            for c in deck
            if constants.CARD_TYPE_LAND not in c.get("types", [])
            for _ in range(c.get("count", 1))
        ]
        rates = [r for r in rates if r > 0]
        features["deck_gihwr"] = sum(rates) / len(rates) if rates else None
    best = 0.0
    for pair in itertools.combinations(constants.CARD_COLORS, 2):
        rates = sorted(
            (
                _stat(c, constants.DATA_FIELD_GIHWR)
                for c in pool
                if set(c.get(constants.DATA_FIELD_COLORS, [])) <= set(pair)
            ),
            reverse=True,
        )[:DECK_SIZE]
        best = max(best, sum(rates) / DECK_SIZE)
    features["pool_gihwr"] = best
    # Rounded so large runs' result files stay small.
    return {k: round(v, 4) if isinstance(v, float) else v for k, v in features.items()}


def pool_strength(pool, metrics):
    """(advisor deck score, pool GIH WR) for a final pool, or Nones if short."""
    features = pool_features(pool, metrics)
    if features is None:
        return None, None
    return features["deck_score"], features["pool_gihwr"]


class DraftScore:
    """Per-method agreement with one drafter, for relating to their result.

    For each method: picks scored, top-1 matches, and summed regret (how far
    below the method's favourite the taken card was, in pack SDs).
    """

    def __init__(self):
        self.methods = defaultdict(lambda: [0, 0, 0.0])

    def add(self, method, scores, target):
        d = self.methods[method]
        d[0] += 1
        d[1] += _order(scores)[0] == target
        d[2] += regret(scores, target)


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
    outcomes = []
    skipped = defaultdict(int)
    start = time.time()

    for n, (draft_id, draft) in enumerate(sorted(drafts.items()), 1):
        groups = ["all"] + (["strong"] if draft["strong"] else [])
        score = DraftScore()
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
                score.add(name, advisor_scores(recs), target)
                for b in blends:
                    weight = BLENDS[b](pk, pi, len(pool) + 1)
                    blended = blend_scores(recs, pack, weight)
                    rank = _rank_of(_order(blended), target)
                    for g in groups:
                        tally.add(f"{name}+{b}", g, slices, rank)
                    score.add(f"{name}+{b}", blended, target)
            for name, order in baseline_orders(pack).items():
                rank = _rank_of(order, target)
                for g in groups:
                    tally.add(name, g, slices, rank)
            for name, by_name in baseline_scores(pack).items():
                score.add(name, by_name, target)

        features = None
        if draft["picks"]:
            # The pool before the last pick, plus the last pick.
            features = pool_features(pool + resolver.cards([picked]), metrics)
        outcomes.append(_outcome(draft, features) | {"methods": dict(score.methods)})

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
        "outcomes": outcomes,
    }


def _outcome(draft, features):
    """A draft's result plus its final pool's features (None if no pool)."""
    return {k: draft.get(k) for k in ("strong", "wins", "losses", "skill", "games")} | (
        features or {"deck_score": None, "pool_gihwr": None}
    )


def score_pools(drafts, dataset, progress_every=0):
    """Score only each draft's final pool, for relating pool strength to wins.

    Much faster than replay(): there is no advice per pick. Drafts need
    "final" (the names in the final pool), as sampled with final_only=True.
    """
    metrics = SetMetrics(dataset)
    resolver = NameResolver(dataset)
    outcomes = []
    start = time.time()
    patch = mock.patch.object(deck_builder, "stack_cards", _fast_stack_cards)
    with patch:
        for n, (_, draft) in enumerate(sorted(drafts.items()), 1):
            pool = resolver.cards(draft.get("final", []))
            outcomes.append(_outcome(draft, pool_features(pool, metrics)))
            if progress_every and n % progress_every == 0:
                print(
                    f"{n}/{len(drafts)} pools, {time.time() - start:.0f}s",
                    file=sys.stderr,
                    flush=True,
                )
    return {
        "drafts": len(drafts),
        "strong_drafts": sum(d["strong"] for d in drafts.values()),
        "seconds": round(time.time() - start, 1),
        "skipped": {},
        "unmatched_names": dict(
            sorted(resolver.missing.items(), key=lambda x: -x[1])[:20]
        ),
        "tally": {},
        "outcomes": outcomes,
    }


# --- Reporting -------------------------------------------------------------


def merge(results):
    total = {"drafts": 0, "strong_drafts": 0, "tally": {}, "outcomes": []}
    for r in results:
        total["drafts"] += r["drafts"]
        total["strong_drafts"] += r["strong_drafts"]
        code = _set_code(r.get("dump", ""))
        total["outcomes"] += [o | {"set": code} for o in r.get("outcomes", [])]
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


OUTCOME_MIN_DRAFTS = 30


def _complete(o):
    """Finished events only, so wins are not cut short by the dump date."""
    return o.get("wins") == 7 or o.get("losses") == 3


def _dummies(values):
    """Indicator columns for each value but the first (sorted)."""
    levels = sorted(set(values), key=str)[1:]
    return [[float(v == level) for v in values] for level in levels]


def _skill_bin(skill):
    if skill is None:
        return None
    return int((min(max(skill, 0.30), 0.74) - 0.30) // 0.04)


BOOTSTRAP_SAMPLES = 200


def _controls(outcomes, skill=True):
    """Intercept plus set (and, with skill, skill and games bucket) dummies."""
    columns = _dummies([o.get("set") for o in outcomes])
    if skill:
        columns += _dummies([_skill_bin(o.get("skill")) for o in outcomes])
        columns += _dummies([o.get("games") for o in outcomes])
    return np.column_stack([np.ones(len(outcomes)), *columns])


def _wins(outcomes):
    return np.array([o["wins"] for o in outcomes], dtype=float)


def wins_fit(outcomes, columns, skill=True):
    """OLS of event wins on columns plus controls: [(coefficient, robust SE)]."""
    X = np.column_stack([*columns, _controls(outcomes, skill)])
    y = _wins(outcomes)
    xtx_inv = np.linalg.pinv(X.T @ X)
    beta = xtx_inv @ X.T @ y
    resid = y - X @ beta
    # HC1 (heteroskedasticity-robust) standard errors.
    meat = (X * resid[:, None] ** 2).T @ X
    cov = xtx_inv @ meat @ xtx_inv * len(y) / max(1, len(y) - X.shape[1])
    return [(beta[i], math.sqrt(max(cov[i, i], 0.0))) for i in range(len(columns))]


def wins_regression(outcomes, x, extra=()):
    """(coefficient, robust SE) for x, controlling for extra columns too."""
    return wins_fit(outcomes, [x, *extra])[0]


def bootstrap_differences(outcomes, xs, ref, samples=BOOTSTRAP_SAMPLES, seed=0):
    """Bootstrap SE of each method's wins coefficient minus ref's.

    xs is {method: column}. All methods are fit on the same resampled drafts,
    so the SE accounts for their coefficients being correlated.
    """
    y, controls = _wins(outcomes), _controls(outcomes)
    designs = {m: np.column_stack([x, controls]) for m, x in xs.items()}
    rng = np.random.default_rng(seed)
    diffs = defaultdict(list)
    for _ in range(samples):
        idx = rng.integers(0, len(y), len(y))
        coef = {
            m: np.linalg.lstsq(X[idx], y[idx], rcond=None)[0][0]
            for m, X in designs.items()
        }
        for m in xs:
            diffs[m].append(coef[m] - coef[ref])
    return {m: float(np.std(d)) for m, d in diffs.items()}


def format_outcomes(result, sets=None):
    """Markdown table relating each method's agreement with the drafter to wins.

    A drafter's regret under a method is how far below that method's favourite
    their picks were, on average. If a method knows better picks, drafters who
    stray from it should win less, after controlling for drafter skill.
    """
    outcomes = [o for o in result.get("outcomes", []) if _complete(o)]
    methods = sorted(
        (
            set.intersection(*(set(o.get("methods", {})) for o in outcomes))
            if outcomes
            else ()
        ),
        key=_method_order,
    )
    outcomes = [o for o in outcomes if all(o["methods"][m][0] for m in methods)]
    if len(outcomes) < OUTCOME_MIN_DRAFTS or not methods:
        return ""

    def column(m, i):
        return np.array([o["methods"][m][i] / o["methods"][m][0] for o in outcomes])

    def cell(coef_se, scale):
        coef, se = coef_se
        return f"{coef * scale:+.3f} ({se * scale:.3f})"

    ata_regret = column("ata", 2) if "ata" in methods else None
    if ata_regret is not None and not ata_regret.std():
        ata_regret = None
    title = f"{', '.join(sets)}: " if sets else ""
    lines = [
        f"{title}{len(outcomes)} complete events. Event wins regressed on how "
        "closely the drafter followed each method, controlling for skill bucket, "
        "games bucket and set. Cells are Δwins (robust SE); negative regret "
        "and positive agreement mean following the method went with winning.",
        "",
        "| method | per +1 SD regret | vs first (bootstrap SE) "
        "| same, controlling for ATA regret | per +10 pts top-1 agreement |",
        "|---|---|---|---|---|",
    ]
    # Regret in SD units, so coefficients are comparable across methods.
    scaled = {}
    for m in methods:
        regret_x = column(m, 2)
        if regret_x.std():
            scaled[m] = regret_x / regret_x.std()
    ref = next(iter(scaled), None)
    fits = {m: wins_regression(outcomes, x) for m, x in scaled.items()}
    diff_se = bootstrap_differences(outcomes, scaled, ref) if ref else {}
    for m in methods:
        if m not in scaled:
            lines.append(f"| {m} | – | – | – | – |")
            continue
        diff = (
            f"{fits[m][0] - fits[ref][0]:+.3f} ({diff_se[m]:.3f})" if m != ref else "–"
        )
        controlled = (
            cell(wins_regression(outcomes, scaled[m], [ata_regret]), 1)
            if ata_regret is not None and m != "ata"
            else "–"
        )
        lines.append(
            f"| {m} | {cell(fits[m], 1)} | {diff} | {controlled} "
            f"| {cell(wins_regression(outcomes, column(m, 1)), 0.1)} |"
        )
    return "\n".join(lines)


CALIBRATION_BINS = 10


def _within_set(outcomes, key, fn):
    """fn(values) applied to key's values separately within each set."""
    out = np.zeros(len(outcomes))
    by_set = defaultdict(list)
    for i, o in enumerate(outcomes):
        by_set[o.get("set")].append(i)
    for idx in by_set.values():
        out[idx] = fn(np.array([outcomes[i][key] for i in idx], dtype=float))
    return out


def _zscore_array(v):
    return (v - v.mean()) / (v.std() or 1.0)


def _decile(v):
    ranks = v.argsort().argsort()
    return ranks * CALIBRATION_BINS // len(v)


def format_calibration(result, sets=None):
    """Markdown tables: does the advisor's score for the final pool track wins?

    Pools are binned by deck score within each set (the scale differs between
    sets). Pool GIH WR is a simple yardstick the deck score should beat.
    """
    outcomes = [
        o
        for o in result.get("outcomes", [])
        if _complete(o) and o.get("deck_score") is not None
    ]
    if len(outcomes) < OUTCOME_MIN_DRAFTS:
        return ""
    deck_z = _within_set(outcomes, "deck_score", _zscore_array)
    gihwr_z = _within_set(outcomes, "pool_gihwr", _zscore_array)
    bins = _within_set(outcomes, "deck_score", _decile)
    wins = _wins(outcomes)
    losses = np.array([o["losses"] for o in outcomes], dtype=float)
    deck = np.array([o["deck_score"] for o in outcomes])
    pool_gihwr = np.array([o["pool_gihwr"] for o in outcomes])
    title = f"{', '.join(sets)}: " if sets else ""
    lines = [
        f"{title}{len(outcomes)} complete events. Final pools binned by the "
        "advisor's deck score (deciles within each set).",
        "",
        "| decile | mean deck score | mean pool GIH WR | events | mean wins "
        "| match win % |",
        "|---|---|---|---|---|---|",
    ]
    for b in range(CALIBRATION_BINS):
        sel = bins == b
        if not sel.any():
            continue
        games = wins[sel].sum() + losses[sel].sum()
        lines.append(
            f"| {b + 1} | {deck[sel].mean():.1f} | {pool_gihwr[sel].mean():.1f} "
            f"| {int(sel.sum())} | {wins[sel].mean():.2f} "
            f"| {100 * wins[sel].sum() / games:.1f} |"
        )

    def cell(coef_se):
        return f"{coef_se[0]:+.3f} ({coef_se[1]:.3f})"

    lines += [
        "",
        "Δwins per +1 SD (within set), robust SE. Skill controls are the "
        "win-rate and games buckets; all fits control for set.",
        "",
        "| pool score | alone | alone, with skill controls "
        "| together, with skill controls |",
        "|---|---|---|---|",
    ]
    together = wins_fit(outcomes, [deck_z, gihwr_z])
    for i, (name, x) in enumerate(
        [("advisor deck score", deck_z), ("pool GIH WR", gihwr_z)]
    ):
        lines.append(
            f"| {name} | {cell(wins_fit(outcomes, [x], skill=False)[0])} "
            f"| {cell(wins_fit(outcomes, [x])[0])} | {cell(together[i])} |"
        )
    return "\n".join(lines)


# Yardsticks outside the deck score, tested alongside its pieces.
DECK_EXTRAS = ("deck_gihwr", "pool_gihwr")
DECK_PART_LABELS = {
    "power": "power from card ratings",
    "curve": "curve / land penalty",
    "aggro": "aggro curve bonus",
    "two_colors": "two-color bonus",
    "tribal": "tribal bonus",
    "domain": "domain bonus",
    "greedy_mana": "greedy mana penalty",
    "evasion": "evasion penalty",
    "incomplete": "incomplete deck penalty",
    "deck_gihwr": "deck mean GIH WR",
    "pool_gihwr": "pool GIH WR (best pair)",
}


def _column(outcomes, key):
    return np.array([o[key] for o in outcomes], dtype=float)


def _varying(outcomes, keys):
    """The keys whose values vary within at least one set."""
    by_set = defaultdict(list)
    for o in outcomes:
        by_set[o.get("set")].append(o)
    return [
        k for k in keys if any(_column(group, k).std() > 0 for group in by_set.values())
    ]


def _refit_scores(train, test, keys):
    """Score test pools with the weights wins put on keys in train."""
    weights = [c for c, _ in wins_fit(train, [_column(train, k) for k in keys])]
    return sum(w * _column(test, k) for w, k in zip(weights, keys))


def format_deck_parts(result, sets=None):
    """Markdown tables: which pieces of the advisor's deck score predict wins?

    Each piece is in score points, so if the score were well weighted every
    piece would be worth as many wins per point as the power from card
    ratings. With 3+ sets, pieces are also reweighted on all sets but one and
    the reweighted score is tested on the held-out set.
    """
    outcomes = [
        o
        for o in result.get("outcomes", [])
        if _complete(o)
        and o.get("power") is not None
        and o.get("deck_gihwr") is not None
    ]
    if len(outcomes) < OUTCOME_MIN_DRAFTS:
        return ""
    parts = _varying(outcomes, ("power",) + DECK_PARTS)
    extras = _varying(outcomes, DECK_EXTRAS)
    alone = dict(zip(parts, wins_fit(outcomes, [_column(outcomes, k) for k in parts])))
    both = dict(
        zip(
            parts + extras,
            wins_fit(outcomes, [_column(outcomes, k) for k in parts + extras]),
        )
    )
    power = alone.get("power", (0.0, 0.0))[0]

    def cell(coef_se):
        return f"{coef_se[0]:+.4f} ({coef_se[1]:.4f})"

    title = f"{', '.join(sets)}: " if sets else ""
    lines = [
        f"{title}{len(outcomes)} complete events. Event wins regressed on the "
        "pieces of the final pool's deck score (in score points), controlling "
        "for skill bucket, games bucket and set. A well-weighted piece is worth "
        "as much per point as the power from card ratings (ratio 1).",
        "",
        "| piece | applies | mean when applied | Δwins per point (robust SE) "
        "| ratio to power | with GIH WR yardsticks added |",
        "|---|---|---|---|---|---|",
    ]
    for k in ("power",) + DECK_PARTS + DECK_EXTRAS:
        if k not in parts and k not in extras:
            continue
        x = _column(outcomes, k)
        applied = x != 0
        ratio = (
            f"{alone[k][0] / power:+.2f}"
            if k in alone and power and k != "power"
            else "–"
        )
        lines.append(
            f"| {DECK_PART_LABELS[k]} "
            f"| {100 * applied.mean():.1f}% | {x[applied].mean():+.1f} "
            f"| {cell(alone[k]) if k in alone else '–'} | {ratio} | {cell(both[k])} |"
        )

    by_set = defaultdict(list)
    for o in outcomes:
        by_set[o["set"]].append(o)
    if len(by_set) < 3:
        return "\n".join(lines)

    # Leave one set out: weights from the other sets, tested on this one.
    scores = {
        "advisor deck score": lambda train, test: _column(test, "deck_score"),
        "pool GIH WR": lambda train, test: _column(test, "pool_gihwr"),
        "reweighted pieces": lambda train, test: _refit_scores(train, test, parts),
        "reweighted pieces + yardsticks": lambda train, test: _refit_scores(
            train, test, parts + extras
        ),
    }
    held_out = {name: np.zeros(len(outcomes)) for name in scores}
    index = {id(o): i for i, o in enumerate(outcomes)}
    lines += [
        "",
        "Held-out sets: weights fit on every other set. Δwins per +1 SD of "
        "each score (within set), with skill controls, robust SE.",
        "",
        "| held-out set | " + " | ".join(scores) + " |",
        "|---|" + "---|" * len(scores),
    ]
    for code, test in sorted(by_set.items()):
        train = [o for o in outcomes if o["set"] != code]
        idx = [index[id(o)] for o in test]
        cells = []
        for name, fn in scores.items():
            z = _zscore_array(fn(train, test))
            held_out[name][idx] = z
            cells.append(f"{wins_fit(test, [z])[0][0]:+.3f}")
        lines.append(f"| {code} | " + " | ".join(cells) + " |")
    fits = [wins_fit(outcomes, [z])[0] for z in held_out.values()]
    lines.append(
        "| all | " + " | ".join(f"{c:+.3f} ({se:.3f})" for c, se in fits) + " |"
    )
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

    pools = sub.add_parser(
        "pools", help="Score only final pools, for relating pool strength to wins."
    )
    pools.add_argument(
        "--dump", required=True, help="17Lands draft_data_public CSV(.gz)"
    )
    pools.add_argument(
        "--dataset", required=True, help="App dataset JSON(.gz) for the set"
    )
    pools.add_argument("--drafts", type=int, default=2000)
    pools.add_argument("--shard", type=int, default=0)
    pools.add_argument("--num-shards", type=int, default=1)
    pools.add_argument("--out", help="Write results JSON here")
    pools.add_argument("--progress", type=int, default=500, help="Report every N pools")

    summ = sub.add_parser("summarize", help="Merge result files into a table.")
    summ.add_argument("results", nargs="+")
    summ.add_argument("--per-set", action="store_true", help="Also print each set")

    args = parser.parse_args(argv)
    logging.disable(logging.WARNING)

    if args.command in ("run", "pools"):
        t = time.time()
        drafts = sample_drafts(
            args.dump,
            args.drafts,
            args.shard,
            args.num_shards,
            final_only=args.command == "pools",
        )
        print(
            f"Sampled {len(drafts)} drafts in {time.time() - t:.0f}s", file=sys.stderr
        )
        if args.command == "pools":
            result = score_pools(drafts, load_dataset(args.dataset), args.progress)
        else:
            result = replay(
                drafts,
                load_dataset(args.dataset),
                args.variant or ["baseline"],
                args.progress,
                blends=args.blend,
            )
            result["variants"] = args.variant or ["baseline"]
            result["blends"] = args.blend
        result["dump"] = os.path.basename(args.dump)
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(result, f, separators=(",", ":"))
        print(_report(merge([result]), [_set_code(result["dump"])]))
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
                print(_report(merge(rs), [code]) + "\n")
        print(_report(merge(results), sorted(by_set)))


def _report(result, sets):
    """Every table that has data for this merged result."""
    tables = [
        format_table(result, sets) if result["tally"] else "",
        format_outcomes(result, sets),
        format_calibration(result, sets),
        format_deck_parts(result, sets),
    ]
    return "\n\n".join(t for t in tables if t)


def _set_code(dump_name):
    """draft_data_public.FRA.PremierDraft.csv.gz -> FRA"""
    parts = dump_name.split(".")
    return parts[1] if len(parts) > 2 else dump_name or "?"


if __name__ == "__main__":
    main()
