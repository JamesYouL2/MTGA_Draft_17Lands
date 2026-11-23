"""PROTOCOL.md's E3 report: the unconstrained swap a − b with played-deck controls.

    python experiments/2026-11-22-deck-value/e3.py e3-*.json.gz [--json e3.json]

Reads e3_join.py's files. For each head: event wins on a, b, c (diagnose.py
check 10a) plus report.controls, then with each block of deck controls (M1 to
M4), on the same matched complete events; and M0g/M4g with the deck's game win
share as the outcome (weighted by games). Each figure is per salt with
bootstrap SEs, combined over salts by heads.combined.
"""

import argparse
import gzip
import json
import os
import sys
from collections import Counter

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

C, R = H.C, H.R
HEADS = ("lgbm-strong-noalsa", "lgbm-weak", "gihwr-only")
M1 = ["score"]
M2 = ["card_quality", "two_colors", "missing_fixing", "missing_spells"]
M3 = M2 + ["q_top3", "q_top5", "q_low5", "q_max"]
M4 = M3 + ["creatures", "cheap", "removal", "main_colors", "splash", "mana_value", "curve_gaps", "lands"]
MODELS = [
    ("M0", "none", [], "wins"),
    ("M1", "(a) deck score", M1, "wins"),
    ("M2", "(b) deck score parts", M2, "wins"),
    ("M3", "(c) + quality shape", M3, "wins"),
    ("M4", "+ deck counts", M4, "wins"),
    ("M0g", "none; outcome game win share", [], "games"),
    ("M4g", "M4; outcome game win share", M4, "games"),
]


def load(paths):
    rows, sets = [], Counter()
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        for r in data["rows"]:
            r["set"] = data["set"]
            rows.append(r)
    return rows


def match_rates(rows):
    out = {}
    for r in rows:
        if not R.is_complete(r):
            continue
        s = out.setdefault(r["set"], [0, 0, 0])
        s[0] += 1
        s[1] += bool(r["builds"])
        s[2] += bool(r["deck"])
    return out


def fit_head(rows, head):
    keep = [
        r for r in rows
        if R.is_complete(r) and head in r["took"] and r["deck"] and r["deck_games"]
        and all(r["deck"].get(k) is not None for k in M4)
    ]
    keys = [(r["set"], f"{r['salt']}:{r['id']}") for r in keep]
    ctrl = R.controls(keep, [r["set"] for r in keep])
    took = np.array([r["took"][head] for r in keep], dtype=float)
    wins = np.array([r["wins"] for r in keep], dtype=float)
    share = np.array([r["deck_wins"] / r["deck_games"] for r in keep])
    weight = np.sqrt(np.array([r["deck_games"] for r in keep], dtype=float))
    deck = {k: np.array([r["deck"][k] for r in keep], dtype=float) for k in M4 + M1}
    out = {"events": len(keep), "mean_took": took.mean(axis=0).round(3).tolist()}
    for name, _, cols, outcome in MODELS:
        X = np.column_stack([took, ctrl] + [deck[k] for k in cols])
        y = wins if outcome == "wins" else share
        w = np.ones(len(y)) if outcome == "wins" else weight

        def fn(idx, X=X, y=y, w=w):
            beta = np.linalg.lstsq(X[idx] * w[idx, None], y[idx] * w[idx], rcond=None)[0]
            return beta[0] - beta[1]

        out[name] = H.combined(C.by_salt(keys, fn))
    return out


def cell(m):
    return f"{m['estimate']:+.4f} ({m['scaled_se']:.4f}) {m['estimate'] / m['scaled_se']:+.1f}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    rows = load(args.paths)

    rates = match_rates(rows)
    total = np.array(list(rates.values())).sum(axis=0)
    print("## E3: match rate\n")
    print(f"Complete events {total[0]}, with game rows {total[1]} ({total[1] / total[0]:.1%}), "
          f"scored {total[2]} ({total[2] / total[0]:.1%}).\n")
    print("| set | complete | matched | scored |\n|---|---|---|---|")
    for s, (n, m, k) in sorted(rates.items()):
        flag = " (under 80%)" if m / n < 0.8 else ""
        print(f"| {s} | {n} | {m / n:.1%}{flag} | {k / n:.1%} |")

    results = {"match": rates}
    for head in HEADS:
        res = fit_head(rows, head)
        results[head] = res
        print(f"\n## {head}: a − b, event wins per disagreement (estimate (scaled SE) SEs)\n")
        print(f"{res['events']} matched complete events; mean a, b, c per event: {res['mean_took']}\n")
        print("| model | controls | a − b | share of M0 |\n|---|---|---|---|")
        for name, label, _, outcome in MODELS:
            base = res["M0" if outcome == "wins" else "M0g"]["estimate"]
            share = res[name]["estimate"] / base if base else float("nan")
            print(f"| {name} | {label} | {cell(res[name])} | {share:.0%} |")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1, default=float)


if __name__ == "__main__":
    main()
