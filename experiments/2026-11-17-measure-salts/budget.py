"""How to split a fixed budget of job time between salts and drafts per salt.

    python experiments/2026-11-17-measure-salts/budget.py --phi 2.0 --share 1.0 \
        --fixed 2.5 --per-1000 3.5 [--budget 4x3000]

Per job (one set and salt) of n drafts, the estimate's variance is
    b2(n0) * (n0 / n) * (1 + r0 * (n / n0)^2 + u0)
where b2 is the bootstrap's variance (it falls as 1 / n), r0 = share * (phi^2 - 1)
is the ratings' variance over the bootstrap's at n0 = 3000 (it grows with n, as
holding out more drafts moves the ratings more), and u0 = (1 - share) *
(phi^2 - 1) is the rest of the excess, taken to fall as 1 / n like sampling. A
job costs fixed + per-1000 * n / 1000 minutes; a budget buys k = budget / cost
salts. The figure of merit is the scaled SE, sqrt(variance / k) * t(k - 1) / 1.96,
relative to the budget's own split.
"""

import argparse

import numpy as np
from scipy import stats

N0 = 3000


def scaled_se(n, k, phi, share):
    excess = phi**2 - 1
    r0, u0 = share * excess, (1 - share) * excess
    var = (N0 / n) * (1 + r0 * (n / N0) ** 2 + u0) / k
    return np.sqrt(var) * stats.t.ppf(0.975, k - 1) / 1.96


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--phi", type=float, required=True, help="Set-level inflation at 3000")
    p.add_argument("--share", type=float, required=True, help="Excess from the ratings")
    p.add_argument("--fixed", type=float, required=True, help="Minutes per job, fixed")
    p.add_argument("--per-1000", type=float, required=True, help="Minutes per 1000 drafts")
    p.add_argument("--budget", default="4x3000", help="SALTSxDRAFTS whose cost is the budget")
    a = p.parse_args(argv)
    k0, n0 = (int(x) for x in a.budget.split("x"))
    cost = lambda n: a.fixed + a.per_1000 * n / 1000
    budget = k0 * cost(n0)
    ref = scaled_se(n0, k0, a.phi, a.share)
    print(f"phi {a.phi}, share {a.share}; budget {budget:.0f} job-minutes a set "
          f"({a.budget}). Scaled SE relative to {a.budget}:\n")
    print("| drafts per salt | salts | scaled SE |")
    print("|---|---|---|")
    for n in (500, 750, 1000, 1500, 2000, 3000, 4500, 6000):
        k = budget / cost(n)
        if k < 2:
            continue
        kk = int(round(k))
        print(f"| {n} | {k:.1f} | {scaled_se(n, kk, a.phi, a.share) / ref:.2f} |")


if __name__ == "__main__":
    main()
