"""PROTOCOL.md's E1 report: blind spots in the deck score, the shape of card
quality, and whether the blind spots flip the crowd heads' deck deficit.

    python experiments/2026-11-22-deck-value/e1.py e1-*.json.gz \
        [--detail DETAIL_RESULTS] [--json e1.json]

Reads deckfacts.py's files. Each fit is a binomial logistic regression of a
deck's games won with set indicators and the player's skill and experience
buckets (as Tools/DeckScoreFit/fit.py). SEs are the larger of the
dispersion-widened model SE and the set-clustered sandwich SE. --detail is an
Advisor heads run's results with `--detail --simulate` (folders of base.json
and lgbm-strong-noalsa.json), for the flip check.
"""

import argparse
import glob
import gzip
import json
import os
import sys
from collections import Counter

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))

CANDIDATES = ["creatures", "cheap", "cheap_spells", "removal", "main_colors", "splash",
              "mana_value", "curve_gaps", "lands"]
SHAPE = ["q_top3", "q_top5", "q_low5", "q_sd", "q_max"]
PARTS = ["two_colors", "missing_fixing"]  # the deck score's other fitted parts
FLIP = ["creatures", "cheap", "removal", "colors", "mana_value"]  # what sim parts have
RULE_SES, RULE_POINTS = 3.0, 0.5


class Data:
    def __init__(self, paths):
        rows = []
        for path in paths:
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            rows += [dict(r, set=data["set"]) for r in data["rows"]]
        self.read = len(rows)
        keep = [r for r in rows if not r["f"]["missing_spells"] and r["games"]
                and all(r["f"].get(k) is not None for k in SHAPE + CANDIDATES)]
        self.rows = keep
        self.set = np.array([r["set"] for r in keep])
        self.sets = sorted(set(self.set))
        self.wins = np.array([r["wins"] for r in keep], dtype=float)
        self.games = np.array([r["games"] for r in keep], dtype=float)
        cols = []
        for key in ("skill", "experience"):
            values = [r[key] for r in keep]
            for value, _ in Counter(values).most_common()[1:]:
                cols.append([v == value for v in values])
        self.player = np.array(cols, dtype=float).T
        self.setdum = np.array([[s == t for t in self.sets] for s in self.set], dtype=float)
        self.raw = {}

    def col(self, name):
        if name not in self.raw:
            if name == "colors":
                v = [r["f"]["main_colors"] + r["f"]["splash"] for r in self.rows]
            elif name == "q_mean_sq":
                z = self.z("card_quality")
                self.raw[name] = z**2
                return self.raw[name]
            else:
                v = [r["f"][name] for r in self.rows]
            self.raw[name] = np.array(v, dtype=float)
        return self.raw[name]

    def z(self, name):
        """The column standardized within set."""
        x = self.col(name).copy()
        for s in self.sets:
            m = self.set == s
            sd = x[m].std()
            x[m] = (x[m] - x[m].mean()) / (sd if sd > 0 else 1.0)
        return x


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def newton(A, wins, games, offset=0.0):
    beta = np.zeros(A.shape[1])
    ridge = 1e-8 * np.eye(A.shape[1])
    for _ in range(100):
        p = expit(A @ beta + offset)
        Hm = A.T @ (A * (games * p * (1 - p))[:, None]) + ridge
        step = np.linalg.solve(Hm, A.T @ (wins - games * p) - ridge @ beta)
        beta += step
        if np.abs(step).max() < 1e-9:
            break
    p = expit(A @ beta + offset)
    Hm = A.T @ (A * (games * p * (1 - p))[:, None]) + ridge
    return beta, Hm, p


def fit(d, X, mask=None, sets=True):
    """(beta of X's columns, their SEs) with the controls; SEs as the docstring."""
    m = np.ones(len(d.wins), bool) if mask is None else mask
    ctrl = [d.player[m]] + ([d.setdum[m]] if sets else [np.ones((m.sum(), 1))])
    A = np.column_stack([X[m]] + ctrl)
    w, g = d.wins[m], d.games[m]
    beta, Hm, p = newton(A, w, g)
    Hinv = np.linalg.inv(Hm)
    disp = ((w - g * p) ** 2 / (g * p * (1 - p))).sum() / max(1, len(w) - A.shape[1])
    model = np.diag(Hinv) * max(1.0, disp)
    k = X.shape[1]
    groups = np.unique(d.set[m])
    if len(groups) > 1:
        score = A * (w - g * p)[:, None]
        S = np.array([score[d.set[m] == s].sum(axis=0) for s in groups])
        G = len(groups)
        cluster = np.diag(Hinv @ (S.T @ S) @ Hinv) * G / (G - 1)
        var = np.maximum(model, cluster)
    else:
        var = model
    return beta[:k], np.sqrt(var[:k])


def heldout_gain(d, base_cols, more_cols):
    """{set: per-game log-loss of base less base+more, in 1e-4 nats}, each set
    predicted by a fit to the others, its own intercept refit."""
    out = {}
    for s in d.sets:
        test = d.set == s
        losses = []
        for cols in (base_cols, base_cols + more_cols):
            X = np.column_stack(cols)
            A = np.column_stack([X, d.player, d.setdum])
            beta, _, _ = newton(A[~test], d.wins[~test], d.games[~test])
            k = X.shape[1] + d.player.shape[1]
            offset = np.column_stack([X, d.player])[test] @ beta[:k]
            offset -= offset.mean()  # the refit intercept takes the level
            ones = np.ones((test.sum(), 1))
            b0, _, p = newton(ones, d.wins[test], d.games[test], offset)
            w, g = d.wins[test], d.games[test]
            ll = (w * np.log(p) + (g - w) * np.log(1 - p)).sum() / g.sum()
            losses.append(-ll)
        out[s] = 1e4 * (losses[0] - losses[1])
    return out


def set_signs(d, base_cols, f):
    """How many sets give f's coefficient (fit alone, with the score) each sign."""
    pos = 0
    for s in d.sets:
        m = d.set == s
        b, _ = fit(d, np.column_stack(base_cols + [f]), m, sets=False)
        pos += b[-1] > 0
    return pos, len(d.sets) - pos


def verdict(b, se, points):
    return "blind spot" if abs(b) / se >= RULE_SES and abs(points) >= RULE_POINTS else "–"


def flip(detail_root, coefs, rating_coef):
    """Head minus base value change per draft, in points, over sim decks;
    combined over salts. coefs: {part: log-odds per unit}."""
    import heads as H

    C, R = H.C, H.R
    rating, value, keys = [], [], []
    for folder in sorted(glob.glob(os.path.join(detail_root, "*"))):
        b, h = os.path.join(folder, "base.json"), os.path.join(folder, "lgbm-strong-noalsa.json")
        if not (os.path.exists(b) and os.path.exists(h)):
            continue
        base, head = H.read(b), H.read(h)
        salt = os.path.basename(folder).rsplit("-", 1)[-1]
        theirs = {d["id"]: d for d in head["drafts"]}
        for d in base["drafts"]:
            o = theirs.get(d["id"])
            pb = (d.get("sim") or {}).get("parts")
            ph = ((o or {}).get("sim") or {}).get("parts")
            if not pb or not ph or any(pb.get(k) is None or ph.get(k) is None for k in FLIP):
                continue
            dr = ph["rating"] - pb["rating"]
            rating.append(dr)
            value.append(dr + sum(coefs[k] / rating_coef * (ph[k] - pb[k]) for k in FLIP))
            keys.append((base["set"], f"{salt}:{d['id']}"))
        del base, head, theirs
    out = {"drafts": len(keys)}
    if not keys:
        return out
    for name, arr in (("rating", np.array(rating)), ("value", np.array(value))):
        out[name] = H.combined(C.by_salt(keys, lambda i, a=arr: a[i].mean()))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--detail")
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    d = Data(args.paths)
    res = {"decks": len(d.rows), "read": d.read, "sets": d.sets}
    print(f"## E1: {len(d.rows)} decks of {d.read} read, {len(d.sets)} sets\n")

    score = d.col("score")
    b0, s0 = fit(d, score[:, None])
    res["score_only"] = [float(b0[0]), float(s0[0])]
    print(f"Deck score alone: {b0[0]:.5f} log-odds per point (SE {s0[0]:.5f}); app constant 0.05099.\n")

    # Blind spots: alone, then joint.
    print("### Blind spots (effect in deck-score points per SD of the feature)\n")
    print("| feature | mean | SD | alone: β (SE) | alone pts/SD | sets +/− | joint: β (SE) SEs | joint pts/SD | held-out gain (1e-4 nats, sets > 0) | verdict |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    zs = {f: d.z(f) for f in CANDIDATES}
    bj, sj = fit(d, np.column_stack([score] + [zs[f] for f in CANDIDATES]))
    res["joint"] = {"score": [float(bj[0]), float(sj[0])]}
    res["blind"] = {}
    gains_joint = heldout_gain(d, [score], [zs[f] for f in CANDIDATES])
    for i, f in enumerate(CANDIDATES):
        ba, sa = fit(d, np.column_stack([score, zs[f]]))
        pos, neg = set_signs(d, [score], zs[f])
        gains = heldout_gain(d, [score], [zs[f]])
        jb, js = bj[i + 1], sj[i + 1]
        pts_a, pts_j = ba[1] / ba[0], jb / bj[0]
        v = verdict(jb, js, pts_j)
        res["blind"][f] = dict(alone=[float(ba[1]), float(sa[1])], alone_points=float(pts_a),
                               signs=[int(pos), int(neg)], joint=[float(jb), float(js)],
                               joint_points=float(pts_j), heldout=gains, verdict=v)
        raw = d.col(f)
        g = np.array(list(gains.values()))
        print(f"| {f} | {raw.mean():.2f} | {raw.std():.2f} | {ba[1]:+.4f} ({sa[1]:.4f}) | {pts_a:+.2f} | {pos}/{neg} "
              f"| {jb:+.4f} ({js:.4f}) {jb / js:+.1f} | {pts_j:+.2f} | {g.mean():+.1f} ({(g > 0).sum()}/{len(g)}) | {v} |")
    g = np.array(list(gains_joint.values()))
    res["joint_heldout"] = gains_joint
    print(f"\nJoint fit: deck score {bj[0]:.5f} ({sj[0]:.5f}); held-out gain of all candidates over the score: "
          f"{g.mean():+.1f} per game (1e-4 nats), better in {(g > 0).sum()} of {len(g)} sets.\n")

    # Quality shape.
    cq = d.col("card_quality")
    parts = [d.col(k) for k in PARTS]
    bq, sq = fit(d, np.column_stack([cq] + parts))
    per_point = bq[0] / 12.0  # log-odds per deck-score point, from card quality
    res["shape_base"] = [float(bq[0]), float(sq[0])]
    print("### Quality shape (beyond mean card quality and the other parts)\n")
    print(f"Card quality alone: {bq[0]:.4f} per SD of card ratings (SE {sq[0]:.4f}), so {per_point:.5f} log-odds per point.\n")
    print("| stat | mean | deck SD | β per deck SD (SE) SEs | pts per deck SD | card quality β with it | verdict |")
    print("|---|---|---|---|---|---|---|")
    res["shape"] = {}
    for st in SHAPE:
        b, s = fit(d, np.column_stack([cq] + parts + [d.z(st)]))
        pts = b[-1] / per_point
        v = verdict(b[-1], s[-1], pts)
        res["shape"][st] = dict(beta=[float(b[-1]), float(s[-1])], points=float(pts), cq=float(b[0]), verdict=v)
        raw = d.col(st)
        print(f"| {st} | {raw.mean():+.2f} | {raw.std():.2f} | {b[-1]:+.4f} ({s[-1]:.4f}) {b[-1] / s[-1]:+.1f} | {pts:+.2f} | {b[0]:.4f} | {v} |")
    b, s = fit(d, np.column_stack([cq] + parts + [d.z("q_top5"), d.z("q_low5")]))
    res["shape"]["top5+low5"] = dict(top5=[float(b[-2]), float(s[-2])], low5=[float(b[-1]), float(s[-1])],
                                     cq=float(b[0]))
    print(f"\nTop-5 and weakest-5 together: top-5 {b[-2]:+.4f} ({s[-2]:.4f}) = {b[-2] / per_point:+.2f} pts/SD; "
          f"weakest-5 {b[-1]:+.4f} ({s[-1]:.4f}) = {b[-1] / per_point:+.2f} pts/SD; card quality {b[0]:.4f}.\n")
    # Linearity: squared standardized card quality, and deciles held out.
    zq = d.z("card_quality")
    b, s = fit(d, np.column_stack([zq, zq**2] + parts))
    pts = b[1] / per_point
    res["linearity"] = dict(sq=[float(b[1]), float(s[1])], points=float(pts), verdict=verdict(b[1], s[1], pts))
    dec = np.zeros((len(zq), 9))
    for s_ in d.sets:
        m = d.set == s_
        edges = np.quantile(zq[m], np.linspace(0.1, 0.9, 9))
        dec[m] = (zq[m][:, None] > edges[None, :]).astype(float)
    gains = heldout_gain(d, [zq] + parts, [dec])
    g = np.array(list(gains.values()))
    res["linearity"]["deciles_heldout"] = gains
    print(f"Linearity: squared card quality (per deck SD²) {b[1]:+.4f} ({s[1]:.4f}) {b[1] / s[1]:+.1f} SEs, "
          f"{pts:+.2f} pts at ±1 SD -> {'not linear' if res['linearity']['verdict'] != '–' else 'linear'}. "
          f"Deciles over linear, held out: {g.mean():+.1f} (1e-4 nats), better in {(g > 0).sum()} of {len(g)} sets.\n")

    # Flip: unstandardized parts the sim decks have.
    bf, sf = fit(d, np.column_stack([score] + [d.col(k) for k in FLIP]))
    coefs = {k: float(bf[i + 1]) for i, k in enumerate(FLIP)}
    res["flip_fit"] = {"score": [float(bf[0]), float(sf[0])]} | {
        k: [float(bf[i + 1]), float(sf[i + 1]), float(bf[i + 1] / bf[0])] for i, k in enumerate(FLIP)}
    print("### Crowd-deck flip\n")
    print("Fit on E1 decks, per unit (points per unit = β / β_score): " + "; ".join(
        f"{k} {bf[i + 1]:+.4f} ({sf[i + 1]:.4f}) = {bf[i + 1] / bf[0]:+.2f} pts" for i, k in enumerate(FLIP)) + "\n")
    out = flip(args.detail, coefs, float(bf[0])) if args.detail else {"drafts": 0}
    res["flip"] = out
    if not out["drafts"]:
        print("- no drafts with sim deck parts")
    else:
        for name in ("rating", "value"):
            m = out[name]
            print(f"- noalsa minus base, sim decks, {name}: {m['estimate']:+.3f} ({m['scaled_se']:.3f}) "
                  f"{m['estimate'] / m['scaled_se']:+.1f} SEs over {out['drafts']} drafts")
        v = out["value"]
        t = v["estimate"] / v["scaled_se"]
        print(f"\nFlip verdict: {'flips' if t >= 2 else 'closes' if abs(t) < 2 else 'stays negative'}.")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=float)


if __name__ == "__main__":
    main()
