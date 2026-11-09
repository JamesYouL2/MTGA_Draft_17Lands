"""Run the real deck builder on real pools, under versions of it.

    python Tools/DeckScoreFit/builds.py --src . --decks decks.json.gz \
        --games games.json.gz --dataset FRA_PremierDraft_All_Data.json.gz \
        --set FRA --out results/FRA.json.gz

A pool is a sampled deck's cards plus its sideboard, without basics. Each pool
goes through suggest_deck() once per version. Its cards carry win rates from
games.py's counts with the pool's own fold left out, gated at 500 games in hand
as 17Lands does, so no pool's results are in its own ratings. The app's dataset
only supplies the rest of each card.

The simulator's mana penalties are off: the simulator is random, and those
penalties are already judged not worth keeping (exp/mana-penalties). Builds are
the same in every version that doesn't change them, so each pool builds each
deck once. See experiments/2026-11-08-deck-score-rating/PROTOCOL.md.
"""

import argparse
import gzip
import hashlib
import json
import multiprocessing
import os
import sys
import time
from collections import Counter

from features import BASICS, App
from games import fold_of
from quality import ALL, Ratings, training

# A draft is 42 or 45 picks, some of them basics. Less than this is missing cards.
MIN_POOL = 35
BUILDERS = (
    "build_variant_consistency",
    "build_variant_greedy",
    "build_variant_curve",
    "build_variant_soup",
)


def _game_rate(cards):
    """Win rate in points over a group's card-games. Each game counts once per
    card in its deck, about the same number for every deck."""
    wins = sum(s[1] + s[4] for s in cards.values())
    games = sum(s[0] + s[3] for s in cards.values())
    return 100.0 * wins / games if games else None


class Held:
    """What the app reads for one fold's pools, from the other folds' games.

    It stands in for the app's SetMetrics, and adds what a pair baseline needs:
    shifts[kind][pair] moves a card's rating (overall or blend) so that the
    pair's average card has the set's average rating, plus the pair's win rate
    edge over the set's converted at the deck score's own price of a rating
    point. So between pairs, the score then moves as the pairs' results do.
    """

    def __init__(self, counts, win_points_per_sd):
        ratings = Ratings(counts)
        self.mean, self.std = ratings.mean, ratings.std
        self.stats = {}
        for colors, cards in counts.items():
            for name in cards:
                wr = ratings.pair(name, colors)[0]
                if wr is not None:
                    self.stats.setdefault(name, {})[colors] = {"gihwr": wr}
        self.shifts = {"overall": {}, "blend": {}}
        everything = counts.get(ALL, {})
        price = win_points_per_sd / self.std
        rated = [
            (s[0], wr) for n, s in everything.items()
            if (wr := ratings.overall(n)) is not None
        ]
        total = sum(w for w, _ in rated)
        if not total:
            return
        center = sum(w * wr for w, wr in rated) / total
        set_rate = _game_rate(everything)
        for pair, cards in counts.items():
            if pair == ALL or len(pair) != 2:
                continue
            means = _pair_means(ratings, pair, cards)
            if means is None:
                continue
            baseline = (_game_rate(cards) - set_rate) / price
            for kind, mean in means.items():
                self.shifts[kind][pair] = center - mean + baseline

    def get_metrics(self, color, field):
        return self.mean, self.std


def _pair_means(ratings, pair, cards):
    """The games-in-hand average of each kind of rating over a pair's cards."""
    total = overall = blend = 0.0
    for name, s in cards.items():
        g = ratings.overall(name)
        if g is None:
            continue
        a = ratings.pair(name, pair)[0]
        total += s[0]
        overall += s[0] * g
        blend += s[0] * (0.7 * a + 0.3 * g if a is not None else g)
    return {"overall": overall / total, "blend": blend / total} if total else None


def signature(deck):
    """A short name for a deck's exact cards."""
    text = "|".join(sorted(f"{c['name']}:{c.get('count', 1)}" for c in deck))
    return hashlib.sha1(text.encode()).hexdigest()[:8]


class Engine:
    """The app's deck builder, patched per version. Patches module globals, so
    it stays in one process."""

    def __init__(self):
        from src.advisor import deck_builder, deck_scorer
        from src.utils import normalize_color_string

        self.builder, self.scorer = deck_builder, deck_scorer
        self.normalize = normalize_color_string
        self.original_rating = deck_scorer.get_card_rating
        self.memo = {}
        self.saved = {
            name: getattr(deck_builder, name)
            for name in (*BUILDERS, "simulate_deck", "get_sideboard")
        }
        for name in BUILDERS:
            setattr(deck_builder, name, self._remembered(self.saved[name]))
        deck_builder.simulate_deck = lambda *args, **kwargs: None
        # Nothing here reads the sideboards, and they are deep copies.
        deck_builder.get_sideboard = lambda pool, deck: []

    def close(self):
        """Puts the deck builder back."""
        for name, value in self.saved.items():
            setattr(self.builder, name, value)

    def _remembered(self, fn):
        def build(pool, *args):
            colors = tuple(args[0]) if isinstance(args[0], list) else ()
            key = (fn.__name__, colors)
            if key not in self.memo:
                self.memo[key] = fn(pool, *args)
            return self.memo[key]

        return build

    def arch(self, colors):
        return self.normalize("".join(colors[:2]))

    def overall_rating(self, card, colors, metrics=None, tier_data=None):
        """The card's overall rating, however the deck is colored."""
        g = float(card.get("deck_colors", {}).get(ALL, {}).get("gihwr") or 0.0)
        if g > 30.0:
            return g
        return self.original_rating(card, colors, metrics, tier_data)

    def _shifted(self, kind, base):
        def rating(card, colors, metrics=None, tier_data=None):
            value = base(card, colors, metrics, tier_data)
            if value <= 0.0:
                return value
            return value + metrics.shifts[kind].get(self.arch(colors), 0.0)

        return rating

    def rating_of(self, name):
        """The deck score's card rating under a version."""
        return {
            "blend": self.original_rating,
            "overall": self.overall_rating,
            "overall+pair": self._shifted("overall", self.overall_rating),
            "blend+pair": self._shifted("blend", self.original_rating),
        }[name]

    def versions(self):
        """{version: the deck score's rating}. The builds keep the blend: the
        builders read their own reference to it, not deck_scorer's."""
        return {name: {"rating": name} for name in SCORE_VERSIONS}

    def new_pool(self):
        self.memo.clear()

    def run(self, pool, held, version):
        """What the app shows for a pool under a version, or None."""
        self.builder.clear_deck_cache()
        self.scorer.get_card_rating = self.rating_of(version.get("rating", "blend"))
        builds = {}

        def seen(update):
            data = update.get("variant_data")
            if data:
                pair = self.arch(data["colors"])
                builds[pair] = max(builds.get(pair, 0.0), data["rating"])

        decks = self.builder.suggest_deck(pool, held, None, progress_callback=seen)
        self.scorer.get_card_rating = self.original_rating
        if not decks:
            return None
        shown = list(decks.values())
        top = shown[0]
        return {
            "pair": self.arch(top["colors"]),
            "identity": "".join(top["identity_colors"]),
            "kind": top["label_prefix"],
            "score": round(top["rating"], 2),
            "shown": [signature(d["deck_cards"]) for d in shown],
            "pairs": {p: round(s, 2) for p, s in builds.items()},
        }


SCORE_VERSIONS = ("blend", "overall", "overall+pair", "blend+pair")


def pool_of(app, held, d):
    """The deck's pool as the app holds it, a dict per copy, or None if a card
    isn't in the dataset."""
    names = Counter(d["cards"]) + Counter(d["sideboard"])
    pool = []
    for name, count in names.items():
        if name in BASICS:
            continue
        found = app.deck({name: 1})
        if found is None:
            return None
        card = dict(found[0], deck_colors=held.stats.get(name, {}))
        del card["count"]
        pool += [dict(card) for _ in range(count)]
    return pool


def pool_row(app, engine, helds, d, versions):
    """A deck's result row, or the reason it has none."""
    held = helds[fold_of(d["id"])]
    pool = pool_of(app, held, d)
    if pool is None:
        return "card not in dataset"
    if len(pool) < MIN_POOL:
        return "pool under 35 cards"
    engine.new_pool()
    shown = {name: engine.run(pool, held, v) for name, v in versions.items()}
    if not all(shown.values()):
        return "no deck suggested"
    return {
        "id": d["id"],
        "main": d["main_colors"],
        "splash": d["splash_colors"],
        "skill": d["skill"],
        "experience": d["experience"],
        "wins": d["wins"],
        "games": d["games"],
        "pool": len(pool),
        "versions": shown,
    }


_WORKER = {}


def _setup(dataset, folds, win_points_per_sd=None):
    """One process's app, engine and held-out ratings."""
    app = App(dataset)
    engine = Engine()
    if win_points_per_sd is None:
        s = engine.scorer
        # Win rate points a deck's card quality is priced at per SD, near 50%.
        win_points_per_sd = 25.0 * s.WIN_LOG_ODDS_PER_POINT * s.WEIGHTS["card_quality"]
    helds = [
        Held(training(folds, {i}), win_points_per_sd) for i in range(len(folds))
    ]
    return app, engine, helds, engine.versions()


def _init_worker(dataset, folds):
    _WORKER["state"] = _setup(dataset, folds)


def _work(d):
    app, engine, helds, versions = _WORKER["state"]
    return pool_row(app, engine, helds, d, versions)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--src", required=True, help="The copy of the app to use")
    parser.add_argument("--decks", required=True, help="From decks.py (.json.gz)")
    parser.add_argument("--games", required=True, help="From games.py (.json.gz)")
    parser.add_argument("--dataset", required=True, help="The app's set data")
    parser.add_argument("--set", required=True, help="Set code")
    parser.add_argument("--out", required=True, help="Where to write them (.json.gz)")
    parser.add_argument("--pools", type=int, default=None, help="Use only this many")
    parser.add_argument("--workers", type=int, default=os.cpu_count())
    args = parser.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.src))
    with gzip.open(args.decks, "rt", encoding="utf-8") as f:
        decks = json.load(f)[: args.pools]
    with gzip.open(args.games, "rt", encoding="utf-8") as f:
        folds = json.load(f)["folds"]

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
        json.dump({"set": args.set, "skipped": dict(skipped), "rows": rows}, f)
    print(
        f"{args.set}: {len(rows)} pools, skipped {dict(skipped)}, "
        f"{time.time() - started:.0f}s on {args.workers} workers"
    )


if __name__ == "__main__":
    main()
