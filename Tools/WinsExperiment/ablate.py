"""Replay main's advisor with parts of its score switched off.

    python Tools/WinsExperiment/ablate.py nocast --src base --drafts drafts.json.gz \
        --dataset FRA.json.gz --set FRA --label nocast --out results/FRA.nocast.json

nocast: no castability multiplier. nocomp: no composition multiplier.
nocastcomp: neither.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "AdvisorReplay"))

import replay  # noqa: E402


def main():
    which, argv = sys.argv[1], sys.argv[2:]
    src = argv[argv.index("--src") + 1]
    sys.path.insert(0, os.path.abspath(src))
    from src.advisor.engine import DraftAdvisor

    if which in ("nocast", "nocastcomp"):
        DraftAdvisor._calculate_castability_v5 = lambda self, *a: (1.0, "")
    if which in ("nocomp", "nocastcomp"):
        DraftAdvisor._calculate_composition_bonus = lambda self, *a: (1.0, "")
    replay.main(argv)


if __name__ == "__main__":
    main()
