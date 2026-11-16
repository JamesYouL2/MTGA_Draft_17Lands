"""Auto optimize against the same button with only the Power Up swap.

    python experiments/2026-11-16-optimize-power-only/report.py buttons/*.json.gz

Reads buttons.py's rows. Changes in deck score are in win rate points at the score's
own price, with set-clustered SEs. Needs only NumPy.
"""

import gzip
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
from buttons_report import LAND_COUNT, NO_SWAP, clustered_mean  # noqa: E402

VARIANTS = ("power-sim", "power-always")


def load(paths):
    sets, kind, gain = [], [], {k: [] for k in ("app",) + VARIANTS}
    v_kind = {v: [] for v in VARIANTS}
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        price = data["win_points_per_score"]
        for r in data["rows"]:
            o = r["optimize"]
            if not o:
                continue
            sets.append(data["set"])
            kind.append(o["kind"])
            gain["app"].append(price * (o["score_after"] - o["score_before"]))
            for v in VARIANTS:
                v_kind[v].append(o["variants"][v]["kind"])
                gain[v].append(price * (o["variants"][v]["score_after"] - o["score_before"]))
    return (np.array(sets), np.array(kind), {k: np.array(v) for k, v in gain.items()},
            {k: np.array(v) for k, v in v_kind.items()})


def pm(mean, se):
    return f"{mean:+.3f} [{mean - 1.96 * se:+.3f}, {mean + 1.96 * se:+.3f}]"


def main(paths):
    sets, kind, gain, v_kind = load(paths)
    n = len(sets)
    # As in buttons_report: a land-count swap moves the score only by changing which
    # spells its mean is over, so the app's deciding change counts it as zero.
    app = np.where(np.isin(kind, LAND_COUNT), 0.0, gain["app"])
    print(f"{n} decks from {len(set(sets))} sets.\n")
    print("| version | changes the deck | deck score change | minus the app's |")
    print("|---|---|---|---|")
    print(f"| app | {100 * (kind != NO_SWAP).mean():.1f}% | {pm(*clustered_mean(app, sets))} | |")
    for v in VARIANTS:
        print(f"| {v} | {100 * (v_kind[v] != NO_SWAP).mean():.1f}% | {pm(*clustered_mean(gain[v], sets))} "
              f"| {pm(*clustered_mean(gain[v] - app, sets))} |")
    print("\n## By what the app chose\n")
    print("| the app's swap | decks | app's change | power-always's change on the same decks | power-always swaps |")
    print("|---|---|---|---|---|")
    for k, count in Counter(kind.tolist()).most_common():
        m = kind == k
        print(f"| {k} | {100 * count / n:.1f}% | {pm(*clustered_mean(gain['app'][m], sets[m]))} "
              f"| {pm(*clustered_mean(gain['power-always'][m], sets[m]))} "
              f"| {100 * (v_kind['power-always'][m] != NO_SWAP).mean():.1f}% |")


if __name__ == "__main__":
    main(sys.argv[1:])
