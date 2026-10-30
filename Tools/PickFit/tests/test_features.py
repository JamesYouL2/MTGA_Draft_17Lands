import os

import features
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATASET = os.path.join(ROOT, "tests", "data", "MKM_PremierDraft_Data_2024_5_3.json")


@pytest.fixture(scope="module")
def app():
    return features.App(DATASET)


def test_one_row_per_distinct_card(app):
    draft = {
        "picks": [
            [1, 1, "Murder", ["Shock", "Murder", "Shock", "Plains"], []],
            [1, 2, "Shock", ["Shock", "Mystery Key"], ["Murder"]],
        ]
    }

    (first, second), skipped = features.situations(app, [draft])

    assert not skipped
    assert len(first["x"]) == 2  # Shock once, no Plains
    assert first["chosen"] == 1
    assert (second["pack"], second["pick"], second["chosen"]) == (1, 2, 0)
    assert len(second["x"][0]) == len(app.engine.WEIGHTS)
    assert len(second["extra"][0]) == len(features.EXTRA_NAMES)


def test_features_are_the_apps(app):
    pool = app.cards(["Murder", "Murder", "Shock"])
    advisor = app.engine.DraftAdvisor(app.metrics, pool)
    expected = [
        [advisor.pick_features(c)[k] for k in app.engine.WEIGHTS]
        for c in app.cards(["Shock", "Mystery Key"])
    ]
    draft = {
        "picks": [[1, 4, "Shock", ["Shock", "Mystery Key"], ["Murder"] * 2 + ["Shock"]]]
    }

    (row,), _ = features.situations(app, [draft])

    assert row["x"] == expected


def test_skips_basic_and_unknown_picks(app):
    draft = {
        "picks": [
            [1, 14, "Plains", ["Plains", "Shock"], []],
            [1, 13, "Not A Card", ["Not A Card", "Shock"], []],
            [1, 12, "Shock", ["Shock", "Plains"], []],
        ]
    }

    rows, skipped = features.situations(app, [draft])

    assert rows == []
    assert skipped == {
        "took a basic land or an unknown card": 2,
        "one card to choose from": 1,
    }
