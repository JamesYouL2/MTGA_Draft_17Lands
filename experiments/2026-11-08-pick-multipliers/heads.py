"""Compare each head of an Advisor heads run with the base, on held-out ratings.

    python experiments/2026-11-08-pick-multipliers/heads.py RESULTS --json heads.json \
        [--pair HEAD_A:HEAD_B ...]

RESULTS holds one folder for each set and salt, with base.json and a JSON file
for each head, from replay.py. --pair also compares HEAD_B with HEAD_A on the
same drafts, as if HEAD_A were the base.

Each measure is worked out in each salt, with its bootstrap SE, and the salts are
combined by compare.combine: the corrected SE counts the spread between salts,
which the bootstrap can't see (experiments/2026-11-17-measure-salts). A head's
decision reads both measures on the corrected SEs (decide). The bootstrap-only
figures over all salts, and PROTOCOL.md's regret verdict read on them, are kept,
labelled, to compare with runs before 2026-11-17. Reads compare.py's helpers.
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
# No weight's change on held-out ratings: the size already known to be a real loss.
LOSS = 0.0063
SES = 2


def verdict(change, se):
    """PROTOCOL.md's verdict on the regret slope, as read on bootstrap-only SEs."""
    if change == 0 and se == 0:
        return "no change"
    if change >= SES * se:
        return "keep"
    if change + SES * se > LOSS:
        return "inconclusive"
    return "no objection"


def decide(regret, swap):
    """A head's decision from both measures' combined figures (compare.combine).

    Adopt if 2+ scaled SEs better on one measure and not 2 scaled SEs worse on
    either. Regret slope: positive is worse. Swap: negative is worse."""
    if regret["se"] == 0 and swap["se"] == 0:
        return "no change"
    better_regret = -ses(regret)
    better_swap = ses(swap)
    worse = [name for name, z in (("regret", better_regret), ("swap", better_swap)) if z <= -SES]
    if worse:
        return f"worse ({', '.join(worse)})"
    if max(better_regret, better_swap) >= SES:
        return "adopt"
    return "no objection"


def ses(m):
    """A combined figure in scaled SEs."""
    return m["estimate"] / m["scaled_se"] if m["scaled_se"] else 0.0


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load(root, head, base="base"):
    """{(set, "sample:draft id"): {"base": draft, "head": draft}}, for drafts in both.

    base names the file read as the base, for comparing two heads."""
    out = {}
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        head_path = os.path.join(folder, f"{head}.json")
        base_path = os.path.join(folder, f"{base}.json")
        if not (os.path.exists(head_path) and os.path.exists(base_path)):
            continue
        # heads-<set>-<salt>, and the salt's name is all that tells the samples apart.
        sample = os.path.basename(folder).rsplit("-", 1)[-1]
        ours, other = read(base_path), read(head_path)
        theirs = {d["id"]: d for d in other["drafts"]}
        for d in ours["drafts"]:
            if d["id"] in theirs:
                out[(ours["set"], f"{sample}:{d['id']}")] = {"base": d, "head": theirs[d["id"]]}
        del ours, other, theirs
    return dict(sorted(out.items()))


def combined(salts):
    """compare.combine over {salt: (estimate, bootstrap SE)}."""
    return C.combine([v[0] for v in salts.values()], [v[1] for v in salts.values()])


def sim_frame(data):
    """(head minus base simulated deck win rate per draft, keys), for drafts both
    copies simulated (replay.py --simulate). Empty if the run didn't simulate."""
    keys = [k for k, v in data.items() if v["base"].get("sim") and v["head"].get("sim")]
    diff = np.array([data[k]["head"]["sim"]["win"] - data[k]["base"]["sim"]["win"] for k in keys])
    return diff, keys


def sim_measure(data):
    """The simulated draft's deck win rate, head minus base, in win rate points:
    combined over salts like the others, or None if the run didn't simulate."""
    diff, keys = sim_frame(data)
    if not len(diff):
        return None
    salts = C.by_salt(keys, lambda i: diff[i].mean())
    out = combined(salts)
    return out | {
        "drafts": len(diff),
        "sd": float(diff.std()),
        "changed": float(np.mean(diff != 0)),
        "samples": {k: list(v) for k, v in salts.items()},
    }


def measure(data):
    frame = C.regret_frame(data)
    n = len(frame[0])
    change = C.change(frame, np.arange(n))
    se = R.bootstrap(lambda i: C.change(frame, i), n)
    regret_salts = C.by_salt(frame[4], lambda i: C.change(frame, i))
    sframe = C.swap_frame(data)
    swap = C.swap(sframe, np.arange(len(sframe[0])))
    swap_se = R.bootstrap(lambda i: C.swap(sframe, i), len(sframe[0]))
    swap_salts = C.by_salt(sframe[2], lambda i: C.swap(sframe, i))
    regret, swaps = combined(regret_salts), combined(swap_salts)
    total, changed, base_on, head_on, kinds = C.picks(data)
    return {
        "drafts": len(data),
        "events": n,
        # Combined over salts, the SEs counting the spread between them.
        "regret": regret,
        "swap_combined": swaps,
        "decision": decide(regret, swaps),
        # Not part of the decision: see experiments/2026-11-21-simulated-draft.
        "sim": sim_measure(data),
        "samples": {k: list(v) for k, v in regret_salts.items()},
        "swap_samples": {k: list(v) for k, v in swap_salts.items()},
        # Bootstrap only, over all salts at once: as read before 2026-11-17.
        "change": change,
        "se": se,
        "verdict": verdict(change, se),
        "swap": swap,
        "swap_se": swap_se,
        "top1": C.top1(data),
        "top_changes": 100 * changed / total if total else 0.0,
        "on_lane_base": 100 * base_on / total if total else 0.0,
        "on_lane_head": 100 * head_on / total if total else 0.0,
        "kinds": {
            kind: {
                "share": 100 * k[0] / changed,
                "took_base": 100 * k[1] / k[0],
                "took_head": 100 * k[2] / k[0],
            }
            for kind in C.KINDS
            if (k := kinds[kind])[0]
        },
    }


def cell(m, digits):
    return f"{m['estimate']:+.{digits}f} ({m['scaled_se']:.{digits}f}), {ses(m):+.1f}"


def ratio(x, se):
    return x / se if se else 0.0


def report(results):
    k = max((m["regret"]["df"] + 1 for m in results.values()), default=0)
    print(
        f"Combined over {k} salts. Regret slope change: positive is worse for the head. "
        "Event wins per swapped pick: negative is worse. Each figure is estimate "
        "(scaled SE), SEs. The scaled SE counts the spread between salts and is widened "
        "for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. "
        "Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what "
        "2 scaled SEs worse is, the least harm the run could have seen.\n"
    )
    print("| head | regret slope change | event wins per swapped pick | decision "
          "| smallest harm, regret / swap | top card changes | top-1 change "
          "| on-lane, base to head |")
    print("|---|---|---|---|---|---|---|---|")
    for head, m in results.items():
        r, w = m["regret"], m["swap_combined"]
        print(
            f"| {head} | {cell(r, 4)} | {cell(w, 3)} | {m['decision']} "
            f"| +{2 * r['scaled_se']:.4f} / -{2 * w['scaled_se']:.3f} "
            f"| {m['top_changes']:.2f}% | {m['top1']:+.2f} "
            f"| {m['on_lane_base']:.1f}% to {m['on_lane_head']:.1f}% |"
        )
    sims = {head: m["sim"] for head, m in results.items() if m.get("sim")}
    if sims:
        print("\n## Simulated draft deck win rate\n")
        print("The advisor drafts each draft's packs itself; the first deck Suggest Deck "
              "builds from its pool, as an expected game win rate. Head minus base in win "
              "rate points, combined over salts like the others: estimate (scaled SE), SEs. "
              "Positive is better for the head. Not part of the decision: it grades "
              "advisors by the deck score's own beliefs "
              "(experiments/2026-11-21-simulated-draft).\n")
        print("| head | simulated deck win rate change | SD per draft | drafts | decks changed |")
        print("|---|---|---|---|---|")
        for head, m in sims.items():
            print(f"| {head} | {cell(m, 3)} | {m['sd']:.3f} | {m['drafts']} "
                  f"| {100 * m['changed']:.1f}% |")
    print("\n## Bootstrap only, over all salts at once\n")
    print("As read before 2026-11-17: these SEs leave out the spread between salts. "
          "The verdict is PROTOCOL.md's, on the regret slope.\n")
    print("| head | regret slope change (SE), SEs | verdict "
          "| event wins per swapped pick (SE), SEs |")
    print("|---|---|---|---|")
    for head, m in results.items():
        print(
            f"| {head} | {m['change']:+.4f} ({m['se']:.4f}), {ratio(m['change'], m['se']):+.1f} "
            f"| {m['verdict']} | {m['swap']:+.3f} ({m['swap_se']:.3f}), "
            f"{ratio(m['swap'], m['swap_se']):+.1f} |"
        )
    print("\n## By salt\n")
    print("Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the "
          "bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs "
          "the salts spread, with its 95% interval.\n")
    for head, m in results.items():
        print(f"**{head}** ({m['drafts']} drafts, {m['events']} complete events)\n")
        for name, salts, c, d in (("regret slope", m["samples"], m["regret"], 4),
                                  ("swap", m["swap_samples"], m["swap_combined"], 3)):
            each = ", ".join(f"{s or 'none'}: {v[0]:+.{d}f} ({v[1]:.{d}f})" for s, v in salts.items())
            print(f"- {name}: {each}. tau {c['tau']:.{d}f}; phi {c['phi']:.2f} "
                  f"({c['phi_low']:.2f} to {c['phi_high']:.2f}); corrected SE "
                  f"{c['se']:.{d}f}, bootstrap only {c['fixed_se']:.{d}f}")
        for kind, kk in m["kinds"].items():
            print(f"- {kind}: {kk['share']:.1f}% of changes; drafters took base's "
                  f"{kk['took_base']:.1f}%, head's {kk['took_head']:.1f}%")
        print()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("results", help="One folder per set and sample")
    parser.add_argument("--json", help="Also write the numbers here")
    parser.add_argument("--pair", action="append", default=[],
                        help="HEAD_A:HEAD_B: HEAD_B against HEAD_A on the same drafts")
    args = parser.parse_args(argv)
    heads = sorted(
        {
            os.path.basename(p)[: -len(".json")]
            for p in glob.glob(os.path.join(args.results, "*", "*.json"))
        }
        - {"base"}
    )
    results = {head: measure(load(args.results, head)) for head in heads}
    for pair in args.pair:
        a, b = pair.split(":")
        results[f"{b} against {a}"] = measure(load(args.results, b, base=a))
    report(results)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
