"""The confirmation run's extra report: 0.05 against 0.10, and what the threshold does.

    python experiments/2026-11-16-cutoff-sweeps/confirm.py RESULTS

RESULTS holds one folder per set and sample, from the Advisor heads workflow,
with base.json, lane-share-10.json and lane-share-05.json. The pick rows need
replay.py's lane size and pool size columns (7 and 8). See CONFIRM.md.
"""

import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

LABELS = {"base": "0.15 (today)", "lane-share-10": "0.10", "lane-share-05": "0.05"}
BUCKETS = [(0, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 99)]


def load_pair(root, base, head):
    """Like heads.load, with any label as the base."""
    out = {}
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        paths = [os.path.join(folder, f"{label}.json") for label in (base, head)]
        if not all(os.path.exists(p) for p in paths):
            continue
        sample = os.path.basename(folder).rsplit("-", 1)[-1]
        b, h = (H.read(p) for p in paths)
        theirs = {d["id"]: d for d in h["drafts"]}
        for d in b["drafts"]:
            if d["id"] in theirs:
                out[(b["set"], f"{sample}:{d['id']}")] = {"base": d, "head": theirs[d["id"]]}
    return dict(sorted(out.items()))


def head_to_head(root):
    m = H.measure(load_pair(root, "lane-share-10", "lane-share-05"))
    print("## 0.05 against 0.10, head to head\n")
    print("lane-share-10 is the base here. Regret: positive is worse for 0.05. "
          "Event wins: positive is better for 0.05.\n")
    print("| regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs "
          "| top card changes |")
    print("|---|---|---|---|---|")
    print(f"| {m['change']:+.4f} ({m['se']:.4f}) | {m['change'] / m['se']:+.1f} "
          f"| {m['swap']:+.3f} ({m['swap_se']:.3f}) | {m['swap'] / m['swap_se']:+.1f} "
          f"| {m['top_changes']:.2f}% |")
    samples = ", ".join(f"{k}: {v[0]:+.4f} ({v[1]:.4f})" for k, v in m["samples"].items())
    print(f"\nBy sample: {samples}\n")
    return m


def lanes(root):
    """Lane sizes by pool size, for each label, on the same picks."""
    # {label: {bucket: [picks, picks with 3 main colors]}}
    three = {label: defaultdict(lambda: [0, 0]) for label in LABELS}
    # Picks where the head has a third color that today's lane doesn't.
    gained = {label: defaultdict(int) for label in LABELS if label != "base"}
    first = {label: [] for label in gained}  # pool size at a draft's first gain
    drafts = 0
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        runs = {}
        for label in LABELS:
            path = os.path.join(folder, f"{label}.json")
            if os.path.exists(path):
                runs[label] = {d["id"]: d for d in H.read(path)["drafts"]}
        if len(runs) < len(LABELS):
            continue
        for draft_id, base in runs["base"].items():
            others = {label: runs[label].get(draft_id) for label in gained}
            if any(d is None for d in others.values()):
                continue
            drafts += 1
            rows = {"base": {(p[0], p[1]): p for p in base["picks"]}}
            rows |= {label: {(p[0], p[1]): p for p in d["picks"]} for label, d in others.items()}
            seen = {label: False for label in gained}
            for key in sorted(rows["base"]):
                if not all(key in r for r in rows.values()):
                    continue
                pool = rows["base"][key][8]
                bucket = next(b for b in BUCKETS if b[0] <= pool <= b[1])
                for label, r in rows.items():
                    three[label][bucket][0] += 1
                    three[label][bucket][1] += r[key][7] >= 3
                for label in gained:
                    if rows[label][key][7] > rows["base"][key][7]:
                        gained[label][bucket] += 1
                        if not seen[label]:
                            seen[label] = True
                            first[label].append(pool)

    print("## What the lower threshold does\n")
    print(f"{drafts} drafts, picks all three replays scored. The threshold acts only "
          "from 15 cards in the pool.\n")
    print("Share of picks where the advisor's lane has three main colors:\n")
    print("| cards in pool | picks | " + " | ".join(LABELS.values()) + " |")
    print("|---|---|" + "---|" * len(LABELS))
    for bucket in BUCKETS:
        n = three["base"][bucket][0]
        cells = " | ".join(f"{100 * three[label][bucket][1] / n:.1f}%" for label in LABELS)
        name = f"{bucket[0]}+" if bucket[1] == 99 else f"{bucket[0]} to {bucket[1]}"
        print(f"| {name} | {n} | {cells} |")
    print("\nShare of picks where the lane has more main colors than today's "
          "(it gains a third color):\n")
    print("| cards in pool | " + " | ".join(LABELS[label] for label in gained) + " |")
    print("|---|" + "---|" * len(gained))
    for bucket in BUCKETS:
        n = three["base"][bucket][0]
        cells = " | ".join(f"{100 * gained[label][bucket] / n:.1f}%" for label in gained)
        name = f"{bucket[0]}+" if bucket[1] == 99 else f"{bucket[0]} to {bucket[1]}"
        print(f"| {name} | {cells} |")
    print()
    for label in gained:
        f = np.array(first[label])
        if len(f):
            print(f"- {LABELS[label]}: {100 * len(f) / drafts:.1f}% of drafts gain a third "
                  f"color at some pick; first at a median of {np.median(f):.0f} cards "
                  f"(quartiles {np.percentile(f, 25):.0f} to {np.percentile(f, 75):.0f}).")
        else:
            print(f"- {LABELS[label]}: no draft gains a third color.")
    return {
        "drafts": drafts,
        "three": {label: {f"{b[0]}-{b[1]}": v for b, v in t.items()} for label, t in three.items()},
        "gained": {label: {f"{b[0]}-{b[1]}": v for b, v in g.items()} for label, g in gained.items()},
        "first": first,
    }


def main(argv=None):
    root = (argv or sys.argv[1:])[0]
    out = {"head_to_head": head_to_head(root), "lanes": lanes(root)}
    with open("confirm.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
