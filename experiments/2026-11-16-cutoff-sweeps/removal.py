"""The removal run's extra report: no share threshold against 0.05, and what each does.

    python experiments/2026-11-16-cutoff-sweeps/removal.py RESULTS

RESULTS holds one folder per set and sample, from the Advisor heads workflow,
with base.json, lane-share-05.json and lane-share-none.json. The pick rows need
replay.py's columns 7 to 10 (lane size, pool size, the lane's thinnest color's
non-land cards, non-land cards over all colors). See REMOVAL.md.
"""

import glob
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import confirm as C  # noqa: E402

H = C.H
LABELS = {"base": "0.15 (today)", "lane-share-05": "0.05", "lane-share-none": "no threshold"}
# The four sets of the ten with the highest first-day share of three-color decks.
HIGH = {"TDM", "FRA", "TLA", "SOS"}
PAIRS = [
    ("base", "lane-share-05"),
    ("base", "lane-share-none"),
    ("lane-share-05", "lane-share-none"),
]


def by_group(root):
    """Each comparison on the four high three-color sets and on the other six."""
    print("## The four high three-color sets against the other six\n")
    print(f"High: {', '.join(sorted(HIGH))}. Regret: positive is worse for the head. "
          "Event wins: positive is better for the head.\n")
    print("| base | head | sets | events | regret slope change (SE) | SEs "
          "| event wins per swapped pick (SE) | SEs |")
    print("|---|---|---|---|---|---|---|---|")
    out = {}
    for base, head in PAIRS:
        data = C.load_pair(root, base, head)
        for name, keep in (("high four", lambda s: s in HIGH), ("other six", lambda s: s not in HIGH)):
            m = H.measure({k: v for k, v in data.items() if keep(k[0])})
            out[f"{head} vs {base}, {name}"] = m
            print(f"| {LABELS[base]} | {LABELS[head]} | {name} | {m['events']} "
                  f"| {m['change']:+.4f} ({m['se']:.4f}) | {m['change'] / m['se']:+.1f} "
                  f"| {m['swap']:+.3f} ({m['swap_se']:.3f}) | {m['swap'] / m['swap_se']:+.1f} |")
    print()
    return out


def thin(root):
    """How often each lane holds a color with few or no non-land cards."""
    # {label: [picks, lane has a color with 0 cards, under 5% of cards, under 10%]}
    stats = {label: [0, 0, 0, 0] for label in LABELS}
    small = {label: [0, 0] for label in LABELS}  # pools of 15+: [picks, lane of 3]
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        for label in LABELS:
            path = os.path.join(folder, f"{label}.json")
            if not os.path.exists(path):
                continue
            for d in H.read(path)["drafts"]:
                for p in d["picks"]:
                    if len(p) < 11 or p[8] < 15:
                        continue
                    s = stats[label]
                    s[0] += 1
                    share = p[9] / p[10] if p[10] else 0.0
                    s[1] += p[9] == 0
                    s[2] += share < 0.05
                    s[3] += share < 0.10
                    small[label][0] += 1
                    small[label][1] += p[7] >= 3
    print("## Thin colors in the lane, from 15 cards\n")
    print("Share of picks where the lane's thinnest color has no non-land cards, or under "
          "5% or 10% of the non-land cards counted over all colors:\n")
    print("| threshold | picks | no cards | under 5% | under 10% | lane of three |")
    print("|---|---|---|---|---|---|")
    for label, s in stats.items():
        if s[0]:
            print(f"| {LABELS[label]} | {s[0]} | {100 * s[1] / s[0]:.2f}% | {100 * s[2] / s[0]:.2f}% "
                  f"| {100 * s[3] / s[0]:.2f}% | {100 * small[label][1] / small[label][0]:.1f}% |")
    print()
    return stats


def main(argv=None):
    root = (argv or sys.argv[1:])[0]
    out = {
        "head_to_head": C.head_to_head(root, "lane-share-05", "lane-share-none", LABELS),
        "groups": by_group(root),
        "lanes": C.lanes(root, LABELS),
        "thin": thin(root),
    }
    with open("removal.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=lambda x: dict(x))


if __name__ == "__main__":
    main()
