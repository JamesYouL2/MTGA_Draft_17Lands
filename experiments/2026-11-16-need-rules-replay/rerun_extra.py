"""The rerun's extra report: ranks, the four high three-color sets against the
other fifteen on both measures, the two 2-drop heads head to head, and where each
regret slope change comes from.

    python experiments/2026-11-16-need-rules-replay/rerun_extra.py RESULTS

See the addendum in PROTOCOL.md. Reads one folder at a time and keeps only a row
per event, so a full run fits in a few GB.
"""

import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import attribute  # noqa: E402
import ranks  # noqa: E402

C, R = attribute.C, attribute.R
# First-day share of three-color decks 20% or more (by_set.py's split).
HIGH = {"KTK", "TDM", "SNC", "DMU"}


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def summarise(root, pairs):
    """{(a, b): rows}: a row per complete event in both, comparing b against a.

    Each row holds what compare.py's regret_frame, disagreements and picks use."""
    rows = {pair: [] for pair in pairs}
    labels = sorted({x for pair in pairs for x in pair})
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        sample = os.path.basename(folder).rsplit("-", 1)[-1]
        runs = {x: read(os.path.join(folder, f"{x}.json")) for x in labels
                if os.path.exists(os.path.join(folder, f"{x}.json"))}
        code = runs["base"]["set"]
        by_id = {x: {d["id"]: d for d in r["drafts"]} for x, r in runs.items()}
        for a, b in pairs:
            if a not in by_id or b not in by_id:
                continue
            for i, da in by_id[a].items():
                db = by_id[b].get(i)
                if db is None or not R.is_complete(da) or not da["picks"] or not db["picks"]:
                    continue
                head = {(q[0], q[1]): q for q in db["picks"]}
                net = n = total = 0
                for p in da["picks"]:
                    q = head.get((p[0], p[1]))
                    if q is None:
                        continue
                    total += 1
                    if p[5] != q[5]:
                        n += 1
                        net += int(q[2] == 0) - int(p[2] == 0)
                rows[(a, b)].append({
                    "key": (code, f"{sample}:{i}"),
                    "wins": da["wins"], "skill": da["skill"], "games": da["games"],
                    "a": np.mean([p[3] for p in da["picks"]]),
                    "b": np.mean([q[3] for q in db["picks"]]),
                    "net": net, "n": n, "total": total,
                })
        del runs, by_id
    return rows


def measures(rows):
    rows = sorted(rows, key=lambda r: r["key"])
    keys = [r["key"] for r in rows]
    wins = np.array([r["wins"] for r in rows], dtype=float)
    ctrl = R.controls(rows, [k[0] for k in keys])
    frame = (wins, ctrl, np.array([r["a"] for r in rows]), np.array([r["b"] for r in rows]), keys)
    idx = np.arange(len(rows))
    change = C.change(frame, idx)
    se = R.bootstrap(lambda i: C.change(frame, i), len(rows))
    a = np.array([[r["net"], r["n"]] for r in rows], dtype=float)

    def fit(i):
        X = np.column_stack([a[i, 0], a[i, 1], ctrl[i]])
        return 2 * np.linalg.lstsq(X, wins[i], rcond=None)[0][0]

    swap, swap_se = fit(idx), R.bootstrap(fit, len(rows))
    top = 100 * a[:, 1].sum() / sum(r["total"] for r in rows)
    return change, se, swap, swap_se, top


def cells(m):
    ch, se, sw, sw_se, top = m
    return (f"{ch:+.4f} ({se:.4f}), {ch / se:+.1f} | {sw:+.3f} ({sw_se:.3f}), "
            f"{sw / sw_se if sw_se else 0:+.1f} | {top:.2f}%")


def main(argv=None):
    root = (argv or sys.argv[1:])[0]
    heads = sorted(
        {os.path.basename(p)[: -len(".json")] for p in glob.glob(os.path.join(root, "*", "*.json"))}
        - {"base"}
    )
    ranks.main([root])
    pairs = [("base", h) for h in heads]
    both = {"no-needs-2drops", "2drops-cap-1.25"} <= set(heads)
    if both:
        pairs.append(("2drops-cap-1.25", "no-needs-2drops"))
    rows = summarise(root, pairs)

    print("\n# The four high three-color sets against the other fifteen\n")
    print(f"High: {', '.join(sorted(HIGH))}. Regret slope: positive is worse for the head; "
          "swap: negative is worse.\n")
    print("| head | sets | regret slope (SE), SEs | swap (SE), SEs | top card changes |")
    print("|---|---|---|---|---|")
    for h in heads:
        for name, high in (("four high", True), ("other 15", False)):
            sub = [r for r in rows[("base", h)] if (r["key"][0] in HIGH) == high]
            print(f"| {h} | {name} | {cells(measures(sub))} |", flush=True)

    if both:
        print("\n# Head to head: no-needs-2drops against 2drops-cap-1.25\n")
        print("Removing the bonus against the 1.25x cap: positive regret slope or negative "
              "swap is worse for removing.\n")
        print("| sets | regret slope (SE), SEs | swap (SE), SEs | top card differs |")
        print("|---|---|---|---|")
        h2h = rows[("2drops-cap-1.25", "no-needs-2drops")]
        print(f"| all 19 | {cells(measures(h2h))} |")
        for name, high in (("four high", True), ("other 15", False)):
            sub = [r for r in h2h if (r["key"][0] in HIGH) == high]
            print(f"| {name} | {cells(measures(sub))} |", flush=True)
    del rows

    print("\n# Where each regret slope change comes from\n")
    attribute.main([root, *heads])


if __name__ == "__main__":
    main()
