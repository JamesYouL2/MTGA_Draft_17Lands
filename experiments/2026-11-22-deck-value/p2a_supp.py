"""Supplementary Phase 2a numbers (not registered rules): the whole-game (D1)
version of Rules 2 and 3, S and O per set, and the pooled S and O without EOE.

    python p2a_supp.py reports/p2a_sets
"""
import glob
import json
import sys

import numpy as np

import p2a_report as R

S = [json.load(open(p)) for p in sorted(glob.glob(sys.argv[1] + "/p2a-*.json"))]
K = 12 / 23
E1 = {"C": (0.193, 0.035), "R": (0.196, 0.046), "K": (0.076, 0.048)}
SD = {"C": 2.69, "R": 2.40, "K": 2.41}
RBAR = 0.961


def pts(c, n):
    names = c["names"]
    i, q = names.index(n), names.index("Q")
    b, V = c["beta"], c["cov"]
    g = np.array([1 / b[q], -b[i] / b[q] ** 2])
    se = float(np.sqrt(g @ V[np.ix_([i, q], [i, q])] @ g))
    return b[i] / b[q] * K, se * K


def label(lo, hi):
    if hi < 0.5:
        return "mostly confound"
    if hi < 1:
        return "partly confound"
    if lo > 1:
        return "larger within deck"
    if lo <= 1 <= hi and (hi - lo) / 2 < 0.5:
        return "consistent"
    return "unclear"


print("D1 (whole game, seen-count dummies) against E1, points per card")
c = R.combine([s["models"]["D1"] for s in S])
for n in ("C", "R", "K"):
    p, se = pts(c, n)
    e, ese = E1[n]
    rho = p / e
    rse = abs(rho) * np.sqrt((se / p) ** 2 + (ese / e) ** 2)
    print(f"  {n}: {p:+.3f} ({se:.3f}), dis. {p * RBAR:+.3f}; per E1 SD {p * SD[n]:+.2f} / {p * RBAR * SD[n]:+.2f};"
          f" rho {rho:.2f} ({rse:.2f}) -> {label(rho - 2 * rse, rho + 2 * rse)}")
p, se = pts(c, "B5")
print(f"  B5: {p:+.3f} ({se:.3f}) points per card = premium {p / K:.2f} z units")

print("S and O per set (M1, points per card)")
for s in S:
    cs = R.combine([s["models"]["M1"]])
    print(f"  {s['set']}: S {pts(cs, 'S')[0]:+.3f} ({pts(cs, 'S')[1]:.3f})  O {pts(cs, 'O')[0]:+.3f} ({pts(cs, 'O')[1]:.3f})")
for drop in ([], ["EOE"]):
    for m in ("M1", "D1", "D0"):
        c = R.combine([s["models"][m] for s in S if s["set"] not in drop])
        print(f"  pooled {m}{' without EOE' if drop else ''}: S %+.3f (%.3f)" % pts(c, "S"), " O %+.3f (%.3f)" % pts(c, "O"))
