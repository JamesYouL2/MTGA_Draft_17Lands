"""The joint run's change in regret slope, with regret scaled within each set.

    python experiments/2026-11-16-proposed-together/within_set.py RESULTS --json within_set.json

heads.py divides regret by its spread over every draft in the run. That spread
includes the differences between sets' regret levels, so a head that moves regret in
a few sets changes the scale for all of them. This reads the same results three ways:

- pooled: heads.py's figure;
- scaled within set: each set's regret divided by that set's own spread, then pooled;
- mean of sets: each set's own change, averaged by its number of events.

Needs only NumPy.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-15-off-color-share"))
import by_set as B  # noqa: E402

H, C, R = B.H, B.C, B.R
SAMPLES = 200


def measure(data, shares):
    wins, ctrl, base, head, keys = C.regret_frame(data)
    names = sorted({k[0] for k in keys})
    codes = np.array([names.index(k[0]) for k in keys])
    high_sets = np.array([B.share_of(shares[s]) >= 0.3 for s in names])

    frame = (wins, ctrl, base, head, keys)
    pooled = lambda i: C.pooled_change(frame, i)
    within = lambda i: C.change(frame, i)

    def mean_of_sets(i):
        c = codes[i]
        total, weight = 0.0, 0
        for s in np.unique(c):
            j = i[c == s]
            total += len(j) * pooled(j)
            weight += len(j)
        return total / weight

    out = {}
    groups = {
        "all": np.arange(len(wins)),
        "four": np.flatnonzero(high_sets[codes]),
        "fifteen": np.flatnonzero(~high_sets[codes]),
    }
    for group, idx in groups.items():
        rng = np.random.default_rng(0)
        draws = [idx[rng.integers(0, len(idx), len(idx))] for _ in range(SAMPLES)]
        out[group] = {
            name: (float(fn(idx)), float(np.std([fn(d) for d in draws])))
            for name, fn in (("pooled", pooled), ("within", within), ("mean", mean_of_sets))
        }
    out["spread"] = {
        s: (float(base[codes == n].std()), float(head[codes == n].std()),
            float(base[codes == n].mean()), float(head[codes == n].mean()))
        for n, s in enumerate(names)
    }
    out["spread"]["all"] = (float(base.std()), float(head.std()), float(base.mean()), float(head.mean()))
    return out


def slim(draft):
    """A draft with its picks boiled down to their mean regret, to fit in memory."""
    picks = draft["picks"]
    keep = {k: v for k, v in draft.items() if k != "picks"}
    keep["picks"] = [[None, None, None, float(np.mean([p[3] for p in picks]))]] if picks else []
    return keep


def load_all(root):
    """{head: heads.py's load(root, head)}, reading one folder at a time."""
    out = {}
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        sample = os.path.basename(folder).rsplit("-", 1)[-1]
        base = H.read(os.path.join(folder, "base.json"))
        code = base["set"]
        mine = {d["id"]: slim(d) for d in base["drafts"]}
        del base
        for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
            head = os.path.basename(path)[:-5]
            if head == "base":
                continue
            for d in H.read(path)["drafts"]:
                if d["id"] in mine:
                    out.setdefault(head, {})[(code, f"{sample}:{d['id']}")] = {
                        "base": mine[d["id"]], "head": slim(d)}
    return {h: dict(sorted(v.items())) for h, v in sorted(out.items())}


def cell(pair):
    return f"{pair[0]:+.4f} ({pair[1]:.4f}), {pair[0] / pair[1]:+.1f} SEs" if pair[1] else f"{pair[0]:+.4f}"


def report(results):
    print("Regret slope change, head minus base: positive is worse for the head.\n")
    for group, title in (("all", "All sets"), ("four", "Sets over a 30% share"),
                         ("fifteen", "The other sets")):
        print(f"## {title}\n")
        print("| head | pooled (heads.py) | regret scaled within set | mean of sets |")
        print("|---|---|---|---|")
        for head, m in results.items():
            g = m[group]
            print(f"| {head} | {cell(g['pooled'])} | {cell(g['within'])} | {cell(g['mean'])} |")
        print()
    print("## Regret's spread, base to head\n")
    print("| head | over all drafts | " + " | ".join(
        s for s in next(iter(results.values()))["spread"] if s != "all") + " |")
    print("|---|" + "---|" * len(next(iter(results.values()))["spread"]))
    for head, m in results.items():
        sp = m["spread"]
        row = [f"{sp[s][0]:.2f} to {sp[s][1]:.2f}" for s in sp if s != "all"]
        print(f"| {head} | {sp['all'][0]:.2f} to {sp['all'][1]:.2f} | " + " | ".join(row) + " |")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("results")
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    with open(os.path.join(HERE, "..", "2026-11-15-off-color-share", "shares.json"), encoding="utf-8") as f:
        shares = json.load(f)["sets"]
    results = {h: measure(data, shares) for h, data in load_all(args.results).items()}
    report(results)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
