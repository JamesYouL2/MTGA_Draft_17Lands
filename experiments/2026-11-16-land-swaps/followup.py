"""Two checks added after the first result was seen. Not part of the protocol.

    python experiments/2026-11-16-land-swaps/followup.py buttons/*.json.gz

1. Each of the button's picks against every other deck, not against the Power Up
   decks, which turned out to be the unusual group.
2. The protocol's comparison again, with the deck's colors held equal too: how many
   main colors, and whether it splashes.
"""

import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
from fit import fit_clustered, varying  # noqa: E402
from score_rating import indicators  # noqa: E402

KINDS = ("Power Up", "Base Deck", "Play 18 Lands", "Play 16 Lands", "Fix Mana Base",
         "Optimize Mana", "Curve Lower")
FLAGS = KINDS[2:]


def load(paths):
    cols = {k: [] for k in ("set", "skill", "experience", "wins", "games", "quality",
                            "kind", "lands", "colors", "off")}
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        for r in data["rows"]:
            o = r["optimize"]
            if not o or o["kind"] not in KINDS or not r["games"]:
                continue
            for key in ("skill", "experience", "wins", "games", "quality"):
                cols[key].append(r[key])
            cols["set"].append(data["set"])
            cols["kind"].append(o["kind"])
            cols["lands"].append(str(min(max(o["lands_before"], 15), 18)))
            cols["colors"].append(f"{min(len(r['main']), 3)}{'s' if r['splash'] else ''}")
            played, rule = r["lands"]["played"], r["lands"]["rule"]
            cols["off"].append(str(min(sum(abs(a - b) for a, b in zip(played, rule)) // 2, 3)))
    numeric = ("wins", "games", "quality")
    return {k: np.array(v, dtype=float if k in numeric else None) for k, v in cols.items()}


def fit(t, X, extra=()):
    sets = sorted(set(t["set"].tolist()))
    dummies = np.array([t["set"] == s for s in sets], dtype=float).T
    player = np.hstack([indicators(t["skill"]), indicators(t["experience"])])
    blocks = [X, t["quality"][:, None], dummies, varying(player), varying(indicators(t["lands"]))]
    blocks += [varying(indicators(t[k])) for k in extra]
    beta, model, cluster = fit_clustered(np.hstack(blocks), t["wins"], t["games"], t["set"])
    p = t["wins"].sum() / t["games"].sum()
    scale = 100.0 * p * (1 - p)
    out = []
    for i in range(X.shape[1]):
        variance = model[i, i] if cluster is None else max(model[i, i], cluster[i, i])
        out.append((scale * float(beta[i]), scale * math.sqrt(variance)))
    return out


def cell(e, se):
    return f"{e:+.2f} [{e - 1.96 * se:+.2f}, {e + 1.96 * se:+.2f}], {e / se:+.1f} SEs"


def main():
    t = load(sys.argv[1:])
    n = len(t["set"])
    print(f"{n} decks. Win rate in points; negative means the decks did worse than "
          "their cards say.\n")
    print("## Each pick against every other deck\n")
    print("| the button's pick | decks | against all other decks |")
    print("|---|---|---|")
    for kind in KINDS:
        m = (t["kind"] == kind).astype(float)[:, None]
        print(f"| {kind} | {100 * m.mean():.1f}% | {cell(*fit(t, m)[0])} |")
    X = np.array([t["kind"] == k for k in FLAGS], dtype=float).T
    rows = {"as in the protocol": fit(t, X),
            "colors held equal": fit(t, X, ("colors",)),
            "colors and distance from the rule's basics held equal": fit(t, X, ("colors", "off"))}
    print("\n## Against the Power Up decks, with more held equal\n")
    print("| the button's pick | " + " | ".join(rows) + " |")
    print("|---|" + "---|" * len(rows))
    for i, kind in enumerate(FLAGS):
        print(f"| {kind} | " + " | ".join(cell(*r[i]) for r in rows.values()) + " |")
    print("\n## Who gets each pick\n")
    print("| the button's pick | three or more main colors | splashing | basics two or more from the rule's |")
    print("|---|---|---|---|")
    for kind in KINDS:
        m = t["kind"] == kind
        three = np.char.startswith(t["colors"][m].astype(str), "3").mean()
        splash = np.char.endswith(t["colors"][m].astype(str), "s").mean()
        off = (t["off"][m].astype(int) >= 2).mean()
        print(f"| {kind} | {100 * three:.1f}% | {100 * splash:.1f}% | {100 * off:.1f}% |")


if __name__ == "__main__":
    main()
