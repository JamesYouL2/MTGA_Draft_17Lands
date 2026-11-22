"""Report on the three Auto-Optimize heads.

    python experiments/2026-11-21-optimize-guard/report.py heads/*.json.gz --json guard.json

Changes in deck score are in win rate points at the score's own price, with
set-clustered SEs. As in the 11-16 report, the base button's land-count swaps
(16 or 18 lands) count as zero, since the score can't price a land. Needs only
NumPy.
"""

import argparse
import gzip
import json
import math

import numpy as np

HEADS = ("base", "no-guard", "guard")
NO_SWAP = "Base Deck"
LAND_COUNT = ("Play 18 Lands", "Play 16 Lands")


def clustered_mean(x, clusters):
    """The mean of x and its SE, clustered by set (as buttons_report.py)."""
    n, mean = len(x), float(np.mean(x))
    groups = np.unique(clusters)
    if len(groups) < 2:
        return mean, float(np.std(x, ddof=1) / math.sqrt(n)) if n > 1 else math.nan
    sums = np.array([(x[clusters == g] - mean).sum() for g in groups])
    g = len(groups)
    return mean, float(math.sqrt(g / (g - 1) * (sums**2).sum()) / n)


def load(paths):
    sets, kind, gain = [], {h: [] for h in HEADS}, {h: [] for h in HEADS}
    skipped = {}
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        skipped[data["set"]] = data["skipped"]
        price = data["win_points_per_score"]
        for r in data["rows"]:
            o = r["optimize"]
            if not o:
                continue
            sets.append(data["set"])
            for h in HEADS:
                kind[h].append(o[h]["kind"])
                gain[h].append(price * (o[h]["score_after"] - o["score_before"]))
    kind = {h: np.array(v) for h, v in kind.items()}
    gain = {h: np.array(v, dtype=float) for h, v in gain.items()}
    gain["base"] = np.where(np.isin(kind["base"], LAND_COUNT), 0.0, gain["base"])
    return np.array(sets), kind, gain, skipped


def summary(x, sets):
    mean, se = clustered_mean(x, sets)
    return {"mean": mean, "se": se, "lo": mean - 1.96 * se, "hi": mean + 1.96 * se,
            "z": mean / se if se else math.nan}


def pm(s):
    return f"{s['mean']:+.3f} [{s['lo']:+.3f}, {s['hi']:+.3f}]"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--json", default=None)
    args = parser.parse_args(argv)

    sets, kind, gain, skipped = load(args.paths)
    out = {"decks": int(len(sets)), "sets": sorted(set(sets.tolist())), "heads": {},
           "differences": {}, "by_set": {}, "skipped": skipped}
    print(f"{len(sets)} decks from {len(set(sets))} sets.\n")
    print("| head | changes the deck | deck score change |")
    print("|---|---|---|")
    for h in HEADS:
        changed = 100.0 * float((kind[h] != NO_SWAP).mean())
        s = summary(gain[h], sets)
        out["heads"][h] = {"changed": changed, **s}
        print(f"| {h} | {changed:.1f}% | {pm(s)} |")

    print("\n| difference | effect | SEs |")
    print("|---|---|---|")
    for a, b in (("no-guard", "base"), ("guard", "base"), ("guard", "no-guard")):
        s = summary(gain[a] - gain[b], sets)
        out["differences"][f"{a} minus {b}"] = s
        print(f"| {a} minus {b} | {pm(s)} | {s['z']:+.1f} |")

    blocked = (kind["no-guard"] != NO_SWAP) & (kind["guard"] == NO_SWAP)
    out["blocked"] = {"share": 100.0 * float(blocked.mean())}
    print(f"\nThe guard blocks a swap the plain version makes in {100 * blocked.mean():.2f}% "
          "of decks.", end="")
    if blocked.sum() > 1:
        s = summary(gain["no-guard"][blocked], sets[blocked])
        out["blocked"]["no_guard_gain_there"] = s
        print(f" There the plain swap's change is {pm(s)}.")
    else:
        print()

    print("\n## By set: guard minus no-guard, guard minus base\n")
    print("| set | decks | blocked | guard minus no-guard | guard minus base |")
    print("|---|---|---|---|---|")
    for st in sorted(set(sets.tolist())):
        m = sets == st
        d1, d2 = gain["guard"][m] - gain["no-guard"][m], gain["guard"][m] - gain["base"][m]
        se = lambda x: float(np.std(x, ddof=1) / math.sqrt(len(x)))  # noqa: E731
        out["by_set"][st] = {"decks": int(m.sum()), "blocked": 100.0 * float(blocked[m].mean()),
                             "guard_minus_no_guard": [float(d1.mean()), se(d1)],
                             "guard_minus_base": [float(d2.mean()), se(d2)]}
        print(f"| {st} | {m.sum()} | {100 * blocked[m].mean():.2f}% | "
              f"{d1.mean():+.3f} ({se(d1):.3f}) | {d2.mean():+.3f} ({se(d2):.3f}) |")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
