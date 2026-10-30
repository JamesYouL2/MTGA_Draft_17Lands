"""Throwaway: does a set-level "three-color set" flag earn a weight on off_pips?

    python Tools/PickFit/flags.py --flags Tools/PickFit/flags.json results/*.json.gz

For each candidate flag (a number per set), adds off_pips x flag to the app's
features and compares it with the app's features alone, each set scored by
weights fitted on the other sets.
"""

import argparse
import gzip
import json
import sys

import numpy as np
from fit import Data, fit_logit, softmax, top_k


def load(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def held_out_ll(u, te):
    return float(np.mean(u[te.chosen] - softmax(u, te)[1]))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--flags", required=True)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args(argv)

    with open(args.flags, encoding="utf-8") as f:
        flags = json.load(f)
    data = Data(load(p) for p in args.files)
    names = flags["names"]
    per_set = flags["sets"]
    sets = [s for s in data.sets if s in per_set]
    missing = [s for s in data.sets if s not in per_set]
    if missing:
        data = data.subset(np.isin(data.set, sets))
    off = data.names.index("off_pips")
    row_set = np.repeat(data.set, data.sizes)

    def X_for(flag):
        if flag is None:
            return data.X
        f = np.array([per_set[s][flag] for s in row_set])
        return np.column_stack([data.X, data.X[:, off] * f])

    out = []
    p = out.append
    p(f"{len(data.sizes):,} picks by strong drafters, {len(sets)} sets.")
    if missing:
        p(f"Left out for having no flags: {', '.join(missing)}.")
    p("")
    p("## The flags")
    p("")
    for k, desc in flags["descriptions"].items():
        p(f"- **{k}**: {desc}")
    p("")

    # Each set alone: its own off_pips weight, in points.
    p("## Each set's own off_pips weight (fitted on that set alone)")
    p("")
    p("| set | off_pips (points) | " + " | ".join(names) + " |")
    p("|---|---|" + "---|" * len(names))
    own = {}
    for s in sets:
        d = data.subset(data.set == s)
        beta, _ = fit_logit(d.X, d)
        own[s] = 15.0 * beta[off] / beta[data.q]
        p(
            f"| {s} | {own[s]:+.1f} | "
            + " | ".join(f"{per_set[s][k]:.2f}" for k in names)
            + " |"
        )
    p("")
    w = np.array([own[s] for s in sets])
    for k in names:
        f = np.array([per_set[s][k] for s in sets])
        no_tdm = np.array([s != "TDM" for s in sets])
        r = np.corrcoef(f, w)[0, 1]
        r2 = np.corrcoef(f[no_tdm], w[no_tdm])[0, 1]
        p(
            f"- Correlation of {k} with sets' own off_pips weight: {r:+.2f} "
            f"({r2:+.2f} without TDM)."
        )
    p("")

    # Leave one set out.
    models = [None] + names
    label = {None: "app features"} | {k: f"+ off_pips x {k}" for k in names}
    ll = {m: {} for m in models}
    t1 = {m: {} for m in models}
    eff = {m: {} for m in models}
    full = {}
    for m in models:
        X = X_for(m)
        full[m] = fit_logit(X, data)
        for s in sets:
            test = data.set == s
            tr, te = data.subset(~test), data.subset(test)
            rows_te = np.repeat(test, data.sizes)
            beta, _ = fit_logit(X[~rows_te], tr)
            u = X[rows_te] @ beta
            ll[m][s] = held_out_ll(u, te)
            t1[m][s] = 100 * top_k(u, te, 1).mean()
            e = beta[off] + (beta[-1] * per_set[s][m] if m else 0.0)
            eff[m][s] = 15.0 * e / beta[data.q]
        del X
        print(f"done {label[m]}", file=sys.stderr, flush=True)

    n = {s: int((data.set == s).sum()) for s in sets}

    def pooled(d, keep):
        tot = sum(n[s] for s in keep)
        return sum(d[s] * n[s] for s in keep) / tot

    p("## Weights fitted on all sets")
    p("")
    p("Log-odds per unit; the interaction is per off-color pip per unit of flag.")
    p("")
    p("| model | off_pips | off_pips x flag (SE) | flag's effect at TDM's value |")
    p("|---|---|---|---|")
    for m in models:
        beta, cov = full[m]
        if m is None:
            p(f"| {label[m]} | {beta[off]:+.3f} | - | - |")
            continue
        se = float(np.sqrt(cov[-1, -1]))
        p(
            f"| {label[m]} | {beta[off]:+.3f} | {beta[-1]:+.3f} ({se:.3f}) | "
            f"{beta[-1] * per_set['TDM'][m]:+.3f} |"
        )
    p("")
    p("## Held out: each set scored by weights fitted on the others")
    p("")
    p(
        "Log-likelihood per pick (higher is better) and top-1 %. "
        "Differences are from the app's features alone."
    )
    p("")
    no_tdm = [s for s in sets if s != "TDM"]
    p(
        "| model | log-lik, all sets | log-lik, without TDM | top-1, all | top-1, without TDM |"
    )
    p("|---|---|---|---|---|")
    for m in models:
        cells = []
        for d, fmt in [(ll, "{:.4f}"), (t1, "{:.2f}")]:
            for keep in [sets, no_tdm]:
                v = pooled(d[m], keep)
                b = pooled(d[None], keep)
                d_fmt = fmt.replace("{:", "{:+")
                cells.append(
                    fmt.format(v) + ("" if m is None else f" ({d_fmt.format(v - b)})")
                )
        p(f"| {label[m]} | " + " | ".join(cells) + " |")
    p("")
    p("## By set, held out")
    p("")
    p(
        "Δ log-lik per pick ×1000 against the app's features alone; in brackets, "
        "the off_pips weight in points the held-out fit gives that set (the "
        "set's own weight is in the first table)."
    )
    p("")
    p("| set | own weight | app features | " + " | ".join(names) + " |")
    p("|---|---|---|" + "---|" * len(names))
    for s in sets:
        p(
            f"| {s} | {own[s]:+.1f} | ({eff[None][s]:+.1f}) | "
            + " | ".join(
                f"{1000 * (ll[m][s] - ll[None][s]):+.1f} ({eff[m][s]:+.1f})"
                for m in names
            )
            + " |"
        )
    print("\n".join(out))


if __name__ == "__main__":
    main()
