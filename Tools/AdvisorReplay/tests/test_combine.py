import os
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "experiments", "2026-11-08-heldout-replay"))
import compare as C  # noqa: E402


def test_no_spread_between_salts_gives_the_bootstrap_se():
    m = C.combine([0.02] * 4, [0.01] * 4)
    assert m["estimate"] == pytest.approx(0.02)
    assert m["tau"] == 0
    # Four salts of SE 0.01 pooled: the bootstrap-only SE of the whole run.
    assert m["se"] == pytest.approx(0.005) and m["fixed_se"] == pytest.approx(0.005)
    assert m["q"] == pytest.approx(0) and m["phi"] == pytest.approx(0)


def test_spread_within_the_bootstrap_ses_keeps_the_bootstrap_se():
    # Q = 2.5 on 3 df: no more spread than the SEs allow.
    m = C.combine([0.01, 0.0, 0.015, 0.005], [0.01] * 4)
    assert m["tau"] == 0
    assert m["se"] == pytest.approx(m["fixed_se"])


def test_spread_between_salts_widens_the_se():
    e, b = [0.03, -0.02, 0.04, -0.01], [0.005] * 4
    m = C.combine(e, b)
    assert m["tau"] > 0
    assert m["se"] > 2 * m["fixed_se"]
    # The salts as four plain observations: their SE of the mean.
    assert m["se"] == pytest.approx(np.std(e, ddof=1) / 2, rel=0.05)
    assert m["phi"] == pytest.approx(np.sqrt(m["q"] / 3))
    assert m["phi_low"] < m["phi"] < m["phi_high"]


def test_few_salts_use_t_quantiles():
    four = C.combine([0.0, 0.01, 0.0, 0.01], [0.01] * 4)
    assert four["df"] == 3
    assert four["t"] == pytest.approx(3.182, abs=1e-3)
    assert four["scaled_se"] == pytest.approx(four["se"] * 3.182 / 1.960, rel=1e-3)
    eight = C.combine([0.0, 0.01] * 4, [0.01] * 8)
    assert eight["scaled_se"] / eight["se"] == pytest.approx(2.365 / 1.960, rel=1e-3)
    assert four["high"] - four["low"] == pytest.approx(2 * four["t"] * four["se"])


def test_a_thin_salt_counts_less():
    m = C.combine([0.0, 0.0, 0.0, 1.0], [0.01, 0.01, 0.01, 1.0])
    assert m["estimate"] < 0.01


def test_one_salt_is_its_bootstrap_alone():
    m = C.combine([0.02], [0.01])
    assert (m["estimate"], m["se"], m["scaled_se"], m["df"]) == (0.02, 0.01, 0.01, 0)
    assert np.isnan(m["phi"])


def test_a_head_that_changes_nothing():
    m = C.combine([0.0, 0.0], [0.0, 0.0])
    assert (m["estimate"], m["se"]) == (0.0, 0.0)


def test_a_salt_where_the_head_changed_nothing_counts_as_the_surest_other():
    m = C.combine([0.0, 0.02, 0.04], [0.0, 0.01, 0.02])
    assert m["estimate"] == pytest.approx(C.combine([0.0, 0.02, 0.04], [0.01, 0.01, 0.02])["estimate"])


def test_inflation_interval_narrows_with_more_degrees_of_freedom():
    _, lo3, hi3 = C.inflation(3 * 4.0, 3)
    _, lo70, hi70 = C.inflation(70 * 4.0, 70)
    assert lo3 < lo70 < 2 < hi70 < hi3


def test_by_salt_groups_events_by_salt():
    keys = [("FRA", f"{s}:{i}") for s in ("a", "b") for i in range(20)]
    x = np.r_[np.zeros(20), np.ones(20)] + np.tile(np.linspace(-1, 1, 20), 2)
    out = C.by_salt(keys, lambda idx: x[idx].mean())
    assert list(out) == ["a", "b"]
    assert out["a"][0] == pytest.approx(0) and out["b"][0] == pytest.approx(1)
    assert out["a"][1] > 0
