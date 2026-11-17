"""How far below the top card each head reaches, and whose regret it moves.

    python experiments/2026-11-16-need-rules-replay/ranks.py RESULTS

RESULTS is an Advisor heads run's results folder; the pick records need the top
three cards (index 7), which replay.py writes from 2026-11-16. For each head, the
share of picks where the top card, the top three (in order), the drafter's card's
rank and its regret change, and, on the picks where only the drafter's regret
moved, which way and for drafters who went on to win how much. See PROTOCOL.md.
"""

import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

R = H.R


def counts(data):
    n = top1 = top3 = rank = moved = only_moved = up = 0
    rows = []  # complete events: wins, picks with regret moved, change in mean regret
    for v in data.values():
        head = {(p[0], p[1]): p for p in v["head"]["picks"]}
        k = shift = m = 0
        for p in v["base"]["picks"]:
            q = head.get((p[0], p[1]))
            if q is None:
                continue
            n += 1
            m += 1
            top1 += p[5] != q[5]
            top3 += p[-1] != q[-1]
            rank += p[2] != q[2]
            if p[3] != q[3]:
                moved += 1
                if p[-1] == q[-1]:
                    only_moved += 1
                up += q[3] > p[3]
                k += 1
                shift += q[3] - p[3]
        if R.is_complete(v["base"]) and m:
            rows.append([v["base"]["wins"], k, shift / m])
    a = np.array(rows, dtype=float)
    hit = a[:, 1] > 0
    return {
        "picks": n,
        "top1": 100 * top1 / n,
        "top3": 100 * top3 / n,
        "rank": 100 * rank / n,
        "regret": 100 * moved / n,
        "regret_top3_same": 100 * only_moved / max(moved, 1),
        "regret_up": 100 * up / max(moved, 1),
        "drafts_hit": 100 * hit.mean(),
        "wins_hit": a[hit, 0].mean() if hit.any() else float("nan"),
        "wins_rest": a[~hit, 0].mean(),
        # Change in the draft's mean regret, by the event's wins: positive where
        # the head raises winners' regret more than losers'.
        "shift_by_wins": np.polyfit(a[:, 0], a[:, 2], 1)[0] if hit.any() else 0.0,
    }


def main(argv=None):
    root = (argv or sys.argv[1:])[0]
    heads = sorted(
        {os.path.basename(p)[: -len(".json")] for p in glob.glob(os.path.join(root, "*", "*.json"))}
        - {"base"}
    )
    print("# Ranks below the top\n")
    print("Share of picks where each changes. \"regret moves\" is the drafter's own card's "
          "regret; \"top three same\" and \"up\" are shares of those picks.\n")
    print("| head | top card | top three | drafter's rank | regret moves | top three same "
          "| up | drafts hit | wins, hit / rest | regret shift per win |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for head in heads:
        c = counts(H.load(root, head))
        print(f"| {head} | {c['top1']:.2f}% | {c['top3']:.2f}% | {c['rank']:.2f}% "
              f"| {c['regret']:.2f}% | {c['regret_top3_same']:.1f}% | {c['regret_up']:.1f}% "
              f"| {c['drafts_hit']:.1f}% | {c['wins_hit']:.2f} / {c['wins_rest']:.2f} "
              f"| {c['shift_by_wins']:+.5f} |")


if __name__ == "__main__":
    main()
