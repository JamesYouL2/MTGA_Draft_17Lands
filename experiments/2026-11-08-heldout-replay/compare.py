"""Pool replay results from Advisor replay runs and compare the three ratings.

    python experiments/2026-11-08-heldout-replay/compare.py RUN_DIR [RUN_DIR ...]

Each RUN_DIR holds one run's downloaded replay-* artifacts. Reads report.py's
helpers, and needs NumPy and SciPy (for combine's quantiles).
"""

import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np
from scipy import stats

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


# What a pick reads on each regret-style measure. SD regret reads the advisor's
# spacing of its scores within a pack as well as its order; rank regret and
# missed top read only the order (2026-11-21-learned-pick, README "Diagnosis").
PICK_MEASURES = {
    "regret": lambda p: p[3],
    "rank": lambda p: p[2],
    "missed": lambda p: float(p[2] != 0),
}


def regret_frame(data, measure="regret"):
    """(wins, controls, base mean, head mean, keys) for complete events, where
    each draft's mean is of PICK_MEASURES[measure] over its picks."""
    keys = [
        k for k, v in data.items()
        if R.is_complete(v["base"]) and v["base"]["picks"] and v["head"]["picks"]
    ]
    base = [data[k]["base"] for k in keys]
    of_pick = PICK_MEASURES[measure]
    regret = lambda label: np.array(
        [np.mean([of_pick(p) for p in data[k][label]["picks"]]) for k in keys]
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


def swap_frame(data):
    """(rows of [wins, net, n, a, b, c], controls, keys) for complete events: of the
    event's n changed picks, the drafter took head's top card in a, base's in b and
    neither in c; net is a - b."""
    rows, base, sets, keys = [], [], [], []
    for key, v in data.items():
        code = key[0]
        if not R.is_complete(v["base"]):
            continue
        head = {(p[0], p[1]): p for p in v["head"]["picks"]}
        took = [0, 0, 0]
        for p in v["base"]["picks"]:
            q = head.get((p[0], p[1]))
            if q is not None and p[5] != q[5]:
                took[0 if q[2] == 0 else 1 if p[2] == 0 else 2] += 1
        a, b, c = took
        rows.append([v["base"]["wins"], a - b, a + b + c, a, b, c])
        base.append(v["base"])
        sets.append(code)
        keys.append(key)
    return np.array(rows, dtype=float), R.controls(base, sets), keys


def swap(frame, idx):
    """Event wins per pick swapped from base's top card to head's, over events idx."""
    a, ctrl, _ = frame
    X = np.column_stack([a[idx, 1], a[idx, 2], ctrl[idx]])
    # Swapping a pick moves net by 2: -1 for base's card to +1 for head's.
    return 2 * np.linalg.lstsq(X, a[idx, 0], rcond=None)[0][0]


def swap_free(frame, idx):
    """swap without its constraint: event wins on a, b and c (swap_frame) with the
    controls, and the coefficient on a less the one on b.

    swap fits wins on net = a - b and n = a + b + c, which holds c's coefficient at
    the mean of a's and b's: a changed pick the drafter settled with neither top
    card is taken to be worth halfway between the two. Where it isn't, swap reads
    some of the gap between c and the others as a gap between a and b. For a
    learned pick model this figure was 55% of swap's
    (2026-11-21-learned-pick, DIAGNOSE.md check 10a)."""
    a, ctrl, _ = frame
    X = np.column_stack([a[idx, 3], a[idx, 4], a[idx, 5], ctrl[idx]])
    beta = np.linalg.lstsq(X, a[idx, 0], rcond=None)[0]
    return beta[0] - beta[1]


def disagreements(data):
    """Event wins per pick swapped from base's top card to head's, with its SE."""
    frame = swap_frame(data)
    fit = lambda idx: swap(frame, idx)
    return fit(np.arange(len(frame[0]))), R.bootstrap(fit, len(frame[0]))


# --- Combining salts -----------------------------------------------------------
#
# Each salt of a heads run is its own sample of drafts and its own held-out
# ratings, and R.bootstrap, which resamples events, sees neither. So the salts'
# estimates spread more than their bootstrap SEs allow (2026-11-17-measure-salts),
# and a run's SE has to come from that spread. combine is a random-effects
# combination of the salts:
#
# - DerSimonian-Laird between-salt variance tau2, so a salt counts by
#   1 / (bootstrap SE^2 + tau2): equal-sized salts count about equally, a thin one
#   less.
# - The SE is Hartung-Knapp-Sidik-Jonkman's, which rescales by the salts' own
#   weighted spread and so stays honest when tau2 is poorly estimated from a few
#   salts, floored at the plain random-effects SE (the "modified" HKSJ), so it is
#   never narrower than the bootstrap alone when the salts happen to agree.
# - Its interval uses t with k - 1 degrees of freedom. scaled_se is the SE times
#   t / 1.96, so "2 scaled SEs" keeps meaning about 95% when k is small: with 4
#   salts it is 1.62 times the SE, with 8 salts 1.21.


def salt_of(key):
    """The salt of a heads.py key, (set, "salt:draft id")."""
    return key[1].split(":", 1)[0]


def by_salt(keys, fn):
    """{salt: (fn(indices), bootstrap SE)} over each salt's events."""
    groups = {}
    for i, key in enumerate(keys):
        groups.setdefault(salt_of(key), []).append(i)
    out = {}
    for name, idx in sorted(groups.items()):
        idx = np.array(idx)
        out[name] = (float(fn(idx)), R.bootstrap(lambda i, a=idx: fn(a[i]), len(idx)))
    return out


def inflation(q, df, level=0.95):
    """(phi, low, high): sqrt(Q / df), the spread over the SEs' allowance, with its
    interval from chi-square(df), treating the SEs as known."""
    if df < 1:
        return float("nan"), float("nan"), float("nan")
    tail = (1 - level) / 2
    return (
        float(np.sqrt(q / df)),
        float(np.sqrt(q / stats.chi2.ppf(1 - tail, df))),
        float(np.sqrt(q / stats.chi2.ppf(tail, df))),
    )


def combine(estimates, ses, level=0.95):
    """Random-effects combination of per-salt estimates and their bootstrap SEs.

    A dict: estimate, se (the corrected SE), scaled_se (se times t / z), df, t,
    low and high (the interval), tau (between-salt SD), and for comparison fixed
    and fixed_se (the inverse-variance mean and its bootstrap-only SE), q
    (Cochran's Q) and phi with its interval (the inflation factor)."""
    e, b = np.asarray(estimates, dtype=float), np.asarray(ses, dtype=float)
    k = len(e)
    if k == 0:
        raise ValueError("nothing to combine")
    z = float(stats.norm.ppf(0.5 + level / 2))
    if not np.all(b > 0):
        if np.all(b == 0) and np.all(e == e[0]):  # the head changed nothing
            out = dict(estimate=float(e[0]), se=0.0, scaled_se=0.0, df=k - 1, t=z,
                       low=float(e[0]), high=float(e[0]), tau=0.0, fixed=float(e[0]),
                       fixed_se=0.0, q=0.0)
            return out | dict(zip(("phi", "phi_low", "phi_high"), (float("nan"),) * 3))
        if not np.any(b > 0):
            raise ValueError("the salts differ but none has an SE")
        # A salt where the head changed nothing measured has no spread of its own:
        # count it as sure as the surest other salt, not infinitely sure.
        b = np.where(b > 0, b, b[b > 0].min())
    w = 1 / b**2
    fixed = float((w * e).sum() / w.sum())
    fixed_se = float(1 / np.sqrt(w.sum()))
    q = float((w * (e - fixed) ** 2).sum())
    if k == 1:
        # No spread to measure: the bootstrap SE alone, and normal quantiles.
        out = dict(estimate=fixed, se=fixed_se, scaled_se=fixed_se, df=0, t=z,
                   low=fixed - z * fixed_se, high=fixed + z * fixed_se, tau=0.0)
    else:
        tau2 = max(0.0, (q - (k - 1)) / (w.sum() - (w**2).sum() / w.sum()))
        ws = 1 / (b**2 + tau2)
        mean = float((ws * e).sum() / ws.sum())
        re_se = 1 / np.sqrt(ws.sum())
        hk = (ws * (e - mean) ** 2).sum() / (k - 1)
        se = float(re_se * max(1.0, np.sqrt(hk)))
        t = float(stats.t.ppf(0.5 + level / 2, k - 1))
        out = dict(estimate=mean, se=se, scaled_se=se * t / z, df=k - 1, t=t,
                   low=mean - t * se, high=mean + t * se, tau=float(np.sqrt(tau2)))
    phi = inflation(q, k - 1, level)
    return out | dict(fixed=fixed, fixed_se=fixed_se, q=q, phi=phi[0], phi_low=phi[1],
                      phi_high=phi[2])


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
