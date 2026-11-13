import gzip
import json

import deck_variants as dv
import pytest


def shown(pair="WU", identity="WU", decks=("a", "b", "c"), kind="Consistent"):
    return {"pair": pair, "identity": identity, "kind": kind, "shown": list(decks),
            "score": 80.0, "pairs": {pair: 80.0}}


def row(i, main="WU", splash="", wins=5, games=10, quality=0.5, nearer=0.0, versions=None):
    base = {v: shown() for v in ("blend", "no-tempo", "no-promotion", "neither")}
    return {"main": main, "splash": splash, "skill": str(i % 3), "experience": str(i % 2),
            "wins": wins, "games": games,
            "played": {"quality": quality, "nearer": nearer} if nearer is not None else None,
            "versions": base | (versions or {})}


def table(tmp_path, by_set):
    paths = []
    for name, rows in by_set.items():
        path = tmp_path / f"{name}.json.gz"
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump({"set": name, "skipped": {"small": 1}, "rows": rows}, f)
        paths.append(str(path))
    return dv.Table(paths)


def test_rates_count_top_top_two_and_list(tmp_path):
    rows = [
        row(0, versions={"no-tempo": shown(decks=("x", "b", "c"))}),
        row(1, versions={"no-tempo": shown(decks=("a", "x", "c"))}),
        row(2, versions={"no-tempo": shown(decks=("a", "b", "x"))}),
        row(3, versions={"no-tempo": shown(decks=("b", "a", "c"))}),
    ]
    r = dv.rates(table(tmp_path, {"A": rows}))["no-tempo"]
    assert r["pools"] == 4
    assert r["top"] == 25.0 + 25.0  # the first and the reordered one
    assert r["second"] == 75.0
    assert r["shown"] == 75.0


def test_simulator_rates_are_over_the_pools_that_ran_it(tmp_path):
    sim = {"sim": shown(), "sim-no-tempo": shown(decks=("x", "b", "c")),
           "sim-no-promotion": shown(), "sim-neither": shown()}
    rows = [row(0, versions=sim), row(1)]
    r = dv.rates(table(tmp_path, {"A": rows}))
    assert r["sim-no-tempo"]["pools"] == 1
    assert r["sim-no-tempo"]["top"] == 100.0
    assert r["no-tempo"]["pools"] == 2


def simulated(**top):
    """The versions a simulated pool adds, with this as today's app."""
    return {"sim": shown(**top), "sim-no-tempo": shown(), "sim-no-promotion": shown(),
            "sim-neither": shown()}


def test_first_builds_groups_splashes_and_counts_only_pools_run(tmp_path):
    rows = [
        row(0, versions={"blend": shown(kind="Splash W"), **simulated(kind="Safe Tempo")}),
        row(1, versions={"blend": shown(kind="Splash R")}),
        row(2, versions={"blend": shown(kind="Safe Core")}),
        row(3, versions={"blend": shown(kind="Safe Core")}),
    ]
    first = dv.first_builds(table(tmp_path, {"A": rows}))
    assert first["blend"] == {"Splash": 50.0, "Safe Core": 50.0}
    assert first["sim"] == {"Safe Tempo": 100.0}


def test_penalties_count_only_pools_run_both_ways(tmp_path):
    rows = [
        row(0, versions=simulated(pair="UB", decks=("x", "b", "c"))),
        row(1, versions=simulated(decks=("x", "b", "c"))),
        row(2, versions=simulated()),
        row(3),
    ]
    t = table(tmp_path, {"A": rows})
    assert t.penalties == {"pools": 3, "top": 2, "pair": 1}


def decks_by_nearer(won_near, won_far, n=300):
    rows = []
    for i in range(n):
        rows.append(row(i, nearer=1.0, quality=0.5 + (i % 5) / 10, wins=won_near - i % 2))
        rows.append(row(i, nearer=-1.0, quality=0.5 + (i % 5) / 10, wins=won_far - i % 2))
    return rows


def test_tempo_outcome_is_a_full_move_toward_tempos_cards(tmp_path):
    t = table(tmp_path, {"A": decks_by_nearer(7, 4), "B": decks_by_nearer(6, 4)})
    r = dv.tempo_outcome(t)
    assert r["decks"] == 1200
    # Half of the 25-point gap, since -1 to +1 is two units.
    assert r["effect"] == pytest.approx(12.5, abs=3.0)
    assert dv.tempo_outcome(t, control_quality=False)["effect"] == pytest.approx(
        r["effect"], abs=1.0
    )


def test_tempo_outcome_needs_decks(tmp_path):
    t = table(tmp_path, {"A": [row(0), row(1, nearer=None)]})
    r = dv.tempo_outcome(t)
    assert r["effect"] is None and r["decks"] == 1


def promoted(i, main, splash, wins):
    """Safe is WU; left alone, the top is WUB."""
    return row(i, main=main, splash=splash, wins=wins, versions={
        "blend": shown(identity="WU", decks=("safe", "soup")),
        "no-promotion": shown(identity="WUB", decks=("soup", "safe")),
    })


def test_promotion_outcome_compares_safe_colors_with_the_tops(tmp_path):
    rows = []
    for i in range(200):
        rows.append(promoted(i, "WU", "", 6 - i % 2))
        rows.append(promoted(i, "WU", "B", 4 - i % 2))
    rows.append(promoted(0, "BR", "", 10))  # played neither
    t = table(tmp_path, {"A": rows, "B": rows})
    r = dv.promotion_outcome(t)
    assert (r["decks_safe"], r["decks_top"]) == (400, 400)
    assert r["pools"] == 802
    assert r["rate_safe"] > r["rate_top"]
    assert r["effect"] > 0


def test_promotion_outcome_ignores_pools_it_doesnt_move(tmp_path):
    t = table(tmp_path, {"A": [row(0), row(1)]})
    r = dv.promotion_outcome(t)
    assert r["pools"] == 0 and r["effect"] is None


def test_promotion_within_the_same_colors_isnt_compared(tmp_path):
    rows = [row(0, versions={
        "blend": shown(identity="WU", decks=("x", "y")),
        "no-promotion": shown(identity="WU", decks=("y", "x")),
    })]
    assert dv.promotion_outcome(table(tmp_path, {"A": rows}))["pools"] == 0


@pytest.mark.parametrize("top, value, se, expected", [
    (1.0, 0.1, 0.2, "remove"),      # rare and no case for it
    (1.0, 1.0, 0.2, "keep"),        # rare, but it wins
    (20.0, -1.0, 0.2, "remove"),    # common and it loses
    (20.0, 1.0, 0.2, "keep"),
    (20.0, 0.1, 0.2, "no verdict"),
    (1.0, None, None, "remove"),    # rare and no outcome to read
    (20.0, None, None, "no verdict"),
])
def test_verdict(top, value, se, expected):
    assert dv.verdict(top, {"effect": value, "se": se}) == expected


def test_report_runs(tmp_path, capsys):
    rows = decks_by_nearer(6, 5)
    for i in range(200):
        rows.append(promoted(i, "WU", "", 6 - i % 2))
        rows.append(promoted(i, "WU", "B", 5 - i % 2))
    results = dv.report(table(tmp_path, {"A": rows, "B": rows}))
    out = capsys.readouterr().out
    assert "## Verdicts" in out
    assert results["verdicts"]["tempo"] in ("keep", "remove", "no verdict")
    assert results["promotion_outcome"]["effect"] > 0
