import random
from pathlib import Path
import sys
from unittest.mock import Mock

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[3])]
from variants import (ALL_VARIANTS, PICK_VARIANTS, DECK_VARIANTS, ENGINE, ROOT,
                      advisor_class, traced_class, variant_source, scores_from_trace)


def test_every_ablation_is_a_compilable_one_file_edit():
    for variant in ALL_VARIANTS:
        path, source = variant_source(variant)
        assert source != (ROOT / path).read_text()
        compile(source, path, "exec")


def test_fast_path_matches_each_independently_edited_engine():
    source = (ROOT / ENGINE).read_text()
    Trace = traced_class(source)
    classes = {v: advisor_class(variant_source(v, source)[1]) for v in PICK_VARIANTS}
    m = Mock()
    m.get_metrics.return_value = (55., 4.)
    rng = random.Random(271828)
    tags = ["removal", "fixing_ramp", "synergy_artifacts", "synergy_graveyard", "synergy_counters", ""]
    for trial in range(120):
        pack = []
        for i in range(7):
            colors = rng.choice([["G"], ["R"], ["U"], ["W", "B"], ["G", "U"], []])
            cost = "{2}{G/U}" if colors == ["G", "U"] else "{2}" + "".join("{"+c+"}" for c in colors)
            pack.append({"name": f"Card {i}", "types": [rng.choice(["Land", "Creature", "Instant"])],
                         "cmc": rng.randint(1, 7), "mana_cost": cost, "colors": colors,
                         "tags": [rng.choice(tags)], "deck_colors": {
                             "All Decks": {"gihwr": rng.uniform(45, 70), "iwd": rng.uniform(0, 8)},
                             "RG": {"gihwr": rng.uniform(30, 75), "samples": rng.randint(10, 2000)}}})
        pool = [pack[0]] * rng.randint(2, 40)
        a = Trace(m, pool)
        a.main_colors = ["R", "G"]
        a.main_archetype = "RG"
        for k, value in a.pool_metrics.items():
            a.pool_metrics[k] = {"U", "B"} if isinstance(value, set) else rng.randint(0, 12)
        a._trace = []
        a._pick = rng.randint(1, 14)
        pack_no = rng.randint(1, 3)
        a.evaluate_pack(pack, a._pick, pack_no)
        for v, cls in classes.items():
            other = object.__new__(cls)
            other.__dict__.update(a.__dict__)
            recs = other.evaluate_pack(pack, a._pick, pack_no)
            expected = {r.card_name: r.contextual_score for r in recs}
            assert scores_from_trace(a, v, cls, pack_no) == expected, (trial, v)
