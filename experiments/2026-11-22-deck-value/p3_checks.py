"""Post hoc checks on Phase 3-lite's regret guard (after the results; no rule).

    python p3_checks.py EVAL DATASETS

EVAL holds run 45187839933's p3-SET artifacts; DATASETS holds SET.json.gz, the
app's datasets, for card types only.

PHASE3LITE.md calls its guard "rank regret" but computes compare.change, which
reads SD regret (pick field 3: the gap to the top card in SDs of the pack's
scores). That measure penalizes a head that spaces its scores differently, and
the blend changes the spacing by construction. This reads the guard three ways
(SD regret, rank regret = field 2, missed top = field 2 > 0), with the old and
the fixed skill bins, on all picks and on subsets of picks:
- no land: picks where neither main's nor the head's top card is a land;
- by pack.
The subset keeps the same picks for main and the head.
"""

import gzip
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p3_report import load  # noqa: E402
import report as R  # noqa: E402  (Tools/AdvisorReplay, via p3_report's compare)

FIELDS = {"SD regret": lambda p: p[3], "rank regret": lambda p: p[2], "missed top": lambda p: float(p[2] > 0)}


def skill_bin(s, fixed):
    if s is None:
        return None
    if fixed:
        return (round(min(max(s, 0.30), 0.74) * 100) - 30) // 4
    return int((min(max(s, 0.30), 0.74) - 0.30) // 0.04)


def controls(drafts, sets, fixed):
    dummies = R._dummies
    skill = [skill_bin(d["skill"], fixed) for d in drafts]
    cols = dummies(sets) + dummies(skill) + dummies([d["games"] for d in drafts])
    return np.column_stack([np.ones(len(drafts)), *cols])


def within_set_z(x, codes, n):
    out = np.zeros(len(x))
    for c in range(n):
        m = codes == c
        v = x[m]
        out[m] = (v - v.mean()) / (v.std() or 1.0)
    return out


def frame(sets, head, lands, keep=lambda p, q, code: True, fixed=True, base="base"):
    """wins, controls, set codes, {field: (base per draft, head per draft)}."""
    rows, codes, names = [], [], sorted(sets)
    for code in names:
        lab = sets[code]
        if head not in lab:
            continue
        for i, b in lab[base].items():
            h = lab[head].get(i)
            if h is None or not R.is_complete(b) or not b["picks"] or not h["picks"]:
                continue
            hp = {(p[0], p[1]): p for p in h["picks"]}
            pairs = [(p, hp[(p[0], p[1])]) for p in b["picks"] if (p[0], p[1]) in hp]
            pairs = [(p, q) for p, q in pairs if keep(p, q, code)]
            if not pairs:
                continue
            rows.append((b, pairs))
            codes.append(names.index(code))
    drafts = [b for b, _ in rows]
    wins = np.array([d["wins"] for d in drafts], dtype=float)
    ctrl = controls(drafts, [names[c] for c in codes], fixed)
    vals = {f: (np.array([np.mean([g(p) for p, _ in pr]) for _, pr in rows]),
                np.array([np.mean([g(q) for _, q in pr]) for _, pr in rows])) for f, g in FIELDS.items()}
    return wins, ctrl, np.array(codes), len(names), vals, sum(len(pr) for _, pr in rows)


def change(wins, ctrl, codes, n, base, head, idx):
    c = codes[idx]
    slope = lambda x: R.wins_slope(within_set_z(x[idx], c, n), wins[idx], ctrl[idx])
    return slope(head) - slope(base)


def read(sets, head, lands, keep, fixed=True, samples=500, base="base"):
    wins, ctrl, codes, n, vals, picks = frame(sets, head, lands, keep, fixed, base)
    out = {}
    for f, (b, h) in vals.items():
        fn = lambda idx: change(wins, ctrl, codes, n, b, h, idx)
        m = fn(np.arange(len(wins)))
        se = R.bootstrap(fn, len(wins), samples=samples)
        out[f] = (m, se)
    return out, len(wins), picks


def main():
    eval_dir, data_dir = sys.argv[1], sys.argv[2]
    sets, _ = load(eval_dir)
    lands = {}
    for code in sets:
        with gzip.open(os.path.join(data_dir, f"{code}.json.gz"), "rt", encoding="utf-8") as f:
            cr = json.load(f)["card_ratings"]
        lands[code] = {c["name"] for c in cr.values() if "Land" in (c.get("types") or [])}

    is_land = lambda name, code: name in lands[code]
    subsets = {
        "all picks": lambda p, q, code: True,
        "no land top (either)": lambda p, q, code: not is_land(p[5], code) and not is_land(q[5], code),
        "pack 1": lambda p, q, code: p[0] == 1,
        "pack 2": lambda p, q, code: p[0] == 2,
        "pack 3": lambda p, q, code: p[0] == 3,
    }
    print("# Post hoc: the Phase 3-lite regret guard read three ways\n")
    print("Change in Δevent wins per +1 SD (within set), head minus main; positive is worse. "
          "Draft-bootstrap SE (500 samples).\n")
    for head in ("blend-1", "marginal", "gihwr-only"):
        # Top changes involving lands.
        cnt = Counter()
        for code, lab in sets.items():
            if head not in lab:
                continue
            for i, b in lab["base"].items():
                h = lab[head].get(i)
                if not h:
                    continue
                hp = {(p[0], p[1]): p for p in h["picks"]}
                for p in b["picks"]:
                    q = hp.get((p[0], p[1]))
                    if q is None:
                        continue
                    cnt["picks"] += 1
                    if p[5] != q[5]:
                        cnt["changed"] += 1
                        cnt["changed, main's top a land"] += is_land(p[5], code)
                        cnt["changed, head's top a land"] += is_land(q[5], code)
                    cnt["main's top a land"] += is_land(p[5], code)
                    cnt["head's top a land"] += is_land(q[5], code)
        print(f"## {head}\n")
        print(f"Top cards changed: {cnt['changed']} of {cnt['picks']} picks "
              f"({cnt['changed'] / cnt['picks']:.1%}). Of the changes, main's top was a land in "
              f"{cnt['changed, main' + chr(39) + 's top a land'] / max(1, cnt['changed']):.1%} and the head's in "
              f"{cnt['changed, head' + chr(39) + 's top a land'] / max(1, cnt['changed']):.1%}. "
              f"Main tops a land on {cnt['main' + chr(39) + 's top a land'] / cnt['picks']:.2%} of picks, "
              f"the head on {cnt['head' + chr(39) + 's top a land'] / cnt['picks']:.2%}.\n")
        print("| picks | skill bins | events | picks read | SD regret (guard as computed) | rank regret | missed top |")
        print("|---|---|---|---|---|---|---|")
        for name, keep in subsets.items():
            for fixed in ((False, True) if name == "all picks" else (True,)):
                res, n, picks = read(sets, head, lands, keep, fixed)
                cells = [f"{m:+.4f} ({se:.4f}), {m / se:+.1f}" for m, se in res.values()]
                print(f"| {name} | {'fixed' if fixed else 'old'} | {n} | {picks} | " + " | ".join(cells) + " |")
        print()


if __name__ == "__main__":
    main()
