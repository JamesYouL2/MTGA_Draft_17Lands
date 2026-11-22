"""The simulated draft measure's validation, as PROTOCOL.md reads it.

    python experiments/2026-11-21-simulated-draft/sim_report.py RESULTS [--json extra.json]

RESULTS is an Advisor heads run's results, replayed with --simulate. Prints:

1. Every head on all three measures, combined over all salts and over the first
   six salts (60,000 drafts in a 10-set, 1000-draft run): criterion (a) is read
   on the six.
2. Relative power: each measure's SEs per square root of a draft, and the
   drafts it would need to put the head 3 scaled SEs from zero.
3. Sign agreement with event wins (and regret) on every head.
4. The sanity check: does the deck score of a pool track the events' wins?
5. What the simulation did: wheel swaps, forced picks, quick builds.
"""

import argparse
import glob
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

C, R = H.C, H.R
CRITERION_SALTS = 6
SKIPPED = "drafts: pools don't account for missing picks"


def salts_in(root):
    return sorted({os.path.basename(f).rsplit("-", 1)[-1] for f in glob.glob(os.path.join(root, "*"))})


def per_salt(data):
    """{measure: {salt: (estimate, bootstrap SE)}} and drafts per measure."""
    frame = C.regret_frame(data)
    sframe = C.swap_frame(data)
    diff, keys = H.sim_frame(data)
    out = {
        "regret": C.by_salt(frame[4], lambda i: C.change(frame, i)),
        "swap": C.by_salt(sframe[2], lambda i: C.swap(sframe, i)),
        "sim": C.by_salt(keys, lambda i: diff[i].mean()) if len(diff) else {},
    }
    counts = {
        "regret": Counter(C.salt_of(k) for k in frame[4]),
        "swap": Counter(C.salt_of(k) for k in sframe[2]),
        "sim": Counter(C.salt_of(k) for k in keys),
    }
    return out, counts, diff


def combine_on(salts, chosen):
    picked = {s: v for s, v in salts.items() if s in chosen}
    return H.combined(picked) if len(picked) >= 2 else None


# Each measure's sign for "head better": regret slope change is worse when positive.
BETTER = {"regret": -1, "swap": 1, "sim": 1}


def z(m, name):
    return BETTER[name] * H.ses(m) if m else float("nan")


def needed(m, n, name, target=3.0):
    """Drafts (or events) to put the estimate `target` scaled SEs from zero, if the
    SE falls as 1 / sqrt(n)."""
    zz = abs(z(m, name))
    return n * (target / zz) ** 2 if zz else float("inf")


def sanity(root):
    """Deck score against event wins, on the base's replay of complete events."""
    rows = []
    for path in sorted(glob.glob(os.path.join(root, "*", "base.json"))):
        d = H.read(path)
        for x in d["drafts"]:
            s = x.get("sim")
            if not s or not R.is_complete(x):
                continue
            rows.append((d["set"], x["wins"], s["win"], s.get("drafter_win"), s["agree"],
                         s["decided"], x["skill"]))
    if not rows:
        return None
    sets = np.array([r[0] for r in rows])
    wins = np.array([r[1] for r in rows], float)
    sim = np.array([r[2] for r in rows], float)
    mine = np.array([np.nan if r[3] is None else r[3] for r in rows], float)
    share = np.array([r[4] / r[5] if r[5] else np.nan for r in rows], float)

    def within(x):
        out = x.copy()
        for code in set(sets):
            m = sets == code
            out[m] = x[m] - np.nanmean(x[m])
        return out

    def corr(x, y, mask):
        x, y = within(x)[mask], within(y)[mask]
        ok = ~(np.isnan(x) | np.isnan(y))
        if ok.sum() < 30:
            return {"n": int(ok.sum()), "r": None}
        r = float(np.corrcoef(x[ok], y[ok])[0, 1])
        return {"n": int(ok.sum()), "r": r, "se": float(np.sqrt((1 - r * r) / (ok.sum() - 2))),
                "slope": float(np.polyfit(x[ok], y[ok], 1)[0])}

    everything = np.ones(len(rows), bool)
    out = {
        "events": len(rows),
        "full agreement": corr(sim, wins, share == 1.0),
        "drafter's own pool": corr(mine, wins, everything),
        "advisor's draft": corr(sim, wins, everything),
        "by agreement share": {},
    }
    cuts = np.nanquantile(share, [0, 1 / 3, 2 / 3, 1])
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        m = (share >= lo) & (share <= hi)
        out["by agreement share"][f"{lo:.2f} to {hi:.2f}"] = corr(sim, wins, m)
    out["agreement share, mean"] = float(np.nanmean(share))
    return out


def counters(root):
    """{label: Counter} of the simulation's counts, summed over sets and salts."""
    out = {}
    for path in sorted(glob.glob(os.path.join(root, "*", "*.json"))):
        d = H.read(path)
        if d.get("simulation"):
            out.setdefault(d.get("label") or os.path.basename(path)[:-5], Counter()).update(
                d["simulation"])
    return out


def fmt(m, d):
    return "–" if m is None else H.cell(m, d)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("results")
    parser.add_argument("--json", default="extra.json")
    args = parser.parse_args(argv)
    root = args.results
    salts = salts_in(root)
    six = salts[:CRITERION_SALTS]
    heads = sorted({os.path.basename(p)[:-5] for p in glob.glob(os.path.join(root, "*", "*.json"))}
                   - {"base"})
    digits = {"regret": 4, "swap": 3, "sim": 3}
    results = {}
    for head in heads:
        data = H.load(root, head)
        each, counts, diff = per_salt(data)
        r = {"salts": salts, "criterion salts": six}
        for name in each:
            r[name] = {
                "all": combine_on(each[name], salts),
                "six": combine_on(each[name], six),
                "n all": sum(counts[name].values()),
                "n six": sum(v for s, v in counts[name].items() if s in six),
                "by salt": {s: list(v) for s, v in each[name].items()},
            }
        r["sim decks changed"] = float(np.mean(diff != 0)) if len(diff) else None
        r["sim sd"] = float(diff.std()) if len(diff) else None
        results[head] = r
        del data

    print("# Simulated draft deck score: validation\n")
    print(f"Salts: {', '.join(salts)}. Criterion (a) is read on the first {len(six)}: "
          f"{', '.join(six)}. Each cell: estimate (scaled SE), scaled SEs, signed so "
          "positive is the measure's own direction (regret: positive is worse; swap and "
          "simulated: positive is better).\n")
    for label, key in (("All salts", "all"), (f"First {len(six)} salts", "six")):
        print(f"## {label}\n")
        print("| head | regret slope change | event wins per swapped pick "
              "| simulated deck win rate | simulated drafts | decks changed |")
        print("|---|---|---|---|---|---|")
        for head, r in results.items():
            ch = r["sim decks changed"]
            print(f"| {head} | {fmt(r['regret'][key], 4)} | {fmt(r['swap'][key], 3)} "
                  f"| {fmt(r['sim'][key], 3)} | {r['sim']['n ' + key]} "
                  f"| {'–' if ch is None else f'{100 * ch:.1f}%'} |")
        print()

    print("## Relative power\n")
    print("z per root draft: scaled SEs toward 'head better' divided by the square root of "
          "the drafts (events, for regret and swap) the measure used, all salts. Drafts "
          "for 3 SEs: what the measure would need to put this head 3 scaled SEs from "
          "zero. The power ratio is (z per root draft, simulated / swap) squared: how many "
          "times as many drafts swap needs as the simulated measure for the same SEs.\n")
    print("| head | regret z/√n | swap z/√n | simulated z/√n | drafts for 3 SEs: regret "
          "/ swap / simulated | power ratio, simulated to swap |")
    print("|---|---|---|---|---|---|")
    for head, r in results.items():
        zs = {n: z(r[n]["all"], n) / np.sqrt(r[n]["n all"]) if r[n]["n all"] else float("nan")
              for n in ("regret", "swap", "sim")}
        need = [needed(r[n]["all"], r[n]["n all"], n) for n in ("regret", "swap", "sim")]
        ratio = (zs["sim"] / zs["swap"]) ** 2 if zs["swap"] else float("nan")
        r["z per root draft"], r["drafts for 3 SEs"], r["power ratio"] = zs, need, ratio
        print(f"| {head} | {zs['regret']:+.4f} | {zs['swap']:+.4f} | {zs['sim']:+.4f} "
              f"| {' / '.join(f'{x:,.0f}' for x in need)} | {ratio:.2f} |")
    print()

    print("## Sign agreement\n")
    print("Direction each measure reads for the head, all salts: + better, − worse, "
          "and in brackets when under 2 scaled SEs.\n")
    print("| head | regret | swap | simulated | simulated agrees with swap |")
    print("|---|---|---|---|---|")
    for head, r in results.items():
        signs = {}
        for n in ("regret", "swap", "sim"):
            zz = z(r[n]["all"], n)
            s = "+" if zz > 0 else "−" if zz < 0 else "0"
            signs[n] = s if abs(zz) >= 2 else f"({s})"
        a, b = signs["sim"].strip("()"), signs["swap"].strip("()")
        agree = "n/a" if "0" in (a, b) else "yes" if a == b else "no"
        r["signs"] = signs | {"agree": agree}
        print(f"| {head} | {signs['regret']} | {signs['swap']} | {signs['sim']} | {agree} |")
    print()

    check = sanity(root)
    print("## Sanity check: deck score against event wins\n")
    if check is None:
        print("No simulated drafts.\n")
    else:
        print(f"{check['events']} complete events, base replay. Correlation of the deck "
              "win rate with the event's wins, both centred within set (r, its SE, and "
              "the slope in event wins per deck win rate point). The base agrees with the "
              f"drafter on {100 * check['agreement share, mean']:.1f}% of its decided picks "
              "on average.\n")
        print("| pools | events | r (SE) | slope |")
        print("|---|---|---|---|")
        rows = [("advisor's draft, full agreement with the drafter", check["full agreement"]),
                ("the drafter's own pool, Suggest Deck", check["drafter's own pool"]),
                ("advisor's draft, all events", check["advisor's draft"])]
        rows += [(f"advisor's draft, agreement share {k}", v)
                 for k, v in check["by agreement share"].items()]
        for label, c in rows:
            if c["r"] is None:
                print(f"| {label} | {c['n']} | too few | |")
            else:
                print(f"| {label} | {c['n']} | {c['r']:+.3f} ({c['se']:.3f}) "
                      f"| {c['slope']:+.4f} |")
        print()

    print("## What the simulation did\n")
    counts = counters(root)
    print("| copy | drafts | picks | wheel picks | wheel swaps applied | dropped "
          "| applied share | forced picks | quick builds | skipped |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for label, c in sorted(counts.items(), key=lambda kv: (kv[0] != "base", kv[0])):
        a = c["wheel swap applied"]
        dropped = c["wheel swap dropped (taken by another drafter)"]
        drafts = c["decks: suggest deck"] + c["decks: quick build (no suggested deck)"]
        print(f"| {label} | {drafts} | {c['picks']} | {c['wheel picks']} | {a} | {dropped} "
              f"| {100 * a / (a + dropped) if a + dropped else 0:.1f}% "
              f"| {c['picks forced (no row in the dump)']} "
              f"| {c['decks: quick build (no suggested deck)']} "
              f"| {c[SKIPPED]} |")
    print()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"heads": results, "sanity": check,
                       "counts": {k: dict(v) for k, v in counts.items()}}, f, indent=1)


if __name__ == "__main__":
    main()
