"""PROTOCOL.md's E4 pilot report: cost, hindsight-best agreement, label
distribution and build flips.

    python experiments/2026-11-22-deck-value/e4_report.py --labels e4/ \
        --replays conf weak [--json e4.json]

--labels holds e4_hindsight.py's shards (any depth). --replays folders hold
heads-SET-r36s1 folders with replay.py results; each copy's top card at a pick
(p[5]) is compared with the pick's hindsight-best cards. Circular: the labels
are the app's own deck score.
"""

import argparse
import glob
import gzip
import json
import os
import statistics
from collections import defaultdict

COPIES = {"base": "main", "gihwr-only": "gihwr-only", "lgbm-strong-noalsa": "noalsa", "lgbm-weak": "lgbm-weak"}
FULL = 19 * 3000


def tops(roots, code):
    """{copy: {(draft id, pack, pick): top card}} for the set's r36s1 replays."""
    out = defaultdict(dict)
    for root in roots:
        folder = os.path.join(root, f"heads-{code}-r36s1")
        for path in glob.glob(os.path.join(folder, "*.json")):
            name = os.path.basename(path)[:-5]
            if name not in COPIES or (name == "base" and out["base"]):
                continue
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for d in data["drafts"]:
                for p in d["picks"]:
                    out[name][(d["id"], p[0], p[1])] = p[5]
    return out


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else float("nan")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--labels", required=True)
    parser.add_argument("--replays", nargs="+", required=True)
    parser.add_argument("--json")
    args = parser.parse_args(argv)

    shards = defaultdict(list)
    for path in glob.glob(os.path.join(args.labels, "**", "*.json.gz"), recursive=True):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        shards[data["set"]].append(data)

    res, all_secs = {}, []
    print("## E4 pilot: hindsight value labels (circular: V is the app's deck score)\n")
    for code in sorted(shards):
        secs = [s for sh in shards[code] for s in sh["seconds"]]
        all_secs += secs
        drafts = [d for sh in shards[code] for d in sh["drafts"]]
        top = tops(args.replays, code)
        n = best_tie = best_strict = all_zero = informative = 0
        agree = {c: [0, 0, 0, 0] for c in COPIES}  # [best of matched, matched, best of informative, informative]
        by_pack = defaultdict(list)
        zero_by_pack = defaultdict(lambda: [0, 0])
        flips = [0, 0]
        for d in drafts:
            for pack, pick, taken, labels in d["labels"] or []:
                vals = {c: v[0] for c, v in labels.items()}
                hi, lo = max(vals.values()), min(vals.values())
                n += 1
                best_tie += vals[taken] >= hi
                best_strict += vals[taken] >= hi and sum(v == hi for v in vals.values()) == 1
                all_zero += hi == 0 and lo == 0
                inform = hi > lo
                informative += inform
                for c, v in labels.items():
                    if c == taken:
                        continue
                    by_pack[pack].append(v[0])
                    zero_by_pack[pack][0] += v[0] == 0
                    zero_by_pack[pack][1] += 1
                    flips[0] += v[1]
                    flips[1] += 1
                for c in COPIES:
                    t = top[c].get((d["id"], pack, pick))
                    if t is None or t not in vals:
                        continue
                    ok = vals[t] >= hi
                    agree[c][0] += ok
                    agree[c][1] += 1
                    if inform:
                        agree[c][2] += ok
                        agree[c][3] += 1
        mean_s = statistics.mean(secs) if secs else float("nan")
        res[code] = dict(
            drafts=len(drafts), seconds_mean=mean_s, seconds_median=statistics.median(secs) if secs else None,
            picks=n, drafter_best_ties=best_tie / n, drafter_best_strict=best_strict / n,
            all_zero=all_zero / n, informative=informative / n,
            agree={COPIES[c]: dict(any=a[0] / max(1, a[1]), picks=a[1], informative=a[2] / max(1, a[3]),
                                   informative_picks=a[3]) for c, a in agree.items()},
            by_pack={p: dict(mean=statistics.mean(v), p10=pct(v, 0.1), p50=pct(v, 0.5), p90=pct(v, 0.9),
                             zero=zero_by_pack[p][0] / zero_by_pack[p][1]) for p, v in sorted(by_pack.items())},
            flips=flips[0] / max(1, flips[1]),
        )
        r = res[code]
        print(f"### {code}: {r['drafts']} drafts, {n} picks\n")
        print(f"- Cost: {mean_s:.1f} s per draft (median {r['seconds_median']:.1f}).")
        print(f"- Drafter's card hindsight-best: {r['drafter_best_ties']:.1%} counting ties, "
              f"{r['drafter_best_strict']:.1%} strictly. Every label 0: {r['all_zero']:.1%}; "
              f"labels differ: {r['informative']:.1%}.")
        print(f"- Build flips: {r['flips']:.1%} of labelled non-taken cards change the best build's colors.\n")
        print("| copy | top card hindsight-best (all picks) | picks | on picks where labels differ | picks |")
        print("|---|---|---|---|---|")
        for c, a in r["agree"].items():
            print(f"| {c} | {a['any']:.1%} | {a['picks']} | {a['informative']:.1%} | {a['informative_picks']} |")
        print("\n| pack | mean label (log-odds) | p10 | median | p90 | share exactly 0 |\n|---|---|---|---|---|---|")
        for p, s in r["by_pack"].items():
            print(f"| {p} | {s['mean']:+.4f} | {s['p10']:+.4f} | {s['p50']:+.4f} | {s['p90']:+.4f} | {s['zero']:.1%} |")
        print()
    if all_secs:
        m = statistics.mean(all_secs)
        hours = FULL * m / 3600
        res["projection"] = dict(seconds_per_draft=m, job_hours=hours, wall_hours_20=hours / 20)
        print(f"Projected for 19 sets × 3000 drafts at {m:.1f} s per draft: {hours:.0f} job-hours, "
              f"{hours / 20:.1f} h wall-clock at 20 concurrent jobs "
              f"({'within' if hours <= 480 else 'over'} the 480 job-hour bar).")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
