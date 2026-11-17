"""Do decks at the app's 17 lands win more than decks at 16 or 18, curve held equal?

    python experiments/2026-11-16-land-count/lands.py results/*.json > lands.md

Reads the features.py output of the Deck score fit's features step. The model is
fit.py's logistic regression of each deck's games won, here on card quality,
missing_fixing, the deck's color group (splash, three main colors, more; as in
experiments/2026-11-16-splash-price), mean mana value (band indicators and a
straight line), the set and the player's buckets, plus indicators for the land
count against 17. Results in game win rate points. See PROTOCOL.md.
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-16-splash-price"))
from colors import group  # noqa: E402
from fit import fit_clustered, varying  # noqa: E402

RULE = 17
SIDES = ("15-", "16", "18", "19+")  # against the rule's 17
GROUPS = ("splash", "three", "more")
BANDS = 5
MIN_DECKS = 300


def side(lands):
    off = lands - RULE
    if off <= -2:
        return "15-"
    if off >= 2:
        return "19+"
    return {-1: "16", 0: "17", 1: "18"}[off]


def indicators(values):
    """Indicator columns for each value but the most common."""
    values = np.asarray(values)
    kinds, counts = np.unique(values, return_counts=True)
    keep = [k for k in kinds if k != kinds[counts.argmax()]]
    return np.array([values == k for k in keep], dtype=float).T.reshape(len(values), -1)


class Decks:
    def __init__(self, files, mdfc_as_spells=False):
        rows, sets, self.dropped = [], [], 0
        for f in files:
            for r in f["rows"]:
                if r["mana"]["cards"] != 40:
                    self.dropped += 1
                    continue
                rows.append(r)
                sets.append(f["set"])
        self.set = np.array(sets)
        self.sets = sorted(set(sets))
        lands = np.array([r["mana"]["lands"] for r in rows])
        if mdfc_as_spells:
            lands = lands - np.array([r["mana"]["mdfc"] for r in rows])
        self.lands = lands
        self.mdfc = np.array([r["mana"]["mdfc"] for r in rows])
        self.side = np.array([side(n) for n in lands])
        self.quality = np.array([r["features"]["card_quality"] for r in rows])
        self.fixing = np.array([r["features"]["missing_fixing"] for r in rows])
        self.group = np.array([group(r) for r in rows])
        self.mv = np.array([r["extra"]["mean_mana_value"] for r in rows])
        self.wins = np.array([r["wins"] for r in rows], dtype=float)
        self.games = np.array([r["games"] for r in rows], dtype=float)
        self.player = np.hstack(
            [indicators([r["skill"] for r in rows]),
             indicators([r["experience"] for r in rows])]
        )
        # Mean mana value quintiles over all decks, fixed before any fit.
        self.edges = np.quantile(self.mv, np.linspace(0, 1, BANDS + 1)[1:-1])
        self.band = np.searchsorted(self.edges, self.mv, side="right")

    def fit(self, mask, clusters=True):
        """{side: (win rate points, SE)} for the decks in mask; sides with no
        decks in mask are left out."""
        sides = [s for s in SIDES if (mask & (self.side == s)).any()]
        S = np.column_stack([self.side[mask] == s for s in sides]).astype(float)
        controls = np.column_stack(
            [self.quality[mask], self.fixing[mask], self.mv[mask]]
            + [self.group[mask] == g for g in GROUPS]
        ).astype(float)
        sets = sorted(set(self.set[mask]))
        dummies = np.array([[s == t for t in sets] for s in self.set[mask]], dtype=float)
        # Bands 2 to 5 against band 1; within one band they are constant and drop.
        bands = np.array([[b == k for k in range(1, BANDS)] for b in self.band[mask]],
                         dtype=float)
        A = np.hstack([S, varying(controls), dummies, varying(bands),
                       varying(self.player[mask])])
        beta, model, cluster = fit_clustered(
            A, self.wins[mask], self.games[mask], self.set[mask] if clusters else None
        )
        p = self.wins[mask].sum() / self.games[mask].sum()
        scale = 100.0 * p * (1 - p)
        out = {}
        for i, s in enumerate(sides):
            var = model[i, i] if cluster is None else max(model[i, i], cluster[i, i])
            out[s] = (scale * beta[i], scale * math.sqrt(var))
        return out


def cell(v):
    if v is None:
        return "–"
    e, se = v
    return f"{e:+.2f} ± {se:.2f} ({e / se:+.1f})"


def by_set(d, mask, pooled, w=None):
    """For each side: (sets on the same side as the pooled estimate, sets counted)."""
    tally = {s: [0, 0] for s in SIDES}
    per = {}
    for t in d.sets:
        m = mask & (d.set == t)
        if not m.any():
            continue
        res = d.fit(m, clusters=False)
        per[t] = res
        for s in SIDES:
            if s not in pooled or (m & (d.side == s)).sum() < MIN_DECKS or s not in res:
                continue
            tally[s][1] += 1
            tally[s][0] += (res[s][0] > 0) == (pooled[s][0] > 0)
    return tally, per


def verdict(est, tally):
    if est is None:
        return "–"
    e, se = est
    agree, n = tally
    passes = e >= 2 * se and n > 0 and agree >= math.ceil(0.7 * n)
    return "**beats 17**" if passes else "no"


def report(d, w, label=""):
    everyone = np.ones(len(d.set), dtype=bool)
    n = len(d.set)
    w(f"{n} decks of exactly 40 cards ({d.dropped} others left out), "
      f"{int(d.games.sum())} games, {len(d.sets)} sets.\n")

    w("## Land counts\n")
    w("| lands | decks | mean mana value | game win rate | with an MDFC counted as a land |")
    w("|---|---|---|---|---|")
    for s in ("15-", "16", "17", "18", "19+"):
        m = d.side == s
        if not m.any():
            continue
        w(f"| {s} | {m.mean():.1%} | {d.mv[m].mean():.2f} | "
          f"{d.wins[m].sum() / d.games[m].sum():.1%} | {(d.mdfc[m] > 0).mean():.1%} |")
    w()
    edges = ", ".join(f"{e:.2f}" for e in d.edges)
    w(f"Mean mana value bands (quintiles of all decks), edges: {edges}.\n")
    w("| band | " + " | ".join(("15-", "16", "17", "18", "19+")) + " |")
    w("|---" * 6 + "|")
    for b in range(BANDS):
        m = d.band == b
        w(f"| {b + 1} | " + " | ".join(
            f"{(d.side[m] == s).mean():.1%}" for s in ("15-", "16", "17", "18", "19+")) + " |")
    w()

    w("## Pooled: each land count against 17\n")
    w("Game win rate points, ± SE (the larger of model and set-clustered), "
      "(SEs). Positive: decks at that count won more than decks at 17.\n")
    pooled = d.fit(everyone)
    tally, per = by_set(d, everyone, pooled)
    w("| lands | against 17 | same sign by set | by the rule |")
    w("|---|---|---|---|")
    for s in SIDES:
        est = pooled.get(s)
        t = tally[s]
        w(f"| {s} | {cell(est)} | {t[0]}/{t[1]} | {verdict(est, t)} |")
    w()

    w("## By mean mana value band\n")
    w("| band | " + " | ".join(SIDES) + " |")
    w("|---" * (len(SIDES) + 1) + "|")
    band_verdicts = []
    for b in range(BANDS):
        m = d.band == b
        res = d.fit(m)
        t, _ = by_set(d, m, res)
        cells = []
        for s in SIDES:
            est = res.get(s) if (m & (d.side == s)).sum() >= MIN_DECKS else None
            v = verdict(est, t[s])
            if v != "no" and v != "–":
                band_verdicts.append((b + 1, s, est, t[s]))
            cells.append(f"{cell(est)} {t[s][0]}/{t[s][1]}" + (" ✔" if v.startswith("**") else ""))
        w(f"| {b + 1} | " + " | ".join(cells) + " |")
    w("\nEach cell: estimate against 17 in that band, and sets on the same side of "
      f"zero out of sets with {MIN_DECKS}+ decks at that count in the band. ✔ passes "
      "the rule.\n")

    w("## Each set alone\n")
    w("| set | " + " | ".join(SIDES) + " |")
    w("|---" * (len(SIDES) + 1) + "|")
    for t in d.sets:
        res = per.get(t, {})
        w(f"| {t} | " + " | ".join(
            (f"{res[s][0]:+.1f}" if s in res and ((d.set == t) & (d.side == s)).sum() >= MIN_DECKS else "–")
            for s in SIDES) + " |")
    w()
    return pooled, tally, band_verdicts


def main(argv=None):
    paths = argv if argv is not None else sys.argv[1:]
    files = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            files.append(json.load(f))
    w = print
    w("# Land count against the app's 17\n")
    w("MDFCs (spell // land) counted as lands, as the app counts them.\n")
    pooled, tally, bands = report(Decks(files), w)
    w("## Verdict by the rule\n")
    passed = [s for s in SIDES if verdict(pooled.get(s), tally[s]).startswith("**")]
    w(f"- Pooled, a count that beats 17: **{', '.join(passed) or 'none'}**.")
    if bands:
        for b, s, est, t in bands:
            w(f"- Band {b}: {s} beats 17, {cell(est)}, same sign in {t[0]}/{t[1]} sets.")
    else:
        w("- By band: no count beats 17 in any band.")
    w()
    w("# Sensitivity: MDFCs counted as spells\n")
    w("Not part of the rule; shows whether the answer rests on how MDFCs count.\n")
    report(Decks(files, mdfc_as_spells=True), w)


if __name__ == "__main__":
    main()
