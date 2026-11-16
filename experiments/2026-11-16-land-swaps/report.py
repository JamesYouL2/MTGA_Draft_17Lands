"""Whether the swap Auto optimize picks says something about how a deck did.

    python experiments/2026-11-16-land-swaps/report.py buttons/*.json.gz --json out.json

Reads buttons.py's rows. For each kind of swap, the win rate of the decks the button
picked it for, against decks it picked Power Up or nothing for, at the same card
quality, land count, set and player. Needs only NumPy.
"""

import argparse
import gzip
import json
import math
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
from fit import fit_clustered, varying  # noqa: E402
from score_rating import indicators  # noqa: E402

# Decks the button finds nothing wrong with the lands or the curve of.
REFERENCE = ("Power Up", "Base Deck")
FLAGS = ("Play 18 Lands", "Play 16 Lands", "Fix Mana Base", "Optimize Mana", "Curve Lower")
MEANING = {
    "Play 18 Lands": "wants one more land",
    "Play 16 Lands": "wants one land fewer",
    "Fix Mana Base": "wants a utility land out for a basic",
    "Optimize Mana": "wants the basics split differently",
    "Curve Lower": "wants the dearest spell out for a cheap one",
}
MIN_DECKS = int(os.environ.get("MIN_DECKS", "100"))


def load(paths):
    cols = {k: [] for k in ("set", "skill", "experience", "wins", "games", "quality",
                            "kind", "lands")}
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        for r in data["rows"]:
            o = r["optimize"]
            if not o or o["kind"] not in REFERENCE + FLAGS or not r["games"]:
                continue
            for key in ("skill", "experience", "wins", "games", "quality"):
                cols[key].append(r[key])
            cols["set"].append(data["set"])
            cols["kind"].append(o["kind"])
            cols["lands"].append(min(max(o["lands_before"], 15), 18))
    numeric = ("wins", "games", "quality")
    return {k: np.array(v, dtype=float if k in numeric else None) for k, v in cols.items()}


def measure(t):
    n = len(t["set"])
    flags = [k for k in FLAGS if (t["kind"] == k).sum() >= MIN_DECKS]
    X = np.array([t["kind"] == k for k in flags], dtype=float).T.reshape(n, len(flags))
    sets = sorted(set(t["set"].tolist()))
    dummies = np.array([t["set"] == s for s in sets], dtype=float).T
    player = np.hstack([indicators(t["skill"]), indicators(t["experience"])])
    lands = indicators(t["lands"].astype(str))
    A = np.hstack([X, t["quality"][:, None], dummies, varying(player), varying(lands)])
    beta, model, cluster = fit_clustered(A, t["wins"], t["games"], t["set"])
    p = t["wins"].sum() / t["games"].sum()
    scale = 100.0 * p * (1 - p)
    out = {"decks": n, "sets": len(sets), "kinds": {}}
    counts = Counter(t["kind"].tolist())
    for i, kind in enumerate(flags):
        variance = model[i, i] if cluster is None else max(model[i, i], cluster[i, i])
        m = t["kind"] == kind
        out["kinds"][kind] = {
            "share": 100.0 * counts[kind] / n,
            "win_rate": 100.0 * float(t["wins"][m].sum() / t["games"][m].sum()),
            "effect": scale * float(beta[i]),
            "se": scale * math.sqrt(variance),
        }
    ref = np.isin(t["kind"], REFERENCE)
    out["reference"] = {
        "share": 100.0 * float(ref.mean()),
        "win_rate": 100.0 * float(t["wins"][ref].sum() / t["games"][ref].sum()),
    }
    out["by_lands"] = {
        str(k): {"decks": int((t["lands"] == k).sum()),
                 "more": 100.0 * float((t["kind"][t["lands"] == k] == "Play 18 Lands").mean()),
                 "fewer": 100.0 * float((t["kind"][t["lands"] == k] == "Play 16 Lands").mean())}
        for k in sorted(set(t["lands"].tolist()))
    }
    return out


def report(r):
    print(f"{r['decks']} decks in {r['sets']} sets. Win rate in points, against decks "
          f"the button picked Power Up or nothing for ({r['reference']['share']:.1f}% of "
          f"decks, {r['reference']['win_rate']:.1f}% won), at the same card quality, land "
          f"count, set and player. Negative: the flagged decks did worse.\n")
    print("| the button's pick | what it says of the deck | decks | won | against the rest |")
    print("|---|---|---|---|---|")
    for kind, k in r["kinds"].items():
        lo, hi = k["effect"] - 1.96 * k["se"], k["effect"] + 1.96 * k["se"]
        print(f"| {kind} | {MEANING[kind]} | {k['share']:.1f}% | {k['win_rate']:.1f}% "
              f"| {k['effect']:+.2f} [{lo:+.2f}, {hi:+.2f}], {k['effect'] / k['se']:+.1f} SEs |")
    print("\n## By the lands the deck played\n")
    print("| lands | decks | button wants one more | button wants one fewer |")
    print("|---|---|---|---|")
    for lands, b in r["by_lands"].items():
        label = {"15": "15 or fewer", "18": "18 or more"}.get(lands, lands)
        print(f"| {label} | {b['decks']} | {b['more']:.1f}% | {b['fewer']:.1f}% |")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+", help="buttons.py's outputs")
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    results = measure(load(args.paths))
    report(results)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
