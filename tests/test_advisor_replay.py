import csv
import gzip
import importlib.util
import json
import os

import numpy as np
import pytest

from src.card_utils import stack_cards

_PATH = os.path.join(
    os.path.dirname(__file__), "..", "Tools", "AdvisorReplay", "advisor_replay.py"
)
_spec = importlib.util.spec_from_file_location("advisor_replay", _PATH)
ar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ar)

# Twelve cards; GIH WR falls with the index, so "Card 0" is the best.
NAMES = [f"Card {i}" for i in range(11)] + ["Dawn // Dusk"]
COLORS = ["W", "U", "B", "R", "G"]


def _card(i, name):
    stats = {
        "gihwr": 65.0 - i,
        "ohwr": 60.0,
        "gpwr": 55.0,
        "alsa": 2.0 + i,
        "ata": 1.5 + i,
        "iwd": 3.0,
        "samples": 5000,
    }
    color = COLORS[i % 5]
    return {
        "name": name,
        "cmc": 2,
        "mana_cost": "{1}{" + color + "}",
        "types": ["Creature"],
        "rarity": "common",
        "colors": [color],
        "deck_colors": {"All Decks": stats, color: dict(stats)},
    }


@pytest.fixture
def dataset(tmp_path):
    data = {
        "meta": {"version": 2, "start_date": "2026-01-01", "end_date": "2026-02-01"},
        "color_ratings": {},
        "card_ratings": {str(1000 + i): _card(i, n) for i, n in enumerate(NAMES)},
    }
    path = tmp_path / "TST_PremierDraft_All_Data.json.gz"
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(data, f)
    return ar.load_dataset(str(path))


def _dump_names():
    # Dumps name double-faced cards by their front face.
    return [n.split(" // ")[0] for n in NAMES]


def _write_dump(path, drafts):
    """drafts: list of (draft_id, win_rate, games, [(pack, pick, taken, pack_names)])."""
    names = _dump_names()
    header = [
        "expansion",
        "event_type",
        "draft_id",
        "draft_time",
        "rank",
        "event_match_wins",
        "event_match_losses",
        "pack_number",
        "pick_number",
        "pick",
        "pick_2",
        "user_n_games_bucket",
        "user_game_win_rate_bucket",
    ]
    header += [f"pack_card_{n}" for n in names] + [f"pool_{n}" for n in names]
    with gzip.open(path, "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for draft_id, wr, games, picks in drafts:
            pool = []
            for pack, pick, taken, pack_names in picks:
                row = [
                    "TST",
                    "PremierDraft",
                    draft_id,
                    "",
                    "gold",
                    3,
                    3,
                    pack,
                    pick,
                    taken,
                    "",
                ]
                row += [games, wr]
                row += [pack_names.count(n) for n in names]
                row += [pool.count(n) for n in names]
                w.writerow(row)
                pool.append(taken)
    return str(path)


def _best_first_draft(draft_id, wr=0.5, games=10):
    """Three 3-card packs, and the drafter always takes the best card."""
    picks = []
    for pack in range(3):
        cards = [_dump_names()[pack * 3 + k] for k in range(3)]
        for pick in range(3):
            picks.append((pack, pick, cards[0], list(cards)))
            cards = cards[1:]
    return (draft_id, wr, games, picks)


def test_sample_drafts_keeps_whole_drafts_and_is_deterministic(tmp_path):
    ids = [f"d{i:02d}" for i in range(12)]
    dump = _write_dump(tmp_path / "dump.csv.gz", [_best_first_draft(i) for i in ids])

    first = ar.sample_drafts(dump, 5)
    assert len(first) == 5
    assert set(first) == set(ar.sample_drafts(dump, 5))
    assert all(len(d["picks"]) == 9 for d in first.values())
    pack, pick, taken, pack_names, pool = next(iter(first.values()))["picks"][1]
    assert (pack, pick, taken, pool) == (0, 1, "Card 1", ["Card 0"])
    assert sorted(pack_names) == ["Card 1", "Card 2"]


def test_sample_drafts_shards_partition_the_dump(tmp_path):
    ids = [f"d{i:02d}" for i in range(12)]
    dump = _write_dump(tmp_path / "dump.csv.gz", [_best_first_draft(i) for i in ids])

    shards = [set(ar.sample_drafts(dump, 100, s, 3)) for s in range(3)]
    assert set().union(*shards) == set(ids)
    assert sum(len(s) for s in shards) == len(ids)


def test_sample_drafts_marks_strong_drafters(tmp_path):
    dump = _write_dump(
        tmp_path / "dump.csv.gz",
        [
            _best_first_draft("strong", wr=0.62, games=50),
            _best_first_draft("few_games", wr=0.7, games=10),
            _best_first_draft("weak", wr=0.5, games=100),
        ],
    )
    drafts = ar.sample_drafts(dump, 10)
    assert {k: d["strong"] for k, d in drafts.items()} == {
        "strong": True,
        "few_games": False,
        "weak": False,
    }
    strong = drafts["strong"]
    assert (strong["wins"], strong["losses"]) == (3, 3)
    assert (strong["skill"], strong["games"]) == (0.62, 50)


def test_replay_scores_every_contested_pick(tmp_path, dataset):
    dump = _write_dump(
        tmp_path / "dump.csv.gz",
        [_best_first_draft("a", wr=0.65, games=100), _best_first_draft("b")],
    )
    result = ar.replay(ar.sample_drafts(dump, 10), dataset, ["baseline"])

    # Each pack's last pick has one card left, so 2 picks per pack count.
    assert result["skipped"] == {"fewer than 2 distinct cards": 6}
    assert result["unmatched_names"] == {}
    tally = result["tally"]
    assert tally["gihwr|all|all"] == {"n": 12, "top1": 12, "top3": 12, "rank": 0}
    assert tally["gihwr|strong|all"]["n"] == 6
    assert tally["gihwr|all|pack 3"]["n"] == 4
    assert tally["baseline|all|all"]["n"] == 12
    # ATA follows GIH WR in the fixture, so it agrees too.
    assert tally["ata|all|all"]["top1"] == 12


def test_replay_resolves_front_face_names(tmp_path, dataset):
    picks = [
        (0, 0, "Dawn", ["Dawn", "Card 10"]),
        (0, 1, "Card 9", ["Card 10", "Card 9"]),
    ]
    dump = _write_dump(tmp_path / "dump.csv.gz", [("dfc", 0.5, 10, picks)])
    result = ar.replay(ar.sample_drafts(dump, 10), dataset, ["baseline"])

    assert result["unmatched_names"] == {}
    # Dawn // Dusk is the worst card by GIH WR, so the baseline ranks it last.
    assert result["tally"]["gihwr|all|all"] == {"n": 2, "top1": 1, "top3": 2, "rank": 1}


def test_fast_stack_cards_matches_stack_cards():
    cards = [_card(0, "A"), _card(1, "B"), _card(0, "A")]
    assert ar._fast_stack_cards(cards) == stack_cards(cards)
    assert ar._fast_stack_cards(cards)[0]["count"] == 2


def test_arch_overall_pick_uses_pool_size(dataset):
    from src.advisor.engine import DraftAdvisor
    from src.set_metrics import SetMetrics

    seen = []
    original = DraftAdvisor._calculate_weighted_score

    def spy(self, card, pick_number):
        seen.append(pick_number)
        return original(self, card, pick_number)

    pool = dataset.get_data_by_name(["Card 0"] * 16)
    pack = dataset.get_data_by_name(["Card 1", "Card 2"])
    DraftAdvisor._calculate_weighted_score = spy
    try:
        with ar.VARIANTS["arch-overall-pick"](dataset):
            DraftAdvisor(SetMetrics(dataset), pool).evaluate_pack(
                pack, 3, current_pack=2
            )
    finally:
        DraftAdvisor._calculate_weighted_score = original
    assert set(seen) == {17}


def test_pick_lane_prefers_popular_archetype_the_pool_supports():
    shares = {"URG": 0.18, "UBG": 0.15, "UG": 0.04, "WU": 0.10}
    counts = {"U": 8, "G": 7, "R": 5, "B": 1, "W": 0}
    lane, options = ar.pick_lane(["U", "G", "R"], counts, shares)
    assert lane == "URG"
    assert options == ["URG", "UG", "UBG"]

    # With no third color in the pool, the pair beats both clans.
    counts = {"U": 8, "G": 7, "R": 0, "B": 0, "W": 0}
    assert ar.pick_lane(["U", "G"], counts, shares)[0] == "UG"
    assert ar.pick_lane(["U"], counts, shares) == (None, [])


def test_archetype_shares_ignores_rare_combos(dataset):
    cards = dataset.get_card_ratings()
    for i, card in enumerate(cards.values()):
        card["deck_colors"]["All Decks"]["samples"] = 1000
        card["deck_colors"]["URG"] = {"samples": 300}
        card["deck_colors"]["WB"] = {"samples": 10}
    assert ar.archetype_shares(dataset) == {"URG": 0.3}


def test_arch_lane_treats_clan_cards_as_castable(dataset):
    from src.advisor.engine import DraftAdvisor
    from src.set_metrics import SetMetrics

    for card in dataset.get_card_ratings().values():
        card["deck_colors"]["All Decks"]["samples"] = 1000
        card["deck_colors"]["URG"] = dict(card["deck_colors"]["All Decks"])
    pool = dataset.get_data_by_name(["Card 1", "Card 6", "Card 4"] * 6)  # U, U, G
    clan = dataset.get_data_by_name(["Card 3"])[0]  # R
    metrics = SetMetrics(dataset)

    # Baseline: R is outside the U/G lane, so it is penalized.
    assert DraftAdvisor(metrics, pool)._calculate_castability_v5(clan, 3, 5, 0.0)[0] < 1
    # URG is the only frequent archetype containing U and G, so it is the lane.
    with ar.VARIANTS["arch-lane"](dataset):
        advisor = DraftAdvisor(metrics, pool)
        assert advisor.lane == "URG"
        assert advisor.main_archetype == "URG"
        assert advisor._calculate_castability_v5(clan, 3, 5, 0.0) == (1.0, "")


class _Rec:
    def __init__(self, name, score):
        self.card_name, self.contextual_score = name, score


def test_blend_order_moves_from_advisor_to_ata(dataset):
    # The advisor likes Card 5 best; ATA prefers Card 0 (lower ATA).
    pack = dataset.get_data_by_name(["Card 0", "Card 5", "Card 9"])
    recs = [_Rec("Card 5", 80.0), _Rec("Card 0", 60.0), _Rec("Card 9", 10.0)]
    assert ar.blend_order(recs, pack, 0.0) == ["Card 5", "Card 0", "Card 9"]
    assert ar.blend_order(recs, pack, 1.0) == ["Card 0", "Card 5", "Card 9"]


def test_replay_scores_blends_per_variant(tmp_path, dataset):
    dump = _write_dump(tmp_path / "dump.csv.gz", [_best_first_draft("a")])
    result = ar.replay(
        ar.sample_drafts(dump, 10),
        dataset,
        ["baseline"],
        blends=["ata50", "ata-first4"],
    )
    tally = result["tally"]
    assert tally["baseline+ata50|all|all"]["n"] == 6
    # ATA follows the drafter's picks in the fixture, so ATA-first agrees.
    assert tally["baseline+ata-first4|all|all"]["top1"] == 6
    table = ar.format_table(result)
    assert table.index("| baseline |") < table.index("| baseline+ata50 |")
    assert table.index("| baseline+ata-first4 |") < table.index("| gihwr |")


def test_summarize_merges_results(tmp_path, dataset, capsys):
    paths = []
    for i in range(2):
        dump = _write_dump(tmp_path / f"d{i}.csv.gz", [_best_first_draft(f"x{i}")])
        result = ar.replay(ar.sample_drafts(dump, 10), dataset, ["baseline"])
        result["dump"] = "draft_data_public.TST.PremierDraft.csv.gz"
        path = tmp_path / f"r{i}.json"
        path.write_text(json.dumps(result))
        paths.append(str(path))

    ar.main(["summarize", *paths])
    out = capsys.readouterr().out
    assert "TST: 2 drafts" in out
    assert "| gihwr | 100.0 / 100.0 / 0.00 |" in out
    assert "12 picks scored." in out


def test_regret_is_distance_below_the_favourite_in_pack_sds():
    scores = {"A": 3.0, "B": 2.0, "C": 1.0}
    assert ar.regret(scores, "A") == 0
    # Population SD of 3, 2, 1 is sqrt(2/3).
    assert ar.regret(scores, "C") == pytest.approx(2 / (2 / 3) ** 0.5)
    assert ar.regret({"A": 1.0, "B": 1.0}, "B") == 0


def test_replay_records_each_drafts_agreement_and_result(tmp_path, dataset):
    dump = _write_dump(
        tmp_path / "dump.csv.gz",
        [_best_first_draft("a", wr=0.62, games=50), _best_first_draft("b")],
    )
    result = ar.replay(
        ar.sample_drafts(dump, 10), dataset, ["baseline"], blends=["ata50"]
    )
    assert len(result["outcomes"]) == 2
    a = next(o for o in result["outcomes"] if o["skill"] == 0.62)
    assert (a["wins"], a["losses"], a["games"], a["strong"]) == (3, 3, 50, True)
    assert set(a["methods"]) == {"baseline", "baseline+ata50", "gihwr", "ata"}
    # The drafter always takes the best card, which GIH WR and ATA both favour.
    assert a["methods"]["gihwr"] == [6, 6, 0.0]
    assert a["methods"]["ata"] == [6, 6, 0.0]
    # Nine-card pools are too small to build a deck from.
    assert (a["deck_score"], a["pool_gihwr"]) == (None, None)


def _outcomes(n, effect):
    """Complete events whose wins fall by effect per unit of baseline regret."""
    out = []
    for i in range(n):
        skill = 0.46 + 0.04 * (i % 4)
        regret = (i * 7 % 11) / 10
        wins = round(2 + 10 * (skill - 0.46) + effect * regret + (i % 3 - 1) * 0.5)
        wins = min(7, max(0, wins))
        out.append(
            {
                "wins": wins,
                "losses": 3 if wins < 7 else 1,
                "skill": skill,
                "games": 50,
                "set": "TST",
                "methods": {
                    "baseline": [10, 5, 10 * regret],
                    "ata": [10, 4, 5.0],
                    "gihwr": [10, 4, 1.0 + i % 5],
                },
            }
        )
    return out


def test_wins_regression_recovers_a_planted_effect():
    outcomes = _outcomes(200, -2.0)
    regret = [o["methods"]["baseline"][2] / 10 for o in outcomes]
    coef, se = ar.wins_regression(outcomes, regret)
    assert coef == pytest.approx(-2.0, abs=0.3)
    assert 0 < se < 0.5


def test_format_outcomes_needs_enough_complete_events():
    table = ar.format_outcomes({"outcomes": _outcomes(40, -2.0)}, ["TST"])
    assert "TST: 40 complete events" in table
    assert table.index("| baseline |") < table.index("| gihwr |")
    # ATA regret is the same for every drafter, so it explains nothing.
    assert "| ata | – | – | – | – |" in table
    # Unfinished events are dropped, leaving too few to report.
    unfinished = _outcomes(40, -2.0)
    for o in unfinished[:20]:
        o["wins"], o["losses"] = 2, 1
    assert ar.format_outcomes({"outcomes": unfinished}) == ""


def test_pool_strength_scores_full_pools(dataset):
    from src.set_metrics import SetMetrics

    metrics = SetMetrics(dataset)
    assert ar.pool_strength(dataset.get_data_by_name(["Card 0"] * 22), metrics) == (
        None,
        None,
    )
    # 12 W cards at 65 and 12 U cards at 64; the best 23 in W/U.
    pool = dataset.get_data_by_name(["Card 0"] * 12 + ["Card 1"] * 12)
    deck_score, pool_gihwr = ar.pool_strength(pool, metrics)
    assert deck_score > 0
    assert pool_gihwr == pytest.approx((12 * 65 + 11 * 64) / 23)


def test_bootstrap_differences_compare_methods_on_the_same_drafts():
    outcomes = _outcomes(200, -2.0)
    xs = {
        m: np.array([o["methods"][m][2] for o in outcomes])
        for m in ("baseline", "gihwr")
    }
    se = ar.bootstrap_differences(outcomes, xs, "baseline", samples=50)
    assert se["baseline"] == 0
    assert 0 < se["gihwr"] < 1


def test_format_calibration_bins_pools_by_deck_score():
    outcomes = _outcomes(60, 0.0)
    for i, o in enumerate(outcomes):
        o["deck_score"] = 50.0 + o["wins"] + (i % 2)
        o["pool_gihwr"] = 55.0 + (i % 5)
    table = ar.format_calibration({"outcomes": outcomes}, ["TST"])
    assert "TST: 60 complete events" in table
    assert "| 10 |" in table
    assert "| advisor deck score |" in table
    # Wins rise with deck score by construction.
    first = next(line for line in table.splitlines() if line.startswith("| 1 |"))
    last = next(line for line in table.splitlines() if line.startswith("| 10 |"))
    assert float(first.split("|")[5]) < float(last.split("|")[5])

    for o in outcomes:
        o["deck_score"] = None
    assert ar.format_calibration({"outcomes": outcomes}) == ""


def test_sample_drafts_final_only_keeps_just_the_final_pool(tmp_path):
    dump = _write_dump(
        tmp_path / "dump.csv.gz",
        [_best_first_draft("a", wr=0.62, games=50), _best_first_draft("b")],
    )
    full = ar.sample_drafts(dump, 10)
    final = ar.sample_drafts(dump, 10, final_only=True)
    assert set(final) == set(full)
    for draft_id, draft in final.items():
        _, _, taken, _, pool = full[draft_id]["picks"][-1]
        assert draft["picks"] == []
        assert sorted(draft["final"]) == sorted(pool + [taken])
    assert final["a"]["strong"] and final["a"]["skill"] == 0.62


def _long_draft(draft_id, taken):
    """A draft whose picks are taken, each from a two-card pack."""
    return (
        draft_id,
        0.5,
        10,
        [(i // 12, i % 12, name, [name, "Card 10"]) for i, name in enumerate(taken)],
    )


def test_score_pools_splits_each_final_pools_deck_score(tmp_path, dataset):
    dump = _write_dump(
        tmp_path / "dump.csv.gz",
        [
            _long_draft("full", ["Card 0"] * 12 + ["Card 1"] * 12),
            _long_draft("short", ["Card 0"] * 9),
        ],
    )
    result = ar.score_pools(ar.sample_drafts(dump, 10, final_only=True), dataset)
    assert result["tally"] == {} and result["unmatched_names"] == {}
    full, short = sorted(result["outcomes"], key=lambda o: o["deck_score"] is None)
    assert short["deck_score"] is None and short["wins"] == 3
    parts = full["power"] + sum(full[k] for k in ar.DECK_PARTS)
    assert full["deck_score"] == pytest.approx(max(0.0, parts), abs=1e-3)
    assert full["colors"] == 2
    assert 64.0 <= full["deck_gihwr"] <= 65.0
    assert full["pool_gihwr"] == pytest.approx((12 * 65 + 11 * 64) / 23)


def _pool_outcomes(n, sets=("AAA", "BBB", "CCC")):
    """Complete events whose wins rise with power; the curve penalty is noise."""
    out = []
    for i in range(n):
        power = 70.0 + (i * 7 % 13)
        curve = -3.0 * (i % 4 == 0)
        wins = min(7, max(0, round((power - 70.0) / 2 + (i % 3 - 1))))
        out.append(
            {
                "wins": wins,
                "losses": 3 if wins < 7 else 1,
                "skill": 0.5,
                "games": 50,
                "set": sets[i % len(sets)],
                "deck_score": power + curve,
                "power": power,
                "deck_gihwr": 55.0 + (i % 5),
                "pool_gihwr": 54.0 + power / 100,
            }
            | {k: 0.0 for k in ar.DECK_PARTS}
            | {"curve": curve}
        )
    return out


def test_format_deck_parts_weighs_each_piece_against_power():
    table = ar.format_deck_parts({"outcomes": _pool_outcomes(90)}, ["AAA"])
    assert "AAA: 90 complete events" in table
    power = next(r for r in table.splitlines() if r.startswith("| power"))
    assert float(power.split("|")[4].split()[0]) == pytest.approx(0.5, abs=0.05)
    assert "| curve / land penalty | 25.6% | -3.0 |" in table
    # Pieces that never apply have nothing to estimate.
    assert "tribal" not in table
    # Three sets, so each is held out in turn.
    assert "| held-out set |" in table
    assert "| BBB |" in table and "| all |" in table

    one_set = _pool_outcomes(90, sets=("AAA",))
    assert "| held-out set |" not in ar.format_deck_parts({"outcomes": one_set})
    assert ar.format_deck_parts({"outcomes": _pool_outcomes(20)}) == ""
