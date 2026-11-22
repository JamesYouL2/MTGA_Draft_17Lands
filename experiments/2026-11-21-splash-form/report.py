"""How the split color terms change the suggested deck, and how the changed
suggestions did: the report on builds.py's versions for this test.

    python experiments/2026-11-21-splash-form/report.py results/*.json.gz --json report.json

See PROTOCOL.md next to this file. Needs NumPy.
"""

import argparse
import gzip
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
import score_rating as S  # noqa: E402

BASE = "old"
VERSIONS = ("app", "flat-splash")
GROUPS = ("two", "splash", "more")


def played_group(main, splash):
    """The drafter's deck by 17Lands' colors, in the builder's groups."""
    if len(main) <= 2:
        return "splash" if splash else "two"
    return "more"


class Table(S.Table):
    """score_rating's table, plus each version's top-deck group and the
    drafter's own group."""

    def __init__(self, paths, versions):
        super().__init__(paths, versions)
        groups = {v: [] for v in versions}
        played = []
        for path in paths:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            for r in data["rows"]:
                played.append(played_group(r["main"], r["splash"]))
                for v in versions:
                    groups[v].append(r["versions"][v]["group"])
            del data
        self.group = {v: np.array(g) for v, g in groups.items()}
        self.played = np.array(played)


def group_head_to_head(t, a, b):
    """Where a and b suggest the same pair in different groups (a splash build
    against a two-color one, say) and the drafter played that pair in one of
    the two groups: how much better the decks in a's group did."""
    same_pair = t.pair[a] == t.pair[b]
    differ = same_pair & (t.group[a] != t.group[b])
    # The drafter's main colors are the pair, or hold it for three or more.
    in_pair = np.array([set(p) <= set(m) for p, m in zip(t.pair[a], t.main)])
    in_a = differ & in_pair & (t.played == t.group[a])
    in_b = differ & in_pair & (t.played == t.group[b])
    mask = in_a | in_b
    out = {"differ": int(differ.sum()), "decks_a": int(in_a.sum()),
           "decks_b": int(in_b.sum()), "sets": len(set(t.set[mask]))}
    for side, m in (("a", in_a), ("b", in_b)):
        out[f"rate_{side}"] = 100.0 * t.wins[m].sum() / t.games[m].sum() if m.any() else None
    if min(out["decks_a"], out["decks_b"]) < S.MIN_DECKS or out["sets"] < 2:
        return out | {"effect": None, "se": None, "verdict": "insufficient data"}
    value, se = S.effect(t, mask, in_a[mask].astype(float))
    return out | {"effect": value, "se": se, "verdict": S.verdict(value, se)}


def matches(t, v):
    """Share of decks whose pair and group are the suggestion's."""
    return 100.0 * float(((t.main == t.pair[v]) & (t.played == t.group[v])).mean())


def report(t):
    results = {"pools": len(t), "skipped": dict(t.skipped),
               "sets": sorted(set(t.set.tolist()))}
    print(f"{len(t)} pools in {len(results['sets'])} sets; {int(t.games.sum())} games. "
          f"Skipped: {dict(t.skipped)}.\n")

    print("## How often the suggestion changes from the old score's\n")
    print("| version | suggested pair | suggested deck | deck's group |\n|---|---|---|---|")
    results["changes"] = {}
    for v in VERSIONS:
        c = S.changes(t, v, BASE)
        c["group"] = 100.0 * float((t.group[v] != t.group[BASE]).mean())
        results["changes"][v] = c
        print(f"| {v} | {c['pair']:.2f}% | {c['deck']:.2f}% | {c['group']:.2f}% |")
    c = S.changes(t, "app", "flat-splash")
    print(f"\n`app` against `flat-splash` (the weight per splash spell alone): pair "
          f"{c['pair']:.2f}%, deck {c['deck']:.2f}%.\n")
    results["per_spell_alone"] = c

    print("### By set: suggested deck changes, `app` against `old`\n")
    print("| set | pools | deck | group |\n|---|---|---|---|")
    results["by_set"] = {}
    for s in results["sets"]:
        m = t.set == s
        deck = 100 * float((t.top["app"][m] != t.top[BASE][m]).mean())
        grp = 100 * float((t.group["app"][m] != t.group[BASE][m]).mean())
        results["by_set"][s] = {"deck": deck, "group": grp}
        print(f"| {s} | {int(m.sum())} | {deck:.2f}% | {grp:.2f}% |")

    print("\n## The suggested deck's group\n")
    print("| version | " + " | ".join(GROUPS) + " |\n|---|" + "---|" * len(GROUPS))
    results["groups"] = {}
    for v in (BASE, *VERSIONS):
        counts = Counter(t.group[v].tolist())
        results["groups"][v] = {g: 100.0 * counts[g] / len(t) for g in GROUPS}
        print(f"| {v} | " + " | ".join(f"{results['groups'][v][g]:.2f}%" for g in GROUPS)
              + " |")
    counts = Counter(t.played.tolist())
    print("| drafters played | " + " | ".join(f"{100.0 * counts[g] / len(t):.2f}%"
                                              for g in GROUPS) + " |")

    print("\n### From `old` to `app`\n")
    print("| old \\ app | " + " | ".join(GROUPS) + " |\n|---|" + "---|" * len(GROUPS))
    for g in GROUPS:
        m = t.group[BASE] == g
        print(f"| {g} | " + " | ".join(str(int((m & (t.group['app'] == h)).sum()))
                                         for h in GROUPS) + " |")

    def h2h_table(title, fn, note):
        print(f"\n## {title}\n\n{note}\n")
        print("| version | pools differing | decks in its | in old's | raw win rates "
              "| effect | verdict |\n|---|---|---|---|---|---|---|")
        out = {}
        for v in VERSIONS:
            r = fn(t, v, BASE)
            out[v] = r
            rates = (f"{r['rate_a']:.1f}% vs {r['rate_b']:.1f}%"
                     if r["rate_a"] is not None and r["rate_b"] is not None else "–")
            print(f"| {v} | {r['differ']} | {r['decks_a']} | {r['decks_b']} | {rates} "
                  f"| {S._ci(r)} | {r['verdict']} |")
        return out

    results["group_head_to_head"] = h2h_table(
        "Head to head within a pair: the group", group_head_to_head,
        "Pools where the two suggest the same pair in different groups and the "
        "drafter played that pair in one of them. The effect is how much better "
        "decks in the version's group did, in win rate points, with set and player "
        "controlled and a 95% interval.")
    results["pair_head_to_head"] = h2h_table(
        "Head to head between pairs", S.head_to_head,
        "As in the earlier Deck builds tests: pools where the two suggest different "
        "pairs and the drafter played one of them, two-main-color decks only.")

    print("\n## Drafters who played the suggestion's pair and group (reported only)\n")
    print("| version | share |\n|---|---|")
    results["matches"] = {v: matches(t, v) for v in (BASE, *VERSIONS)}
    for v, r in results["matches"].items():
        print(f"| {v} | {r:.2f}% |")
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+", help="builds.py's outputs")
    parser.add_argument("--json", help="Where to write the numbers")
    args = parser.parse_args(argv)
    results = report(Table(args.paths, (BASE, *VERSIONS)))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
