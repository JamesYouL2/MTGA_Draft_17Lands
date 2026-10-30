"""Fit the deck builder's Monte Carlo penalties to which build drafters chose.

    python fit_sim.py results/*.json

As in fit_choice.py, but the drafter "chose" the candidate in their own main
and splash colors with the fewest non-basic cards different from their deck.
The builder takes points off for color screw on turn 3 above 10%, mana screw
on turn 3 above 22% and flood on turn 5 above 27%; each is fitted on its own,
in deck score points per percentage point over its threshold. A second fit
uses the raw percentages, with no thresholds.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from fit_choice import diff, fit

BASE = ["card_quality", "two_colors", "missing_fixing"]
# Name, stat, threshold and the app's points per percentage point over it.
PENALTIES = [
    ("color_screw", "color_screw_t3", 10.0, -2.5),
    ("mana_screw", "screw_t3", 22.0, -1.5),
    ("flood", "flood_t5", 27.0, -1.5),
]
APP = {"card_quality": 12.0, "two_colors": 3.5, "missing_fixing": -2.5}
APP.update({name: app for name, _, _, app in PENALTIES})


def row(c, thresholds):
    sim = c.get("sim") or {}
    base = [
        c["features"]["card_quality"],
        c["features"]["two_colors"],
        c["missing_fixing"],
    ]
    over = [
        max(0.0, (sim.get(stat) or 0.0) - (t if thresholds else 0.0))
        for _, stat, t, _ in PENALTIES
    ]
    return base + over


def load(files, max_diff, min_wr, thresholds=True):
    groups = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            for d in json.load(f):
                cands = d["candidates"]
                if d["wr_bucket"] < min_wr or len(cands) < 2:
                    continue
                colors = set(d["main_colors"]) | set(d["splash_colors"])
                diffs = [
                    diff(c["cards"], d["actual"]) if set(c["colors"]) == colors else 999
                    for c in cands
                ]
                best = min(diffs)
                if best > max_diff:
                    continue
                chosen = np.array([x == best for x in diffs])
                if chosen.all():
                    continue
                X = np.array([row(c, thresholds) for c in cands], dtype=float)
                groups.append((d["set"], X, chosen))
    return groups


def report(groups, title, thresholds=True):
    names = BASE + [name for name, _, _, _ in PENALTIES]
    beta, cov = fit(groups, list(range(len(names))))
    pts = 12.0 / beta[0]
    print(
        f"### {title}: {len(groups):,} pools, "
        f"{sum(len(X) for _, X, _ in groups):,} candidates"
    )
    print()
    print(
        "| feature | app (points) | fitted (points) | candidates it applies to | "
        "chosen builds it applies to |"
    )
    print("|---|---|---|---|---|")
    for i, n in enumerate(names):
        se = np.sqrt(abs(cov[i, i])) * abs(pts)
        app = f"{APP[n]:+.1f}" if thresholds or n in BASE else "-"
        shares = "- | -"
        if n not in BASE:
            cands = np.mean([x for _, X, _ in groups for x in X[:, i] > 0])
            chosen = np.mean([x for _, X, c in groups for x in X[c, i] > 0])
            shares = f"{100 * cands:.1f}% | {100 * chosen:.1f}%"
        print(f"| {n} | {app} | {beta[i] * pts:+.2f} ± {se:.2f} | {shares} |")
    print()


def main(argv=None):
    files = argv if argv is not None else sys.argv[1:]
    for max_diff in (6, 10):
        print(f"## The drafter's colors, at most {max_diff} cards different")
        print()
        print("Penalties in points per percentage point over the builder's threshold.")
        print()
        report(load(files, max_diff, 0.0), "All drafters")
        report(load(files, max_diff, 0.6), "Strong drafters")
    print("## No thresholds: points per percentage point, at most 10 cards different")
    print()
    report(load(files, 10, 0.0, thresholds=False), "All drafters", thresholds=False)


if __name__ == "__main__":
    main()
