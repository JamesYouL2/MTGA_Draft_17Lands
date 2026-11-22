import math

import pytest

from features import FEATURES, card_features, color_counts, lane, off_pips, pack_features


def card(name, colors, gihwr=56.0, cost="", pairs=None, types=("Creature",), cmc=2):
    deck_colors = {"All Decks": {"gihwr": gihwr, "iwd": 3.0, "alsa": 4.5}}
    for pair, (wr, samples) in (pairs or {}).items():
        deck_colors[pair] = {"gihwr": wr, "samples": samples}
    return {
        "name": name,
        "colors": list(colors),
        "mana_cost": cost,
        "types": list(types),
        "cmc": cmc,
        "deck_colors": deck_colors,
    }


def row(c, pool, pack_no=1, pick_no=5, mean=55.0, sd=4.0):
    values = card_features(c, color_counts(pool), lane(pool), pack_no, pick_no, mean, sd)
    return dict(zip(FEATURES, values))


def test_lane_is_the_top_two_colors_of_nonland_cards():
    pool = [card("a", "W"), card("b", "W"), card("c", "U"), card("d", "B")]
    pool += [card("e", "B"), card("f", "B"), card("g", "G", types=("Land",))]
    assert lane(pool) == ["B", "W"]
    assert lane([card("a", "R")]) == ["R"]
    assert lane([]) == []


def test_off_pips_counts_symbols_the_lane_cannot_pay():
    assert off_pips(card("x", "R", cost="{2}{R}{R}"), ["W", "U"]) == 2
    assert off_pips(card("x", "UR", cost="{U}{R}"), ["W", "U"]) == 1
    # Hybrid with one option in the lane, Phyrexian and two-brid symbols are free.
    assert off_pips(card("x", "UR", cost="{U/R}{R/P}{2/R}"), ["W", "U"]) == 0
    assert off_pips(card("x", "R", cost="{R/G}"), ["W", "U"]) == 1
    # Before the pool has a color, nothing is off-color.
    assert off_pips(card("x", "R", cost="{R}"), []) == 0
    # Without a mana cost, each off color counts once.
    assert off_pips(card("x", "BR"), ["W", "B"]) == 1


def test_quality_and_lane_fit_are_in_sds_of_the_set():
    pool = [card("a", "W"), card("b", "U")]
    c = card("x", "W", gihwr=59.0, pairs={"WU": (61.0, 50)})
    r = row(c, pool)
    assert r["quality"] == pytest.approx(1.0)
    assert r["lane_fit"] == pytest.approx(0.5)
    # Too few pair samples, or no second lane color: no lane fit.
    thin = card("x", "W", gihwr=59.0, pairs={"WU": (61.0, 5)})
    assert math.isnan(row(thin, pool)["lane_fit"])
    assert math.isnan(row(c, [card("a", "W")])["lane_fit"])


def test_unrated_card_has_no_quality():
    r = row(card("x", "W", gihwr=0.0), [])
    assert math.isnan(r["quality"]) and math.isnan(r["lane_fit"])


def test_color_share_is_the_thinnest_colors_share():
    pool = [card("a", "W"), card("b", "W"), card("c", "W"), card("d", "U")]
    assert row(card("x", "WU"), pool)["color_share"] == pytest.approx(0.25)
    assert row(card("x", ""), pool)["color_share"] == 1.0
    assert math.isnan(row(card("x", "W"), [])["color_share"])


def test_pack_features_has_one_row_per_distinct_card():
    pack = [card("x", "W"), card("x", "W"), card("y", "U")]
    rows = pack_features(pack, [], 2, 3, 55.0, 4.0)
    assert set(rows) == {"x", "y"}
    assert dict(zip(FEATURES, rows["x"]))["pack"] == 2.0
    assert dict(zip(FEATURES, rows["x"]))["pick"] == 3.0
