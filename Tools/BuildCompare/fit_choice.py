"""Fit deck score weights to which candidate build drafters chose.

    python fit_choice.py results/*.json

For each pool, the drafter "chose" the candidate build with the fewest
non-basic cards different from their deck (ties share the choice), kept only
if that is at most --max-diff cards (a swap of one card is two). A conditional logit over each pool's candidates
gives each feature's weight; weights are reported in deck score points, with
card quality fixed at 12 points per standard deviation.
"""

import argparse
import json

import numpy as np

NAMES = ["card_quality", "two_colors", "domain_supported", "missing_fixing", "sim_penalty", "missing_spells"]
APP = {"card_quality": 12.0, "two_colors": 3.5, "domain_supported": 3.2, "missing_fixing": None, "sim_penalty": -1.0, "missing_spells": -10.0}


def diff(a, b):
    return sum(abs(a.get(n, 0) - b.get(n, 0)) for n in set(a) | set(b))


def load(files, max_diff, min_wr):
    groups = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            for d in json.load(f):
                if d["wr_bucket"] < min_wr or len(d["candidates"]) < 2:
                    continue
                cands = d["candidates"]
                diffs = [diff(c["cards"], d["actual"]) for c in cands]
                best = min(diffs)
                if best > max_diff:
                    continue
                X = np.array(
                    [
                        [c["features"][n] for n in NAMES[:3]]
                        + [c["missing_fixing"], c["sim_penalty"], c["features"]["missing_spells"]]
                        for c in cands
                    ],
                    dtype=float,
                )
                chosen = np.array([x == best for x in diffs])
                if chosen.all():
                    continue
                groups.append((d["set"], X, chosen))
    return groups


def fit(groups, cols):
    """Newton's method on the conditional logit; returns beta and its covariance."""
    beta = np.zeros(len(cols))
    for _ in range(50):
        g = np.zeros(len(cols))
        H = np.zeros((len(cols), len(cols)))
        for _, X, chosen in groups:
            X = X[:, cols]
            u = X @ beta
            p = np.exp(u - u.max())
            p /= p.sum()
            q = p * chosen
            q /= q.sum()
            mp, mq = p @ X, q @ X
            g += mq - mp
            H += (X.T * p) @ X - np.outer(mp, mp) - ((X.T * q) @ X - np.outer(mq, mq))
        step = np.linalg.solve(H + 1e-9 * np.eye(len(cols)), g)
        beta += step
        if np.abs(step).max() < 1e-8:
            break
    return beta, np.linalg.pinv(H)


def report(groups, title):
    cols = list(range(len(NAMES)))
    beta, cov = fit(groups, cols)
    pts = 12.0 / beta[0]
    print(f"### {title}: {len(groups):,} pools, {sum(len(X) for _, X, _ in groups):,} candidates")
    print()
    print("| feature | app (points) | fitted (points) |")
    print("|---|---|---|")
    for i, n in enumerate(NAMES):
        se = np.sqrt(cov[i, i]) * abs(pts)
        app = APP[n]
        print(f"| {n} | {'-' if app is None else f'{app:+.1f}'} | {beta[i] * pts:+.1f} ± {se:.1f} |")
    print()
    return beta * pts


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args(argv)

    for max_diff in (6, 4, 10):
        print(f"## The chosen candidate is at most {max_diff} cards from the drafter's deck")
        print()
        groups = load(args.files, max_diff, 0.0)
        report(groups, "All drafters")
        report(load(args.files, max_diff, 0.6), "Strong drafters")
        # Pools offering both: how often is the chosen build short of fixing?
        both = [g for g in groups if (g[1][:, 3] > 0).any() and (g[1][:, 3] == 0).any()]
        picked = sum(float((X[chosen, 3] > 0).mean()) for _, X, chosen in both)
        offered = sum(float((X[:, 3] > 0).mean()) for _, X, _ in both)
        print(
            f"Pools with candidates both short of fixing and not: {len(both):,}. "
            f"Share of candidates short of fixing: {100 * offered / len(both):.1f}%; "
            f"share of chosen: {100 * picked / len(both):.1f}%."
        )
        print()

    print("## By set, all drafters, at most 6 cards different")
    print()
    groups = load(args.files, 6, 0.0)
    print("| set | pools | pools with a candidate short of fixing | missing_fixing (points) |")
    print("|---|---|---|---|")
    for s in sorted({g[0] for g in groups}):
        sub = [g for g in groups if g[0] == s]
        n_mf = sum((X[:, 3] > 0).any() for _, X, _ in sub)
        beta, cov = fit(sub, list(range(len(NAMES))))
        pts = 12.0 / beta[0]
        cell = f"{beta[3] * pts:+.1f} ± {np.sqrt(abs(cov[3, 3])) * abs(pts):.1f}"
        print(f"| {s} | {len(sub)} | {n_mf} | {cell} |")


if __name__ == "__main__":
    main()
