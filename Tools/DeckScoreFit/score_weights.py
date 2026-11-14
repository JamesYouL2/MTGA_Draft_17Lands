"""Whether changes to the deck score's weights change the suggestion, and how
the changed suggestions did: the report on builds.py's WEIGHT_VERSIONS.

    python Tools/DeckScoreFit/score_weights.py results/*.json.gz --json report.json

See experiments/2026-11-12-deck-score-weights/PROTOCOL.md. Needs NumPy.
"""

import argparse
import json

import score_rating as S

BASE = "app"
VERSIONS = ("no-domain", "no-missing-fixing", "no-domain-or-fixing", "two-colors-3.5")


def report(t):
    results = {"pools": len(t), "two_color": int(t.two.sum()),
               "sets": sorted(set(t.set.tolist())), "skipped": dict(t.skipped)}
    print(f"{len(t)} pools in {len(results['sets'])} sets, {results['two_color']} with "
          f"two-main-color decks. Skipped: {dict(t.skipped)}.\n")

    print("## How often the suggestion changes from the app's\n")
    print("| version | suggested pair | suggested deck | pools with a changed deck |")
    print("|---|---|---|---|")
    results["changes"] = {}
    for v in VERSIONS:
        c = S.changes(t, v, BASE)
        c["decks_changed"] = int((t.top[v] != t.top[BASE]).sum())
        results["changes"][v] = c
        print(f"| {v} | {c['pair']:.2f}% | {c['deck']:.2f}% | {c['decks_changed']} |")

    print("\n### By set: suggested deck changes\n")
    print("| set | " + " | ".join(VERSIONS) + " |\n|---|" + "---|" * len(VERSIONS))
    for s in results["sets"]:
        m = t.set == s
        cells = [f"{100 * (t.top[v][m] != t.top[BASE][m]).mean():.2f}%" for v in VERSIONS]
        print(f"| {s} | " + " | ".join(cells) + " |")

    print("\n## Head to head with the app\n")
    print("Pools where the two suggest different pairs and the drafter played one of "
          "them. The effect is how much better decks in the version's pair did, in win "
          "rate points, with set and player controlled and a 95% interval.\n")
    print("| version | pools differing | decks in its pair | in the app's | raw win rates "
          "| effect | verdict |\n|---|---|---|---|---|---|---|")
    results["head_to_head"] = {v: S.head_to_head(t, v, BASE) for v in VERSIONS}
    for v, r in results["head_to_head"].items():
        rates = (f"{r['rate_a']:.1f}% vs {r['rate_b']:.1f}%"
                 if r["rate_a"] is not None and r["rate_b"] is not None else "–")
        print(f"| {v} | {r['differ']} | {r['decks_a']} | {r['decks_b']} | {rates} "
              f"| {S._ci(r)} | {r['verdict']} |")

    print("\n## Playing the suggested pair (reported, not deciding)\n")
    print("| version | played it | effect |\n|---|---|---|")
    results["followed"] = {v: S.followed(t, v) for v in (BASE, *VERSIONS)}
    for v, r in results["followed"].items():
        print(f"| {v} | {r['played']:.1f}% | {S._signed(r['effect'], r['se'])} |")
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+", help="builds.py's outputs")
    parser.add_argument("--json", help="Where to write the numbers")
    args = parser.parse_args(argv)
    results = report(S.Table(args.paths, (BASE, *VERSIONS)))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
