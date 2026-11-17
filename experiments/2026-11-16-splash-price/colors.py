"""Does the deck score need a different price for a splash than for three colors?

    python experiments/2026-11-16-splash-price/colors.py results/*.json > colors.md

Reads the features.py output of the Deck score fit's features step. Every model
here is fit.py's: a logistic regression of each deck's games won, with the set
and the player's buckets held equal, weights in score points (12 points are one
standard deviation of card quality). See PROTOCOL.md for the questions and the
decision rule.
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
from fit import Data, fit_clustered, fit_logit, log_loss, varying  # noqa: E402

SCALE = 12.0  # the app's card_quality weight: points per SD of card quality
GROUPS = ("splash", "three", "more")  # against two colors or fewer
LABELS = {
    "two": "two colors or fewer, no splash",
    "splash": "two main colors and a splash",
    "three": "three main colors, no splash",
    "more": "three main colors and a splash, or four or more",
}
BINS = ("1", "2", "3", "4+")


def in_bin(n, b):
    """Splash sizes: "1" holds 0 or 1 spells (a splash for a land or a colorless
    card's cost), "4+" four or more."""
    return {"1": n <= 1, "2": n == 2, "3": n == 3, "4+": n >= 4}[b]


def group(row):
    """The deck's color group. "two" is exactly the app's two_colors feature."""
    if row["features"]["two_colors"]:
        return "two"
    main = len(set(row["colors"]["main"]))
    splash = bool(row["colors"]["splash"])
    if main <= 2:
        return "splash"
    if main == 3 and not splash:
        return "three"
    return "more"


class Decks:
    def __init__(self, files):
        self.data = data = Data(files)
        rows = data.rows
        self.group = np.array([group(r) for r in rows])
        self.quality = np.array([r["features"]["card_quality"] for r in rows])
        self.fixing = np.array([r["features"]["missing_fixing"] for r in rows])
        self.splash_cards = np.array([r["colors"]["splash_cards"] for r in rows])
        self.set, self.sets = data.set, data.sets
        self.wins, self.games, self.C = data.wins, data.games, data.C

    def columns(self, model):
        """The deck's own columns for a model; card quality is always first."""
        cols = [self.quality, self.fixing]
        if model == "single":
            cols.append((self.group != "two").astype(float))
        else:
            cols += [(self.group == g).astype(float) for g in GROUPS]
        if model == "size":
            in_splash = self.group == "splash"
            cols = cols[:2] + [(self.group == g).astype(float) for g in GROUPS[1:]]
            for b in BINS:
                cols.append((in_splash & in_bin(self.splash_cards, b)).astype(float))
        if model == "slope":
            in_splash = (self.group == "splash").astype(float)
            cols.append(in_splash * (self.splash_cards - 2.0))
        return np.column_stack(cols)

    def design(self, X, mask):
        sets = sorted(set(self.set[mask]))
        dummies = np.array([[s == t for t in sets] for s in self.set[mask]], dtype=float)
        return np.hstack([X[mask], dummies, varying(self.C[mask])]), len(sets)


def points(beta, covs, c):
    """A contrast c of the deck coefficients, in score points, and its SE: the
    larger of the model's and the set-clustered one."""
    c = np.r_[c, np.zeros(len(beta) - len(c))]
    value = SCALE * (c @ beta) / beta[0]
    g = SCALE * c / beta[0]
    g[0] -= SCALE * (c @ beta) / beta[0] ** 2
    se = max(math.sqrt(g @ cov @ g) for cov in covs if cov is not None)
    return value, se


def fit(d, model, mask=None, clusters=True):
    mask = np.ones(len(d.set), dtype=bool) if mask is None else mask
    X = d.columns(model)
    A, _ = d.design(X, mask)
    beta, cov, cluster = fit_clustered(
        A, d.wins[mask], d.games[mask], d.set[mask] if clusters else None
    )
    return beta, (cov, cluster), X.shape[1]


def unit(k, n):
    c = np.zeros(n)
    c[k] = 1.0
    return c


def held_out(d):
    """Log loss per game on each set, from the single and split models fit on
    the other sets (fit.py's method: player terms kept, one intercept refit)."""
    out = {}
    for s in d.sets:
        train, test = d.set != s, d.set == s
        row = {}
        for model in ("single", "split"):
            X = d.columns(model)
            A, n_sets = d.design(X, train)
            beta = fit_logit(A, d.wins[train], d.games[train])[0]
            k = X.shape[1]
            player_cols = varying(d.C[train])
            # Same player columns on the test rows as in training.
            keep = d.C[train].min(axis=0) != d.C[train].max(axis=0)
            eta = X[test] @ beta[:k] + d.C[test][:, keep] @ beta[k + n_sets :]
            assert player_cols.shape[1] == keep.sum()
            row[model] = log_loss(eta, d.wins[test], d.games[test])
        out[s] = row
    return out


def cell(v, se):
    return f"{v:+.2f} ± {se:.2f} ({v / se:+.1f} SEs)"


def report(d, w):
    n = len(d.set)
    w(f"{n} decks, {int(d.games.sum())} games, {len(d.sets)} sets.\n")

    w("## The groups\n")
    w("| group | decks | game win rate | mean card quality (SDs) |")
    w("|---|---|---|---|")
    for g in ("two", *GROUPS):
        m = d.group == g
        w(f"| {LABELS[g]} | {m.mean():.1%} | {d.wins[m].sum() / d.games[m].sum():.1%} "
          f"| {d.quality[m].mean():+.2f} |")
    w()

    beta, covs, k = fit(d, "single")
    single = points(beta, covs, unit(2, k))
    w("## Q0. Today's single weight, refit\n")
    w(f"3+ colors against two or fewer: {cell(*single)} points "
      f"(the app's two_colors weight is +3.1, so -3.1 here).\n")

    beta, covs, k = fit(d, "split")
    w("## Q1. Splash against three main colors\n")
    w("Each group against decks of two colors or fewer, in score points.\n")
    w("| group | weight |")
    w("|---|---|")
    split = {}
    for i, g in enumerate(GROUPS):
        split[g] = points(beta, covs, unit(2 + i, k))
        w(f"| {LABELS[g]} | {cell(*split[g])} |")
    diff = points(beta, covs, unit(2, k) - unit(3, k))
    w(f"\nSplash less three main colors: **{cell(*diff)}**.\n")

    w("## Q2. Does a bigger splash cost more?\n")
    beta, covs, k = fit(d, "size")
    w("Two main colors and a splash, by how many spells need the splash, against "
      "decks of two colors or fewer.\n")
    w("| spells needing the splash | decks (share of splash decks) | weight |")
    w("|---|---|---|")
    in_splash = d.group == "splash"
    for i, b in enumerate(BINS):
        hit = in_bin(d.splash_cards[in_splash], b)
        w(f"| {b if b != '1' else '0 or 1'} | {hit.mean():.1%} | "
          f"{cell(*points(beta, covs, unit(4 + i, k)))} |")
    beta, covs, k = fit(d, "slope")
    slope = points(beta, covs, unit(5, k))
    w(f"\nPer spell needing the splash, as a straight line: {cell(*slope)}.\n")

    w("## Q3. On sets the fit didn't see\n")
    ho = held_out(d)
    weight = {s: d.games[d.set == s].sum() for s in d.sets}
    gain = {s: 1e5 * (ho[s]["single"] - ho[s]["split"]) for s in d.sets}
    total = sum(gain[s] * weight[s] for s in d.sets) / sum(weight.values())
    better = sum(g > 0 for g in gain.values())
    vals = np.array([gain[s] for s in d.sets])
    w("Log loss per game of the single weight less the split weights, in units of "
      "1e-5 (positive: the split predicts better).\n")
    w("| " + " | ".join(d.sets) + " |")
    w("|---" * len(d.sets) + "|")
    w("| " + " | ".join(f"{gain[s]:+.1f}" for s in d.sets) + " |")
    w(f"\nWeighted by games: {total:+.2f}. Better on {better} of {len(d.sets)} sets. "
      f"Mean {vals.mean():+.2f}, SE across sets {vals.std(ddof=1) / math.sqrt(len(vals)):.2f}.\n")

    w("## Q4. Each set alone\n")
    w("Splash and three-main weights fit on each set by itself (model SEs). "
      "`–` where a group has fewer than 300 decks.\n")
    w("| set | splash | three main | splash less three |")
    w("|---|---|---|---|")
    same_sign = 0
    counted = 0
    for s in d.sets:
        m = d.set == s
        if min((m & (d.group == g)).sum() for g in ("splash", "three")) < 300:
            w(f"| {s} | – | – | – |")
            continue
        beta, covs, k = fit(d, "split", m, clusters=False)
        a = points(beta, covs, unit(2, k))
        b = points(beta, covs, unit(3, k))
        c = points(beta, covs, unit(2, k) - unit(3, k))
        counted += 1
        same_sign += (c[0] > 0) == (diff[0] > 0)
        w(f"| {s} | {a[0]:+.1f} ± {a[1]:.1f} | {b[0]:+.1f} ± {b[1]:.1f} | "
          f"{c[0]:+.1f} ± {c[1]:.1f} |")
    w(f"\nSame sign as the pooled difference in {same_sign} of {counted} sets.\n")

    w("## Verdict by the rule\n")
    split_passes = (
        abs(diff[0]) >= 2 * diff[1] and total > 0 and same_sign >= math.ceil(0.7 * counted)
    )
    w(f"- Split the weight: **{'yes' if split_passes else 'no'}** "
      f"(difference {diff[0] / diff[1]:+.1f} SEs, held-out {total:+.2f}, "
      f"same sign in {same_sign}/{counted}).")
    w(f"- Price the splash's size: **{'yes' if abs(slope[0]) >= 2 * slope[1] else 'no'}** "
      f"(slope {slope[0] / slope[1]:+.1f} SEs; reported only, see PROTOCOL.md).")
    weights = {g: round(v[0], 1) for g, v in split.items()}
    w(f"\nFitted split weights, for the record: {json.dumps(weights)}.")


def main(argv=None):
    paths = (argv if argv is not None else sys.argv[1:])
    files = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            files.append(json.load(f))
    report(Decks(files), print)


if __name__ == "__main__":
    main()
