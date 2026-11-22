"""Which card rating the deck score should use: the report on builds.py's runs.

    python Tools/DeckScoreFit/score_rating.py results/*.json.gz --json report.json

For each version it says how often the suggested pair changes from the blend's
and how those pairs did. See experiments/2026-11-08-deck-score-rating/PROTOCOL.md.
Needs NumPy.
"""

import argparse
import gzip
import json
import math
from collections import Counter

import numpy as np

from fit import expit, fit_clustered, newton, varying

BASE = "blend"
VERSIONS = ("overall", "overall+pair", "blend+pair")
# A pool only counts as agreeing or not if its deck has two main colors.
MIN_DECKS = 100
# How far below the blend the simplification may be and still count as no worse,
# in win rate points, at the bottom of its 95% interval.
NOT_WORSE = -0.5


class Table:
    """Decks from builds.py as arrays, one set at a time, to fit in memory."""

    def __init__(self, paths, versions):
        self.versions = versions
        columns = {k: [] for k in ("set", "main", "skill", "experience", "wins", "games")}
        tops = {v: {"pair": [], "top": [], "gap": []} for v in versions}
        self.skipped = Counter()
        for path in paths:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            self.skipped.update(data["skipped"])
            for r in data["rows"]:
                r["set"] = data["set"]
                for key, values in columns.items():
                    values.append(r[key])
                for v in versions:
                    shown = r["versions"][v]
                    tops[v]["pair"].append(shown["pair"])
                    tops[v]["top"].append(shown["shown"][0])
                    best = shown["pairs"].get(r["main"])
                    tops[v]["gap"].append(
                        max(shown["pairs"].values()) - best
                        if best is not None and len(r["main"]) == 2
                        else math.nan
                    )
            del data
        self.set = np.array(columns["set"])
        self.main = np.array(columns["main"])
        self.skill = np.array(columns["skill"])
        self.experience = np.array(columns["experience"])
        self.wins = np.array(columns["wins"], dtype=float)
        self.games = np.array(columns["games"], dtype=float)
        self.pair = {v: np.array(tops[v]["pair"]) for v in versions}
        self.top = {v: np.array(tops[v]["top"]) for v in versions}
        self.gap = {v: np.array(tops[v]["gap"]) for v in versions}
        self.two = np.char.str_len(self.main) == 2

    def __len__(self):
        return len(self.set)


def indicators(values):
    """Indicator columns for each value but the most common."""
    common = [v for v, _ in Counter(values.tolist()).most_common()[1:]]
    return np.array([values == v for v in common], dtype=float).T.reshape(len(values), len(common))


def player_columns(t, mask):
    return np.hstack([indicators(t.skill[mask]), indicators(t.experience[mask])])


def effect(t, mask, x):
    """x's effect on winning a game over the decks in mask, in win rate points,
    controlling for the set and the player's buckets."""
    sets = sorted(set(t.set[mask]))
    dummies = np.array([t.set[mask] == s for s in sets], dtype=float).T
    A = np.hstack([x[:, None], dummies, varying(player_columns(t, mask))])
    wins, games = t.wins[mask], t.games[mask]
    beta, model, cluster = fit_clustered(A, wins, games, t.set[mask])
    variance = model[0, 0] if cluster is None else max(model[0, 0], cluster[0, 0])
    p = wins.sum() / games.sum()
    scale = 100.0 * p * (1 - p)
    return scale * beta[0], scale * math.sqrt(variance)


def head_to_head(t, a, b):
    """Where a and b suggest different pairs and the drafter played one of them,
    how much better the decks in a's pair did, in win rate points."""
    differ = t.pair[a] != t.pair[b]
    in_a, in_b = t.main == t.pair[a], t.main == t.pair[b]
    mask = differ & t.two & (in_a | in_b)
    out = {
        "differ": int((differ & t.two).sum()),
        "decks": int(mask.sum()),
        "decks_a": int((mask & in_a).sum()),
        "decks_b": int((mask & in_b).sum()),
        "sets": len(set(t.set[mask])),
    }
    for side, m in (("a", mask & in_a), ("b", mask & in_b)):
        out[f"rate_{side}"] = 100.0 * t.wins[m].sum() / t.games[m].sum() if m.any() else None
    if out["decks_a"] < MIN_DECKS or out["decks_b"] < MIN_DECKS or out["sets"] < 2:
        return out | {"effect": None, "se": None, "verdict": "insufficient data"}
    value, se = effect(t, mask, in_a[mask].astype(float))
    return out | {"effect": value, "se": se, "verdict": verdict(value, se)}


def verdict(value, se):
    if value >= 2 * se:
        return "better"
    if value <= -2 * se:
        return "worse"
    return "not worse" if value - 2 * se > NOT_WORSE else "inconclusive"


def changes(t, version, base=BASE):
    """How often a version's suggestion differs from the base's, in percent."""
    return {
        "pair": 100.0 * float((t.pair[version] != t.pair[base]).mean()),
        "deck": 100.0 * float((t.top[version] != t.top[base]).mean()),
    }


def followed(t, version):
    """Among two-color decks, how many played the suggested pair, and how they
    did against those who didn't."""
    x = (t.main == t.pair[version])[t.two].astype(float)
    value, se = effect(t, t.two, x)
    return {"played": 100.0 * float(x.mean()), "effect": value, "se": se}


def gap_slope(t, version, mask):
    """{set: win rate points per SD of the score gap to the pool's best pair}."""
    out = {}
    for s in sorted(set(t.set[mask])):
        m = mask & (t.set == s)
        gap = t.gap[version][m]
        sd = gap.std()
        if not sd:
            continue
        A = np.hstack([np.ones((m.sum(), 1)), (gap / sd)[:, None],
                       varying(player_columns(t, m))])
        beta, _, _ = newton(A, t.wins[m], t.games[m])
        p = float(expit(A @ beta).mean())
        out[s] = 100.0 * beta[1] * p * (1 - p)
    return out


def slope_changes(t, versions):
    """Each version's mean slope over the sets, and against the base's."""
    mask = t.two & np.all([~np.isnan(t.gap[v]) for v in (BASE, *versions)], axis=0)
    base = gap_slope(t, BASE, mask)
    out = {BASE: {"slope": float(np.mean(list(base.values())))}}
    for v in versions:
        slope = gap_slope(t, v, mask)
        diffs = np.array([slope[s] - base[s] for s in base if s in slope])
        out[v] = {
            "slope": float(np.mean(list(slope.values()))),
            "change": float(diffs.mean()),
            "se": float(diffs.std(ddof=1) / math.sqrt(len(diffs))) if len(diffs) > 1 else None,
        }
    return out


def _signed(value, se=None):
    if value is None:
        return "–"
    text = f"{value:+.2f}"
    return text if se is None else f"{text} ({se:.2f})"


def _ci(r):
    if r["effect"] is None:
        return "–"
    return (f"{r['effect']:+.2f} [{r['effect'] - 1.96 * r['se']:+.2f}, "
            f"{r['effect'] + 1.96 * r['se']:+.2f}]")


def report(t):
    results = {"pools": len(t), "two_color": int(t.two.sum()), "skipped": dict(t.skipped),
               "sets": sorted(set(t.set.tolist()))}
    print(f"{len(t)} pools in {len(results['sets'])} sets, {results['two_color']} with "
          f"two-main-color decks; {int(t.games.sum())} games. Skipped: {dict(t.skipped)}.\n")

    print("## How often the suggestion changes from the blend's\n")
    print("| version | suggested pair | suggested deck |\n|---|---|---|")
    results["changes"] = {v: changes(t, v) for v in VERSIONS}
    for v, c in results["changes"].items():
        print(f"| {v} | {c['pair']:.1f}% | {c['deck']:.1f}% |")

    print("\n### By set: suggested pair changes\n")
    print("| set | " + " | ".join(VERSIONS) + " |\n|---|" + "---|" * len(VERSIONS))
    for s in results["sets"]:
        m = t.set == s
        cells = [f"{100 * (t.pair[v][m] != t.pair[BASE][m]).mean():.1f}%" for v in VERSIONS]
        print(f"| {s} | " + " | ".join(cells) + " |")

    print("\n## Head to head with the blend (deciding)\n")
    print("Pools where the two suggest different pairs and the drafter played one of "
          "them. The effect is how much better decks in the version's pair did, in win "
          "rate points, with set and player controlled and a 95% interval.\n")
    print("| version | pools differing | decks in its pair | in the blend's | raw win rates "
          "| effect | verdict |\n|---|---|---|---|---|---|---|")
    results["head_to_head"] = {v: head_to_head(t, v, BASE) for v in VERSIONS}
    for v, r in results["head_to_head"].items():
        rates = (f"{r['rate_a']:.1f}% vs {r['rate_b']:.1f}%"
                 if r["rate_a"] is not None and r["rate_b"] is not None else "–")
        print(f"| {v} | {r['differ']} | {r['decks_a']} | {r['decks_b']} | {rates} "
              f"| {_ci(r)} | {r['verdict']} |")

    print("\n## The versions against each other (for ties)\n")
    print("| a, against b | decks in a's pair | in b's | effect | verdict |\n|---|---|---|---|---|")
    results["pairwise"] = {}
    for i, a in enumerate(VERSIONS):
        for b in VERSIONS[i + 1:]:
            r = head_to_head(t, a, b)
            results["pairwise"][f"{a} vs {b}"] = r
            print(f"| {a}, against {b} | {r['decks_a']} | {r['decks_b']} | {_ci(r)} "
                  f"| {r['verdict']} |")

    print("\n## Playing the suggested pair (reported, not deciding)\n")
    print("Among two-color decks: the share who played it, and how they did against "
          "those who didn't.\n")
    print("| version | played it | effect |\n|---|---|---|")
    results["followed"] = {v: followed(t, v) for v in (BASE, *VERSIONS)}
    for v, r in results["followed"].items():
        print(f"| {v} | {r['played']:.1f}% | {_signed(r['effect'], r['se'])} |")

    print("\n## The score gap to the pool's best pair (secondary)\n")
    print("Win rate points per SD of the gap between the pool's best build and the "
          "played pair's best, averaged over sets. Change is against the blend: "
          "more negative means the version's gap predicts losses better.\n")
    print("| version | slope | change (SE over sets) |\n|---|---|---|")
    results["gap_slopes"] = slope_changes(t, VERSIONS)
    for v, r in results["gap_slopes"].items():
        print(f"| {v} | {_signed(r['slope'])} | {_signed(r.get('change'), r.get('se'))} |")
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
