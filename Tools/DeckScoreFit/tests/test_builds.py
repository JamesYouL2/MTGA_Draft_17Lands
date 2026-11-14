import gzip
import json
import os
from collections import Counter

import builds
import pytest
from features import App
from games import fold_of
from quality import ALL, training

DATASET = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "tests", "data",
    "MKM_PremierDraft_Data_2024_5_3.json",
)


def test_game_rate_counts_in_hand_and_not_drawn():
    # [in hand, won, in hand in every fold, not drawn, won]
    assert builds._game_rate({"A": [60, 30, 60, 40, 30]}) == 60.0
    assert builds._game_rate({}) is None


def counts_with(pair_rate):
    """A set of two strong cards in WU, weak in UB, and one no pair has."""
    def row(rate, games=1000):
        return [games, int(games * rate), games, 0, 0]

    return {
        ALL: {"A": row(0.60), "B": row(0.50), "C": row(0.55)},
        "WU": {"A": row(pair_rate), "B": row(pair_rate)},
        "UB": {"A": row(0.48), "C": [100, 50, 100, 0, 0]},
    }


def test_held_stats_use_the_gate_and_every_group():
    held = builds.Held(counts_with(0.6), 11.6)
    assert held.stats["A"][ALL]["gihwr"] == 60.0
    assert held.stats["A"]["WU"]["gihwr"] == 60.0
    assert "UB" not in held.stats["C"]  # 100 games in hand: under the gate
    assert held.get_metrics(ALL, "gihwr") == (held.mean, held.std)


def test_a_pair_with_the_sets_record_and_rating_has_no_shift():
    counts = {
        ALL: {"A": [1000, 550, 1000, 0, 0], "B": [1000, 550, 1000, 0, 0]},
        "WU": {"A": [1000, 550, 1000, 0, 0], "B": [1000, 550, 1000, 0, 0]},
    }
    held = builds.Held(counts, 11.6)
    assert held.shifts["overall"]["WU"] == pytest.approx(0.0)
    assert held.shifts["blend"]["WU"] == pytest.approx(0.0)


def test_shift_removes_the_pairs_rating_and_adds_its_record_at_the_scores_price():
    counts = {
        ALL: {"A": [1000, 500, 1000, 0, 0], "B": [1000, 500, 1000, 0, 0]},
        # Rated 60 in the pair against 50 overall, and it wins 60% of its games.
        "WU": {"A": [500, 300, 500, 0, 0], "B": [500, 300, 500, 0, 0]},
    }
    held = builds.Held(counts, 11.6)
    price = 11.6 / held.std
    baseline = (60.0 - 50.0) / price
    # The set's games-in-hand rating is 50, and so is the pair's cards' overall.
    assert held.shifts["overall"]["WU"] == pytest.approx(baseline)
    assert held.shifts["blend"]["WU"] == pytest.approx(50.0 - 57.0 + baseline)


@pytest.fixture(scope="module")
def setup():
    app = App(DATASET)
    cards = app.dataset.get_card_ratings().values()
    names = [c["name"].split(" // ")[0] for c in cards]
    # Every card rated in every pair, so scores depend on the ratings here. Each
    # pair's rates are different, so it has its own level.
    pairs = ["WU", "UB", "BR", "RG", "WG", "WB", "UR", "BG", "WR", "UG"]
    counts = {ALL: {}}
    for i, name in enumerate(names):
        wins = 500 + (i * 37) % 200
        counts[ALL][name] = [1000, wins, 1000, 100, 50]
        for k, pair in enumerate(pairs):
            counts.setdefault(pair, {})[name] = [1000, wins + 15 * k, 1000, 100, 50]
    engine = builds.Engine()
    yield app, engine, builds.Held(counts, 11.6), names
    engine.close()


def a_deck(names, n=45):
    return {"cards": {name: 1 for name in names[:23]},
            "sideboard": {name: 1 for name in names[23:n]},
            "id": "a:0", "main_colors": "WU", "splash_colors": "", "skill": "0.56",
            "experience": "50", "wins": 3, "games": 5}


def test_pool_has_deck_and_sideboard_a_dict_per_copy_and_no_basics(setup):
    app, _, held, names = setup
    d = {"cards": {names[0]: 2, "Plains": 8}, "sideboard": {names[0]: 1, names[1]: 1}}
    pool = builds.pool_of(app, held, d)
    assert len(pool) == 4
    assert all("count" not in c for c in pool)
    assert len({id(c) for c in pool}) == 4
    assert pool[0]["deck_colors"] == held.stats[names[0]]


def test_pool_with_an_unknown_card_is_none(setup):
    app, _, held, _ = setup
    assert builds.pool_of(app, held, {"cards": {"Not a Card": 1}, "sideboard": {}}) is None


def test_a_version_changes_only_the_score_not_the_builds(setup):
    app, engine, held, names = setup
    pool = builds.pool_of(app, held, a_deck(names))
    engine.new_pool()
    weights = dict(engine.scorer.WEIGHTS)
    app = engine.run(pool, held, {})
    built = len(engine.memo)
    other = engine.run(pool, held, {"weights": {"two_colors": 30.0}})
    # The second version builds nothing new, and scores the same builds otherwise.
    assert len(engine.memo) == built
    assert set(app["pairs"]) == set(other["pairs"])
    assert app["pairs"] != other["pairs"]
    # The app's weights are back afterwards.
    assert engine.scorer.WEIGHTS == weights
    assert engine.scorer.get_card_rating is engine.original_rating
    assert engine.builder.get_card_rating is engine.original_rating


def test_remembered_builds_match_fresh_ones(setup):
    app, engine, held, names = setup
    pool = builds.pool_of(app, held, a_deck(names))
    engine.new_pool()
    first = engine.run(pool, held, {"rating": "blend"})
    second = engine.run(pool, held, {"rating": "blend"})
    engine.new_pool()
    fresh = engine.run(pool, held, {"rating": "blend"})
    assert first == second == fresh


def test_overall_rating_ignores_the_pair(setup):
    _, engine, _, _ = setup
    card = {"deck_colors": {ALL: {"gihwr": 55.0}, "WU": {"gihwr": 60.0}}}
    assert engine.overall_rating(card, ["WU"]) == 55.0


def test_overall_rating_without_an_overall_rate_falls_back(setup):
    _, engine, _, _ = setup
    assert engine.overall_rating({"deck_colors": {"WU": {"gihwr": 60.0}}}, ["WU"]) == 60.0


def test_a_shifted_rating_moves_rated_cards_only(setup):
    _, engine, _, _ = setup

    class Metrics(builds.Held):
        def __init__(self):
            self.shifts = {"overall": {"WU": 2.0}, "blend": {}}
            self.mean, self.std = 50.0, 4.0

    rate = engine.rating_of("overall+pair")
    card = {"deck_colors": {ALL: {"gihwr": 55.0}}}
    assert rate(card, ["WU"], Metrics()) == 57.0
    assert rate(card, [ALL], Metrics()) == 55.0
    assert rate({"deck_colors": {}}, ["WU"], Metrics()) == 0.0


def test_pool_row_reports_why_a_pool_is_left_out(setup):
    app, engine, held, names = setup
    helds = [held] * 5
    versions = {"blend": {}}
    assert builds.pool_row(app, engine, helds, a_deck(names, n=30), versions) == (
        "pool under 35 cards"
    )
    d = dict(a_deck(names), sideboard={"Not a Card": 1})
    assert builds.pool_row(app, engine, helds, d, versions) == "card not in dataset"


def test_pool_row_has_the_decks_results_and_each_versions_suggestion(setup):
    app, engine, held, names = setup
    row = builds.pool_row(app, engine, [held] * 5, a_deck(names), engine.versions())
    assert (row["id"], row["main"], row["wins"], row["games"]) == ("a:0", "WU", 3, 5)
    assert set(row["versions"]) == {"app"} | set(builds.VARIANT_VERSIONS)
    for shown in row["versions"].values():
        assert len(shown["pair"]) <= 2
        assert shown["shown"]
        # The top can be a promoted deck, which isn't the highest score.
        assert shown["score"] <= max(shown["pairs"].values())


def test_each_pool_is_rated_from_the_other_folds(setup):
    app, engine, _, names = setup
    folds = [
        {ALL: {names[0]: [1000, 100 * (i + 1), 0, 0]}} for i in range(5)
    ]
    helds = [builds.Held(training(folds, {i}), 11.6) for i in range(5)]
    d = a_deck(names)
    pool = builds.pool_of(app, helds[fold_of(d["id"])], d)
    held_out = next(c for c in pool if c["name"].split(" // ")[0] == names[0])
    # Fold f's 100 * (f + 1) wins of 1000 are left out of the 4000 other games.
    expected = 100.0 * (1500 - 100 * (fold_of(d["id"]) + 1)) / 4000
    assert held_out["deck_colors"][ALL]["gihwr"] == pytest.approx(expected)


def test_no_tempo_stops_the_tempo_builds(setup):
    app, engine, held, names = setup
    pool = builds.pool_of(app, held, a_deck(names))
    engine.new_pool()
    full = engine.run(pool, held, {})
    without = engine.run(pool, held, {"tempo": False})
    assert not any("Tempo" in k for k in [without["kind"]])
    assert len(without["shown"]) <= len(full["shown"])
    # A later version gets them back.
    assert engine.run(pool, held, {}) == full


def test_no_promotion_keeps_the_scores_order(setup):
    app, engine, held, names = setup
    pool = builds.pool_of(app, held, a_deck(names))
    engine.new_pool()
    # A gap this wide promotes the safe deck over anything.
    engine.promote_gaps = (1000.0, 1000.0)
    promoted = engine.run(pool, held, {})
    plain = engine.run(pool, held, {"promote": False})
    engine.promote_gaps = (6.0, 20.0)
    assert len(promoted["identity"]) <= 2
    assert plain["score"] == max(plain["pairs"].values())
    assert plain["score"] > promoted["score"]
    assert plain["pairs"] == promoted["pairs"]


def test_simulator_only_runs_in_sim_versions_and_once_per_deck(setup):
    app, engine, held, names = setup
    pool = builds.pool_of(app, held, a_deck(names))
    calls = []

    def fake(deck, iterations):
        calls.append(builds.signature(deck))
        return {"color_screw_t3": 30.0, "screw_t3": 0.0, "flood_t5": 0.0}

    saved, engine.saved["simulate_deck"] = engine.saved["simulate_deck"], fake
    try:
        engine.new_pool()
        off = engine.run(pool, held, {})
        assert calls == []
        on = engine.run(pool, held, {"sim": True})
        assert calls and len(calls) == len(set(calls))
        made = len(calls)
        engine.run(pool, held, {"sim": True, "promote": False})
        assert len(calls) == made
        # The app at this base no longer charges for the simulator's rates.
        assert on["pairs"] == off["pairs"]
    finally:
        engine.saved["simulate_deck"] = saved


def test_nearer_tempo_runs_from_consistent_to_tempo():
    c = Counter({"A": 1, "B": 1, "C": 1})
    t = Counter({"A": 1, "D": 1, "E": 1})
    assert builds.nearer_tempo(c, c, t) == -1.0
    assert builds.nearer_tempo(t, c, t) == 1.0
    assert builds.nearer_tempo(Counter({"A": 1, "B": 1, "D": 1}), c, t) == 0.0
    assert builds.nearer_tempo(Counter({"Z": 1}), c, t) == 0.0
    assert builds.nearer_tempo(c, c, c) is None


def test_played_deck_is_for_two_color_decks_with_held_out_ratings(setup):
    app, engine, held, names = setup
    d = a_deck(names)
    pool = builds.pool_of(app, held, d)
    engine.new_pool()
    played = builds.played_deck(app, engine, held, pool, d)
    assert isinstance(played["quality"], float)
    assert played["quality"] != 0.0
    assert builds.played_deck(app, engine, held, pool, dict(d, main_colors="WUB")) is None


def test_main_marks_the_first_pools_for_the_simulator(tmp_path, setup):
    _, engine, _, names = setup
    engine.close()
    decks = tmp_path / "decks.json.gz"
    games = tmp_path / "games.json.gz"
    out = tmp_path / "out.json.gz"
    with gzip.open(decks, "wt", encoding="utf-8") as f:
        json.dump([a_deck(names), dict(a_deck(names), id="b:0")], f)
    counts = {ALL: {n: [1000, 550, 0, 0] for n in names}}
    with gzip.open(games, "wt", encoding="utf-8") as f:
        json.dump({"folds": [counts] * 5}, f)
    builds.main(["--src", ".", "--decks", str(decks), "--games", str(games), "--sim-pools", "1",
                 "--dataset", DATASET, "--set", "MKM", "--out", str(out), "--workers", "1"])
    with gzip.open(out, "rt", encoding="utf-8") as f:
        rows = {r["id"]: r for r in json.load(f)["rows"]}
    assert "sim" in rows["a:0"]["versions"] and "sim-no-tempo" in rows["a:0"]["versions"]
    assert "sim" not in rows["b:0"]["versions"]


def test_main_writes_rows_and_skips(tmp_path, setup):
    _, engine, _, names = setup
    engine.close()  # The workers patch their own.
    decks = tmp_path / "decks.json.gz"
    games = tmp_path / "games.json.gz"
    out = tmp_path / "results" / "out.json.gz"
    with gzip.open(decks, "wt", encoding="utf-8") as f:
        json.dump([a_deck(names), dict(a_deck(names, n=30), id="b:0")], f)
    counts = {ALL: {n: [1000, 550, 0, 0] for n in names}}
    with gzip.open(games, "wt", encoding="utf-8") as f:
        json.dump({"folds": [counts] * 5}, f)
    builds.main(["--src", ".", "--decks", str(decks), "--games", str(games),
                 "--dataset", DATASET, "--set", "MKM", "--out", str(out), "--workers", "1"])
    with gzip.open(out, "rt", encoding="utf-8") as f:
        data = json.load(f)
    assert data["set"] == "MKM"
    assert [r["id"] for r in data["rows"]] == ["a:0"]
    assert data["skipped"] == {"pool under 35 cards": 1}
