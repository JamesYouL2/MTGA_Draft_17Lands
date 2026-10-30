"""Do pick weights that change with the ratings' sample size beat one set?

    python Tools/PickFit/fit_by_size.py "day 1=results/day1" ... "whole format=results/full"

Each argument is a label and a directory of features.py outputs whose picks
were scored with ratings of one age (a bucket). The models, each scored on
sets it wasn't fitted on (five folds of two sets):

- app: the app's weights.
- one set: one weight set, fitted to every bucket at once.
- by day: a weight set per bucket.
- quality by games: as one set, but the quality weight is a straight line
  in log10 of the dataset's game count.
- by games: each weight a straight line in log10 of the dataset's game count.
- by games, shrunk quality: the same, with each card's quality multiplied by
  samples / (samples + K), K picked by the likelihood over all picks.
"""

import glob
import gzip
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from fit import QUALITY_POINTS, Data, fit_logit, log_lik, softmax, top_k

FOLDS = 5
CENTER = 5.0  # log10 of 100,000 games
SHRINK_K = (0, 250, 500, 1000, 2000, 4000)
SHOW_GAMES = (5_000, 20_000, 100_000, 1_000_000)


def load(args):
    labels, counts = [], []

    def files():
        for b, arg in enumerate(args):
            label, directory = arg.split("=", 1)
            labels.append(label)
            for path in sorted(glob.glob(os.path.join(directory, "*.json.gz"))):
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    d = json.load(f)
                # Data clusters by "set:draft"; keep each bucket's drafts apart.
                for s in d["situations"]:
                    s["draft"] += 1_000_000 * b
                counts.append((b, len(d["situations"])))
                yield d

    data = Data(files())
    data.bucket = np.repeat([b for b, _ in counts], [n for _, n in counts])
    return data, labels


def subset(data, groups):
    out = data.subset(groups)
    out.bucket = data.bucket[groups]
    return out


def column(data, name):
    return data.extra[:, data.extra_names.index(name)]


def log_games(data):
    return np.log10(np.maximum(column(data, "dataset_games"), 1)) - CENTER


def design(data, by_games=False, k=0):
    X = data.X.copy()
    if k:
        n = column(data, "samples")
        X[:, data.q] *= n / (n + k)
    if by_games:
        X = np.hstack([X, X * log_games(data)[:, None]])
    return X


def quality_by_games(data):
    return np.column_stack([data.X, data.X[:, data.q] * log_games(data)])


def scores(tr, te, n_buckets, k):
    """Each model's score for every card of te, fitted on tr."""
    out = {"app": te.X @ tr.app}
    beta, _ = fit_logit(tr.X, tr)
    out["one set"] = te.X @ beta
    u = np.zeros(len(te.X))
    for b in range(n_buckets):
        sub = subset(tr, tr.bucket == b)
        beta, _ = fit_logit(sub.X, sub)
        rows = np.repeat(te.bucket == b, te.sizes)
        u[rows] = te.X[rows] @ beta
    out["by day"] = u
    beta, _ = fit_logit(quality_by_games(tr), tr)
    out["quality by games"] = quality_by_games(te) @ beta
    beta, _ = fit_logit(design(tr, True), tr)
    out["by games"] = design(te, True) @ beta
    beta, _ = fit_logit(design(tr, True, k), tr)
    out["by games, shrunk quality"] = design(te, True, k) @ beta
    return out


def points(beta, q):
    return QUALITY_POINTS * beta / beta[q], beta[q] / QUALITY_POINTS


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    data, labels = load(args)
    nb, nf = len(labels), len(data.names)
    picks = np.bincount(data.bucket, minlength=nb)
    pick_games = column(data, "dataset_games")[data.starts]
    rated = column(data, "samples") > 0

    print("## The picks")
    print()
    print(
        "| ratings from | picks | dataset games (median over sets) | "
        "median samples of a rated card in a pack |"
    )
    print("|---|---|---|---|")
    for b, label in enumerate(labels):
        rows = np.repeat(data.bucket == b, data.sizes)
        print(
            f"| {label} | {picks[b]:,} | "
            f"{np.median(np.unique(pick_games[data.bucket == b])):,.0f} | "
            f"{np.median(column(data, 'samples')[rows & rated]):,.0f} |"
        )

    lik = {}
    for k in SHRINK_K:
        X = design(data, True, k)
        beta, _ = fit_logit(X, data)
        lik[k] = log_lik(X @ beta, data)
    best_k = max(lik, key=lik.get)
    print()
    print("Quality shrunk by samples / (samples + K), fitted by games, all picks:")
    print()
    print("| K | log-likelihood vs K = 0 |")
    print("|---|---|")
    for k in SHRINK_K:
        print(f"| {k} | {lik[k] - lik[0]:+,.1f} |")
    print()
    print(f"K = {best_k} is used below.")

    folds = {s: i % FOLDS for i, s in enumerate(data.sets)}
    fold = np.array([folds[s] for s in data.set])
    hits, losses = {}, {}
    for f in range(FOLDS):
        tr, te = subset(data, fold != f), subset(data, fold == f)
        for model, u in scores(tr, te, nb, best_k).items():
            _, lse = softmax(u, te)
            hits.setdefault(model, []).append((te.bucket, top_k(u, te, 1)))
            losses.setdefault(model, []).append((te.bucket, lse - u[te.chosen]))

    def table(results, fmt):
        print("| model | " + " | ".join(labels) + " | all |")
        print("|---|" + "---|" * (nb + 1))
        for model, parts in results.items():
            bucket = np.concatenate([b for b, _ in parts])
            v = np.concatenate([x for _, x in parts])
            cells = [fmt(v[bucket == b].mean()) for b in range(nb)] + [fmt(v.mean())]
            print(f"| {model} | " + " | ".join(cells) + " |")

    print()
    print("## Held-out sets")
    print()
    print("Top-1, % of picks where the model's best card is the one taken:")
    print()
    table(hits, lambda x: f"{100 * x:.1f}")
    print()
    print("Log loss per pick (lower is better):")
    print()
    table(losses, lambda x: f"{x:.4f}")

    print()
    print("## Weights by day, fitted to all sets")
    print()
    print(
        f"In points (quality = {QUALITY_POINTS:g}); a point's log-odds sets the scale."
    )
    print()
    print("| ratings from | " + " | ".join(data.names) + " | log-odds per point |")
    print("|---|" + "---|" * (nf + 1))
    app = [data.weights[n] for n in data.names]
    print(
        "| app | "
        + " | ".join(f"{w:+.1f}" for w in app)
        + f" | {data.log_odds_per_point:.4f} |"
    )
    for b, label in enumerate(labels):
        sub = subset(data, data.bucket == b)
        beta, _ = fit_logit(sub.X, sub)
        pts, scale = points(beta, data.q)
        print(
            f"| {label} | " + " | ".join(f"{w:+.1f}" for w in pts) + f" | {scale:.4f} |"
        )

    beta, cov = fit_logit(quality_by_games(data), data)
    print()
    print("## Quality by games, fitted to all sets")
    print()
    print(
        "Other weights in the app's points at 1,000,000 games; quality as a "
        "share of its weight there."
    )
    print()
    scale = beta[data.q] + beta[nf] * (6.0 - CENTER)
    pts = QUALITY_POINTS * beta[:nf] / scale
    print(
        "Weights at 1,000,000 games: "
        + ", ".join(f"{n} {w:+.1f}" for n, w in zip(data.names, pts))
    )
    print()
    print("| dataset games | quality weight, share of 1,000,000 games' |")
    print("|---|---|")
    for g in SHOW_GAMES:
        q = beta[data.q] + beta[nf] * (np.log10(g) - CENTER)
        print(f"| {g:,} | {q / scale:.2f} |")
    print()
    print(
        f"Slope per tenfold more games, log-odds: {beta[nf]:+.3f} "
        f"± {np.sqrt(cov[nf, nf]):.3f}"
    )

    for title, k in (
        ("by games", 0),
        (f"by games, quality shrunk with K = {best_k}", best_k),
    ):
        beta, cov = fit_logit(design(data, True, k), data)
        print()
        print(f"## Weights {title}, fitted to all sets")
        print()
        print("| dataset games | " + " | ".join(data.names) + " | log-odds per point |")
        print("|---|" + "---|" * (nf + 1))
        for g in SHOW_GAMES:
            b = beta[:nf] + beta[nf:] * (np.log10(g) - CENTER)
            pts, scale = points(b, data.q)
            print(
                f"| {g:,} | "
                + " | ".join(f"{w:+.1f}" for w in pts)
                + f" | {scale:.4f} |"
            )
        se = np.sqrt(np.diag(cov))
        print()
        print(
            "Slope per tenfold more games, log-odds: "
            + ", ".join(
                f"{n} {beta[nf + j]:+.3f} ± {se[nf + j]:.3f}"
                for j, n in enumerate(data.names)
            )
        )


if __name__ == "__main__":
    main()
