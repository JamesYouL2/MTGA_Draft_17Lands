import io

import fit
import numpy as np
import pytest

TRUE = {"quality": 1.2, "off_pips": -0.4, "unrated": 0.3}


def simulated(sets=("AAA", "BBB"), drafts=150, seed=0):
    """features.py outputs whose picks follow TRUE, with one feature that
    never differs within a pick."""
    rng = np.random.default_rng(seed)
    names = [*TRUE, "constant"]
    files = []
    for s in sets:
        situations = []
        for d in range(drafts):
            for pick in range(1, 15):
                n = int(rng.integers(2, 12))
                x = np.column_stack(
                    [
                        rng.normal(size=n),
                        rng.exponential(2.0, size=n) * (rng.random(n) < 0.5),
                        (rng.random(n) < 0.1).astype(float),
                        np.full(n, 1.0),
                    ]
                )
                u = x[:, :3] @ np.array(list(TRUE.values()))
                p = np.exp(u - u.max())
                situations.append(
                    {
                        "draft": d,
                        "pack": 1 + pick % 3,
                        "pick": pick,
                        "chosen": int(rng.choice(n, p=p / p.sum())),
                        "x": x.tolist(),
                        "extra": [[pick, float(v)] for v in x[:, 0]],
                    }
                )
        files.append(
            {
                "set": s,
                "names": names,
                "weights": {
                    "quality": 15.0,
                    "off_pips": -5.0,
                    "unrated": 0.0,
                    "constant": 0.0,
                },
                "log_odds_per_point": 0.08,
                "extra_names": ["pick", "noise"],
                "drafts": drafts,
                "skipped": {},
                "unmatched": {},
                "situations": situations,
            }
        )
    return files


@pytest.fixture(scope="module")
def data():
    return fit.Data(simulated())


def test_drops_features_that_never_differ(data):
    assert data.never == ["constant"]
    assert data.names == list(TRUE)


def test_recovers_the_weights(data):
    beta, cov = fit.fit_logit(data.X, data)
    se = np.sqrt(np.diag(cov))

    assert np.all(np.abs(beta - np.array(list(TRUE.values()))) < 4 * se)
    assert np.all(se < 0.1)


def test_points_put_quality_at_15(data):
    beta, cov = fit.fit_logit(data.X, data)
    points, se = fit.to_points(beta, cov, data.q)

    assert points[data.q] == pytest.approx(15.0)
    assert se[data.q] == pytest.approx(0.0, abs=1e-9)
    assert points[1] == pytest.approx(15.0 * beta[1] / beta[0])


def test_top_k_splits_ties():
    data = fit.Data(simulated(drafts=1))
    sub = data.subset(np.arange(len(data.sizes)) == 0)
    u = np.zeros(sub.sizes[0])

    assert fit.top_k(u, sub, 1)[0] == pytest.approx(1 / sub.sizes[0])
    assert fit.top_k(u, sub, 3)[0] == pytest.approx(min(1.0, 3 / sub.sizes[0]))


def test_subset_keeps_picks_whole(data):
    sub = data.subset(data.set == "BBB")

    assert len(sub.X) == sub.sizes.sum()
    assert np.all(sub.chosen - sub.starts < sub.sizes)
    assert np.array_equal(sub.X[sub.chosen], data.X[data.chosen][data.set == "BBB"])


def test_report_ends_with_the_weights(data):
    out = io.StringIO()
    fit.report(data, out)
    text = out.getvalue()

    assert "## Held-out sets" in text
    assert '"constant": 0.0,  # not fitted' in text
    assert text.rstrip().endswith("```")
