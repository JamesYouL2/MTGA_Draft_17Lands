"""Whether Tempo builds and safe-deck promotion earn their place: the report on
builds.py's runs.

    python Tools/DeckScoreFit/deck_variants.py results/*.json.gz --json report.json

See experiments/2026-11-08-deck-variants/PROTOCOL.md. Needs NumPy.
"""

import argparse
import gzip
import json
import math
from collections import Counter

import numpy as np

from fit import fit_clustered, varying
from score_rating import effect, player_columns

# Decks the outcome comparisons need on each side.
MIN_DECKS = 100
# Removed if it changes the top deck in fewer than this percent of pools.
RARE = 5.0
COMPARED = ("no-tempo", "no-promotion", "neither")
BASES = {"": "blend", "sim-": "sim"}


def _top_two(shown):
    return shown["shown"][:2]


class Table:
    """What the report needs from builds.py's rows, as arrays, one set at a time."""

    def __init__(self, paths):
        self.rows = {k: [] for k in ("set", "main", "skill", "experience", "wins", "games")}
        self.played_safe, self.played_top, self.quality, self.nearer = [], [], [], []
        self.promoted_different = []
        self.compared = {
            prefix + name: {"top": [], "second": [], "shown": []}
            for prefix in BASES for name in COMPARED
        }
        self.compare_mask = {prefix: [] for prefix in BASES}
        self.skipped = Counter()
        for path in paths:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            self.skipped.update(data["skipped"])
            for r in data["rows"]:
                self._read(r, data["set"])
            del data
        for key, values in self.rows.items():
            setattr(self, key, np.array(values, dtype=float if key in ("wins", "games") else None))
        self.quality = np.array(self.quality, dtype=float)
        self.nearer = np.array(self.nearer, dtype=float)
        self.played_safe = np.array(self.played_safe, dtype=bool)
        self.played_top = np.array(self.played_top, dtype=bool)
        self.promoted_different = np.array(self.promoted_different, dtype=bool)
        self.has = {prefix: np.array(v, dtype=bool) for prefix, v in self.compare_mask.items()}
        self.change = {
            name: {k: np.array(v, dtype=bool) for k, v in columns.items()}
            for name, columns in self.compared.items()
        }

    def _read(self, r, set_name):
        r["set"] = set_name
        for key, values in self.rows.items():
            values.append(r[key])
        versions = r["versions"]
        played = r.get("played") or {}
        self.quality.append(played.get("quality", math.nan))
        nearer = played.get("nearer")
        self.nearer.append(math.nan if nearer is None else nearer)

        for prefix, base in BASES.items():
            present = base in versions
            self.compare_mask[prefix].append(present)
            for name in COMPARED:
                columns = self.compared[prefix + name]
                if not present:
                    for values in columns.values():
                        values.append(False)
                    continue
                head = versions[prefix + name]
                columns["top"].append(head["shown"][0] != versions[base]["shown"][0])
                columns["second"].append(_top_two(head) != _top_two(versions[base]))
                columns["shown"].append(set(head["shown"]) != set(versions[base]["shown"]))

        full, plain = versions["blend"], versions["no-promotion"]
        moved = full["shown"][0] != plain["shown"][0]
        safe, top = set(full["identity"]), set(plain["identity"])
        colors = set(r["main"] + r["splash"])
        different = moved and safe != top
        self.promoted_different.append(different)
        self.played_safe.append(different and colors <= safe)
        self.played_top.append(different and top <= colors and not colors <= safe)


def rates(t):
    """How often each version changes what's shown, in percent of pools."""
    out = {}
    for prefix in BASES:
        mask = t.has[prefix]
        if not mask.any():
            continue
        for name in COMPARED:
            change = t.change[prefix + name]
            out[prefix + name] = {
                "pools": int(mask.sum()),
                **{k: 100.0 * float(change[k][mask].mean()) for k in ("top", "second", "shown")},
            }
    return out


def tempo_outcome(t, control_quality=True):
    """Among two-color decks in a pair whose Tempo and Consistent builds differ, the
    effect of a full move from Consistent's cards to Tempo's, with the pair in the
    set and the player controlled. With card quality too, unless told not to."""
    mask = ~np.isnan(t.nearer) & ~np.isnan(t.quality)
    decks = int(mask.sum())
    if decks < MIN_DECKS:
        return {"decks": decks, "effect": None, "se": None}
    groups = np.char.add(np.char.add(t.set[mask], ":"), t.main[mask])
    labels = sorted(set(groups.tolist()))
    index = {g: i for i, g in enumerate(labels)}
    rows = np.arange(decks)
    dummies = np.zeros((decks, len(labels)))
    dummies[rows, [index[g] for g in groups.tolist()]] = 1.0
    terms = [t.nearer[mask][:, None]]
    if control_quality:
        terms.append(t.quality[mask][:, None])
    terms += [dummies, varying(player_columns(t, mask))]
    A = np.hstack(terms)
    wins, games = t.wins[mask], t.games[mask]
    beta, model, cluster = fit_clustered(A, wins, games, t.set[mask])
    variance = model[0, 0] if cluster is None else max(model[0, 0], cluster[0, 0])
    p = wins.sum() / games.sum()
    scale = 100.0 * p * (1 - p)
    return {"decks": decks, "mean_nearer": float(t.nearer[mask].mean()),
            "effect": scale * beta[0], "se": scale * math.sqrt(variance)}


def promotion_outcome(t):
    """In pools where promotion changes the top deck's colors, how much better
    drafters did in the safe deck's colors than in the unpromoted top's."""
    mask = t.played_safe | t.played_top
    safe, top = int(t.played_safe.sum()), int(t.played_top.sum())
    out = {"pools": int(t.promoted_different.sum()), "decks_safe": safe, "decks_top": top}
    for side, m in (("rate_safe", t.played_safe), ("rate_top", t.played_top)):
        out[side] = 100.0 * t.wins[m].sum() / t.games[m].sum() if m.any() else None
    if safe < MIN_DECKS or top < MIN_DECKS or len(set(t.set[mask])) < 2:
        return out | {"effect": None, "se": None}
    value, se = effect(t, mask, t.played_safe[mask].astype(float))
    return out | {"effect": value, "se": se}


def verdict(top_change, outcome):
    """remove, keep or no verdict, from the top-deck change and the feature's
    outcome, signed so that positive favors the feature."""
    value, se = outcome.get("effect"), outcome.get("se")
    if value is not None and value >= 2 * se:
        return "keep"
    if value is not None and value <= -2 * se:
        return "remove"
    return "remove" if top_change < RARE else "no verdict"


def _pm(r):
    if r.get("effect") is None:
        return "–"
    return (f"{r['effect']:+.2f} [{r['effect'] - 1.96 * r['se']:+.2f}, "
            f"{r['effect'] + 1.96 * r['se']:+.2f}]")


def report(t):
    results = {"pools": len(t.set), "skipped": dict(t.skipped), "rates": rates(t)}
    print(f"{len(t.set)} pools in {len(set(t.set.tolist()))} sets; {int(t.games.sum())} games. "
          f"Skipped: {dict(t.skipped)}.\n")
    print("## How often it changes what's shown, against today's\n")
    print("With the simulator off on every pool, and on for the first pools of each set. "
          "**Top 2** counts either of the first two changing.\n")
    print("| version | pools | top deck | top 2 | list shown |\n|---|---|---|---|---|")
    for name, r in results["rates"].items():
        print(f"| {name} | {r['pools']} | {r['top']:.2f}% | {r['second']:.2f}% | {r['shown']:.2f}% |")

    print("\n### By set, top deck, simulator off\n")
    print("| set | no-tempo | no-promotion |\n|---|---|---|")
    results["by_set"] = {}
    for s in sorted(set(t.set.tolist())):
        m = t.set == s
        by = {n: 100.0 * float(t.change[n]["top"][m].mean()) for n in ("no-tempo", "no-promotion")}
        results["by_set"][s] = by
        print(f"| {s} | {by['no-tempo']:.2f}% | {by['no-promotion']:.2f}% |")

    print("\n## Tempo: playing nearer its cards\n")
    print("Among two-color decks where the pair's Tempo and Consistent builds differ, a "
          "full move from Consistent's cards to Tempo's, in win rate points, within the "
          "pair in the set, with the player controlled.\n")
    results["tempo_outcome"] = tempo_outcome(t)
    results["tempo_outcome_no_quality"] = tempo_outcome(t, control_quality=False)
    print(f"- At the same card quality (deciding): {_pm(results['tempo_outcome'])}, "
          f"on {results['tempo_outcome']['decks']} decks.")
    print(f"- Without controlling for it: {_pm(results['tempo_outcome_no_quality'])}.")

    print("\n## Promotion: drafters in the safe deck's colors against the top's\n")
    p = results["promotion_outcome"] = promotion_outcome(t)
    print(f"Promotion changes the top deck's colors in {p['pools']} pools. "
          f"{p['decks_safe']} decks played the safe colors"
          + (f" at {p['rate_safe']:.1f}%" if p["rate_safe"] is not None else "")
          + f", and {p['decks_top']} the top's"
          + (f" at {p['rate_top']:.1f}%" if p["rate_top"] is not None else "") + ".")
    print(f"\nEffect in win rate points, safe over the top's, set and player controlled: {_pm(p)}.")

    print("\n## Verdicts\n")
    print("| feature | top deck changes | outcome | verdict |\n|---|---|---|---|")
    tempo_rate = results["rates"]["no-tempo"]["top"]
    promotion_rate = results["rates"]["no-promotion"]["top"]
    results["verdicts"] = {
        "tempo": verdict(tempo_rate, results["tempo_outcome"]),
        "promotion": verdict(promotion_rate, p),
    }
    print(f"| Tempo build | {tempo_rate:.2f}% | {_pm(results['tempo_outcome'])} "
          f"| {results['verdicts']['tempo']} |")
    print(f"| Safe-deck promotion | {promotion_rate:.2f}% | {_pm(p)} "
          f"| {results['verdicts']['promotion']} |")
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+", help="builds.py's outputs")
    parser.add_argument("--json", help="Where to write the numbers")
    args = parser.parse_args(argv)
    results = report(Table(args.paths))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
