"""PROTOCOL.md addendum (2026-11-22): E3's skill-confound control.

    python experiments/2026-11-22-deck-value/e3_confound.py e3-*.json.gz [--json e3c.json]

Reads e3_join.py's files (with "picks"). For each head, on e3.py's sample
(matched complete events with every M4 fact), the disagreement picks split in
two:

- neither: neither the head's top card nor base's top card is in any of the
  draft's played builds, so the pick cannot have changed the deck;
- complement: at least one of the two was maindecked.

The a, b, c counts are rebuilt per subset, and both subsets' counts go in one
fit (six count columns plus controls), under M0 and M4. The full-sample fit is
e3.py's, for the reproduction check and the rule's "full estimate". Each figure
is per salt with bootstrap SEs, combined over salts by heads.combined.
"""

import argparse
import json
import os
import sys

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e3 as E  # noqa: E402

H, C, R = E.H, E.C, E.R
MODELS = [("M0", []), ("M4", E.M4)]


def keep_rows(rows, head):
    return [
        r for r in rows
        if R.is_complete(r) and head in r["took"] and r["deck"] and r["deck_games"]
        and all(r["deck"].get(k) is not None for k in E.M4)
    ]


def split_counts(r, head):
    """[a, b, c] for neither, then for the complement; and whether they add up
    to took."""
    n, k = [0, 0, 0], [0, 0, 0]
    for _, _, cls, head_in, base_in in r["picks"].get(head, []):
        (k if head_in or base_in else n)[cls] += 1
    return n + k, [x + y for x, y in zip(n, k)] == list(r["took"][head])


def verdict(full, neither, comp):
    z_n = neither["estimate"] / neither["scaled_se"]
    z_c = comp["estimate"] / comp["scaled_se"]
    share = neither["estimate"] / full["estimate"] if full["estimate"] else float("nan")
    if share >= 0.5 and abs(z_n) > 2:
        return "confound"
    if abs(z_n) < 2 and abs(z_c) > 3:
        return "pick effect"
    return "mixed"


def fit_head(rows, head):
    keep = keep_rows(rows, head)
    keys = [(r["set"], f"{r['salt']}:{r['id']}") for r in keep]
    ctrl = R.controls(keep, [r["set"] for r in keep])
    wins = np.array([r["wins"] for r in keep], dtype=float)
    took = np.array([r["took"][head] for r in keep], dtype=float)
    split, ok = zip(*(split_counts(r, head) for r in keep))
    split = np.array(split, dtype=float)
    deck = {k: np.array([r["deck"][k] for r in keep], dtype=float) for k in E.M4}
    out = {
        "events": len(keep),
        "count_mismatch": int(len(ok) - sum(ok)),
        "picks": {
            "neither": split[:, :3].sum(axis=0).astype(int).tolist(),
            "complement": split[:, 3:].sum(axis=0).astype(int).tolist(),
        },
    }
    for name, cols in MODELS:
        extra = [ctrl] + [deck[k] for k in cols]
        X_full = np.column_stack([took] + extra)
        X_split = np.column_stack([split] + extra)

        def full(idx, X=X_full):
            b = np.linalg.lstsq(X[idx], wins[idx], rcond=None)[0]
            return b[0] - b[1]

        def neither(idx, X=X_split):
            b = np.linalg.lstsq(X[idx], wins[idx], rcond=None)[0]
            return b[0] - b[1]

        def comp(idx, X=X_split):
            b = np.linalg.lstsq(X[idx], wins[idx], rcond=None)[0]
            return b[3] - b[4]

        res = {
            "full": H.combined(C.by_salt(keys, full)),
            "neither": H.combined(C.by_salt(keys, neither)),
            "complement": H.combined(C.by_salt(keys, comp)),
        }
        res["verdict"] = verdict(res["full"], res["neither"], res["complement"])
        out[name] = res
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    rows = E.load(args.paths)
    missing = sum(1 for r in rows if "picks" not in r)
    if missing:
        sys.exit(f"{missing} rows have no picks; rerun e3_join.py")

    print("## E3 skill-confound control (PROTOCOL.md addendum, 2026-11-22)\n")
    print("a − b, event wins per disagreement: estimate (scaled SE) SEs. "
          "Neither: neither top card maindecked. Complement: at least one was. "
          "Reading on M4.\n")
    results = {}
    for head in E.HEADS:
        res = fit_head(rows, head)
        results[head] = res
        pn, pc = res["picks"]["neither"], res["picks"]["complement"]
        tot = sum(pn) + sum(pc)
        print(f"### {head}\n")
        print(f"{res['events']} events; disagreement picks a, b, c: neither {pn} "
              f"({sum(pn) / max(1, tot):.1%}), complement {pc}; "
              f"events whose split doesn't add up to took: {res['count_mismatch']}\n")
        print("| model | full | neither | neither / full | complement | verdict |")
        print("|---|---|---|---|---|---|")
        for name, _ in MODELS:
            m = res[name]
            share = m["neither"]["estimate"] / m["full"]["estimate"] if m["full"]["estimate"] else float("nan")
            print(f"| {name} | {E.cell(m['full'])} | {E.cell(m['neither'])} | {share:.0%} | "
                  f"{E.cell(m['complement'])} | {m['verdict'] if name == 'M4' else '(M0, not read)'} |")
        print()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1, default=float)


if __name__ == "__main__":
    main()
