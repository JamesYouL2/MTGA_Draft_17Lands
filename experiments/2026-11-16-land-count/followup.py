"""A check added after the first result was seen. Not part of the protocol.

    python experiments/2026-11-16-land-count/followup.py results/*.json

16 lands beat 17 by about the same in every curve band. If that came from who
plays 16 (better players than their bucket says), it should shift between the
player's buckets. This fits the protocol's model within each win rate bucket and
each experience bucket.
"""

import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lands import Decks, cell  # noqa: E402


def main():
    files = []
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            files.append(json.load(f))
    d = Decks(files)
    rows = [r for f in files for r in f["rows"] if r["mana"]["cards"] == 40]
    for key, label in (("skill", "player's game win rate bucket"),
                       ("experience", "player's games bucket")):
        values = np.array([r[key] for r in rows])
        print(f"## By {label}\n")
        print("| bucket | decks | share on 16 | 16 against 17 | 15- against 17 | 18 against 17 |")
        print("|---|---|---|---|---|---|")
        for v, n in sorted(Counter(values.tolist()).items(), key=lambda kv: kv[0]):
            m = values == v
            if n < 5000:
                continue
            res = d.fit(m)
            print(f"| {v} | {n} | {(d.side[m] == '16').mean():.1%} | {cell(res.get('16'))} "
                  f"| {cell(res.get('15-'))} | {cell(res.get('18'))} |")
        print()


if __name__ == "__main__":
    main()
