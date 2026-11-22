"""Top-1 and top-3 agreement with the card taken, per head, in a heads run.

    python experiments/2026-11-21-learned-pick/agreement.py RESULTS

RESULTS is an Advisor heads run's results folder (heads-<SET>-<salt>/<head>.json).
Strong drafters are those the models were fitted to: win-rate bucket >= 0.6 and
>= 50 games. The change against base is paired by draft, with its SE from the
spread of per-draft differences (drafts are the independent units).
"""

import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np


def strong(d):
    return (d.get("skill") or 0) >= 0.6 and (d.get("games") or 0) >= 50


def per_draft(root):
    """{head: {(folder, draft id): (strong, [ranks])}}."""
    out = defaultdict(dict)
    for path in sorted(glob.glob(os.path.join(root, "*", "*.json"))):
        head = os.path.basename(path)[: -len(".json")]
        folder = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for d in data.get("drafts", []):
            out[head][(folder, d["id"])] = (strong(d), [p[2] for p in d["picks"]])
    return out


def rates(drafts, keys, k):
    """Per-draft share of picks where the card taken ranked in the top k."""
    return np.array([np.mean([r < k for r in drafts[key][1]]) for key in keys])


def main(root):
    data = per_draft(root)
    if "base" not in data:
        print("No base results.")
        return
    heads = ["base"] + sorted(h for h in data if h != "base")
    print("# Agreement with the card taken")
    print()
    print(
        "Share of picks where the card taken is the head's top card (top-1) or in "
        "its top 3, on the replay's held-out ratings. Change against base in "
        "points, ± its SE, paired by draft."
    )
    print()
    print("| head | drafters | drafts | top-1 | top-3 | top-1 vs base | top-3 vs base |")
    print("|---|---|---|---|---|---|---|")
    for head in heads:
        for who in ("all", "strong"):
            keys = [
                key
                for key, (is_strong, ranks) in data[head].items()
                if ranks and key in data["base"] and (who == "all" or is_strong)
            ]
            if not keys:
                continue
            cells = []
            diffs = []
            for k in (1, 3):
                mine = rates(data[head], keys, k)
                base = rates(data["base"], keys, k)
                cells.append(f"{100 * mine.mean():.1f}")
                d = 100 * (mine - base)
                se = d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else float("nan")
                diffs.append(f"{d.mean():+.2f} ± {se:.2f}" if head != "base" else "")
            print(f"| {head} | {who} | {len(keys)} | {cells[0]} | {cells[1]} | {diffs[0]} | {diffs[1]} |")


if __name__ == "__main__":
    main(sys.argv[1])
