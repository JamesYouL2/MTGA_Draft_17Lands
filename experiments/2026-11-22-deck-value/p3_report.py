"""Phase 3-lite report (PHASE3LITE.md).

    python p3_report.py RESULTS --tune [--json out.json]
    python p3_report.py RESULTS [--labels E4_LABELS --conf CONF] [--json out.json]

RESULTS holds p3-SET and p3tune-SET folders (any depth): JSON files in
replay.py's format, one per copy. In the eval, main is base.json. In tuning,
main is main.json. --labels (e4_hindsight.py shards) and --conf (the
confirmation run's heads-SET-r36s1 folders, for noalsa's tops) add the E4 view.
"""

import argparse
import glob
import gzip
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-heldout-replay"))
import compare as C  # noqa: E402

R = C.R
TUNING_SETS = ["BLB", "DSK", "OTJ"]


def load(root):
    """{set: {label: {draft id: draft}}} merged over shards, and seconds per label."""
    out, seconds = defaultdict(lambda: defaultdict(dict)), defaultdict(float)
    for path in sorted(glob.glob(os.path.join(root, "**", "*.json"), recursive=True)):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if "drafts" not in data or "label" not in data:
            continue
        for d in data["drafts"]:
            out[data["set"]][data["label"]][d["id"]] = d
        seconds[data["label"]] += data.get("seconds") or 0
    return out, seconds


def sim_diff(sets, head, main, only=None):
    """{set: per-draft head − main simulated deck win rate} for drafts both simulated."""
    out = {}
    for code, labels in sorted(sets.items()):
        if only and code not in only or head not in labels or main not in labels:
            continue
        h, m = labels[head], labels[main]
        out[code] = np.array([h[i]["sim"]["win"] - m[i]["sim"]["win"]
                              for i in m if i in h and h[i].get("sim") and m[i].get("sim")])
    return out


def combine(diffs):
    """Equal-weight mean of set means, SE = sqrt(sum SE^2) / sets."""
    means = [d.mean() for d in diffs.values() if len(d) > 1]
    ses = [d.std(ddof=1) / math.sqrt(len(d)) for d in diffs.values() if len(d) > 1]
    if not means:
        return float("nan"), float("nan")
    return float(np.mean(means)), float(math.sqrt(sum(s * s for s in ses)) / len(ses))


def fmt(m, se, d=3):
    z = m / se if se else 0.0
    return f"{m:+.{d}f} ({se:.{d}f}), {z:+.1f} SE"


def regret(sets, head, main="base"):
    data = {}
    for code, labels in sorted(sets.items()):
        if head not in labels:
            continue
        for i, d in labels[main].items():
            if i in labels[head]:
                data[(code, f"p3:{i}")] = {"base": d, "head": labels[head][i]}
    frame = C.regret_frame(data)
    n = len(frame[0])
    change = C.change(frame, np.arange(n))
    se = R.bootstrap(lambda i: C.change(frame, i), n)
    return float(change), float(se), n


def top_changes(sets, head, main="base"):
    """Share of picks where head's top differs from main's, overall and split."""
    count = defaultdict(lambda: [0, 0])
    for code, labels in sets.items():
        if head not in labels:
            continue
        for i, d in labels[main].items():
            if i not in labels[head]:
                continue
            q = {(p[0], p[1]): p for p in labels[head][i]["picks"]}
            for p in d["picks"]:
                if (p[0], p[1]) not in q:
                    continue
                changed = p[5] != q[(p[0], p[1])][5]
                lane = "no lane yet" if p[7] == 0 else ("main on-lane" if p[6] else "main off-lane")
                for g in ("all", f"P{p[0]}", lane):
                    count[g][0] += changed
                    count[g][1] += 1
    return {g: (c / n, n) for g, (c, n) in count.items()}


def e4_view(sets, labels_dir, conf_dir, heads):
    """{set: {chooser: (agree per draft, gap per draft)}} on drafts with labels."""
    labels = defaultdict(dict)
    for path in glob.glob(os.path.join(labels_dir, "**", "*.json.gz"), recursive=True):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        for d in data["drafts"]:
            if d["labels"]:
                labels[data["set"]][d["id"]] = d["labels"]
    out = {}
    for code in sorted(labels):
        if code not in sets:
            continue
        tops = {h: sets[code][lab] for h, lab in heads.items() if lab in sets[code]}
        if conf_dir:
            p = os.path.join(conf_dir, f"heads-{code}-r36s1", "lgbm-strong-noalsa.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    tops["noalsa"] = {d["id"]: d for d in json.load(f)["drafts"]}
        ids = [i for i in sets[code]["base"] if i in labels[code] and all(i in t for t in tops.values())]
        res = {h: ([], []) for h in list(tops) + ["drafter"]}
        for i in ids:
            pick_tops = {h: {(p[0], p[1]): p[5] for p in t[i]["picks"]} for h, t in tops.items()}
            agree, gap = defaultdict(float), defaultdict(float)
            n = 0
            for pack, pick, taken, lab in labels[code][i]:
                vals = {c: v[0] for c, v in lab.items()}
                choice = {h: pt.get((pack, pick)) for h, pt in pick_tops.items()}
                choice["drafter"] = taken
                if any(c not in vals for c in choice.values()):
                    continue
                best = max(vals.values())
                n += 1
                for h, c in choice.items():
                    agree[h] += vals[c] == best
                    gap[h] += vals[c] - best
            if not n:
                continue
            for h in res:
                res[h][0].append(agree[h] / n)
                res[h][1].append(gap[h])
        out[code] = {h: (np.array(a), np.array(g)) for h, (a, g) in res.items()}
    return out


def paired(x, y):
    d = x - y
    return float(d.mean()), float(d.std(ddof=1) / math.sqrt(len(d)))


def tune(sets, seconds, js):
    blends = sorted({lab for labels in sets.values() for lab in labels if lab.startswith("blend-")},
                    key=lambda s: float(s.split("-")[1]))
    print("## Phase 3-lite tuning: blend − main, simulated deck win rate (points)\n")
    print("| λ | " + " | ".join(sorted(sets)) + " | equal-weight mean |")
    print("|---|" + "---|" * (len(sets) + 1))
    res = {}
    for b in blends:
        diffs = sim_diff(sets, b, "main")
        m, se = combine(diffs)
        res[b] = {"mean": m, "se": se, "sets": {k: [float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v))), len(v)]
                                               for k, v in diffs.items()}}
        cells = [f"{v.mean():+.3f} ({v.std(ddof=1) / math.sqrt(len(v)):.3f})" for v in diffs.values()]
        print(f"| {b.split('-')[1]} | " + " | ".join(cells) + f" | {fmt(m, se)} |")
    best = max(blends, key=lambda b: (round(res[b]["mean"], 12), -float(b.split("-")[1])))
    print(f"\nλ* = {best.split('-')[1]} (highest mean; ties to the smaller λ). Drafts per set: "
          + ", ".join(f"{k} {len(next(iter(v.values())))}" for k, v in sorted(sets.items())))
    print(f"\nSeconds by copy: { {k: round(v) for k, v in seconds.items()} }")
    if js:
        with open(js, "w", encoding="utf-8") as f:
            json.dump({"blends": res, "lambda": best}, f, indent=1)


def evaluate(sets, seconds, args):
    heads = [h for h in ["marginal"] + sorted(
        {lab for labels in sets.values() for lab in labels if lab.startswith("blend-")}) + ["gihwr-only"]
        if any(h in labels for labels in sets.values())]
    out = {"sets": sorted(sets), "heads": {}}
    print("## Phase 3-lite: head − main (registered in PHASE3LITE.md)\n")
    print(f"Sets: {len(sets)}. Primary: simulated deck win rate, head − main, win-rate points; "
          "equal-weight mean of set means, SE √ΣSE²/sets. Rank regret: compare.change "
          "(positive is worse), bootstrap SE.\n")
    print("| head | primary, all sets | primary, non-tuning sets | rank regret change | top cards changed |")
    print("|---|---|---|---|---|")
    for h in heads:
        diffs = sim_diff(sets, h, "base")
        m, se = combine(diffs)
        m16, se16 = combine({k: v for k, v in diffs.items() if k not in TUNING_SETS})
        rc, rse, n = regret(sets, h)
        tc = top_changes(sets, h)
        out["heads"][h] = {
            "primary": [m, se], "primary_16": [m16, se16], "regret": [rc, rse, n],
            "drafts": int(sum(len(v) for v in diffs.values())),
            "sets": {k: [float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v))), len(v)] for k, v in diffs.items()},
            "top_changes": tc,
        }
        print(f"| {h} | {fmt(m, se)} | {fmt(m16, se16)} | {fmt(rc, rse, 4)} | {tc['all'][0]:.1%} |")
    print()
    for h in heads:
        if h == "gihwr-only":
            continue
        p, r = out["heads"][h]["primary"], out["heads"][h]["regret"]
        out["heads"][h]["promising"] = bool(p[0] >= 3 * p[1] and r[0] < 3 * r[1])
        out["heads"][h]["within2"] = bool(abs(p[0]) < 2 * p[1])
    cand = [h for h in heads if h != "gihwr-only"]
    if any(out["heads"][h]["promising"] for h in cand):
        verdict = "promising"
    elif all(out["heads"][h]["within2"] for h in cand):
        verdict = "no headroom"
    else:
        verdict = "mixed"
    out["verdict"] = verdict
    print(f"**Verdict: {verdict}** (" + "; ".join(
        f"{h}: promising {out['heads'][h]['promising']}, within ±2 SE {out['heads'][h]['within2']}" for h in cand) + ")\n")

    print("### Per set: head − main simulated deck win rate (points, SE)\n")
    print("| set | drafts | " + " | ".join(heads) + " |")
    print("|---|---|" + "---|" * len(heads))
    for code in sorted(sets):
        row = []
        n = 0
        for h in heads:
            v = out["heads"][h]["sets"].get(code)
            row.append(f"{v[0]:+.2f} ({v[1]:.2f})" if v else "–")
            n = v[2] if v else n
        print(f"| {code}{' (tuning)' if code in TUNING_SETS else ''} | {n} | " + " | ".join(row) + " |")
    print()

    print("### Share of top cards changed vs main (drafter's pool path)\n")
    groups = ["all", "P1", "P2", "P3", "no lane yet", "main on-lane", "main off-lane"]
    print("| group | picks | " + " | ".join(heads) + " |")
    print("|---|---|" + "---|" * len(heads))
    for g in groups:
        n = next((out["heads"][h]["top_changes"].get(g, (0, 0))[1] for h in heads), 0)
        print(f"| {g} | {n} | " + " | ".join(
            f"{out['heads'][h]['top_changes'].get(g, (0, 0))[0]:.1%}" for h in heads) + " |")
    print()

    base_sim = [d["sim"]["win"] for labels in sets.values() for d in labels["base"].values() if d.get("sim")]
    print(f"main's mean simulated deck win rate: {np.mean(base_sim):.2f}% over {len(base_sim)} drafts.\n")

    if args.labels:
        names = {"main": "base", **{h: h for h in heads}}
        view = e4_view(sets, args.labels, args.conf, names)
        out["e4"] = {}
        print("### E4 view (second view, circular): agreement with the hindsight-best card\n")
        print("Per draft: share of labelled picks whose top card has the pack's best label, and the summed "
              "label gap (log-odds). Paired against main per draft; SE clustered by draft.\n")
        for code, res in view.items():
            n = len(res["main"][0])
            print(f"#### {code} ({n} drafts)\n")
            print("| chooser | agreement | − main | label gap per draft | − main |")
            print("|---|---|---|---|---|")
            out["e4"][code] = {}
            for h, (a, g) in res.items():
                da, dg = paired(a, res["main"][0]), paired(g, res["main"][1])
                out["e4"][code][h] = {"agree": float(a.mean()), "agree_vs_main": da,
                                      "gap": float(g.mean()), "gap_vs_main": dg}
                print(f"| {h} | {a.mean():.1%} | {fmt(da[0] * 100, da[1] * 100, 2)} pp | "
                      f"{g.mean():+.4f} | {fmt(*dg, 4)} |")
            print()
    hours = sum(seconds.values()) / 3600
    print(f"Replay seconds by copy: { {k: round(v) for k, v in seconds.items()} } ({hours:.1f} h of replay)\n")
    out["seconds"] = dict(seconds)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("results")
    ap.add_argument("--tune", action="store_true")
    ap.add_argument("--labels")
    ap.add_argument("--conf")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    sets, seconds = load(args.results)
    if args.tune:
        tune(sets, seconds, args.json)
    else:
        evaluate(sets, seconds, args)


if __name__ == "__main__":
    main()
