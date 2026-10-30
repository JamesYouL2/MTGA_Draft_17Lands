"""Fit the pick score's weights to strong drafters' picks, and report how well
they do.

    python Tools/PickFit/fit.py results/*.json.gz > report.md

The fit is a conditional logit: at each pick, the chance a strong drafter takes
a card is proportional to exp(sum of weight * feature) over the cards in the
pack. It is fitted over all sets at once, with standard errors that allow for
picks in the same draft being alike. The weights come out in the score's own
points, where the app's quality weight (15 points) is one standard deviation
of GIH WR.

Needs NumPy. If LightGBM is installed, the report also shows how a ranking
model with no linear form and more facts about each card does, as a yardstick.
"""

import argparse
import gzip
import json
import sys

import numpy as np

QUALITY = "quality"
QUALITY_POINTS = 15.0


class Data:
    """Picks from features.py, as arrays: one row per card, one group per pick."""

    def __init__(self, files):
        """files: features.py outputs, read one at a time (any iterable)."""
        X, extra, sizes, chosen, sets, drafts, packs = [], [], [], [], [], [], []
        self.skipped = {}
        for f in files:
            names = f["names"]
            self.weights = f["weights"]
            self.log_odds_per_point = f["log_odds_per_point"]
            self.extra_names = f["extra_names"]
            self.skipped[f["set"]] = (f["drafts"], f["skipped"], f["unmatched"])
            situations = f.pop("situations")
            X.append(np.array([x for s in situations for x in s["x"]], dtype=float))
            extra.append(
                np.array([e for s in situations for e in s["extra"]], dtype=float)
            )
            sizes += [len(s["x"]) for s in situations]
            chosen += [s["chosen"] for s in situations]
            sets += [f["set"]] * len(situations)
            drafts += [f"{f['set']}:{s['draft']}" for s in situations]
            packs += [s["pack"] for s in situations]
            del situations
        X = np.vstack(X)
        self.extra = np.vstack(extra)
        self.sizes = np.array(sizes)
        self.starts = np.concatenate([[0], np.cumsum(self.sizes)[:-1]]).astype(int)
        self.chosen = self.starts + np.array(chosen, dtype=int)
        self.set = np.array(sets)
        self.sets = sorted(set(sets))
        self.pack = np.array(packs)
        _, self.draft = np.unique(np.array(drafts), return_inverse=True)

        # A feature that never differs between the cards of a pick can't be fitted.
        varies = [
            bool(
                np.any(
                    np.maximum.reduceat(X[:, j], self.starts)
                    - np.minimum.reduceat(X[:, j], self.starts)
                )
            )
            for j in range(len(names))
        ]
        self.never = [k for k, v in zip(names, varies) if not v]
        self.names = [k for k, v in zip(names, varies) if v]
        self.X = X[:, varies]
        self.q = self.names.index(QUALITY)
        self.app = (
            np.array([self.weights[k] for k in self.names]) * self.log_odds_per_point
        )

    def subset(self, groups):
        """The picks where groups (a boolean per pick) is true."""
        out = object.__new__(Data)
        out.__dict__.update(self.__dict__)
        rows = np.repeat(groups, self.sizes)
        out.X, out.extra = self.X[rows], self.extra[rows]
        out.sizes = self.sizes[groups]
        out.starts = np.concatenate([[0], np.cumsum(out.sizes)[:-1]]).astype(int)
        out.chosen = out.starts + (self.chosen - self.starts)[groups]
        out.set, out.pack, out.draft = (
            self.set[groups],
            self.pack[groups],
            self.draft[groups],
        )
        return out


def softmax(u, data):
    """Each card's chance within its pick, and each pick's log-sum-exp."""
    top = np.maximum.reduceat(u, data.starts)
    e = np.exp(u - np.repeat(top, data.sizes))
    total = np.add.reduceat(e, data.starts)
    return e / np.repeat(total, data.sizes), top + np.log(total)


def log_lik(u, data):
    return float(np.sum(u[data.chosen] - softmax(u, data)[1]))


def fit_logit(X, data, ridge=1e-8, iters=100):
    """Conditional logit weights and their covariance, clustered by draft."""
    k = X.shape[1]
    beta = np.zeros(k)
    xc = X[data.chosen]
    ll = log_lik(X @ beta, data)
    for _ in range(iters):
        p, _ = softmax(X @ beta, data)
        xbar = np.add.reduceat(X * p[:, None], data.starts)
        grad = (xc - xbar).sum(0) - ridge * beta
        H = (X * p[:, None]).T @ X - xbar.T @ xbar + ridge * np.eye(k)
        step = np.linalg.solve(H, grad)
        # Newton's method, halving the step if it would lower the likelihood.
        while True:
            new_ll = log_lik(X @ (beta + step), data)
            if new_ll >= ll - 1e-9 or np.max(np.abs(step)) < 1e-12:
                break
            step /= 2
        beta, ll = beta + step, new_ll
        if np.max(np.abs(step)) < 1e-9:
            break
    p, _ = softmax(X @ beta, data)
    xbar = np.add.reduceat(X * p[:, None], data.starts)
    H = (X * p[:, None]).T @ X - xbar.T @ xbar + ridge * np.eye(k)
    order = np.argsort(data.draft, kind="stable")
    cuts = np.flatnonzero(np.diff(data.draft[order])) + 1
    per_draft = np.add.reduceat((xc - xbar)[order], np.concatenate([[0], cuts]))
    H_inv = np.linalg.inv(H)
    return beta, H_inv @ per_draft.T @ per_draft @ H_inv


def to_points(beta, cov, q):
    """Weights in points (quality = 15) and their delta-method SEs."""
    points = QUALITY_POINTS * beta / beta[q]
    se = []
    for j in range(len(beta)):
        g = np.zeros(len(beta))
        g[j] += QUALITY_POINTS / beta[q]
        g[q] -= QUALITY_POINTS * beta[j] / beta[q] ** 2
        se.append(float(np.sqrt(g @ cov @ g)))
    return points, np.array(se)


def top_k(u, data, k):
    """For each pick, the chance the chosen card is in the model's top k, with
    ties broken at random."""
    uc = np.repeat(u[data.chosen], data.sizes)
    above = np.add.reduceat((u > uc + 1e-9).astype(float), data.starts)
    tied = np.add.reduceat((np.abs(u - uc) <= 1e-9).astype(float), data.starts)
    return np.clip((k - above) / tied, 0.0, 1.0)


def evaluate(u, data, calibrated=True):
    """Top-1 and top-3 agreement (%) and log loss per pick."""
    loss = -np.mean(u[data.chosen] - softmax(u, data)[1]) if calibrated else None
    return 100 * top_k(u, data, 1).mean(), 100 * top_k(u, data, 3).mean(), loss


def lightgbm_score(data, train, test, max_picks=150_000, seed=0):
    """Raw scores from a LightGBM ranker on the features and the plain facts."""
    try:
        import lightgbm
    except ImportError:
        return None
    rng = np.random.default_rng(seed)
    picks = np.flatnonzero(train)
    if len(picks) > max_picks:
        keep = np.zeros(len(train), dtype=bool)
        keep[rng.choice(picks, max_picks, replace=False)] = True
        train = keep
    tr, te = data.subset(train), data.subset(test)
    label = np.zeros(len(tr.X))
    label[tr.chosen] = 1
    booster = lightgbm.train(
        {
            "objective": "lambdarank",
            "learning_rate": 0.05,
            "num_leaves": 63,
            "min_data_in_leaf": 200,
            "verbose": -1,
            "seed": seed,
        },
        lightgbm.Dataset(np.hstack([tr.X, tr.extra]), label=label, group=tr.sizes),
        num_boost_round=300,
    )
    return booster.predict(np.hstack([te.X, te.extra]))


def held_out(data):
    """Leave one set out: fit on the others, score the one left out."""
    rows = []
    for s in data.sets:
        test = data.set == s
        tr, te = data.subset(~test), data.subset(test)
        q_only, _ = fit_logit(tr.X[:, [data.q]], tr)
        fitted, _ = fit_logit(tr.X, tr)
        models = {
            "GIH WR only": (te.X[:, [data.q]] @ q_only, True),
            "app weights": (te.X @ data.app, True),
            "fitted": (te.X @ fitted, True),
        }
        gbm = lightgbm_score(data, ~test, test)
        if gbm is not None:
            models["LightGBM"] = (gbm, False)
        rows.append((s, te, models))
    return rows


def pooled(rows, model, k):
    hits = [top_k(m[model][0], te, k) for _, te, m in rows if model in m]
    return 100 * np.concatenate(hits).mean()


def report(data, out=sys.stdout):
    def p(line=""):
        print(line, file=out)

    picks = len(data.sizes)
    p(
        f"{picks:,} picks by strong drafters, {len(np.unique(data.draft)):,} drafts, "
        f"{len(data.sets)} sets, {data.sizes.mean():.1f} cards to choose from on average."
    )
    p()
    p("| set | drafts | picks | skipped | unmatched card names |")
    p("|---|---|---|---|---|")
    for s in data.sets:
        drafts, skipped, unmatched = data.skipped[s]
        p(
            f"| {s} | {drafts} | {(data.set == s).sum():,} | "
            f"{sum(skipped.values())} | {', '.join(unmatched) or '-'} |"
        )
    if data.never:
        p()
        p(f"Never differ within a pick, so not fitted: {', '.join(data.never)}.")

    beta, cov = fit_logit(data.X, data)
    points, se = to_points(beta, cov, data.q)
    p()
    p("## Fitted weights, all sets")
    p()
    p("Points per unit of each feature, ± one standard error (clustered by draft).")
    p()
    p("| feature | app | fitted |")
    p("|---|---|---|")
    for j, k in enumerate(data.names):
        p(f"| {k} | {data.weights[k]:+.1f} | {points[j]:+.1f} ± {se[j]:.1f} |")
    p()
    p(
        f"A point is {beta[data.q] / QUALITY_POINTS:.4f} log-odds "
        f"(app: {data.log_odds_per_point:.4f})."
    )

    p()
    p("## Fitted weights by set")
    p()
    p("| set | " + " | ".join(data.names) + " |")
    p("|---|" + "---|" * len(data.names))
    for s in data.sets:
        sub = data.subset(data.set == s)
        b, c = fit_logit(sub.X, sub)
        pts, err = to_points(b, c, data.q)
        p(
            f"| {s} | "
            + " | ".join(f"{v:+.1f} ± {e:.1f}" for v, e in zip(pts, err))
            + " |"
        )

    rows = held_out(data)
    models = list(rows[0][2])
    p()
    p("## Held-out sets")
    p()
    p(
        "Each set scored by a fit to the other sets. Top-1 is how often the "
        "model's best card is the one the strong drafter took; top-3, how often "
        "it is among the model's best three. Log loss is per pick (lower is "
        "better); LightGBM ranks, so has none."
    )
    p()
    p("| set | picks | " + " | ".join(f"{m} top-1" for m in models) + " |")
    p("|---|---|" + "---|" * len(models))
    for s, te, m in rows:
        p(
            f"| {s} | {len(te.sizes):,} | "
            + " | ".join(f"{evaluate(m[k][0], te)[0]:.1f}" for k in models)
            + " |"
        )
    p()
    p("| model | top-1 | top-3 | log loss | top-1 pack 1 | pack 2 | pack 3 |")
    p("|---|---|---|---|---|---|---|")
    for k in models:
        calibrated = rows[0][2][k][1]
        losses = (
            [evaluate(m[k][0], te)[2] * len(te.sizes) for _, te, m in rows]
            if calibrated
            else None
        )
        by_pack = []
        for pack in (1, 2, 3):
            hits = [top_k(m[k][0], te, 1)[te.pack == pack] for _, te, m in rows]
            by_pack.append(100 * np.concatenate(hits).mean())
        loss = f"{sum(losses) / picks:.3f}" if losses else "-"
        p(
            f"| {k} | {pooled(rows, k, 1):.1f} | {pooled(rows, k, 3):.1f} | {loss} | "
            + " | ".join(f"{v:.1f}" for v in by_pack)
            + " |"
        )

    p()
    p("## For src/advisor/engine.py")
    p()
    p("```python")
    p("WEIGHTS = {")
    for j, k in enumerate(data.names):
        p(f'    "{k}": {points[j]:.1f},')
    for k in data.never:
        p(f'    "{k}": {data.weights[k]:.1f},  # not fitted')
    p("}")
    p(f"PICK_LOG_ODDS_PER_POINT = {beta[data.q] / QUALITY_POINTS:.4f}")
    p("```")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("files", nargs="+", help="features.py outputs")
    args = parser.parse_args(argv)

    def load(path):
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as f:
            return json.load(f)

    report(Data(load(path) for path in args.files))


if __name__ == "__main__":
    main()
