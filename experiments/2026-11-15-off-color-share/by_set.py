"""Each head's change in regret slope by set, against the set's three-color share.

    python experiments/2026-11-15-off-color-share/by_set.py RESULTS --json by_set.json

RESULTS is an Advisor heads run's folder. Reads the heads report's helpers and
shares.json, and needs only NumPy.
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

C, R = H.C, H.R
HIGH = 0.2  # a first-day share at or above this is a high-share set


def share_of(entry):
    """A set's first-day share, or the app's share where that wasn't worked out."""
    return entry.get("day1", entry.get("app"))


def line(x, y, se):
    """Weighted least squares of y on x: (slope, its SE), weights 1 / se^2."""
    x, y, w = np.asarray(x), np.asarray(y), 1.0 / np.asarray(se) ** 2
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    sxx = float(np.sum(w * (x - mx) ** 2))
    return float(np.sum(w * (x - mx) * (y - my)) / sxx), sxx**-0.5


def measure(data, shares):
    frame = C.regret_frame(data)
    codes = np.array([k[0] for k in frame[4]])

    def change(idx):
        return C.change(frame, idx), R.bootstrap(lambda i: C.change(frame, idx[i]), len(idx))

    sets = {}
    for code in sorted(set(codes), key=lambda s: -share_of(shares[s])):
        idx = np.flatnonzero(codes == code)
        sets[code] = {"share": share_of(shares[code]), "events": len(idx)}
        sets[code]["change"], sets[code]["se"] = change(idx)

    def fit(leave_out=()):
        keep = [s for s in sets if s not in leave_out]
        if len(keep) < 3:
            return None
        return line(*([sets[s][k] for s in keep] for k in ("share", "change", "se")))

    high = np.array([share_of(shares[c]) >= HIGH for c in codes])
    return {
        "sets": sets,
        "slope": fit(),
        "without": {s: fit((s,)) for s in ("TDM", "DMU") if s in sets},
        "high": change(np.flatnonzero(high)) if high.any() else None,
        "low": change(np.flatnonzero(~high)) if not high.all() else None,
    }


def cell(pair, scale=1.0):
    if not pair:
        return ""
    return f"{scale * pair[0]:+.4f} ({scale * pair[1]:.4f}), {pair[0] / pair[1]:+.1f} SEs"


def report(results):
    print("Regret slope change, head minus base: positive is worse for the head.")
    print("The line is the change against the set's first-day share of three-color decks,")
    print("per 10 points of share, weighting each set by its SE.\n")
    print("| head | line, all sets | without TDM | without DMU "
          f"| sets at {HIGH:.0%}+ share | the other sets |")
    print("|---|---|---|---|---|---|")
    for head, m in results.items():
        without = [cell(m["without"][s], 0.1) if s in m["without"] else "" for s in ("TDM", "DMU")]
        print(f"| {head} | {cell(m['slope'], 0.1)} | {without[0]} | {without[1]} "
              f"| {cell(m['high'])} | {cell(m['low'])} |")
    heads = list(results)
    print("\n## By set\n")
    print("| set | first-day share | events | " + " | ".join(heads) + " |")
    print("|---|---|---|" + "---|" * len(heads))
    for code, first in results[heads[0]]["sets"].items():
        cells = [
            f"{results[h]['sets'][code]['change']:+.4f} ({results[h]['sets'][code]['se']:.4f})"
            for h in heads
        ]
        print(f"| {code} | {100 * first['share']:.1f}% | {first['events']} | " + " | ".join(cells) + " |")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("results", help="One folder per set and sample")
    parser.add_argument("--json", help="Also write the numbers here")
    args = parser.parse_args(argv)
    with open(os.path.join(HERE, "shares.json"), encoding="utf-8") as f:
        shares = json.load(f)["sets"]
    names = sorted(
        {os.path.basename(p)[: -len(".json")] for p in H.glob.glob(os.path.join(args.results, "*", "*.json"))}
        - {"base"}
    )
    results = {h: measure(H.load(args.results, h), shares) for h in names}
    report(results)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
