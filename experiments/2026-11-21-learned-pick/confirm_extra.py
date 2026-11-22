"""The confirmation run's extra report: agreement, and event wins by skill bucket.

    python experiments/2026-11-21-learned-pick/confirm_extra.py RESULTS

Prints agreement.py's table, then for each head heads.py's swap measure (event
wins per pick swapped from base's top card to the head's) on the drafts in each
skill bucket only, combined over salts as heads.py combines them. The controls
(set, skill bucket, games bucket) are the same as heads.py's. The question is
CONFIRM.md's imitation check: does the gain hold among the strongest drafters?
"""

import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import agreement  # noqa: E402
import heads as H  # noqa: E402

C = H.C

# 17Lands' win-rate bucket of the drafter, over their games.
BUCKETS = [
    ("60%+", lambda s: s >= 0.60),
    ("56 to 60%", lambda s: 0.56 <= s < 0.60),
    ("52 to 56%", lambda s: 0.52 <= s < 0.56),
    ("under 52%", lambda s: s < 0.52),
    ("all with a bucket", lambda s: True),
]


def bucket_rows(data):
    frame = C.swap_frame(data)
    keys = frame[2]
    skill = np.array(
        [np.nan if data[k]["base"]["skill"] is None else data[k]["base"]["skill"] for k in keys]
    )
    rows = []
    for name, test in BUCKETS:
        sub = np.array([i for i, s in enumerate(skill) if not np.isnan(s) and test(s)])
        if len(sub) < 50:
            rows.append((name, len(sub), None))
            continue
        salts = C.by_salt([keys[i] for i in sub], lambda j, sub=sub: C.swap(frame, sub[j]))
        rows.append((name, len(sub), H.combined(salts) if len(salts) >= 2 else None))
    return rows


def main(root):
    agreement.main(root)
    print()
    print("# Event wins per swapped pick by drafter skill bucket")
    print()
    print(
        "Head minus base, on the complete events of drafters in each 17Lands "
        "win-rate bucket, combined over salts: estimate (scaled SE), SEs. "
        "Controls as heads.py's (set, skill bucket, games bucket)."
    )
    print()
    heads = sorted(
        {
            os.path.basename(p)[: -len(".json")]
            for p in glob.glob(os.path.join(root, "*", "*.json"))
        }
        - {"base"}
    )
    print("| head | skill bucket | events | event wins per swapped pick |")
    print("|---|---|---|---|")
    for head in heads:
        data = H.load(root, head)
        for name, n, m in bucket_rows(data):
            cell = "" if m is None else H.cell(m, 3)
            print(f"| {head} | {name} | {n} | {cell} |")
        del data


if __name__ == "__main__":
    main(sys.argv[1])
