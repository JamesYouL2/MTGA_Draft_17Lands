"""Is the expected record that Suggest Deck shows calibrated?

    python experiments/2026-11-16-record-calibration/calibrate.py results/*.json

Reads the features.py output (with 17Lands colors, as recorded since the splash price
experiment). See PROTOCOL.md for the method and the decision rule.
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "Tools", "DeckScoreFit"))
sys.path.insert(0, ROOT)
from fit import FIXED, expected_wins, fit_clustered, fit_logit  # noqa: E402

from src.advisor import deck_scorer  # noqa: E402

BANDS = [(-math.inf, 65), (65, 70), (70, 75), (75, 80), (80, 85), (85, 90), (90, math.inf)]
GROUPS = {
    "two": "two colors or fewer, no splash",
    "splash": "two main colors and a splash",
    "three": "three main colors, no splash",
    "more": "three main colors and a splash, or four or more",
}


def group(row):
    if row["features"]["two_colors"]:
        return "two"
    main = len(set(row["colors"]["main"]))
    if main <= 2:
        return "splash"
    if main == 3 and not row["colors"]["splash"]:
        return "three"
    return "more"


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def band_label(lo, hi):
    if lo == -math.inf:
        return f"under {hi}"
    if hi == math.inf:
        return f"{lo} and over"
    return f"{lo}-{hi}"


def wins_slope(p, h=1e-4):
    """Expected wins per unit of game win rate, at p."""
    return (expected_wins(p + h) - expected_wins(p - h)) / (2 * h)


class Decks:
    def __init__(self, paths):
        """Read one set at a time, keeping only what is needed, so twenty sets of
        features fit in a few hundred MB. Unfinished decks are left out, as in
        fit.py's Data."""
        cols = {k: [] for k in ("set", "score", "group", "wins", "games")}
        for path in paths:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.base, w = data["base_score"], data["weights"]
            for r in data["rows"]:
                if any(r["features"][k] for k in FIXED):
                    continue
                cols["set"].append(data["set"])
                cols["score"].append(self.base + sum(w[k] * r["features"][k] for k in w))
                cols["group"].append(group(r))
                cols["wins"].append(r["wins"])
                cols["games"].append(r["games"])
            del data
        self.set, self.group = np.array(cols["set"]), np.array(cols["group"])
        self.score = np.array(cols["score"])
        self.wins = np.array(cols["wins"], dtype=float)
        self.games = np.array(cols["games"], dtype=float)
        self.sets = sorted(set(cols["set"]))

    def held_out(self):
        """Predicted game win rate of each deck from constants fit on other sets."""
        p = np.zeros(len(self.set))
        constants = {}
        for s in self.sets:
            train, test = self.set != s, self.set == s
            A = np.column_stack([np.ones(train.sum()), self.score[train] - self.base])
            beta = fit_logit(A, self.wins[train], self.games[train])[0]
            constants[s] = beta
            p[test] = expit(beta[0] + beta[1] * (self.score[test] - self.base))
        return p, constants

    def current(self):
        a = deck_scorer.WIN_LOG_ODDS_AT_BASE
        b = deck_scorer.WIN_LOG_ODDS_PER_POINT
        return expit(a + b * (self.score - self.base))


def compare(d, p, mask):
    """Share, predicted and actual game win rate, and the gap in expected wins with
    its set-clustered SE, for the decks in mask."""
    g, wins, games = d.games[mask], d.wins[mask], d.games[mask] * p[mask]
    total = g.sum()
    predicted, actual = games.sum() / total, wins.sum() / total
    resid = {s: (wins - games)[d.set[mask] == s].sum() for s in d.sets}
    n = len(d.sets)
    se_wr = math.sqrt(sum(r * r for r in resid.values()) * n / (n - 1)) / total
    gap = expected_wins(actual) - expected_wins(predicted)
    se = se_wr * wins_slope((actual + predicted) / 2)
    return mask.mean(), predicted, actual, gap, se


def slope_intercept(d, p):
    eta = np.log(p / (1 - p))
    A = np.column_stack([np.ones(len(eta)), eta])
    beta, model, cluster = fit_clustered(A, d.wins, d.games, d.set)
    se = np.sqrt(np.maximum(np.diag(model), np.diag(cluster)))
    return beta, se


def table(d, p, w, title):
    w(f"### {title}\n")
    w("| decks | share | predicted game WR | actual game WR | actual less predicted, in expected wins |")
    w("|---|---|---|---|---|")
    fails = []
    rows = [(band_label(lo, hi), (d.score >= lo) & (d.score < hi)) for lo, hi in BANDS]
    rows += [(GROUPS[k], d.group == k) for k in GROUPS]
    rows.append(("all", np.ones(len(d.set), dtype=bool)))
    for label, mask in rows:
        if not mask.any():
            continue
        share, pred, act, gap, se = compare(d, p, mask)
        flag = share >= 0.02 and abs(gap) > 0.3 and abs(gap) >= 2 * se
        if flag:
            fails.append(label)
        w(f"| {label} | {share:.1%} | {pred:.1%} | {act:.1%} | "
          f"{gap:+.2f} ± {se:.2f}{' **fails**' if flag else ''} |")
    beta, se = slope_intercept(d, p)
    slope_fails = abs(beta[1] - 1) >= 2 * se[1]
    w(f"\nCalibration slope {beta[1]:.3f} ± {se[1]:.3f}"
      f"{' **fails**' if slope_fails else ''}, intercept {beta[0]:+.3f} ± {se[0]:.3f}.\n")
    return fails, slope_fails


def report(d, w):
    w(f"{len(d.set)} decks, {int(d.games.sum())} games, {len(d.sets)} sets. "
      f"Mean score {d.score.mean():.1f}.\n")
    held, constants = d.held_out()
    w("## Held out (the rule's test)\n")
    fails, slope_fails = table(d, held, w, f"Constants fit on the other {len(d.sets) - 1} sets")
    a = np.array([c[0] for c in constants.values()])
    b = np.array([c[1] for c in constants.values()])
    w(f"Held-out constants ranged: at base {a.min():+.4f} to {a.max():+.4f}, per point "
      f"{b.min():.5f} to {b.max():.5f}. App: {deck_scorer.WIN_LOG_ODDS_AT_BASE:+.4f}, "
      f"{deck_scorer.WIN_LOG_ODDS_PER_POINT:.5f}.\n")
    A = np.column_stack([np.ones(len(d.score)), d.score - d.base])
    allfit = fit_logit(A, d.wins, d.games)[0]
    w(f"Fit on all {len(d.sets)} sets: at base {allfit[0]:+.4f}, per point {allfit[1]:.5f}.\n")
    w("## The app's current constants\n")
    cur_fails, cur_slope = table(d, d.current(), w, "As in deck_scorer.py")
    w("## By set, held out\n")
    w("| set | predicted | actual | actual less predicted, expected wins |")
    w("|---|---|---|---|")
    for s in d.sets:
        m = d.set == s
        pred = (d.games[m] * held[m]).sum() / d.games[m].sum()
        act = d.wins[m].sum() / d.games[m].sum()
        w(f"| {s} | {pred:.1%} | {act:.1%} | {expected_wins(act) - expected_wins(pred):+.2f} |")
    w("\n## Verdict by the rule\n")
    verdict = bool(fails or slope_fails)
    w(f"- Held out: **{'refit' if verdict else 'calibrated'}** "
      f"(failing rows: {', '.join(fails) or 'none'}; slope {'fails' if slope_fails else 'passes'}).")
    w(f"- Current constants: failing rows: {', '.join(cur_fails) or 'none'}; "
      f"slope {'fails' if cur_slope else 'passes'}.")


def main(argv=None):
    report(Decks(argv if argv is not None else sys.argv[1:]), print)


if __name__ == "__main__":
    main()
