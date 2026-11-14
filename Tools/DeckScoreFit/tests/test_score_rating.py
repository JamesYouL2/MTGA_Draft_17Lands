import gzip
import json

import numpy as np
import pytest
import score_rating as sr


def shown(pair, top=None, pairs=None):
    return {"pair": pair, "shown": [top or pair], "pairs": pairs or {pair: 80.0}}


def row(main, base, other, wins, games=10, skill="0.56", experience="50", pairs=None):
    pairs = pairs or {"WU": 80.0, "UB": 70.0}
    return {
        "main": main, "skill": skill, "experience": experience, "wins": wins, "games": games,
        "versions": {
            "blend": shown(base, pairs=pairs),
            "overall": shown(other, pairs=pairs),
            "overall+pair": shown(base, pairs=pairs),
            "blend+pair": shown(base, pairs=pairs),
        },
    }


def table(tmp_path, by_set, skipped=None):
    paths = []
    for name, rows in by_set.items():
        path = tmp_path / f"{name}.json.gz"
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump({"set": name, "skipped": skipped or {}, "rows": rows}, f)
        paths.append(str(path))
    return sr.Table(paths, (sr.BASE, *sr.VERSIONS))


def duel(n, won_in_other, won_in_base):
    """n decks in each of the two suggested pairs, where blend says WU and overall UB."""
    rows = []
    for i in range(n):
        rows.append(row("UB", "WU", "UB", won_in_other if i % 2 else won_in_other - 1,
                        skill=str(i % 3)))
        rows.append(row("WU", "WU", "UB", won_in_base if i % 2 else won_in_base - 1,
                        skill=str(i % 3)))
    return rows


def test_table_reads_each_versions_suggestion_and_gap(tmp_path):
    t = table(tmp_path, {"A": [row("UB", "WU", "UB", 5), row("WUB", "WU", "WU", 5)]},
              {"small": 2})
    assert len(t) == 2
    assert t.pair["overall"].tolist() == ["UB", "WU"]
    assert t.two.tolist() == [True, False]
    assert t.gap["blend"][0] == 10.0
    assert np.isnan(t.gap["blend"][1])
    assert t.skipped == {"small": 2}


def test_head_to_head_favors_the_pair_that_won_more(tmp_path):
    t = table(tmp_path, {"A": duel(200, 7, 4), "B": duel(200, 6, 4)})
    r = sr.head_to_head(t, "overall", "blend")
    assert (r["decks_a"], r["decks_b"], r["sets"]) == (400, 400, 2)
    assert r["rate_a"] > r["rate_b"]
    assert r["effect"] > 0 and r["effect"] == pytest.approx(25.0, abs=5.0)
    # And the same comparison turned around.
    flipped = sr.head_to_head(t, "blend", "overall")
    assert flipped["effect"] == pytest.approx(-r["effect"], abs=1e-6)


def test_head_to_head_ignores_pools_that_agree_or_played_neither(tmp_path):
    rows = duel(200, 6, 4) + [
        row("UB", "WU", "WU", 10),  # the two agree
        row("BR", "WU", "UB", 10),  # played neither
        row("WUB", "WU", "UB", 10),  # no pair to speak of
    ]
    t = table(tmp_path, {"A": rows, "B": duel(200, 6, 4)})
    r = sr.head_to_head(t, "overall", "blend")
    assert r["decks"] == 800
    assert r["differ"] == 801


def test_head_to_head_needs_decks_on_both_sides(tmp_path):
    t = table(tmp_path, {"A": duel(10, 6, 4), "B": duel(200, 6, 4)[:50]})
    r = sr.head_to_head(t, "overall", "blend")
    assert r["effect"] is None and r["verdict"] == "insufficient data"


@pytest.mark.parametrize("value, se, expected", [
    (1.0, 0.2, "better"), (-1.0, 0.2, "worse"),
    (0.1, 0.2, "not worse"), (-0.2, 0.2, "inconclusive"), (0.0, 0.3, "inconclusive"),
])
def test_verdict(value, se, expected):
    assert sr.verdict(value, se) == expected


def test_changes_are_percentages_of_pools(tmp_path):
    t = table(tmp_path, {"A": [row("UB", "WU", "UB", 5), row("UB", "WU", "WU", 5)]})
    assert sr.changes(t, "overall") == {"pair": 50.0, "deck": 50.0}


def test_report_runs_and_says_how_the_pairs_did(tmp_path, capsys):
    rows = [
        dict(r, skill=str(i % 3), experience=str((i // 2) % 2))
        for i, r in enumerate(duel(200, 7, 4))
    ]
    t = table(tmp_path, {"A": rows, "B": rows})
    results = sr.report(t)
    out = capsys.readouterr().out
    assert "Head to head with the blend" in out
    assert results["head_to_head"]["overall"]["verdict"] == "better"
    # Only overall differs from the blend here.
    assert results["head_to_head"]["blend+pair"]["verdict"] == "insufficient data"
    assert results["followed"]["blend"]["played"] == 50.0


def test_gap_slope_is_negative_when_gaps_lose(tmp_path):
    good = {"WU": 80.0, "UB": 80.0}
    bad = {"WU": 90.0, "UB": 70.0}
    rows = [row("UB", "WU", "UB", 7, skill=str(i % 2), pairs=good) for i in range(100)]
    rows += [row("UB", "WU", "UB", 3, skill=str(i % 2), pairs=bad) for i in range(100)]
    t = table(tmp_path, {"A": rows, "B": rows})
    r = sr.slope_changes(t, ("overall",))
    assert r["blend"]["slope"] < 0
    assert r["overall"]["change"] == pytest.approx(0.0)
