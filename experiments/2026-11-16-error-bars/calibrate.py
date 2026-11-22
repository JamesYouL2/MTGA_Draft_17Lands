"""Are the Advisor heads harness's standard errors the right size?

    python experiments/2026-11-16-error-bars/calibrate.py RESULTS

For each head, splits each set's drafts into FOLDS random parts, measures the
change in regret slope in each part with its bootstrap SE, and compares how far
the parts sit from their set's mean with what those SEs say. A ratio of 1 means
the SEs are right; 2 means they are half what they should be. Also counts drafts
that are in more than one sample of a set. Needs only NumPy.
"""

import glob
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

C, R = H.C, H.R
FOLDS = 8


def folds_of(frame, seed=0):
    """Per fold: (set, change, SE), drafts dealt to folds at random within a set."""
    codes = np.array([k[0] for k in frame[4]])
    rng = np.random.default_rng(seed)
    out = []
    for code in sorted(set(codes)):
        idx = rng.permutation(np.flatnonzero(codes == code))
        for part in np.array_split(idx, FOLDS):
            change = C.change(frame, part)
            se = R.bootstrap(lambda i, p=part: C.change(frame, p[i]), len(part), samples=200)
            out.append((code, change, se))
    return out


def spread(parts):
    """Root mean square of each part's (change - its set's mean) / SE, corrected
    for the mean being estimated: 1.0 when the SEs are the right size."""
    by_set = {}
    for code, change, se in parts:
        by_set.setdefault(code, []).append((change, se))
    total = dof = 0.0
    for values in by_set.values():
        w = np.array([1 / se**2 for _, se in values])
        x = np.array([c for c, _ in values])
        mean = np.sum(w * x) / np.sum(w)
        total += float(np.sum(w * (x - mean) ** 2))
        dof += len(values) - 1
    return (total / dof) ** 0.5, int(dof)


def overlap(root):
    """Share of each set's sampled drafts that are in more than one sample."""
    seen = {}
    for path in glob.glob(os.path.join(root, "*", "base.json")):
        with open(path, encoding="utf-8") as f:
            run = json.load(f)
        seen.setdefault(run["set"], Counter()).update(d["id"] for d in run["drafts"])
    return {s: sum(1 for n in c.values() if n > 1) / len(c) for s, c in sorted(seen.items())}


def main(root):
    names = sorted(
        {os.path.basename(p)[: -len(".json")] for p in glob.glob(os.path.join(root, "*", "*.json"))}
        - {"base"}
    )
    print("# Error bars\n")
    print("| head | change (SE) | SEs | top card changes | spread of the folds against their SEs |")
    print("|---|---|---|---|---|")
    ratios, zs = [], []
    for head in names:
        data = H.load(root, head)
        frame = C.regret_frame(data)
        n = len(frame[0])
        change = C.change(frame, np.arange(n))
        se = R.bootstrap(lambda i: C.change(frame, i), n)
        total, changed, *_ = C.picks(data)
        ratio, dof = spread(folds_of(frame))
        ratios.append(ratio)
        zs.append(change / se if se else 0.0)
        print(f"| {head} | {change:+.4f} ({se:.4f}) | {zs[-1]:+.1f} | {100 * changed / total:.2f}% | {ratio:.2f} |")
    print(f"\n{FOLDS} random folds a set. Spread over the heads: mean {np.mean(ratios):.2f}, "
          f"from {min(ratios):.2f} to {max(ratios):.2f}. 1.00 means the SEs are the right size.")
    print(f"Heads at 2+ SEs either way: {sum(abs(z) >= 2 for z in zs)} of {len(zs)}.")
    print("\nDrafts in more than one sample, by set: "
          + ", ".join(f"{s} {100 * v:.1f}%" for s, v in overlap(root).items()) + ".")


if __name__ == "__main__":
    main(sys.argv[1])
