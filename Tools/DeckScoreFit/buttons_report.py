"""Whether Auto lands' simulation and Auto optimize earn their place: the report
on buttons.py's runs.

    python Tools/DeckScoreFit/buttons_report.py results/*.json.gz --json report.json

See experiments/2026-11-13-builder-leftovers/PROTOCOL.md. Needs NumPy.
"""

import argparse
import gzip
import json
import math
from collections import Counter

import numpy as np

from fit import fit_clustered, varying
from score_rating import indicators

# Decks an outcome needs.
MIN_DECKS = 100
# Auto optimize is removed if it changes fewer than this percent of decks.
RARE = 5.0
CHOICES = ("rule", "simulated", "pips")
NO_SWAP = "Base Deck"
# Swaps of a spell for a land. They move the deck score only by changing which
# spells its mean is over, so the deciding change counts them as zero.
LAND_COUNT = ("Play 18 Lands", "Play 16 Lands")


def moved(a, b):
    """Lands that differ between two splits of the same number of basics."""
    return sum(abs(x - y) for x, y in zip(a, b)) / 2.0


class Table:
    """buttons.py's rows as arrays."""

    def __init__(self, paths):
        cols = {k: [] for k in ("set", "skill", "experience", "wins", "games", "quality")}
        self.from_played = {c: [] for c in CHOICES}
        self.apart, self.kind, self.gain, self.land_change = [], [], [], []
        self.skipped = Counter()
        for path in paths:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            self.skipped.update(data["skipped"])
            price = data["win_points_per_score"]
            for r in data["rows"]:
                r["set"] = data["set"]
                for key, values in cols.items():
                    values.append(r[key])
                lands = r["lands"]
                for c in CHOICES:
                    self.from_played[c].append(moved(lands[c], lands["played"]))
                self.apart.append(moved(lands["rule"], lands["simulated"]))
                o = r["optimize"]
                self.kind.append(o["kind"] if o else "")
                self.gain.append(
                    price * (o["score_after"] - o["score_before"]) if o else math.nan
                )
                self.land_change.append(o["lands_after"] - o["lands_before"] if o else 0)
        for key, values in cols.items():
            numeric = key in ("wins", "games", "quality")
            setattr(self, key, np.array(values, dtype=float if numeric else None))
        self.from_played = {c: np.array(v) for c, v in self.from_played.items()}
        self.apart = np.array(self.apart)
        self.kind = np.array(self.kind)
        self.gain = np.array(self.gain, dtype=float)
        self.land_change = np.array(self.land_change)


def clustered_mean(x, clusters):
    """The mean of x and its SE, clustered (plain with a single cluster)."""
    n, mean = len(x), float(np.mean(x))
    groups = np.unique(clusters)
    if len(groups) < 2:
        return mean, float(np.std(x, ddof=1) / math.sqrt(n)) if n > 1 else math.nan
    sums = np.array([(x[clusters == g] - mean).sum() for g in groups])
    g = len(groups)
    return mean, float(math.sqrt(g / (g - 1) * (sums**2).sum()) / n)


def agreement(t):
    """How far each choice of basics is from the drafter's, in lands, and the
    simulation's distance less the rule's and the rule's less pips'."""
    out = {"decks": len(t.set)}
    for c in CHOICES:
        d = t.from_played[c]
        out[c] = {"lands": float(d.mean()), "same": 100.0 * float((d == 0).mean())}
    for name, a, b in (("simulated_less_rule", "simulated", "rule"),
                       ("rule_less_pips", "rule", "pips")):
        mean, se = clustered_mean(t.from_played[a] - t.from_played[b], t.set)
        out[name] = {"effect": mean, "se": se}
    return out


def lands_outcome(t):
    """Among decks where the simulation's basics differ from the rule's, the
    effect of a full move from the rule's to the simulation's, in win rate
    points, with card quality, the set and the player controlled."""
    mask = t.apart > 0
    decks = int(mask.sum())
    if decks < MIN_DECKS:
        return {"decks": decks, "effect": None, "se": None}
    position = (t.from_played["rule"][mask] - t.from_played["simulated"][mask]) / t.apart[mask]
    sets = sorted(set(t.set[mask].tolist()))
    dummies = np.array([t.set[mask] == s for s in sets], dtype=float).T
    player = np.hstack([indicators(t.skill[mask]), indicators(t.experience[mask])])
    A = np.hstack([position[:, None], t.quality[mask][:, None], dummies, varying(player)])
    wins, games = t.wins[mask], t.games[mask]
    beta, model, cluster = fit_clustered(A, wins, games, t.set[mask])
    variance = model[0, 0] if cluster is None else max(model[0, 0], cluster[0, 0])
    p = wins.sum() / games.sum()
    scale = 100.0 * p * (1 - p)
    return {"decks": decks, "mean_position": float(position.mean()),
            "at_rule": 100.0 * float((position == -1).mean()),
            "at_simulated": 100.0 * float((position == 1).mean()),
            "effect": scale * beta[0], "se": scale * math.sqrt(variance)}


def optimize_summary(t):
    """How often Auto optimize changes the deck, by which swap, and what each
    does to the deck score, in win rate points."""
    ran = t.kind != ""
    kinds, sets, gain = t.kind[ran], t.set[ran], t.gain[ran]
    mean, se = clustered_mean(np.where(np.isin(kinds, LAND_COUNT), 0.0, gain), sets)
    out = {"decks": int(ran.sum()), "changed": 100.0 * float((kinds != NO_SWAP).mean()),
           "effect": mean, "se": se, "kinds": {},
           "lands": {str(k): 100.0 * n / int(ran.sum())
                     for k, n in sorted(Counter(t.land_change[ran].tolist()).items())}}
    for kind, n in Counter(kinds.tolist()).most_common():
        m = kinds == kind
        k_mean, k_se = clustered_mean(gain[m], sets[m])
        out["kinds"][kind] = {"share": 100.0 * n / len(kinds), "effect": k_mean, "se": k_se}
    return out


def lands_verdict(outcome, simulated_less_rule):
    """keep or remove the simulation, from the games and then from agreement."""
    value, se = outcome.get("effect"), outcome.get("se")
    if value is not None and value >= 2 * se:
        return "keep"
    if value is not None and value <= -2 * se:
        return "remove"
    nearer = -simulated_less_rule["effect"]
    return "keep" if nearer >= 2 * simulated_less_rule["se"] else "remove"


def optimize_verdict(summary):
    if summary["changed"] < RARE:
        return "remove"
    if summary["effect"] <= -2 * summary["se"]:
        return "remove"
    if summary["effect"] >= 2 * summary["se"]:
        return "keep"
    return "no verdict"


def _pm(r, digits=2):
    if r.get("effect") is None:
        return "–"
    lo, hi = r["effect"] - 1.96 * r["se"], r["effect"] + 1.96 * r["se"]
    return f"{r['effect']:+.{digits}f} [{lo:+.{digits}f}, {hi:+.{digits}f}]"


def report(t):
    results = {"decks": len(t.set), "skipped": dict(t.skipped)}
    print(f"{len(t.set)} decks in {len(set(t.set.tolist()))} sets. "
          f"Skipped: {dict(t.skipped)}.\n")

    print("## Auto lands: the simulation against the rule it starts from\n")
    differ = t.apart > 0
    results["differ"] = {
        "share": 100.0 * float(differ.mean()),
        "one_land": 100.0 * float((t.apart[differ] == 1).mean()) if differ.any() else None,
    }
    print(f"The simulation's basics differ from the rule's in "
          f"{results['differ']['share']:.1f}% of decks"
          + (f", by one land in {results['differ']['one_land']:.1f}% of those."
             if differ.any() else "."))
    a = results["agreement"] = agreement(t)
    print("\n| basics chosen by | lands from the drafter's | same as the drafter's |")
    print("|---|---|---|")
    for c, label in (("rule", "the app's rule"), ("simulated", "Auto lands' simulation"),
                     ("pips", "share of pips")):
        print(f"| {label} | {a[c]['lands']:.3f} | {a[c]['same']:.1f}% |")
    print(f"\n- Simulation less rule, in lands from the drafter's: "
          f"{_pm(a['simulated_less_rule'], 3)}. Negative is nearer the drafter.")
    print(f"- Rule less pips: {_pm(a['rule_less_pips'], 3)}.")
    o = results["lands_outcome"] = lands_outcome(t)
    print(f"\nOutcome, a full move from the rule's basics to the simulation's, in win "
          f"rate points at the same card quality: {_pm(o)}, on {o['decks']} decks"
          + (f" ({o['at_rule']:.1f}% played the rule's, {o['at_simulated']:.1f}% the "
             f"simulation's)." if o.get("effect") is not None else "."))

    print("\n## Auto optimize\n")
    s = results["optimize"] = optimize_summary(t)
    print(f"It changes {s['changed']:.1f}% of {s['decks']} decks. Deck score change in "
          f"win rate points, with the swaps of a spell for a land counted as zero "
          f"(deciding): {_pm(s, 3)}.\n")
    print("| swap | decks | deck score change, win rate points |\n|---|---|---|")
    for kind, k in s["kinds"].items():
        print(f"| {kind} | {k['share']:.1f}% | {_pm(k, 3)} |")
    print("\nLand count change: "
          + ", ".join(f"{int(k):+d} in {v:.1f}%" for k, v in s["lands"].items()) + ".")

    results["verdicts"] = {
        "auto_lands_simulation": lands_verdict(o, a["simulated_less_rule"]),
        "auto_optimize": optimize_verdict(s),
    }
    print("\n## Verdicts\n")
    print("| feature | verdict |\n|---|---|")
    print(f"| Auto lands' simulation | {results['verdicts']['auto_lands_simulation']} |")
    print(f"| Auto optimize | {results['verdicts']['auto_optimize']} |")
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+", help="buttons.py's outputs")
    parser.add_argument("--json", help="Where to write the numbers")
    args = parser.parse_args(argv)
    results = report(Table(args.paths))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
