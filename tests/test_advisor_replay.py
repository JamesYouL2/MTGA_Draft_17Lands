import csv
import gzip
import importlib.util
import json
import os

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
