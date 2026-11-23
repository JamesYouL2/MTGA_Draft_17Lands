"""Deck facts for PROTOCOL.md's E1 and E3: the deck score and its parts, the
shape of the deck's card quality, and plain deck counts.

    python experiments/2026-11-22-deck-value/deckfacts.py --src . \
        --decks decks.json.gz --dataset dataset.json.gz --set FDN --out e1-FDN.json.gz

--decks is Tools/DeckScoreFit/decks.py's output. Card data and the deck score
come from the app at --src through Tools/DeckScoreFit/features.py's App, so
the parts are the app's own.
"""

import argparse
import gzip
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
import features as F  # noqa: E402

POOL_SIZE = F.POOL_SIZE


def cmc(card):
    return float(card.get("cmc", 0) or 0)


def facts(app, cards, main_colors, splash_colors):
    """{fact: value} for a deck of {name: copies}, or None if it can't be scored."""
    deck = app.deck(cards)
    if deck is None:
        return None
    colors = list(main_colors + splash_colors)
    parts = app.scorer.deck_features(deck, colors, POOL_SIZE, app.metrics)
    if parts is None:
        return None
    score = app.scorer.BASE_SCORE + sum(app.scorer.WEIGHTS[k] * v for k, v in parts.items())
    mean, sd = app.metrics.get_metrics("All Decks", "gihwr")
    mean, sd = (mean or 54.0), (sd or 4.0)
    spells = [c for c in deck if "Land" not in c.get("types", [])]
    copies = lambda keep: sum(c["count"] for c in spells if keep(c))  # noqa: E731
    creature = lambda c: "Creature" in c.get("types", [])  # noqa: E731
    removal = lambda c: "removal" in c.get("tags", [])  # noqa: E731
    n = copies(lambda c: True)
    # Per copy, as deck_features rates them: overall GIH WR, else nothing.
    z = sorted(
        ((r - mean) / sd for c in spells for _ in range(c["count"]) if (r := app.gihwr(c)) > 30.0),
        reverse=True,
    )
    shape = {}
    if len(z) >= 5:
        shape = {
            "q_top3": sum(z[:3]) / 3,
            "q_top5": sum(z[:5]) / 5,
            "q_low5": sum(z[-5:]) / 5,
            "q_sd": statistics.pstdev(z),
            "q_max": z[0],
            "q_mean": sum(z) / len(z),
        }
    creature_mv = [cmc(c) for c in spells if creature(c) for _ in range(c["count"])]
    return {
        "score": round(score, 4),
        **{k: round(float(v), 4) for k, v in parts.items()},
        **{k: round(v, 4) for k, v in shape.items()},
        "creatures": copies(creature),
        "cheap": copies(lambda c: (creature(c) or removal(c)) and cmc(c) <= 2),
        "cheap_spells": copies(lambda c: app.get_functional_cmc(c) <= 2),
        "removal": copies(removal),
        "main_colors": len(main_colors),
        "splash": int(bool(splash_colors)),
        "mana_value": round(sum(cmc(c) * c["count"] for c in spells) / n, 4) if n else None,
        "curve_gaps": sum(sum(1 for m in creature_mv if m == v) < 2 for v in (2, 3, 4)),
        "lands": sum(c["count"] for c in deck if "Land" in c.get("types", [])),
        "spells": n,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--src", required=True)
    parser.add_argument("--decks", required=True, help="From decks.py (.json.gz)")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--set", required=True)
    parser.add_argument("--out", required=True, help=".json.gz")
    args = parser.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.src))
    app = F.App(args.dataset)
    with gzip.open(args.decks, "rt", encoding="utf-8") as f:
        decks = json.load(f)
    rows, skipped = [], 0
    for d in decks:
        got = facts(app, d["cards"], d["main_colors"], d["splash_colors"])
        if got is None:
            skipped += 1
            continue
        rows.append({k: d[k] for k in ("id", "wins", "games", "skill", "experience")} | {"f": got})
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump({"set": args.set, "rows": rows, "skipped": skipped,
                   "unmatched": dict(app.unmatched.most_common(10))}, f)
    print(f"{args.set}: {len(rows)} decks, {skipped} skipped")


if __name__ == "__main__":
    main()
