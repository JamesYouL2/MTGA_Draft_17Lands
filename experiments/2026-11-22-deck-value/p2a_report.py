"""PHASE2A.md's report: combine p2a_fit.py's per-set fits and apply the rules.

    python experiments/2026-11-22-deck-value/p2a_report.py p2a-*.json \
        --e1 experiments/2026-11-22-deck-value/reports/e1.json [--json p2a.json]

Sets are combined by inverse-variance weighting of each model's coefficient
vector (over the terms every set has). Ratios and points use the delta method.
"""

import argparse
import json

import numpy as np

PER_Z = 12.0 / 23.0  # deck-score points per z unit of one card
E1_SD = {"C": 2.69, "R": 2.40, "K": 2.41}  # E1's deck SDs (reports/e1.md)
E1_NAME = {"C": "creatures", "R": "removal", "K": "cheap"}
E1_TOP5_SD = 0.30
RULE_SES, RULE_PTS_SD, RULE_PREMIUM, PER_COPY = 3.0, 0.5, 0.5, 0.186
LABEL = {"Q": "(a) quality Q", "B5": "(d) best-five seen", "T": "(d') best-five slope T",
         "L": "(d') weakest-five slope L", "Q2": "(d'') convex Q2", "C": "(b) creatures",
         "R": "(c) removal", "K": "cheap (E1 def.)", "S": "(e) splash-color spells",
         "O": "(e) off-color spells", "F": "(f) 2-drop creature in hand",
         "lands<=1": "(e) ≤1 land in hand", "lands=2": "(e) 2 lands", "lands=4": "(e) 4 lands",
         "lands>=5": "(e) ≥5 lands", "lands": "(e) lands seen", "U": "unrated spells", "on_play": "on the play"}


MIN_SEEN = 100


def combine(fits, names=None):
    """Inverse-variance combination of {names, beta, cov} fits over common names."""
    if names is None:
        names = [n for n in fits[0]["names"] if all(n in f["names"] for f in fits)]
    P = np.zeros((len(names), len(names)))
    Pb = np.zeros(len(names))
    for f in fits:
        idx = [f["names"].index(n) for n in names]
        V = np.array(f["cov"])[np.ix_(idx, idx)]
        b = np.array(f["beta"])[idx]
        live = np.diag(V) < 1e11  # p2a_fit marks a term with no variation in a set by 1e12
        # near-dead too (deviation, see README.md, Phase 2a): a term seen fewer than
        # MIN_SEEN times over the set's games, e.g. O in EOE (about one game), has a
        # clustered SE from a deck or two that is meaningless
        means, games = f.get("means"), f.get("games")
        if means and games:
            seen = np.array([abs(means.get(n, 1.0)) * games for n in names])
            live &= seen >= MIN_SEEN
        li = np.flatnonzero(live)
        Vi = np.zeros_like(V)
        # pseudo-inverse with a relative eigenvalue cutoff: a set whose live block is
        # numerically singular (EOE in M1, where O barely varies) would otherwise
        # inject a huge, indefinite precision and distort every pooled term
        Vi[np.ix_(li, li)] = np.linalg.pinv(V[np.ix_(li, li)], rcond=1e-10, hermitian=True)
        P += Vi
        Pb += Vi @ b
    live = np.diag(P) > 0
    li = np.flatnonzero(live)
    V = np.eye(len(names)) * 1e12
    V[np.ix_(li, li)] = np.linalg.inv(P[np.ix_(li, li)])
    beta = np.zeros(len(names))
    beta[li] = V[np.ix_(li, li)] @ Pb[li]
    return dict(names=names, beta=beta, cov=V)


def coef(c, n):
    i = c["names"].index(n)
    return c["beta"][i], float(np.sqrt(c["cov"][i, i]))


def ratio(c, a, b):
    """(a/b, SE) by the delta method."""
    i, j = c["names"].index(a), c["names"].index(b)
    x, y = c["beta"][i], c["beta"][j]
    V = c["cov"]
    var = V[i, i] / y**2 + x**2 * V[j, j] / y**4 - 2 * x * V[i, j] / y**3
    return x / y, float(np.sqrt(max(var, 0)))


def rho_verdict(r, se):
    lo, hi = r - 2 * se, r + 2 * se
    if hi < 0.5:
        return "mostly confound"
    if hi < 1:
        return "partly confound"
    if lo > 1:
        return "larger within deck"
    if lo <= 1 <= hi and 2 * se < 0.5:
        return "consistent"
    return "unclear"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--e1", required=True)
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    sets = []
    for p in args.paths:
        with open(p, encoding="utf-8") as f:
            sets.append(json.load(f))
    sets.sort(key=lambda s: s["set"])
    with open(args.e1, encoding="utf-8") as f:
        e1 = json.load(f)
    keys = list(sets[0]["models"])
    comb = {k: combine([s["models"][k] for s in sets]) for k in keys}
    res = {"sets": [s["set"] for s in sets]}

    # Reliability, weighted as M1's Q.
    wq = np.array([1 / s["models"]["M1"]["cov"][0][0] for s in sets])
    rel = np.array([s["info"]["reliability"] for s in sets])
    rbar = float((wq * rel).sum() / wq.sum())
    res["reliability"] = rbar

    print(f"## Phase 2a: within-deck draw effects, {len(sets)} sets\n")
    print("| set | games | M1 games | M1 decks | rated share (held-out) | reliability r | pass 1 s | pass 2 s |")
    print("|---|---|---|---|---|---|---|---|")
    tot = [0, 0, 0]
    for s in sets:
        i, m1 = s["info"], s["models"]["M1"]
        tot = [tot[0] + i["rows"], tot[1] + m1["games"], tot[2] + m1["decks"]]
        print(f"| {s['set']} | {i['rows']} | {m1['games']} | {m1['decks']} | {i['rated_share_open']['heldout']:.3f} "
              f"| {i['reliability']:.3f} | {i['pass1_s']:.0f} | {i['pass2_s']:.0f} |")
    print(f"| all | {tot[0]} | {tot[1]} | {tot[2]} | | {rbar:.3f} (Q-weighted) | | |\n")
    res["games"] = dict(zip(("rows", "m1_games", "m1_decks"), tot))

    def signs(model, n):
        pos = sum(1 for s in sets if n in s["models"][model]["names"]
                  and s["models"][model]["beta"][s["models"][model]["names"].index(n)] > 0)
        return pos, len(sets) - pos

    def pts(model, n):
        r, se = ratio(comb[model], n, "Q")
        return r * PER_Z, se * PER_Z

    # Sanity.
    bq0, sq0 = coef(comb["M0"], "Q")
    bq1, sq1 = coef(comb["M1"], "Q")
    sane = bq1 > 0 and bq1 / sq1 >= 10
    res["sanity"] = dict(M0=[bq0, sq0], M1=[bq1, sq1], passes=sane)
    print(f"Sanity: β_Q (win probability per seen z unit) M0 {bq0:+.5f} ({sq0:.5f}) {bq0 / sq0:+.1f} SEs; "
          f"M1 {bq1:+.5f} ({sq1:.5f}) {bq1 / sq1:+.1f} SEs -> {'passes' if sane else 'FAILS: inconclusive'}.\n")

    # Term table for M1-family terms.
    print("### Terms (win probability per unit seen; points per card = β/β_Q × 12/23; "
          f"disattenuated = × r̄ {rbar:.3f})\n")
    print("| term | model | β (SE) SEs | sets +/− | pts per card (SE) | disattenuated | pts per E1 deck SD (raw / dis.) |")
    print("|---|---|---|---|---|---|---|")
    res["terms"] = {}
    rows = [("M1", n) for n in comb["M1"]["names"] if n != "Q"] + [
        ("M2", "T"), ("M2", "L"), ("M3", "Q2"), ("M4", "F")]
    for model, n in rows:
        b, s = coef(comb[model], n)
        p, ps = pts(model, n)
        pos, neg = signs(model, n)
        sd = E1_SD.get(n)
        per_sd = f"{p * sd:+.2f} / {p * sd * rbar:+.2f}" if sd else ""
        res["terms"][f"{model}:{n}"] = dict(beta=[b, s], points=[p, ps], dis=p * rbar, signs=[pos, neg])
        print(f"| {LABEL.get(n, n)} | {model} | {b:+.5f} ({s:.5f}) {b / s:+.1f} | {pos}/{neg} | {p:+.3f} ({ps:.3f}) "
              f"| {p * rbar:+.3f} | {per_sd} |")
    print()

    # Rule 1.
    b5, s5 = coef(comb["M1"], "B5")
    prem, prem_se = ratio(comb["M1"], "B5", "Q")
    r1 = b5 > 0 and b5 / s5 >= RULE_SES and prem >= RULE_PREMIUM and prem * rbar >= RULE_PREMIUM
    tr, tr_se = ratio(comb["M2"], "T", "Q")
    lr, lr_se = ratio(comb["M2"], "L", "Q")
    t5 = e1["shape"]["top5+low5"]
    base = t5["cq"] / 23
    e1_extra = t5["top5"][0] / E1_TOP5_SD / 5 / base
    e1_extra_se = t5["top5"][1] / E1_TOP5_SD / 5 / base
    e1_low = (t5["low5"][0] / 0.38 / 5) / base
    rho_t = tr / e1_extra
    rho_t_se = float(np.sqrt((tr_se / e1_extra) ** 2 + (tr * e1_extra_se / e1_extra**2) ** 2))
    q2, q2s = coef(comb["M3"], "Q2")
    res["rule1"] = dict(B5=[b5, s5], premium=[prem, prem_se], premium_dis=prem * rbar, passes=r1,
                        top_slope_ratio=[1 + tr, tr_se], low_slope_ratio=[1 + lr, lr_se],
                        e1_top_slope_ratio=1 + e1_extra, e1_low_slope_ratio=1 + e1_low,
                        rho=[rho_t, rho_t_se], rho_verdict=rho_verdict(rho_t, rho_t_se), Q2=[q2, q2s])
    print("### Rule 1: top-heavy within a deck\n")
    print(f"- B5 {b5:+.5f} ({s5:.5f}) {b5 / s5:+.1f} SEs; premium {prem:+.2f} ({prem_se:.2f}) z units per seen "
          f"best-five copy, disattenuated {prem * rbar:+.2f} (rule: ≥ 3 SEs and ≥ {RULE_PREMIUM}) -> "
          f"**{'top-heavy' if r1 else 'not top-heavy'}**.")
    print(f"- Slope per z unit relative to a middle card (M2): best five {1 + tr:.2f} ({tr_se:.2f}), weakest five "
          f"{1 + lr:.2f} ({lr_se:.2f}). E1: best five {1 + e1_extra:.1f} ({e1_extra_se:.1f}), weakest five {1 + e1_low:.1f}.")
    print(f"- ρ (within-deck extra slope / E1's) {rho_t:.2f} ({rho_t_se:.2f}) -> {rho_verdict(rho_t, rho_t_se)}.")
    print(f"- Convex Q2 (M3) {q2:+.5f} ({q2s:.5f}) {q2 / q2s:+.1f} SEs.\n")

    # Rule 2 and 3.
    print("### Rules 2 and 3: creatures, removal (and cheap) against E1\n")
    print("| term | within pts/card (SE) | dis. | pts per E1 SD (raw / dis.) | Rule 2 | E1 joint pts/card (SE) | ρ (SE) | Rule 3 | ρ dis. | Rule 3 dis. | E1 flip pts/unit |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    bs, ss = e1["joint"]["score"]
    res["rule2"], res["rule3"] = {}, {}
    for n in ("C", "R", "K"):
        b, s = coef(comb["M1"], n)
        p, ps = pts("M1", n)
        sd = E1_SD[n]
        jb, js = e1["blind"][E1_NAME[n]]["joint"]
        pe, pes = jb / bs / sd, js / bs / sd
        r2 = b / s >= RULE_SES and p * sd >= RULE_PTS_SD and p * sd * rbar >= RULE_PTS_SD
        neg = b / s <= -RULE_SES and p * sd <= -RULE_PTS_SD and p * sd * rbar <= -RULE_PTS_SD
        v2 = "carries value" if r2 else "negative value" if neg else "not shown"
        rho = p / pe
        rse = float(np.sqrt((ps / pe) ** 2 + (p * pes / pe**2) ** 2))
        rho_d, rse_d = rho * rbar, rse * rbar
        flip = e1["flip_fit"][E1_NAME[n]][2]
        if n != "K":
            res["rule2"][n] = dict(points=[p, ps], dis=p * rbar, per_sd=p * sd, verdict=v2)
        res["rule3"][n] = dict(rho=[rho, rse], verdict=rho_verdict(rho, rse), rho_dis=[rho_d, rse_d],
                               verdict_dis=rho_verdict(rho_d, rse_d), e1=[pe, pes], flip=flip)
        print(f"| {LABEL[n]} | {p:+.3f} ({ps:.3f}) | {p * rbar:+.3f} | {p * sd:+.2f} / {p * sd * rbar:+.2f} "
              f"| {v2 if n != 'K' else '–'} | {pe:+.3f} ({pes:.3f}) | {rho:.2f} ({rse:.2f}) | {rho_verdict(rho, rse)} "
              f"| {rho_d:.2f} ({rse_d:.2f}) | {rho_verdict(rho_d, rse_d)} | {flip:+.2f} |")
    print()

    # Draws check and sensitivity.
    print("### Draws versions (D1 with seen-count dummies, D0 without) and in-sample ratings (S1), points per card\n")
    print("| term | M1 | S1 (app ratings) | D1 | D0 | flag |")
    print("|---|---|---|---|---|---|")
    res["checks"] = {}
    for n in ("B5", "C", "R", "K", "S", "O"):
        vals = {}
        for model in ("M1", "S1", "D1", "D0"):
            p, ps = pts(model, n)
            b, s = coef(comb[model], n)
            vals[model] = (p, ps, b / s)
        bm = coef(comb["M1"], n)[0]
        flag = "sign flips at ≥3 SEs" if (np.sign(vals["D1"][0]) != np.sign(bm) and abs(vals["D1"][2]) >= 3) else ""
        res["checks"][n] = {k: list(v) for k, v in vals.items()} | {"flag": flag}
        print(f"| {LABEL[n]} | " + " | ".join(f"{vals[m][0]:+.3f} ({vals[m][1]:.3f})" for m in ("M1", "S1", "D1", "D0"))
              + f" | {flag} |")
    bqs, sqs = coef(comb["S1"], "Q")
    bqd, sqd = coef(comb["D1"], "Q")
    print(f"\nβ_Q: S1 {bqs:+.5f} ({sqs:.5f}), D1 {bqd:+.5f} ({sqd:.5f}), D0 {coef(comb['D0'], 'Q')[0]:+.5f}.\n")
    bl, sl = coef(comb["D1"], "lands")
    pl, pls = pts("D1", "lands")
    print(f"Lands seen instead of a spell (D1): {bl:+.5f} ({sl:.5f}) {bl / sl:+.1f} SEs = {pl:+.3f} points per card.\n")

    # Value function.
    print("### Value-function form (PHASE2A.md's decision rule)\n")
    V = []
    for n in ("C", "R"):
        if res["rule2"][n]["verdict"] == "carries value":
            V.append((n, res["rule2"][n]["dis"], "points per copy"))
    if r1:
        bt, st = coef(comb["M2"], "T")
        if bt / st >= RULE_SES:
            V.append(("T", tr * PER_Z * rbar, "points per z unit of each best-five copy's (z − z̄), on top of card quality"))
        elif q2 / q2s >= RULE_SES:
            pq2 = ratio(comb["M3"], "Q2", "Q")[0] * PER_Z * rbar
            V.append(("Q2", pq2, "points per (z − z̄)² of each rated copy"))
    for n in ("S", "O"):
        b, s = coef(comb["M1"], n)
        p = pts("M1", n)[0] * rbar
        if abs(b / s) >= RULE_SES and abs(p) >= PER_COPY:
            V.append((n, p, "points per copy"))
    res["value_function"] = [dict(term=t, weight=w, unit=u) for t, w, u in V]
    if V:
        print("V = deck score " + " ".join(f"{'+' if w >= 0 else '−'} {abs(w):.3f} × {t}" for t, w, _ in V) + "\n")
        for t, w, u in V:
            print(f"- {LABEL.get(t, t)}: {w:+.3f} {u}")
    else:
        print("V = deck score (no term passes its rule)")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=float)


if __name__ == "__main__":
    main()
