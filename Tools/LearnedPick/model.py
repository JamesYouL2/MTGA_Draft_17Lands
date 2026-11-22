"""The learned pick models: scoring, shared by training and the replay heads.

Four models score the cards of a pack from features.py's rows:

- "lgbm-strong": LightGBM ranking fitted to strong drafters' picks.
- "lgbm-wins": the same, fitted to all drafters' picks, each draft weighted by
  its event wins.
- "lgbm-strong-noalsa": lgbm-strong without ALSA. ALSA is the crowd's pick
  order, so it can buy agreement with human picks without buying wins; this
  head shows what the other features carry.
- "lgbm-weak": lgbm-strong-noalsa fitted to weak drafters' picks instead, a
  placebo (experiments/2026-11-21-learned-pick/DIAGNOSE.md, check 6).
- "logit-simple": a conditional logit on three inputs, on the app's point scale
  (50 at the set's mean card, 15 points a standard deviation of GIH WR).

A set's models live in <models>/<set>/, fitted without that set (train.py).
"""

import json
import os

import numpy as np

from features import FEATURES, pack_features

HEADS = ("lgbm-strong", "lgbm-wins", "lgbm-strong-noalsa", "lgbm-weak", "logit-simple")
# LightGBM heads: (training picks, features hidden from the model).
LGBM_HEADS = {
    "lgbm-strong": ("strong", ()),
    "lgbm-wins": ("wins", ()),
    "lgbm-strong-noalsa": ("strong", ("alsa",)),
    "lgbm-weak": ("weak", ("alsa",)),
}
LOGIT_INPUTS = ["quality", "lane_fit", "off_settled"]
UNRATED_QUALITY = -2.0  # the logit's stand-in for a card with no GIH WR
QUALITY_POINTS = 15.0
_col = {name: i for i, name in enumerate(FEATURES)}


def logit_inputs(X):
    """The logit's three inputs from feature rows.

    off_settled is off-color pips times how settled the lane is: from 0 at
    pick 1 to 1 by the end of pack 1, and 1 after."""
    X = np.asarray(X, dtype=np.float64)
    quality = np.nan_to_num(X[:, _col["quality"]], nan=UNRATED_QUALITY)
    lane_fit = np.nan_to_num(X[:, _col["lane_fit"]], nan=0.0)
    pack, pick = X[:, _col["pack"]], X[:, _col["pick"]]
    settled = np.where(pack >= 2, 1.0, np.clip((pick - 1) / 14.0, 0.0, 1.0))
    return np.column_stack([quality, lane_fit, X[:, _col["off_pips"]] * settled])


class Logit:
    def __init__(self, weights):
        self.weights = dict(weights)  # points per unit of each LOGIT_INPUTS

    def score(self, X):
        w = np.array([self.weights[k] for k in LOGIT_INPUTS])
        return 50.0 + logit_inputs(X) @ w


def masked(X, hidden):
    """X (a copy, if anything is hidden) with the hidden features missing."""
    if not hidden:
        return X
    X = np.array(X)
    for f in hidden:
        X[:, _col[f]] = np.nan
    return X


class LightGBM:
    def __init__(self, path, hidden=()):
        import lightgbm

        self.booster = lightgbm.Booster(model_file=path)
        self.hidden = tuple(hidden)

    def score(self, X):
        X = masked(np.asarray(X, dtype=np.float64), self.hidden)
        return 50.0 + 10.0 * self.booster.predict(X, num_threads=1)


def load(models_dir, set_code, head):
    folder = os.path.join(models_dir, set_code)
    if head == "logit-simple":
        with open(os.path.join(folder, "logit-simple.json"), encoding="utf-8") as f:
            return Logit(json.load(f)["weights"])
    return LightGBM(os.path.join(folder, f"{head}.txt"), LGBM_HEADS[head][1])


def score_pack(model, pack, pool, pack_no, pick_no, mean, sd):
    """{card name: score} for the distinct cards in the pack."""
    rows = pack_features(pack, pool, pack_no, pick_no, mean, sd)
    if not rows:
        return {}
    names = list(rows)
    scores = model.score(np.array([rows[n] for n in names], dtype=np.float64))
    return {n: float(s) for n, s in zip(names, scores)}
