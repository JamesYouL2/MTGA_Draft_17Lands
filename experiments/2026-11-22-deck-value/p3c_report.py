"""Phase 3-lite confirmation report (P3CONFIRM.md).

    python p3c_report.py RESULTS [--json out.json]

RESULTS holds p3_decomp.py's main.json, blend-1.json and gihwr-only.json per set
(any depth, merged over parts), run with --replay and --judge.
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p3_report import combine, fmt, load, TUNING_SETS  # noqa: E402
from p3_decomp_report import DESCRIBE  # noqa: E402
import p3_checks  # noqa: E402

MAIN = "main"
W = 12.0  # deck_scorer.WEIGHTS["card_quality"]


def paired(sets, head, get):
    """{set: per-draft get(head) − get(main)} where both have a value."""
    out = {}
    for code, lab in sorted(sets.items()):
        if head not in lab or MAIN not in lab:
            continue
        vals = []
        for i, m in lab[MAIN].items():
            h = lab[head].get(i)
            if not h or not h.get("sim") or not m.get("sim"):
                continue
            a, b = get(h), get(m)
            if a is None or b is None:
                continue
            vals.append(a - b)
        out[code] = np.array(vals, dtype=float)
    return out


def parts(key):
    return lambda d: (d["sim"].get("parts") or {}).get(key)


def judged(key, scale=1.0):
    """parts[key] × scale, only on drafts the judge graded (same drafts on A and B)."""
    def get(d):
        p = d["sim"].get("parts") or {}
        return None if p.get("judge_win") is None or p.get(key) is None else scale * p[key]
    return get


def win_where_judged(d):
    p = d["sim"].get("parts") or {}
    return None if p.get("judge_win") is None else d["sim"]["win"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("results")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    sets, seconds = load(args.results)

    rep = {"sets": sorted(sets), "heads": {}}
    print("# Phase 3-lite confirmation (P3CONFIRM.md)\n")
    print(f"{len(sets)} sets. Process hours: "
          + ", ".join(f"{h} {s / 3600:.1f}" for h, s in sorted(seconds.items())) + "\n")
    non_tuning = [s for s in sets if s not in TUNING_SETS]

    for head in ("blend-1", "gihwr-only"):
        e = rep["heads"][head] = {}
        judged_b = paired(sets, head, parts("judge_win"))
        judged_a = paired(sets, head, lambda d: d["sim"]["win"])
        e["primary_B"] = combine(judged_b)
        e["A_on_all"] = combine(judged_a)
        a_same = paired(sets, head, win_where_judged)
        e["A_same_drafts"] = combine(a_same)
        e["primary_B_16"] = combine({c: v for c, v in judged_b.items() if c in non_tuning})
        n_b = sum(len(v) for v in judged_b.values())
        n_all = sum(len(v) for v in judged_a.values())
        q_b = combine(paired(sets, head, judged("judge_quality", W)))
        q_a = combine(paired(sets, head, judged("card_quality", W)))
        r_b = combine(paired(sets, head, judged("judge_rating")))
        r_a = combine(paired(sets, head, judged("rating")))
        e.update(quality_B=q_b, quality_A=q_a, rating_B=r_b, rating_A=r_a)

        print(f"## {head} minus main\n")
        print(f"Drafts simulated by both: {n_all}; with a judge grade for both: {n_b} "
              "(the rest fell back to the quick build).\n")
        print("| reading | win-rate points (SE) |\n|---|---|")
        print(f"| **primary: judged on half B, 19 sets** | **{fmt(*e['primary_B'])}** |")
        print(f"| judged on half B, 16 non-tuning sets | {fmt(*e['primary_B_16'])} |")
        print(f"| judged on half A (the advisor's own ratings), same drafts | {fmt(*e['A_same_drafts'])} |")
        print(f"| judged on half A, all drafts | {fmt(*e['A_on_all'])} |")
        share = e["primary_B"][0] / e["A_same_drafts"][0] if e["A_same_drafts"][0] else float("nan")
        e["share_B_of_A"] = share
        print(f"\nShare of the half-A gain that survives on half B: {share:.0%}.\n")
        print("| deck score, points | half A | half B |\n|---|---|---|")
        print(f"| score difference | {fmt(*r_a)} | {fmt(*r_b)} |")
        print(f"| card quality term | {fmt(*q_a)} | {fmt(*q_b)} |")
        print()

        # Regret, order-only guard.
        print("| regret measure (positive is worse) | change (SE), z |\n|---|---|")
        res, n, picks = p3_checks.read(sets, head, {}, lambda p, q, code: True, True, base=MAIN)
        e["regret"] = {k: v for k, v in res.items()}
        for k, label in (("rank regret", "**rank regret (guard)**"), ("missed top", "missed top"),
                         ("SD regret", "SD regret (the old guard's measure)")):
            m, se = res[k]
            print(f"| {label} | {m:+.4f} ({se:.4f}), {m / se:+.1f} |")
        print(f"\n{n} complete events, {picks} picks.\n")
        desc = {k: combine({c: v[~np.isnan(v)] for c, v in paired(sets, head, parts(k)).items()}) for k in DESCRIBE}
        e["describe"] = desc
        print("| deck fact | head minus main (SE) |\n|---|---|")
        for k, (m, se) in desc.items():
            print(f"| {k} | {m:+.3f} ({se:.3f}) |")
        print()

    b = rep["heads"]["blend-1"]
    p_m, p_se = b["primary_B"]
    g_m, g_se = b["regret"]["rank regret"]
    if p_m < 2 * p_se:
        verdict = "not confirmed"
    elif p_m >= 3 * p_se and g_m < 3 * g_se:
        verdict = "confirmed"
    else:
        verdict = "mixed"
    rep["verdict"] = verdict
    print(f"## Decision\n\nPrimary {fmt(p_m, p_se)}; rank regret {g_m:+.4f} ({g_se:.4f}), {g_m / g_se:+.1f} SE.\n")
    print(f"**Registered reading: {verdict}.**\n")
    gm, gse = rep["heads"]["gihwr-only"]["regret"]["rank regret"]
    if gm < 2 * gse:
        print(f"Power note: gihwr-only reads {gm / gse:+.1f} SEs on rank regret, under +2, so the guard "
              "had too little power here to see a known-worse head.\n")
    else:
        print(f"Power check: gihwr-only reads {gm / gse:+.1f} SEs worse on rank regret.\n")

    # Per set, primary.
    jb = paired(sets, "blend-1", parts("judge_win"))
    ja = paired(sets, "blend-1", win_where_judged)
    print("### blend-1 per set (win-rate points)\n\n| set | half B | half A | drafts |\n|---|---|---|---|")
    for c in sorted(jb):
        print(f"| {c} | {jb[c].mean():+.3f} | {ja[c].mean():+.3f} | {len(jb[c])} |")
    print()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1, default=float)


if __name__ == "__main__":
    main()
