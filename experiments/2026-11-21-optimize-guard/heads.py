"""Auto-Optimize three ways on real played decks.

    python experiments/2026-11-21-optimize-guard/heads.py --src . --decks decks.json.gz \
        --games games.json.gz --dataset FRA_PremierDraft_All_Data.json.gz \
        --set FRA --first 20000 --out heads/FRA.json.gz

For each sampled 40-card deck and its sideboard, as Tools/DeckScoreFit/buttons.py
on fork branch exp/optimize-power-only did it (same filters, same held-out
ratings, same deck score):

- base: today's main button (main_button.py, a verbatim copy), which simulates
  up to six kinds of one-card swap and keeps the best by a weighted fitness;
- no-guard: the Power Up swap whenever there is one (src with _EXP_GUARD off);
- guard: the Power Up swap only if the incoming spell rates strictly higher
  (src as on simplify/optimize-power-up).

The two Power Up heads don't use the simulator to choose, so their display
simulation is skipped here. See PROTOCOL.md.
"""

import argparse
import gzip
import json
import multiprocessing
import os
import sys
import time
from collections import Counter
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
sys.path.insert(0, HERE)

from builds import Held  # noqa: E402
from features import BASICS, POOL_SIZE, App  # noqa: E402
from games import fold_of  # noqa: E402
from quality import training  # noqa: E402

HEADS = ("base", "no-guard", "guard")


def swap_kind(note):
    """The optimizer's note without its cards: "Power Up", "Play 16 Lands"."""
    text = note.removeprefix("Optimized: ")
    return text.split(" (")[0]


class Heads:
    """The three versions of the button, from the src/ on sys.path."""

    def __init__(self):
        from src import constants
        from src.advisor import deck_builder, deck_scorer, mana_base
        from src.utils import normalize_color_string

        import main_button

        self.constants, self.scorer = constants, deck_scorer
        self.builder, self.mana, self.main = deck_builder, mana_base, main_button
        self.normalize = normalize_color_string

    def is_basic(self, card):
        return (
            "Basic" in card.get("types", [])
            or card.get("name") in self.constants.BASIC_LANDS
        )

    def has_basics(self, deck):
        """buttons.py's filter: decks with spells and basics."""
        spells = [c for c in deck if "Land" not in c.get("types", [])]
        return bool(spells) and any(
            self.is_basic(c) for c in deck if "Land" in c.get("types", [])
        )

    def score(self, deck, metrics):
        spells = [c for c in deck if "Land" not in c.get("types", [])]
        colors = self.mana.get_strict_colors(spells)
        return self.scorer.calculate_holistic_score(deck, colors, POOL_SIZE, metrics)[0]

    def power_up(self, deck, sideboard, key, colors, guard):
        self.builder._EXP_GUARD = guard
        try:
            with patch.object(self.builder, "simulate_deck", lambda *a, **k: {}):
                return self.builder.optimize_deck(deck, sideboard, key, colors)
        finally:
            self.builder._EXP_GUARD = True

    def optimize(self, deck, sideboard, metrics):
        spells = [c for c in deck if "Land" not in c.get("types", [])]
        colors = self.mana.get_strict_colors(spells)
        key = self.normalize("".join(colors[:2])) if colors else "All Decks"
        after, _, stats, note = self.main.optimize_deck(deck, sideboard, key, colors)
        if stats is None:
            return None
        lands = lambda cards: sum(  # noqa: E731
            c.get("count", 1) for c in cards if "Land" in c.get("types", [])
        )
        out = {
            "score_before": round(self.score(deck, metrics), 3),
            "base": {
                "kind": swap_kind(note),
                "score_after": round(self.score(after, metrics), 3),
                "land_change": lands(after) - lands(deck),
            },
        }
        for name, guard in (("no-guard", False), ("guard", True)):
            v_after, _, _, v_note = self.power_up(deck, sideboard, key, colors, guard)
            out[name] = {
                "kind": "Power Up" if "Power Up" in v_note else "Base Deck",
                "score_after": round(self.score(v_after, metrics), 3),
            }
        return out


def with_ratings(cards, names, held):
    return [dict(c, deck_colors=held.stats.get(n, {})) for n, c in zip(names, cards)]


def deck_row(app, heads, helds, d):
    """A deck's result row, or the reason it has none (as buttons.py)."""
    if sum(d["cards"].values()) != 40:
        return "not 40 cards"
    held = helds[fold_of(d["id"])]
    sideboard_names = {n: c for n, c in d["sideboard"].items() if n not in BASICS}
    deck, sideboard = app.deck(d["cards"]), app.deck(sideboard_names)
    if deck is None or sideboard is None:
        return "card not in dataset"
    deck = with_ratings(deck, d["cards"], held)
    sideboard = with_ratings(sideboard, sideboard_names, held)
    if not heads.has_basics(deck):
        return "no basics"
    features = heads.scorer.deck_features(
        deck, list(d["main_colors"] + d["splash_colors"]), POOL_SIZE, held
    )
    if features is None:
        return "no spells"
    return {"id": d["id"], "optimize": heads.optimize(deck, sideboard, held)}


_WORKER = {}


def _setup(dataset, folds):
    app = App(dataset)
    heads = Heads()
    s = heads.scorer
    win_points_per_sd = 25.0 * s.WIN_LOG_ODDS_PER_POINT * s.WEIGHTS["card_quality"]
    helds = [Held(training(folds, {i}), win_points_per_sd) for i in range(len(folds))]
    return app, heads, helds


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
