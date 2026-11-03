from pathlib import Path
import importlib.util
import sys

import numpy as np

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[3])]
spec = importlib.util.spec_from_file_location("ablation_report", Path(__file__).resolve().parents[1] / "report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def test_batched_outcome_slopes_match_separate_regressions():
    rng = np.random.default_rng(42)
    x = rng.normal(size=(300, 5))
    ctrl = np.column_stack([np.ones(300), rng.normal(size=(300, 3))])
    wins = 0.5*x[:, 0] + 0.3*ctrl[:, 1] + rng.normal(size=300)
    actual = report.slopes(x, wins, ctrl)
    expected = [np.linalg.lstsq(np.column_stack([x[:, i]/x[:, i].std(), ctrl]), wins, rcond=None)[0][0]
                for i in range(5)]
    np.testing.assert_allclose(actual, expected, atol=1e-12)
