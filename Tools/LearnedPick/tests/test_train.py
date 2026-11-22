import json
import os

import numpy as np
import pytest

from features import FEATURES
import train as T

col = {f: i for i, f in enumerate(FEATURES)}


def synthetic(seed, n_picks=1500, weights=(1.2, 0.6, -0.9), pack_size=6):
    """Rows whose picks follow a conditional logit with known coefficients
    on (quality, lane_fit, off_settled)."""
    rng = np.random.default_rng(seed)
    X = np.full((n_picks * pack_size, len(FEATURES)), np.nan, dtype=np.float32)
    X[:, col["quality"]] = rng.normal(size=len(X))
    X[:, col["lane_fit"]] = rng.normal(scale=0.5, size=len(X))
    X[:, col["off_pips"]] = rng.integers(0, 3, size=len(X))
    X[:, col["pack"]] = 2.0  # lane settled: off_settled == off_pips
    X[:, col["pick"]] = 3.0
    for f in ("color_share", "iwd", "mana_value", "creature", "alsa", "n_colors"):
        X[:, col[f]] = rng.normal(size=len(X))
    u = (
        weights[0] * X[:, col["quality"]]
        + weights[1] * X[:, col["lane_fit"]]
        + weights[2] * X[:, col["off_pips"]]
    ).reshape(n_picks, pack_size)
    p = np.exp(u - u.max(axis=1, keepdims=True))
    p /= p.sum(axis=1, keepdims=True)
    taken = np.array([rng.choice(pack_size, p=row) for row in p])
    label = np.zeros((n_picks, pack_size), dtype=np.int8)
    label[np.arange(n_picks), taken] = 1
    return {
        "X": X,
        "label": label.ravel(),
        "group": np.full(n_picks, pack_size, dtype=np.int32),
        "wins": rng.integers(0, 8, size=n_picks).astype(np.float32),
        "strong": rng.random(n_picks) < 0.5,
        "in_strong": np.ones(n_picks, dtype=bool),
        "in_all": np.ones(n_picks, dtype=bool),
        "draft": np.arange(n_picks, dtype=np.int32) // 40,
    }


def test_logit_recovers_known_weights():
    data = synthetic(0, n_picks=6000)
    picks = T.Picks(data["X"], data["label"], data["group"],
                    np.ones(len(data["group"])), np.array(["S"] * len(data["group"])))
    beta, cov = T.fit_logit(picks)
    assert beta == pytest.approx([1.2, 0.6, -0.9], abs=0.08)
    points, ses = T.logit_points(beta, cov)
    assert points["quality"] == pytest.approx(15.0)
    assert points["lane_fit"] == pytest.approx(15 * 0.6 / 1.2, abs=1.2)
    assert all(v > 0 for k, v in ses.items() if k != "quality")


def test_agreement_counts_the_card_taken_being_top():
    X = np.zeros((6, len(FEATURES)), dtype=np.float32)
    picks = T.Picks(X, np.array([1, 0, 0, 0, 1, 0], dtype=np.int8),
                    np.array([3, 3]), np.ones(2), np.array(["S", "S"]))
    # First pick: taken card scores best. Second: taken card is second of three.
    scores = np.array([3.0, 2.0, 1.0, 5.0, 4.0, 0.0])
    assert T.agreement(picks, scores) == (50.0, 100.0)


def test_validation_sets_come_from_the_training_sets_only():
    sets = [f"S{i}" for i in range(10)]
    valid = T.validation_sets(sets, "HELD")
    assert len(valid) == 4 and set(valid) <= set(sets)
    assert T.validation_sets(sets, "HELD") == valid


def test_heldout_set_never_reaches_the_fit(tmp_path, monkeypatch):
    """Changing every pick of the held-out set leaves its models unchanged."""
    rows = {s: synthetic(i) for i, s in enumerate(["A", "B", "C", "D", "E", "F"])}
    seen = []
    real_fit_lgbm = T.fit_lgbm

    def no_lgbm(train, valid):
        seen.append(set(train.sets) | set(valid.sets))

        class Booster:
            def save_model(self, path):
                open(path, "w").close()

            def feature_importance(self, importance_type):
                return np.ones(len(FEATURES))

            def predict(self, X):
                return np.asarray(X[:, col["quality"]], dtype=np.float64)

        return {"leaves": 0, "rounds": 0}, [], Booster()

    monkeypatch.setattr(T, "fit_lgbm", no_lgbm)
    s1 = T.train(rows, "F", str(tmp_path / "one"))
    flipped = dict(rows)
    flipped["F"] = synthetic(99)
    s2 = T.train(flipped, "F", str(tmp_path / "two"))
    assert all("F" not in s for s in seen)
    assert "F" not in s1["train_sets"] and set(s1["validation_sets"]) <= set(s1["train_sets"])
    assert s1["models"]["logit-simple"]["weights"] == s2["models"]["logit-simple"]["weights"]
    # The held-out check does read the held-out set.
    assert s1["models"]["logit-simple"]["heldout"] != s2["models"]["logit-simple"]["heldout"]
    with open(tmp_path / "one" / "F" / "logit-simple.json") as f:
        assert json.load(f)["weights"]["quality"] == pytest.approx(15.0)
    assert real_fit_lgbm is not no_lgbm


def test_lightgbm_ranks_better_than_chance():
    pytest.importorskip("lightgbm")
    train, valid = synthetic(1), synthetic(2)
    to_picks = lambda d: T.picks_of({"S": d}, ["S"], "strong")
    best, grid, booster = T.fit_lgbm(to_picks(train), to_picks(valid))
    test = to_picks(synthetic(3))
    top1, _ = T.agreement(test, booster.predict(test.X))
    assert top1 > 100 / 6 + 10
    assert best in grid
