"""Compare each head of an Advisor heads run with the base, on held-out ratings.

    python experiments/2026-11-08-pick-multipliers/heads.py RESULTS --json heads.json

RESULTS holds one folder for each set and sample, with base.json and a JSON file
for each head, from replay.py. Each head's change in regret slope gets the verdict
in PROTOCOL.md. Reads compare.py's helpers, and needs only NumPy.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-heldout-replay"))
import compare as C  # noqa: E402

R = C.R
# No weight's change on held-out ratings: the size already known to be a real loss.
LOSS = 0.0063
SES = 2


def verdict(change, se):
    if change == 0 and se == 0:
        return "no change"
    if change >= SES * se:
        return "keep"
    if change + SES * se > LOSS:
        return "inconclusive"
    return "no objection"


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load(root, head):
    """{(set, "sample:draft id"): {"base": draft, "head": draft}}, for drafts in both."""
    out = {}
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        head_path = os.path.join(folder, f"{head}.json")
        if not os.path.exists(head_path):
            continue
        # heads-<set>-<salt>, and the salt's name is all that tells the samples apart.
        sample = os.path.basename(folder).rsplit("-", 1)[-1]
        base, other = read(os.path.join(folder, "base.json")), read(head_path)
        theirs = {d["id"]: d for d in other["drafts"]}
        for d in base["drafts"]:
            if d["id"] in theirs:
                out[(base["set"], f"{sample}:{d['id']}")] = {"base": d, "head": theirs[d["id"]]}
    return dict(sorted(out.items()))


def by_sample(frame):
    """The change in regret slope and its SE in each sample."""
    samples = {}
    for i, key in enumerate(frame[4]):
        samples.setdefault(key[1].split(":", 1)[0], []).append(i)
    return {
        name: (
            C.change(frame, np.array(idx)),
            R.bootstrap(lambda i, a=np.array(idx): C.change(frame, a[i]), len(idx)),
        )
        for name, idx in sorted(samples.items())
    }


def measure(data):
    frame = C.regret_frame(data)
    n = len(frame[0])
    every = np.arange(n)
    change = C.change(frame, every)
    se = R.bootstrap(lambda i: C.change(frame, i), n)
    total, changed, base_on, head_on, kinds = C.picks(data)
    swap, swap_se = C.disagreements(data)
    return {
        "drafts": len(data),
        "events": n,
        "change": change,
        "se": se,
        "verdict": verdict(change, se),
        "samples": {k: list(v) for k, v in by_sample(frame).items()},
        "top1": C.top1(data),
        "top_changes": 100 * changed / total,
        "on_lane_base": 100 * base_on / total,
        "on_lane_head": 100 * head_on / total,
        "swap": swap,
        "swap_se": swap_se,
        "kinds": {
            kind: {
                "share": 100 * k[0] / changed,
                "took_base": 100 * k[1] / k[0],
                "took_head": 100 * k[2] / k[0],
            }
            for kind in C.KINDS
            if (k := kinds[kind])[0]
        },
    }


def report(results):
    print("More positive is worse for the head. Verdicts follow PROTOCOL.md.\n")
    print("| head | regret slope change (SE) | SEs | verdict | top card changes | top-1 change "
          "| on-lane, base to head | event wins per swapped pick (SE) |")
    print("|---|---|---|---|---|---|---|---|")
    for head, m in results.items():
        print(
            f"| {head} | {m['change']:+.4f} ({m['se']:.4f}) | {m['change'] / m['se']:+.1f} "
            f"| {m['verdict']} | {m['top_changes']:.2f}% | {m['top1']:+.2f} "
            f"| {m['on_lane_base']:.1f}% to {m['on_lane_head']:.1f}% "
            f"| {m['swap']:+.3f} ({m['swap_se']:.3f}) |"
        )
    print("\n## By sample and kind of change\n")
    for head, m in results.items():
        samples = ", ".join(f"{k}: {v[0]:+.4f} ({v[1]:.4f})" for k, v in m["samples"].items())
        print(f"**{head}** ({m['drafts']} drafts, {m['events']} complete events). {samples}\n")
        for kind, k in m["kinds"].items():
            print(f"- {kind}: {k['share']:.1f}% of changes; drafters took base's "
                  f"{k['took_base']:.1f}%, head's {k['took_head']:.1f}%")
        print()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("results", help="One folder per set and sample")
    parser.add_argument("--json", help="Also write the numbers here")
    args = parser.parse_args(argv)
    heads = sorted(
        {
            os.path.basename(p)[: -len(".json")]
            for p in glob.glob(os.path.join(args.results, "*", "*.json"))
        }
        - {"base"}
    )
    results = {head: measure(load(args.results, head)) for head in heads}
    report(results)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
