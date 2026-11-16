"""Pool replay results from Advisor replay runs and compare the three ratings.

    python experiments/2026-11-08-heldout-replay/compare.py RUN_DIR [RUN_DIR ...]

Each RUN_DIR holds one run's downloaded replay-* artifacts. Reads report.py's
helpers, and needs only NumPy.
"""

import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Tools", "AdvisorReplay"),
)
import report as R  # noqa: E402

ARMS = {"app": "", "rebuilt": "rebuilt/", "heldout": "heldout/"}
KINDS = ["both on-lane", "base on, head off", "base off, head on", "both off-lane"]


def load(runs, arm):
    """{(set, draft id): {label: draft}} over the runs, drafts both labels have."""
    out = {}
    for run in runs:
        for path in glob.glob(f"{run}/replay-*/{ARMS[arm]}*.json"):
            with open(path, encoding="utf-8") as f:
                result = json.load(f)
            for d in result["drafts"]:
                out.setdefault((result["set"], d["id"]), {})[result["label"]] = d
    return {k: v for k, v in sorted(out.items()) if len(v) == 2}


def regret_frame(data):
    """(wins, controls, base regret, head regret, keys) for complete events."""
    keys = [
        k for k, v in data.items()
        if R.is_complete(v["base"]) and v["base"]["picks"] and v["head"]["picks"]
    ]
    base = [data[k]["base"] for k in keys]
    regret = lambda label: np.array(
        [np.mean([p[3] for p in data[k][label]["picks"]]) for k in keys]
    )
    wins = np.array([d["wins"] for d in base], dtype=float)
    return wins, R.controls(base, [k[0] for k in keys]), regret("base"), regret("head"), keys


_CODES = {}


def set_codes(keys):
    """Each key's set as an integer, worked out once per list of keys."""
    if id(keys) not in _CODES:
        names = sorted({k[0] for k in keys})
        _CODES[id(keys)] = (keys, np.array([names.index(k[0]) for k in keys]), len(names))
    return _CODES[id(keys)][1:]


def within_set_z(x, codes, n_sets):
    """x as z-scores within each set: less the set's mean, over the set's own SD."""
    count = np.maximum(np.bincount(codes, minlength=n_sets), 1)
    mean = np.bincount(codes, x, n_sets) / count
    sd = np.sqrt(np.bincount(codes, (x - mean[codes]) ** 2, n_sets) / count)
    sd[sd == 0] = 1.0
    return (x - mean[codes]) / sd[codes]


def pooled_change(frame, idx):
    """The change with regret divided by its spread over every draft, as it was read
    until 2026-11-16. That spread includes the gaps between sets' regret levels, so a
    head that moves regret in a few sets rescales all of them. Kept for comparison."""
    wins, ctrl, base, head, _ = frame
    return R.wins_slope(head[idx], wins[idx], ctrl[idx]) - R.wins_slope(base[idx], wins[idx], ctrl[idx])


def change(frame, idx):
    """Head's regret slope minus base's, in event wins per SD of regret within a set."""
    wins, ctrl, base, head, keys = frame
    codes, n_sets = set_codes(keys)
    c = codes[idx]
    slope = lambda x: R.wins_slope(within_set_z(x[idx], c, n_sets), wins[idx], ctrl[idx])
    return slope(head) - slope(base)


def top1(data):
    b = R.top1_per_draft([v["base"] for v in data.values()])
    h = R.top1_per_draft([v["head"] for v in data.values()])
    return 100 * (h[:, 0].sum() / h[:, 1].sum() - b[:, 0].sum() / b[:, 1].sum())


def picks(data):
    """How often the top card changes, by kind, and which top drafters took."""
    total = changed = base_on = head_on = 0
    kinds = defaultdict(lambda: [0, 0, 0])
    for v in data.values():
        head = {(p[0], p[1]): p for p in v["head"]["picks"]}
        for p in v["base"]["picks"]:
            q = head.get((p[0], p[1]))
            if q is None:
                continue
            total += 1
            base_on += p[6]
            head_on += q[6]
            if p[5] != q[5]:
                changed += 1
                k = kinds[KINDS[(0 if p[6] else 2) + (0 if q[6] else 1)]]
                k[0] += 1
                k[1] += p[2] == 0
                k[2] += q[2] == 0
    return total, changed, base_on, head_on, kinds


def disagreements(data):
    """Event wins per pick swapped from base's top card to head's, with its SE."""
    rows, base, sets = [], [], []
    for (code, _), v in data.items():
        if not R.is_complete(v["base"]):
            continue
        head = {(p[0], p[1]): p for p in v["head"]["picks"]}
        net = n = 0
        for p in v["base"]["picks"]:
            q = head.get((p[0], p[1]))
            if q is not None and p[5] != q[5]:
                n += 1
                net += int(q[2] == 0) - int(p[2] == 0)
        rows.append([v["base"]["wins"], net, n])
        base.append(v["base"])
        sets.append(code)
    a = np.array(rows, dtype=float)
    ctrl = R.controls(base, sets)

    def fit(idx):
        X = np.column_stack([a[idx, 1], a[idx, 2], ctrl[idx]])
        # Swapping a pick moves net by 2: -1 for base's card to +1 for head's.
        return 2 * np.linalg.lstsq(X, a[idx, 0], rcond=None)[0][0]

    return fit(np.arange(len(a))), R.bootstrap(fit, len(a))


def main(runs):
    frames = {}
    for arm in ARMS:
        data = load(runs, arm)
        if not data:
            continue
        frame = regret_frame(data)
        frames[arm] = frame
        n = len(frame[0])
        total, changed, base_on, head_on, kinds = picks(data)
        slope = change(frame, np.arange(n))
        se = R.bootstrap(lambda i: change(frame, i), n)
        swap, swap_se = disagreements(data)
        print(f"## {arm}: {len(data)} drafts, {n} complete events")
        print(f"regret slope, head minus base: {slope:+.4f} ({se:.4f}), {slope / se:+.1f} SEs")
        print(f"top-1, head minus base: {top1(data):+.2f} points")
        print(f"top card changes on {100 * changed / total:.1f}% of picks")
        print(f"top card on-lane: base {100 * base_on / total:.1f}%, head {100 * head_on / total:.1f}%")
        print(f"event wins per pick swapped to head's top: {swap:+.4f} ({swap_se:.4f})")
        for kind in KINDS:
            k = kinds[kind]
            if k[0]:
                print(
                    f"  {kind}: {100 * k[0] / changed:.1f}% of changes; took base "
                    f"{100 * k[1] / k[0]:.1f}%, head {100 * k[2] / k[0]:.1f}%"
                )
    if {"rebuilt", "heldout"} <= frames.keys():
        rebuilt, held = frames["rebuilt"], frames["heldout"]
        common = sorted(set(rebuilt[4]) & set(held[4]))
        ri = np.array([rebuilt[4].index(k) for k in common])
        hi = np.array([held[4].index(k) for k in common])
        fn = lambda i: change(held, hi[i]) - change(rebuilt, ri[i])
        all_ = np.arange(len(common))
        print(f"## held out minus rebuilt: {fn(all_):+.4f} ({R.bootstrap(fn, len(common)):.4f})")


if __name__ == "__main__":
    main(sys.argv[1:])
