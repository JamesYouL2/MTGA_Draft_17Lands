"""Every candidate build the deck builder makes for real pools, with its features.

    python candidates.py --src . --games games.csv.gz --dataset FRA.json.gz \
        --set FRA --drafts 600 --out FRA.json

For each pool (a 17Lands deck plus its sideboard), the builder runs with the
new deck score and no fixing penalty. Each candidate it scores is kept with the
deck score's features, its missing fixing, its mana simulation penalty, and how
many of the drafter's non-basic cards it plays.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from compare import BASICS, read_drafts  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--games", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--set", required=True)
    parser.add_argument("--drafts", type=int, default=600)
    parser.add_argument("--salt", default="candidates")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    sys.path.insert(0, args.src)
    from compare import App

    app = App(args.dataset, os.path.join(os.path.dirname(__file__), "old_deck_scorer.py"), [])
    from src.advisor import deck_scorer
    from src.advisor.mana_base import ManaSourceAnalyzer

    db = app.deck_builder
    db.calculate_holistic_score = deck_scorer.calculate_holistic_score
    drafts = read_drafts(args.games, args.drafts, args.salt)
    t0 = time.time()
    out = []
    for i, d in enumerate(drafts):
        pool = app.cards(d["pool"])
        actual = {n: k for n, k in d["deck"].items() if n not in BASICS}
        found = []

        def collect(msg):
            if "variant_data" in msg:
                found.append(msg["variant_data"])

        db.clear_deck_cache()
        db.suggest_deck(pool, app.metrics, None, "PremierDraft", collect)
        cands = []
        for v in found:
            deck, colors = v["deck_cards"], v["colors"]
            f = deck_scorer.deck_features(deck, colors, len(pool), app.metrics)
            if f is None:
                continue
            missing = 0
            if len(colors) >= 3 and not f["domain_supported"]:
                fixing = ManaSourceAnalyzer(deck).total_fixing_cards
                missing = max(0, len(colors) - 1 - fixing)
            score = deck_scorer.BASE_SCORE + sum(
                deck_scorer.WEIGHTS[k] * f[k] for k in deck_scorer.WEIGHTS
            )
            names = {}
            for c in deck:
                names[c["name"]] = names.get(c["name"], 0) + c.get("count", 1)
            cands.append(
                {
                    "features": f,
                    "missing_fixing": missing,
                    # What the builder's mana simulation took off the score.
                    "sim_penalty": max(0.0, score) - v["rating"],
                    "overlap": sum(min(k, names.get(n, 0)) for n, k in actual.items()),
                    "cards": {n: k for n, k in names.items() if n not in BASICS},
                    "colors": colors,
                }
            )
        out.append(
            {
                "id": d["id"],
                "set": args.set,
                "wr_bucket": d["wr_bucket"],
                "spells": sum(actual.values()),
                "actual": actual,
                "main_colors": d["main_colors"],
                "splash_colors": d["splash_colors"],
                "candidates": cands,
            }
        )
        if i % 50 == 0:
            print(f"{args.set} {i}/{len(drafts)} {time.time() - t0:.0f}s", file=sys.stderr)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f)


if __name__ == "__main__":
    main()
