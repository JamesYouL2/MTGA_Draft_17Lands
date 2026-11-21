"""Which picks a head's regret slope change comes from.

    python experiments/2026-11-16-need-rules-replay/attribute.py RESULTS HEAD [HEAD ...]

Written after the run, to explain readings that move the regret slope with almost
no change to the top card. For each head, the slope change with the head's regret
used only on one class of picks (today's everywhere else):

- top changed: the top card changes;
- rank changed: the top card stays, the drafter's own card moves in rank;
- regret only: neither moves, but the drafter's regret does (the pack's spread or
  top score changed).

The three add up to about the whole change. Also the wins of drafters whose own
card dropped in rank against those whose card rose, the top card unchanged.
Reads one folder at a time, so a full run fits in memory.
"""

import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-heldout-replay"))
import compare as C  # noqa: E402

R = C.R
KINDS = ("top changed", "rank changed", "regret only")


def kind(p, q):
    if p[5] != q[5]:
        return "top changed"
    if p[2] != q[2]:
        return "rank changed"
    if p[3] != q[3]:
        return "regret only"
    return None


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def summarise(root, heads):
    """{head: rows}, one row per complete event in both base and head."""
    rows = {h: [] for h in heads}
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        base = read(os.path.join(folder, "base.json"))
        sample = os.path.basename(folder).rsplit("-", 1)[-1]
        drafts = {d["id"]: d for d in base["drafts"] if R.is_complete(d) and d["picks"]}
        for h in heads:
            path = os.path.join(folder, f"{h}.json")
            if not os.path.exists(path):
                continue
            for d in read(path)["drafts"]:
                b = drafts.get(d["id"])
                if b is None or not d["picks"]:
                    continue
                head = {(q[0], q[1]): q for q in d["picks"]}
                shift = dict.fromkeys(KINDS, 0.0)
                down = up = False
                for p in b["picks"]:
                    q = head.get((p[0], p[1]))
                    k = q is not None and kind(p, q)
                    if k:
                        shift[k] += q[3] - p[3]
                        down |= k == "rank changed" and q[2] > p[2]
                        up |= k == "rank changed" and q[2] < p[2]
                n = len(b["picks"])
                regret = sum(p[3] for p in b["picks"]) / n
                rows[h].append({
                    "key": (base["set"], f"{sample}:{d['id']}"),
                    "wins": b["wins"], "skill": b["skill"], "games": b["games"],
                    "base": regret,
                    "head": sum(q[3] for q in d["picks"]) / len(d["picks"]),
                    **{k: regret + shift[k] / n for k in KINDS},
                    "down": down, "up": up,
                })
    return rows


def main(argv=None):
    root, *heads = argv or sys.argv[1:]
    rows = summarise(root, heads)
    print("Regret slope change, head minus today's, with the head's regret on one class "
          "of picks only. Positive is worse for the head.\n")
    print("| head | whole | top changed | rank changed | regret only |")
    print("|---|---|---|---|---|")
    notes = []
    for h in heads:
        rs = sorted(rows[h], key=lambda r: r["key"])
        keys = [r["key"] for r in rs]
        wins = np.array([r["wins"] for r in rs], dtype=float)
        ctrl = R.controls(rs, [k[0] for k in keys])
        base = np.array([r["base"] for r in rs])
        cells = []
        for col in ("head", *KINDS):
            frame = (wins, ctrl, base, np.array([r[col] for r in rs]), keys)
            n = len(rs)
            ch = C.change(frame, np.arange(n))
            se = R.bootstrap(lambda i: C.change(frame, i), n)
            cells.append(f"{ch:+.5f} ({se:.5f}), {ch / se:+.1f} SEs")
        print(f"| {h} | " + " | ".join(cells) + " |", flush=True)
        down = wins[[r["down"] for r in rs]]
        up = wins[[r["up"] for r in rs]]
        notes.append(
            f"- **{h}**: drafters whose own card dropped in rank, top card unchanged: "
            f"{len(down)} events, {down.mean():.2f} wins; whose card rose: {len(up)}, "
            f"{up.mean():.2f}; every event {wins.mean():.2f}."
        )
    print()
    print("\n".join(notes))


if __name__ == "__main__":
    main()
