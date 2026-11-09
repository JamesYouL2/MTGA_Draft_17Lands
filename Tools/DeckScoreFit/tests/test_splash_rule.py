import math

import numpy as np
import rules
import splash_rule

WEIGHTS = {"card_quality": 12.0, "two_colors": 3.5, "missing_fixing": -2.5,
           "missing_spells": -10.0}
EXTRA_WORTH = 0.04


def files(n=24000, sets=("AAA", "BBB", "CCC", "DDD"), seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for s in sets:
        rows = []
        for i in range(n // len(sets)):
            off = int(rng.integers(0, 6)) * int(rng.random() < 0.5)
            bombs = int(rng.integers(0, off + 1)) if off else 0
            fixing = int(rng.integers(0, 7))
            f = {"card_quality": rng.normal(), "two_colors": float(off == 0),
                 "missing_fixing": 0.0, "missing_spells": 0.0}
            skill = rng.choice(["0.48", "0.54", "0.60"])
            eta = (float(skill) - 0.54) * 4 + 0.2 + 0.4 * f["card_quality"]
            eta += EXTRA_WORTH * fixing * (bombs > 0)
            games = int(rng.integers(3, 10))
            rows.append({
                "id": f"{s}{i}",
                "wins": int(rng.binomial(games, 1 / (1 + math.exp(-eta)))),
                "games": games,
                "skill": skill,
                "experience": rng.choice(["5", "50"]),
                "features": f,
                "extra": {"lands": 17.0, "creatures": 15.0, "colors": 2.0 + (off > 0)},
                "rules": {"fixing": fixing, "off_color": off, "off_bomb": bombs},
            })
        out.append({"set": s, "base_score": 75.0, "weights": WEIGHTS, "rows": rows,
                    "tags": {"removal": 40, "fixing_ramp": 10}})
    return out


def test_terms_separate_fixing_with_a_bomb():
    r = {"off_color": np.array([0.0, 2, 2]), "fixing": np.array([1.0, 3, 3]),
         "off_bomb": np.array([0.0, 0, 1])}
    terms = splash_rule.splash_terms(r)
    assert list(terms["fixing_with_off_bomb"]) == [0, 0, 3]
    assert list(terms["fixing_in_off_color_deck"]) == [0, 3, 3]


def test_recovers_the_simulated_effect():
    rd = rules.RuleData(files())
    everything = np.ones(len(rd.base.set), dtype=bool)
    est = rules.estimate(rd, splash_rule.SPLASH, everything)
    per_pp = 100 * rd.win_rate * (1 - rd.win_rate)
    assert abs(est["pp"] - per_pp * EXTRA_WORTH) < 3 * est["se"]
    assert est["pp"] > 0


def test_main_reports_only_this_rule(tmp_path, monkeypatch):
    import json

    paths = []
    for f in files(n=6000):
        path = tmp_path / f"{f['set']}.json"
        path.write_text(json.dumps(f))
        paths.append(str(path))
    monkeypatch.setattr(rules, "RULES", rules.RULES)
    monkeypatch.setattr(rules, "Z", rules.Z)
    out = tmp_path / "out.json"
    splash_rule.main(paths + ["--json", str(out)])
    assert list(json.loads(out.read_text())) == ["bomb_splash"]
