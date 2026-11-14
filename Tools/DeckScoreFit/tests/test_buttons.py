import math

import numpy as np
import pytest

import buttons
import buttons_report as br


def test_proportional_gives_whole_shares_then_largest_remainders():
    assert buttons.proportional([10, 0, 5, 0, 0], 15) == [10, 0, 5, 0, 0]
    assert buttons.proportional([10, 0, 6, 0, 0], 17) == [11, 0, 6, 0, 0]
    assert sum(buttons.proportional([7, 3, 3, 0, 1], 16)) == 16


def test_proportional_breaks_a_tie_toward_more_pips():
    assert buttons.proportional([3, 1, 0, 0, 0], 2) == [2, 0, 0, 0, 0]
    assert buttons.proportional([0, 0, 0, 0, 0], 5) == [0, 0, 0, 0, 0]


def test_split_of_counts_basics_by_color():
    lands = [{"colors": ["W"], "count": 9}, {"colors": ["G"]}, {"colors": ["G"]}]
    assert buttons.split_of(lands) == [9, 0, 0, 0, 2]


def test_swap_kind_drops_the_cards():
    assert buttons.swap_kind("Optimized: Power Up (-Bear, +Bolt)") == "Power Up"
    assert buttons.swap_kind("Optimized: Play 16 Lands (+Bolt)") == "Play 16 Lands"
    assert buttons.swap_kind("Optimized: Base Deck") == "Base Deck"


def test_moved_is_lands_that_differ():
    assert br.moved([9, 8, 0, 0, 0], [8, 9, 0, 0, 0]) == 1.0
    assert br.moved([9, 8, 0, 0, 0], [9, 8, 0, 0, 0]) == 0.0


def test_clustered_mean_widens_when_clusters_disagree():
    x = np.array([1.0] * 50 + [-1.0] * 50)
    together = np.array(["A"] * 50 + ["B"] * 50)
    mixed = np.array(["A", "B"] * 50)
    assert br.clustered_mean(x, together)[0] == 0.0
    assert br.clustered_mean(x, together)[1] > 5 * br.clustered_mean(x, mixed)[1]
    assert br.clustered_mean(x, np.array(["A"] * 100))[1] == pytest.approx(
        np.std(x, ddof=1) / 10
    )


@pytest.mark.parametrize("outcome, nearer, expected", [
    ({"effect": 1.0, "se": 0.4}, {"effect": 0.1, "se": 0.01}, "keep"),
    ({"effect": -1.0, "se": 0.4}, {"effect": -0.1, "se": 0.01}, "remove"),
    ({"effect": 0.1, "se": 0.4}, {"effect": -0.1, "se": 0.01}, "keep"),
    ({"effect": 0.1, "se": 0.4}, {"effect": -0.01, "se": 0.01}, "remove"),
    ({"effect": None, "se": None}, {"effect": 0.1, "se": 0.01}, "remove"),
])
def test_lands_verdict(outcome, nearer, expected):
    assert br.lands_verdict(outcome, nearer) == expected


@pytest.mark.parametrize("changed, effect, se, expected", [
    (3.0, 1.0, 0.1, "remove"),
    (90.0, -0.3, 0.1, "remove"),
    (90.0, 0.3, 0.1, "keep"),
    (90.0, 0.1, 0.1, "no verdict"),
])
def test_optimize_verdict(changed, effect, se, expected):
    assert br.optimize_verdict({"changed": changed, "effect": effect, "se": se}) == expected


def test_land_count_swaps_count_as_zero_in_the_deciding_change():
    t = br.Table([])
    t.kind = np.array(["Play 18 Lands", "Power Up", "Base Deck", ""])
    t.set = np.array(["A", "A", "B", "B"])
    t.gain = np.array([2.0, 1.0, 0.0, math.nan])
    t.land_change = np.array([1, 0, 0, 0])
    s = br.optimize_summary(t)
    assert s["decks"] == 3
    assert s["effect"] == pytest.approx(1.0 / 3)
    assert s["kinds"]["Play 18 Lands"]["effect"] == 2.0
    assert s["changed"] == pytest.approx(200.0 / 3)
