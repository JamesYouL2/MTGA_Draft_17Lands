"""Fit the unrated weight on picks made with early ratings.

    python Tools/PickFit/fit_unrated.py "day 1=results/day1" "full=results/full" ...

Each argument is a label and a directory of features.py outputs. For each, the
pick score's other weights stay at the app's, as one combined score, and the
fit finds the unrated weight in the same points. A free fit of every weight
(quality fixed at 15 points) is shown too.
"""

import glob
import gzip
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from fit import QUALITY_POINTS, Data, evaluate, fit_logit, to_points

UNRATED = "unrated"


def load(directory):
    def files():
        for path in sorted(glob.glob(os.path.join(directory, "*.json.gz"))):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                yield json.load(f)

    return Data(files())


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    print(
        "| ratings from | picks | pack cards unrated | picks unrated | "
        "unrated, others at the app's (points) | unrated, free fit (points) | "
        "top-1, app | top-1, refit unrated |"
    )
    print("|---|---|---|---|---|---|---|---|")
    free = {}
    for arg in args:
        label, directory = arg.split("=", 1)
        data = load(directory)
        if UNRATED not in data.names:
            print(f"| {label} | {len(data.sizes):,} | no unrated cards | | | | | |")
            continue
        u = data.names.index(UNRATED)
        others = [j for j in range(len(data.names)) if j != u]
        points = np.array([data.weights[k] for k in data.names])
        score = data.X[:, others] @ points[others]
        X = np.column_stack([score, data.X[:, u]])
        beta, cov = fit_logit(X, data)
        w = beta[1] / beta[0]
        g = np.array([-beta[1] / beta[0] ** 2, 1 / beta[0]])
        se = float(np.sqrt(g @ cov @ g))
        app = data.X @ points
        refit = score + w * data.X[:, u]
        top_app = evaluate(app, data, calibrated=False)[0]
        top_refit = evaluate(refit, data, calibrated=False)[0]

        b, c = fit_logit(data.X, data)
        pts, ses = to_points(b, c, data.q)
        free[label] = (data.names, pts, ses)

        cards = data.X[:, u].mean()
        picked = data.X[data.chosen, u].mean()
        print(
            f"| {label} | {len(data.sizes):,} | {100 * cards:.1f}% | "
            f"{100 * picked:.1f}% | {w:+.1f} ± {se:.1f} | "
            f"{pts[u]:+.1f} ± {ses[u]:.1f} | {top_app:.1f}% | {top_refit:.1f}% |"
        )
    print()
    print(f"Free fits, every weight in points (quality fixed at {QUALITY_POINTS:g}):")
    print()
    for label, (names, pts, ses) in free.items():
        cells = ", ".join(f"{n} {p:+.1f} ± {s:.1f}" for n, p, s in zip(names, pts, ses))
        print(f"- {label}: {cells}")


if __name__ == "__main__":
    main()
