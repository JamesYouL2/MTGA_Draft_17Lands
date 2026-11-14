"""Run the Custom Deck window's two simulator buttons on real played decks.

    python Tools/DeckScoreFit/buttons.py --src . --decks decks.json.gz \
        --games games.json.gz --dataset FRA_PremierDraft_All_Data.json.gz \
        --set FRA --out results/FRA.json.gz

For each sampled 40-card deck:

- **Auto lands.** The deck keeps its spells and nonbasic lands, and its basics
  are chosen again three ways: by the app's rule (calculate_dynamic_mana_base),
  by the button's simulation around that rule (brute_force_mana_base), and in
  proportion to the spells' colored pips. Each is kept next to the basics the
  drafter played.
- **Auto optimize.** The deck and its sideboard go through optimize_deck(), as
  the button does it. The swap it picks is kept, with the deck score before
  and after.

Cards carry win rates with the deck's own fold left out, as in builds.py. See
experiments/2026-11-13-builder-leftovers/PROTOCOL.md.
"""

import argparse
import gzip
import json
import multiprocessing
import os
import sys
import time
from collections import Counter

from builds import Held
from features import BASICS, POOL_SIZE, App
from games import fold_of
from quality import training

COLORS = "WUBRG"


def split_of(lands):
    """Basic lands as counts in WUBRG order."""
    counts = Counter()
    for land in lands:
        color = (land.get("colors") or [""])[0]
        counts[color] += land.get("count", 1)
    return [counts[c] for c in COLORS]


def proportional(pips, n):
    """n basics split in proportion to the colored pips, WUBRG order: whole
    shares first, then the largest remainders, the color with more pips first."""
    total = sum(pips)
    if not total or n <= 0:
        return [0] * len(pips)
    shares = [n * p / total for p in pips]
    split = [int(s) for s in shares]
    order = sorted(range(len(pips)), key=lambda i: (split[i] - shares[i], -pips[i]))
    for i in order[: n - sum(split)]:
        split[i] += 1
    return split


def swap_kind(note):
    """The optimizer's note without its cards: "Power Up", "Play 16 Lands"."""
    text = note.removeprefix("Optimized: ")
    return text.split(" (")[0]


class Buttons:
    """The app's two buttons, from the src/ on sys.path."""

    def __init__(self):
        from src import constants
        from src.advisor import deck_builder, deck_scorer, mana_base
        from src.mana_cost import mana_color_demand
        from src.utils import normalize_color_string

        self.constants, self.scorer = constants, deck_scorer
        self.builder, self.mana = deck_builder, mana_base
        self.demand, self.normalize = mana_color_demand, normalize_color_string

    def is_basic(self, card):
        return "Basic" in card.get("types", []) or card.get("name") in self.constants.BASIC_LANDS

    def lands(self, deck):
        """What Auto lands would choose for the deck's basics, three ways, next
        to what was played. None if the deck has no basics to choose."""
        spells = [c for c in deck if "Land" not in c.get("types", [])]
        lands = [c for c in deck if "Land" in c.get("types", [])]
        basics = [c for c in lands if self.is_basic(c)]
        others = [c for c in lands if not self.is_basic(c)]
        needed = sum(c.get("count", 1) for c in basics)
        if not spells or not needed:
            return None
        colors = self.mana.get_strict_colors(spells) or list(COLORS)
        pips = self.demand(spells, colors)
        return {
            "played": split_of(basics),
            "rule": split_of(
                self.mana.calculate_dynamic_mana_base(spells, others, colors, needed)
            ),
            "simulated": split_of(
                self.mana.brute_force_mana_base(spells, others, colors, needed)
            ),
            "pips": proportional([pips[c] for c in COLORS], needed),
        }

    def score(self, deck, metrics):
        spells = [c for c in deck if "Land" not in c.get("types", [])]
        colors = self.mana.get_strict_colors(spells)
        return self.scorer.calculate_holistic_score(deck, colors, POOL_SIZE, metrics)[0]

    def optimize(self, deck, sideboard, metrics):
        """The swap Auto optimize picks, and what it does to the deck."""
        spells = [c for c in deck if "Land" not in c.get("types", [])]
        colors = self.mana.get_strict_colors(spells)
        key = self.normalize("".join(colors[:2])) if colors else "All Decks"
        after, _, stats, note = self.builder.optimize_deck(deck, sideboard, key, colors)
        if stats is None:
            return None
        lands = lambda cards: sum(  # noqa: E731
            c.get("count", 1) for c in cards if "Land" in c.get("types", [])
        )
        return {
            "kind": swap_kind(note),
            "score_before": round(self.score(deck, metrics), 3),
            "score_after": round(self.score(after, metrics), 3),
            "lands_before": lands(deck),
            "lands_after": lands(after),
        }


def with_ratings(cards, names, held):
    return [dict(c, deck_colors=held.stats.get(n, {})) for n, c in zip(names, cards)]


def deck_row(app, buttons, helds, d):
    """A deck's result row, or the reason it has none."""
    if sum(d["cards"].values()) != 40:
        return "not 40 cards"
    held = helds[fold_of(d["id"])]
    sideboard_names = {n: c for n, c in d["sideboard"].items() if n not in BASICS}
    deck, sideboard = app.deck(d["cards"]), app.deck(sideboard_names)
    if deck is None or sideboard is None:
        return "card not in dataset"
    deck = with_ratings(deck, d["cards"], held)
    sideboard = with_ratings(sideboard, sideboard_names, held)
    lands = buttons.lands(deck)
    if lands is None:
        return "no basics"
    features = buttons.scorer.deck_features(
        deck, list(d["main_colors"] + d["splash_colors"]), POOL_SIZE, held
    )
    if features is None:
        return "no spells"
    return {
        "id": d["id"],
        "main": d["main_colors"],
        "splash": d["splash_colors"],
        "skill": d["skill"],
        "experience": d["experience"],
        "wins": d["wins"],
        "games": d["games"],
        "quality": round(features["card_quality"], 4),
        "lands": lands,
        "optimize": buttons.optimize(deck, sideboard, held),
    }


_WORKER = {}


def _setup(dataset, folds):
    """One process's app, buttons and held-out ratings."""
    app = App(dataset)
    buttons = Buttons()
    s = buttons.scorer
    # Win rate points a deck's card quality is priced at per SD, near 50%.
    win_points_per_sd = 25.0 * s.WIN_LOG_ODDS_PER_POINT * s.WEIGHTS["card_quality"]
    helds = [Held(training(folds, {i}), win_points_per_sd) for i in range(len(folds))]
    return app, buttons, helds


def _init_worker(dataset, folds):
    _WORKER["state"] = _setup(dataset, folds)


def _work(d):
    return deck_row(*_WORKER["state"], d)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--src", required=True, help="The copy of the app to use")
    parser.add_argument("--decks", required=True, help="From decks.py (.json.gz)")
    parser.add_argument("--games", required=True, help="From games.py (.json.gz)")
    parser.add_argument("--dataset", required=True, help="The app's set data")
    parser.add_argument("--set", required=True, help="Set code")
    parser.add_argument("--out", required=True, help="Where to write them (.json.gz)")
    parser.add_argument("--first", type=int, default=None, help="Use only this many decks")
    parser.add_argument("--workers", type=int, default=os.cpu_count())
    args = parser.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.src))
    with gzip.open(args.decks, "rt", encoding="utf-8") as f:
        decks = json.load(f)[: args.first]
    with gzip.open(args.games, "rt", encoding="utf-8") as f:
        folds = json.load(f)["folds"]

    from src.advisor import deck_scorer

    started = time.time()
    rows, skipped = [], Counter()
    with multiprocessing.get_context("fork").Pool(
        args.workers, _init_worker, (args.dataset, folds)
    ) as workers:
        for row in workers.imap_unordered(_work, decks, chunksize=10):
            if isinstance(row, str):
                skipped[row] += 1
            else:
                rows.append(row)
    rows.sort(key=lambda r: r["id"])
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump(
            {
                "set": args.set,
                "skipped": dict(skipped),
                # Win rate points a point of deck score is worth, near 50%.
                "win_points_per_score": 25.0 * deck_scorer.WIN_LOG_ODDS_PER_POINT,
                "rows": rows,
            },
            f,
        )
    print(
        f"{args.set}: {len(rows)} decks, skipped {dict(skipped)}, "
        f"{time.time() - started:.0f}s on {args.workers} workers"
    )


if __name__ == "__main__":
    main()
