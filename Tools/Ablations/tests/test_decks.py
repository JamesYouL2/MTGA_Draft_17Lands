from pathlib import Path
import sys

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[3])]
from decks import rescored
from src.advisor import deck_scorer as ds


def test_removing_mc_penalty_recomputes_before_zero_clamp():
    features = dict.fromkeys(ds.WEIGHTS, 0.0)
    features["card_quality"] = (10 - ds.BASE_SCORE) / ds.WEIGHTS["card_quality"]
    data = {"features": features, "stats": {"color_screw_t3": 20., "screw_t3": 0., "flood_t5": 0.}}
    assert rescored([["test", data]], "baseline")[0][1]["rating"] == 0
    assert rescored([["test", data]], "no-mc-color")[0][1]["rating"] == 10
    assert "rating" not in data
