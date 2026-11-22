"""How much heads results vary from salt to salt, and how much of it the ratings explain.

    python experiments/2026-11-17-measure-salts/salts.py MAIN [--diag DIAG] [--json salts.json]

MAIN holds a heads run's folders, one per set and salt (heads-<set>-<salt>);
DIAG the diagnostic's, one per set and ratings salt (heads-<set>-ms1+<rsalt>, and
heads-<set>-ms1 for none). See PROTOCOL.md. Reads one folder at a time and keeps a
row per event, so a full run fits in a few GB.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-heldout-replay"))
import compare as C  # noqa: E402

R = C.R
MEASURES = {"regret": 4, "swap": 3}  # digits to print
SET_BOOT = 2000


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def heads_in(root):
    return sorted(
        {os.path.basename(p)[: -len(".json")] for p in glob.glob(os.path.join(root, "*", "*.json"))}
        - {"base"}
    )


def summarise(root, heads):
    """{head: frames}: a row per complete event, one folder at a time.

    frames is (regret frame, swap frame) as compare.change and compare.swap read them,
    over keys (set, "salt:draft id")."""
    rows = {h: [] for h in heads}
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        if not os.path.exists(os.path.join(folder, "base.json")):
            continue
        salt = os.path.basename(folder).rsplit("-", 1)[-1]
        base = read(os.path.join(folder, "base.json"))
        code = base["set"]
        for h in heads:
            path = os.path.join(folder, f"{h}.json")
            if not os.path.exists(path):
                continue
            theirs = {d["id"]: d for d in read(path)["drafts"]}
            for d in base["drafts"]:
                e = theirs.get(d["id"])
                if e is None or not R.is_complete(d) or not d["picks"] or not e["picks"]:
                    continue
                head = {(q[0], q[1]): q for q in e["picks"]}
                net = n = 0
                for p in d["picks"]:
                    q = head.get((p[0], p[1]))
                    if q is not None and p[5] != q[5]:
                        n += 1
                        net += int(q[2] == 0) - int(p[2] == 0)
                rows[h].append((
                    (code, f"{salt}:{d['id']}"), d["wins"], d["skill"], d["games"],
                    float(np.mean([p[3] for p in d["picks"]])),
                    float(np.mean([q[3] for q in e["picks"]])), net, n,
                ))
            del theirs
        del base
    frames = {}
    for h, rs in rows.items():
        rs.sort(key=lambda r: r[0])
        keys = [r[0] for r in rs]
        wins = np.array([r[1] for r in rs], dtype=float)
        ctrl = R.controls([{"skill": r[2], "games": r[3]} for r in rs], [k[0] for k in keys])
        regret = (wins, ctrl, np.array([r[4] for r in rs]), np.array([r[5] for r in rs]), keys)
        swap = (np.array([[r[1], r[6], r[7]] for r in rs], dtype=float), ctrl, keys)
        frames[h] = (regret, swap)
    return frames


def fns(frames):
    regret, swap = frames
    return {"regret": lambda i: C.change(regret, i), "swap": lambda i: C.swap(swap, i)}


def cells(frames):
    """{measure: {(set, salt): (estimate, bootstrap SE)}} and {measure: {salt: ...}}."""
    keys = frames[0][4]
    groups, salts = {}, {}
    for i, k in enumerate(keys):
        groups.setdefault((k[0], C.salt_of(k)), []).append(i)
    by_cell, by_salt = {}, {}
    for name, fn in fns(frames).items():
        out = {}
        for cell, idx in sorted(groups.items()):
            idx = np.array(idx)
            out[cell] = (float(fn(idx)), R.bootstrap(lambda i, a=idx: fn(a[i]), len(idx)))
        by_cell[name] = out
        by_salt[name] = C.by_salt(keys, fn)
    return by_cell, by_salt


def set_level(by_cell):
    """Within each set across its salts: Q, df, excess variance (var - mean b^2)."""
    sets = sorted({s for s, _ in by_cell})
    out = {}
    for s in sets:
        e = np.array([v[0] for (t, _), v in by_cell.items() if t == s])
        b = np.array([v[1] for (t, _), v in by_cell.items() if t == s])
        if len(e) < 2 or not np.all(b > 0):
            continue
        m = C.combine(e, b)
        out[s] = {"q": m["q"], "df": len(e) - 1, "var": float(np.var(e, ddof=1)),
                  "b2": float(np.mean(b**2)), "phi": m["phi"]}
    return out


def pooled(per_set):
    q = sum(v["q"] for v in per_set.values())
    df = sum(v["df"] for v in per_set.values())
    return C.inflation(q, df) + (q, df)


def fmt_phi(p):
    return f"{p[0]:.2f} ({p[1]:.2f} to {p[2]:.2f})"


def study(root):
    heads = heads_in(root)
    out = {}
    for h in heads:
        frames = summarise(root, [h])[h]
        by_cell, by_salt = cells(frames)
        del frames
        out[h] = {}
        for name in MEASURES:
            salt_comb = C.combine([v[0] for v in by_salt[name].values()],
                                  [v[1] for v in by_salt[name].values()])
            per_set = set_level(by_cell[name])
            out[h][name] = {
                "salts": by_salt[name],
                "cells": {f"{s}|{t}": v for (s, t), v in by_cell[name].items()},
                "combined": salt_comb,
                "per_set": per_set,
                "set_level": pooled(per_set),
            }
        print(f"<!-- {h} done -->", flush=True)
    return out


def report_study(res):
    print("# Spread between salts against the bootstrap\n")
    print("phi = sqrt(Q / df): how many times the bootstrap SEs the estimates spread "
          "(1 is what the bootstrap expects), with 95% intervals from chi-square. Salt "
          "level: the salts' estimates over all sets (salts - 1 df). Set level: within "
          "each set across its salts, summed over sets.\n")
    print("| head | measure | salt-level phi | set-level phi (df) | combined (corrected SE) "
          "| bootstrap-only SE | tau |")
    print("|---|---|---|---|---|---|---|")
    for h, ms in res.items():
        for name, d in MEASURES.items():
            m = ms[name]
            c, sl = m["combined"], m["set_level"]
            print(f"| {h} | {name} | {fmt_phi((c['phi'], c['phi_low'], c['phi_high']))} "
                  f"| {fmt_phi(sl)} ({sl[4]}) | {c['estimate']:+.{d}f} ({c['se']:.{d}f}) "
                  f"| {c['fixed_se']:.{d}f} | {c['tau']:.{d}f} |")
    print("\nPooled over heads (heads share drafts and ratings, so these intervals are "
          "too narrow):\n")
    for group, names in (("three candidates", [h for h in res if h != "noise20"]),
                         ("all four", list(res))):
        for name in MEASURES:
            q = sum(res[h][name]["combined"]["q"] for h in names)
            df = sum(res[h][name]["combined"]["df"] for h in names)
            qs = sum(res[h][name]["set_level"][3] for h in names)
            dfs = sum(res[h][name]["set_level"][4] for h in names)
            print(f"- {group}, {name}: salt level {fmt_phi(C.inflation(q, df))}; "
                  f"set level {fmt_phi(C.inflation(qs, dfs))}")
    print("\n## Per salt\n")
    for h, ms in res.items():
        for name, d in MEASURES.items():
            each = ", ".join(f"{s}: {v[0]:+.{d}f} ({v[1]:.{d}f})"
                             for s, v in ms[name]["salts"].items())
            print(f"- {h}, {name}: {each}")
    print("\n## Set-level phi by set\n")
    sets = sorted({s for ms in res.values() for s in ms["regret"]["per_set"]})
    print("| head | measure | " + " | ".join(sets) + " |")
    print("|---|---|" + "---|" * len(sets))
    for h, ms in res.items():
        for name in MEASURES:
            ps = ms[name]["per_set"]
            print(f"| {h} | {name} | " + " | ".join(
                f"{ps[s]['phi']:.2f}" if s in ps else "–" for s in sets) + " |")
    print(flush=True)


def same_output(a, b):
    """Whether two replay results hold the same drafts and picks."""
    return read(a)["drafts"] == read(b)["drafts"]


def diagnostic(diag, main, res):
    """Ratings-only variance against the main study's excess, for the diag's sets."""
    heads = heads_in(diag)
    folders = sorted(glob.glob(os.path.join(diag, "*")))
    # Determinism: the diag's ms1 jobs are the main study's ms1 jobs.
    checks = []
    for folder in folders:
        name = os.path.basename(folder)
        if "+" in name:
            continue
        twin = os.path.join(main, name)
        if not os.path.isdir(twin):
            continue
        for label in ["base", *heads]:
            a, b = os.path.join(folder, f"{label}.json"), os.path.join(twin, f"{label}.json")
            if os.path.exists(a) and os.path.exists(b):
                checks.append((name, label, same_output(a, b)))
    out = {"determinism": checks, "heads": {}}
    rng = np.random.default_rng(0)
    for h in heads:
        frames = summarise(diag, [h])[h]
        by_cell, _ = cells(frames)
        del frames
        out["heads"][h] = {}
        for name in MEASURES:
            per_set = {}
            for (s, salt), v in by_cell[name].items():
                if "+" in salt:
                    per_set.setdefault(s, []).append(v)
            sets = sorted(per_set)
            var_r = np.array([np.var([v[0] for v in per_set[s]], ddof=1) for s in sets])
            main_sets = res.get(h, {}).get(name, {}).get("per_set", {})
            excess = np.array([main_sets[s]["var"] - main_sets[s]["b2"] if s in main_sets
                               else np.nan for s in sets])
            b2 = np.array([main_sets[s]["b2"] if s in main_sets else np.nan for s in sets])
            # No excess over the bootstrap leaves nothing to share out.
            ok = np.all(np.isfinite(excess)) and len(sets) and excess.mean() > 0
            share = var_r.mean() / excess.mean() if ok else np.nan
            boots = []
            if np.isfinite(share):
                for _ in range(SET_BOOT):
                    i = rng.integers(0, len(sets), len(sets))
                    if excess[i].mean() > 0:
                        boots.append(var_r[i].mean() / excess[i].mean())
            out["heads"][h][name] = {
                "sets": sets,
                "cells": {f"{s}|{salt}": v for (s, salt), v in by_cell[name].items()},
                "var_ratings": var_r.tolist(),
                "excess": excess.tolist(),
                "b2": b2.tolist(),
                "sigma2_r": float(var_r.mean()),
                "tau2": float(excess.mean()),
                "b2_mean": float(np.mean(b2)),
                "share": float(share),
                "share_low": float(np.percentile(boots, 2.5)) if boots else np.nan,
                "share_high": float(np.percentile(boots, 97.5)) if boots else np.nan,
                "df_r": int(sum(len(per_set[s]) - 1 for s in sets)),
            }
        print(f"<!-- diag {h} done -->", flush=True)
    return out


def report_diag(d):
    print("# Diagnostic: drafts fixed, ratings varied\n")
    bad = [c for c in d["determinism"] if not c[2]]
    print(f"Determinism: {len(d['determinism'])} result files of the diagnostic's ms1 jobs "
          f"against the main study's; {len(bad)} differ"
          + (": " + ", ".join(f"{a} {b}" for a, b, _ in bad) if bad else "") + ".\n")
    print("sigma2_r: variance of a set's estimate across the ratings salts, drafts fixed "
          "(pooled over sets). tau2: the main study's variance across salts in excess of "
          "the bootstrap (b2), same sets. Share: sigma2_r / tau2, 95% interval from "
          "resampling sets.\n")
    print("| head | measure | sigma2_r (df) | tau2 | b2 | share of excess from ratings |")
    print("|---|---|---|---|---|---|")
    for h, ms in d["heads"].items():
        for name in MEASURES:
            m = ms[name]
            share = (f"{m['share']:.2f} ({m['share_low']:.2f} to {m['share_high']:.2f})"
                     if np.isfinite(m["share"]) else "n/a (no excess)")
            print(f"| {h} | {name} | {m['sigma2_r']:.3g} ({m['df_r']}) | {m['tau2']:.3g} "
                  f"| {m['b2_mean']:.3g} | {share} |")
    print("\n## By set\n")
    for h, ms in d["heads"].items():
        for name, dg in MEASURES.items():
            m = ms[name]
            each = "; ".join(
                f"{s}: " + ", ".join(f"{k.split('|')[1]} {v[0]:+.{dg}f}"
                                     for k, v in m["cells"].items() if k.startswith(s + "|"))
                for s in m["sets"])
            print(f"- {h}, {name}: {each}")
    print(flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("main", help="The main study's folders")
    parser.add_argument("--diag", help="The diagnostic's folders")
    parser.add_argument("--json", help="Also write the numbers here")
    args = parser.parse_args(argv)
    res = study(args.main)
    report_study(res)
    out = {"study": res}
    if args.diag:
        out["diagnostic"] = diagnostic(args.diag, args.main, res)
        report_diag(out["diagnostic"])
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=float)


if __name__ == "__main__":
    main()
