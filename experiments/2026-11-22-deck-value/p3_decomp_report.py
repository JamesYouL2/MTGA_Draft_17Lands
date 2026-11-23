"""Phase 3-lite decomposition report (P3DECOMP.md).

    python p3_decomp_report.py RESULTS [--eval EVAL] [--json out.json]

RESULTS holds p3_decomp.py's <head>.json files (any depth, merged over parts).
EVAL holds run 45187839933's p3-SET artifacts, for the reproduction check.
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p3_report import combine, fmt, load, TUNING_SETS  # noqa: E402

WEIGHTS = {"card_quality": 12.0, "two_colors": 3.1, "missing_fixing": -2.5, "missing_spells": -10.0}
TERMS = list(WEIGHTS) + ["residual"]
DESCRIBE = ["colors", "splash", "spells", "creatures", "removal", "cheap", "mana_value",
            "pool_quality", "pool_on_color", "pool_spells"]


def term_diffs(sets, head, main="main", only=None):
    """{term: {set: per-draft head − main points}}, the rating difference, and drop counts."""
    out = {t: {} for t in TERMS + ["rating"]}
    desc = {k: {} for k in DESCRIBE}
    kept = dropped = 0
    for code, labels in sorted(sets.items()):
        if only and code not in only or head not in labels or main not in labels:
            continue
        h, m = labels[head], labels[main]
        rows, drows = [], []
        for i in m:
            if i not in h or not h[i].get("sim") or not m[i].get("sim"):
                continue
            ph, pm = h[i]["sim"].get("parts"), m[i]["sim"].get("parts")
            if not ph or not pm:
                dropped += 1
                continue
            kept += 1
            pts = {t: w * (ph[t] - pm[t]) for t, w in WEIGHTS.items()}
            total = ph["rating"] - pm["rating"]
            pts["residual"] = total - sum(pts.values())
            pts["rating"] = total
            rows.append(pts)
            drows.append({k: (ph.get(k) if ph.get(k) is not None else np.nan)
                          - (pm.get(k) if pm.get(k) is not None else np.nan) for k in DESCRIBE})
        for t in out:
            out[t][code] = np.array([r[t] for r in rows])
        for k in desc:
            desc[k][code] = np.array([r[k] for r in drows], dtype=float)
    return out, desc, kept, dropped


def combine_nan(diffs):
    return combine({c: d[~np.isnan(d)] for c, d in diffs.items()})


def reproduction(sets, eval_sets):
    """Share of drafts whose simulated score matches the eval's to 4 places."""
    out = {}
    for head, ev in (("main", "base"), ("blend-1", "blend-1"), ("marginal", "marginal")):
        same = total = 0
        for code, labels in eval_sets.items():
            if head not in sets.get(code, {}) or ev not in labels:
                continue
            new, old = sets[code][head], labels[ev]
            for i, d in new.items():
                if i in old and d.get("sim") and old[i].get("sim"):
                    total += 1
                    same += round(d["sim"]["score"], 4) == round(old[i]["sim"]["score"], 4)
        out[head] = (same, total)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("results")
    ap.add_argument("--eval")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    sets, seconds = load(args.results)
    report = {"sets": sorted(sets), "heads": {}}
    print("# Phase 3-lite decomposition (P3DECOMP.md)\n")
    print(f"{len(sets)} sets. Job seconds per head: "
          + ", ".join(f"{h} {s / 3600:.1f} h" for h, s in sorted(seconds.items())) + "\n")

    if args.eval:
        eval_sets, _ = load(args.eval)
        rep = reproduction(sets, eval_sets)
        report["reproduction"] = rep
        print("## Reproduction check against run 45187839933\n")
        print("| head | drafts matching the eval's score | flag |\n|---|---|---|")
        for h, (same, total) in rep.items():
            share = same / total if total else float("nan")
            print(f"| {h} | {same} / {total} ({share:.1%}) | {'MISMATCH > 1%' if total and share < 0.99 else 'ok'} |")
        print()

    for head in ("blend-1", "marginal"):
        for label, only in (("19 sets", None), ("16 non-tuning sets", [s for s in sets if s not in TUNING_SETS])):
            diffs, desc, kept, dropped = term_diffs(sets, head, only=only)
            total = combine(diffs["rating"])
            rows = {t: combine(diffs[t]) for t in TERMS}
            q = rows["card_quality"][0] / total[0] if total[0] else float("nan")
            c = (rows["two_colors"][0] + rows["missing_fixing"][0]) / total[0] if total[0] else float("nan")
            if label == "19 sets":
                if q >= 0.75 and rows["card_quality"][0] >= 3 * rows["card_quality"][1]:
                    verdict = "quality-led"
                elif c >= 0.5:
                    verdict = "colors-led"
                else:
                    verdict = "mixed"
            entry = report["heads"].setdefault(head, {})
            entry[label] = {"rating": total, "terms": rows, "Q": q, "C": c, "kept": kept, "dropped": dropped,
                            "describe": {k: combine_nan(v) for k, v in desc.items()}}
            print(f"## {head} minus main, {label}\n")
            print(f"Drafts with parts for both: {kept}; dropped (a quick build, no parts): {dropped}.\n")
            print("| term | points (SE) | share of the score difference |\n|---|---|---|")
            print(f"| **score difference** | {fmt(*total)} | 100% |")
            for t in TERMS:
                m, se = rows[t]
                print(f"| {t} | {fmt(m, se)} | {m / total[0]:.0%} |")
            print(f"\nQ (card quality share) = {q:.0%}; C (two_colors + missing_fixing) = {c:.0%}.")
            if label == "19 sets":
                entry["verdict"] = verdict
                print(f"\n**Registered reading: {verdict}.**")
            print("\nDescriptive, head minus main:\n\n| fact | difference (SE) |\n|---|---|")
            for k, (m, se) in entry[label]["describe"].items():
                print(f"| {k} | {m:+.3f} ({se:.3f}) |")
            print()

        # Per set, 19 sets.
        diffs, *_ = term_diffs(sets, head)
        print(f"### {head}: per set (points)\n")
        print("| set | score | card quality | two colors | fixing | spells | residual |\n|---|---|---|---|---|---|---|")
        for code in sorted(diffs["rating"]):
            cells = [f"{diffs[t][code].mean():+.3f}" for t in ["rating"] + TERMS]
            print(f"| {code} | " + " | ".join(cells) + " |")
        print()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1, default=float)


if __name__ == "__main__":
    main()
