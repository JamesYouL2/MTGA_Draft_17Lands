"""Compare the deck builder's suggested build for real pools under several deck scorers.

    python compare.py --src DSWT --old-scorer deck_scorer_main.py \
        --games game_data.csv.gz --dataset FRA.json.gz --set FRA --drafts 200 \
        --out FRA.json

Pools come from 17Lands game data (deck + sideboard of the drafter's last
build), sampled by hashed ID as in Tools/DeckScoreFit/decks.py, with the deck
the drafter actually played and its game results.
"""

import argparse
import csv
import gzip
import hashlib
import heapq
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time

BASICS = {"Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"}
csv.field_size_limit(10**9)


def deck_hash(key, salt):
    return int(hashlib.sha1(f"{salt}{key}".encode()).hexdigest()[:15], 16)


def read_drafts(path, n, salt=""):
    """n decks sampled by hashed ID: pool (deck + sideboard), deck, colors, results."""
    kept, heap = {}, []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        header = next(csv.reader([next(f)]))
        col = {h: i for i, h in enumerate(header)}
        deck_cols = [(i, h[5:]) for i, h in enumerate(header) if h.startswith("deck_")]
        sb_cols = {h[10:]: i for i, h in enumerate(header) if h.startswith("sideboard_")}
        for line in f:
            if '"' in line:
                fields = next(csv.reader([line]))
            else:
                fields = line.rstrip("\r\n").split(",")
            key = f"{fields[col['draft_id']]}:{fields[col['build_index']]}"
            d = kept.get(key)
            if d is None:
                h = deck_hash(key, salt)
                if len(heap) < n:
                    heapq.heappush(heap, (-h, key))
                elif h < -heap[0][0]:
                    del kept[heapq.heapreplace(heap, (-h, key))[1]]
                else:
                    continue
                deck, pool = {}, {}
                for i, name in deck_cols:
                    k = int(fields[i] or 0)
                    j = sb_cols.get(name)
                    s = int(fields[j] or 0) if j is not None else 0
                    if k:
                        deck[name] = k
                    if k + s and name not in BASICS:
                        pool[name] = k + s
                d = kept[key] = {
                    "id": key,
                    "deck": deck,
                    "pool": pool,
                    "main_colors": fields[col["main_colors"]],
                    "splash_colors": fields[col["splash_colors"]],
                    "wr_bucket": float(fields[col["user_game_win_rate_bucket"]] or 0),
                    "games": 0,
                    "wins": 0,
                }
            d["games"] += 1
            d["wins"] += fields[col["won"]] == "True"
    return sorted(kept.values(), key=lambda d: d["id"])


class App:
    def __init__(self, dataset_path, old_scorer_path, fix_weights):
        from src.advisor import deck_builder, deck_scorer
        from src.advisor.mana_base import ManaSourceAnalyzer
        from src.dataset import Dataset
        from src.set_metrics import SetMetrics

        self.deck_builder = deck_builder
        self.dataset = Dataset()
        with tempfile.TemporaryDirectory() as tmp:
            plain = os.path.join(tmp, "dataset.json")
            opener = gzip.open if dataset_path.endswith(".gz") else open
            with opener(dataset_path, "rb") as src, open(plain, "wb") as dst:
                shutil.copyfileobj(src, dst)
            self.dataset.open_file(plain)
        self.metrics = SetMetrics(self.dataset)
        self.full_names = {}
        for card in self.dataset.get_card_ratings().values():
            name = card.get("name", "")
            self.full_names.setdefault(name.split(" // ")[0], name)

        spec = importlib.util.spec_from_file_location("old_scorer", old_scorer_path)
        old = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)

        def missing_fixers(deck, colors):
            if len(colors) < 3:
                return 0
            f = deck_scorer.deck_features(deck, colors, 40, self.metrics)
            if f is None or f["domain_supported"]:
                return 0
            return max(0, len(colors) - 1 - ManaSourceAnalyzer(deck).total_fixing_cards)

        def with_fixing(weight):
            def score_deck(deck, colors, pool_size, metrics, tier_data=None):
                score, notes = deck_scorer.calculate_holistic_score(
                    deck, colors, pool_size, metrics, tier_data
                )
                missing = missing_fixers(deck, colors)
                if missing and score:
                    pen = -weight * missing
                    score = max(0.0, score - pen)
                    note = f"Greedy Mana Strain (-{pen:.1f})"
                    notes = f"{notes}, {note}" if notes else note
                return score, notes

            return score_deck

        self.missing_fixers = missing_fixers
        self.scorers = {
            "old": old.calculate_holistic_score,
            "new": deck_scorer.calculate_holistic_score,
        } | {f"new, fixing {w:g}": with_fixing(w) for w in fix_weights}

        # Each deck is simulated once, whichever scorer asks.
        sims, simulate = {}, deck_builder.simulate_deck

        def cached(deck, iterations=10000):
            key = tuple(sorted(f"{c['name']}:{c.get('count', 1)}" for c in deck))
            if key not in sims:
                sims[key] = simulate(deck, iterations)
            return sims[key]

        deck_builder.simulate_deck = cached

    def cards(self, counts):
        out = []
        for name, k in counts.items():
            found = self.dataset.get_data_by_name([self.full_names.get(name, name)])
            if found:
                out.extend([found[0]] * k)
        return out

    def suggest(self, pool, scorer):
        db = self.deck_builder
        db.calculate_holistic_score = self.scorers[scorer]
        db.clear_deck_cache()
        decks = db.suggest_deck(pool, self.metrics, None, "PremierDraft")
        if not decks:
            return None
        label, data = next(iter(decks.items()))
        cards = {}
        for c in data["deck_cards"]:
            cards[c["name"]] = cards.get(c["name"], 0) + c.get("count", 1)
        return {
            "label": label,
            "colors": data["colors"],
            "identity": data.get("identity_colors", data["colors"]),
            "rating": round(data["rating"], 1),
            "breakdown": data["breakdown"],
            "missing_fixers": self.missing_fixers(data["deck_cards"], data["colors"]),
            "cards": cards,
        }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--old-scorer", required=True)
    parser.add_argument("--games", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--set", required=True)
    parser.add_argument("--drafts", type=int, default=200)
    parser.add_argument("--salt", default="")
    parser.add_argument("--fix-weights", type=float, nargs="+", default=[-3.0, -6.0])
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    sys.path.insert(0, args.src)
    app = App(args.dataset, args.old_scorer, args.fix_weights)
    drafts = read_drafts(args.games, args.drafts, args.salt)
    t0 = time.time()
    for i, d in enumerate(drafts):
        pool = app.cards(d["pool"])
        d["suggested"] = {s: app.suggest(pool, s) for s in app.scorers}
        actual = app.cards(d["deck"])
        colors = list(d["main_colors"]) + list(d["splash_colors"])
        d["actual_missing_fixers"] = app.missing_fixers(actual, colors)
        d["set"] = args.set
        if i % 20 == 0:
            print(f"{args.set} {i}/{len(drafts)} {time.time() - t0:.0f}s", file=sys.stderr)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(drafts, f)


if __name__ == "__main__":
    main()
