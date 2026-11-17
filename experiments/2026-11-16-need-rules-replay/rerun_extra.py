"""The rerun's extra report: ranks, the four high three-color sets against the
other fifteen on both measures, and where each regret slope change comes from.

    python experiments/2026-11-16-need-rules-replay/rerun_extra.py RESULTS

See the addendum in PROTOCOL.md.
"""

import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import attribute  # noqa: E402
import ranks  # noqa: E402

H = ranks.H
C, R = H.C, H.R
# First-day share of three-color decks 20% or more (by_set.py's split).
HIGH = {"KTK", "TDM", "SNC", "DMU"}


def group(data, high):
    sub = {k: v for k, v in data.items() if (k[0] in HIGH) == high}
    frame = C.regret_frame(sub)
    n = len(frame[0])
    change = C.change(frame, np.arange(n))
    se = R.bootstrap(lambda i: C.change(frame, i), n)
    swap, swap_se = C.disagreements(sub)
    total, changed = C.picks(sub)[:2]
    return change, se, swap, swap_se, 100 * changed / total


def main(argv=None):
    root = (argv or sys.argv[1:])[0]
    heads = sorted(
        {os.path.basename(p)[: -len(".json")] for p in glob.glob(os.path.join(root, "*", "*.json"))}
        - {"base"}
    )
    ranks.main([root])
    print("\n# The four high three-color sets against the other fifteen\n")
    print(f"High: {', '.join(sorted(HIGH))}. Regret slope: positive is worse for the head; "
          "swap: negative is worse.\n")
    print("| head | sets | regret slope (SE), SEs | swap (SE), SEs | top card changes |")
    print("|---|---|---|---|---|")
    for head in heads:
        data = H.load(root, head)
        for name, high in (("four high", True), ("other 15", False)):
            ch, se, sw, sw_se, top = group(data, high)
            print(f"| {head} | {name} | {ch:+.4f} ({se:.4f}), {ch / se:+.1f} "
                  f"| {sw:+.3f} ({sw_se:.3f}), {sw / sw_se if sw_se else 0:+.1f} | {top:.2f}% |",
                  flush=True)
        del data
    if {"no-needs-2drops", "2drops-cap-1.25"} <= set(heads):
        print("\n# Head to head: no-needs-2drops against 2drops-cap-1.25\n")
        cap, none = H.load(root, "2drops-cap-1.25"), H.load(root, "no-needs-2drops")
        pairs = {k: {"base": cap[k]["head"], "head": none[k]["head"]} for k in cap.keys() & none.keys()}
        del cap, none
        pairs = dict(sorted(pairs.items()))
        frame = C.regret_frame(pairs)
        n = len(frame[0])
        ch = C.change(frame, np.arange(n))
        se = R.bootstrap(lambda i: C.change(frame, i), n)
        sw, sw_se = C.disagreements(pairs)
        total, changed = C.picks(pairs)[:2]
        print("Removing the bonus against the 1.25x cap: positive regret slope or negative "
              "swap is worse for removing.\n")
        print(f"- regret slope: {ch:+.4f} ({se:.4f}), {ch / se:+.1f} SEs")
        print(f"- swap: {sw:+.3f} ({sw_se:.3f}), {sw / sw_se if sw_se else 0:+.1f} SEs")
        print(f"- top card differs on {100 * changed / total:.2f}% of picks")
        del pairs, frame
    print("\n# Where each regret slope change comes from\n")
    attribute.main([root, *heads])


if __name__ == "__main__":
    main()
