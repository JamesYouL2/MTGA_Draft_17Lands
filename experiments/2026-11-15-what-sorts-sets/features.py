"""Which of a set's features go with a softer off-color penalty doing better?

    python experiments/2026-11-15-what-sorts-sets/features.py DATASETS

DATASETS holds each set's app dataset as <SET>.json.gz. Reads the per-set changes
of the four off-color runs from their folders. Exploratory; needs only NumPy.
"""

import gzip, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..")
D = sys.argv[1]
def load(p): return json.load(gzip.open(p))
est = {}
def add(path, head):
    for s, v in json.load(open(path))[head]["sets"].items():
        est.setdefault(s, []).append((v["change"], v["se"]))
# flag-step is the same change as softer in the four sets over a 30% share.
add(f"{EXP}/2026-11-15-off-color-share/by_set.json", "softer")
add(f"{EXP}/2026-11-15-flag-threshold/by_set.json", "softer")
add(f"{EXP}/2026-11-15-off-color-flag/high_share_by_set.json", "flag-step")
add(f"{EXP}/2026-11-15-flag-snc-ktk/by_set.json", "flag-step")
comb = {}
for s, v in est.items():
    w = [1 / se**2 for _, se in v]
    comb[s] = (sum(x * wi for (x, _), wi in zip(v, w)) / sum(w), sum(w) ** -0.5, len(v))

def features(s):
    d = load(f"{D}/{s}.json.gz"); cr = d.get("color_ratings", {})
    tot = fix = fixland = hyb = gold = heavy = colored = 0
    grp = {}
    for c in d["card_ratings"].values():
        dc = c.get("deck_colors", {}); g = dc.get("All Decks", {}).get("game_count") or 0
        types = c.get("types", []); cols = c.get("colors", []); cost = c.get("mana_cost") or ""
        for k, st in dc.items():
            if k != "All Decks": grp[k] = grp.get(k, 0) + (st.get("game_count") or 0)
        if "Basic" in types or not g: continue
        tot += g
        isfix = "fixing_ramp" in c.get("tags", []) or ("Land" in types and len(cols) > 1)
        fix += g * isfix; fixland += g * ("Land" in types and len(cols) > 1)
        syms = re.findall(r"\{([^}]+)\}", cost)
        hyb += g * any("/" in x and "P" not in x for x in syms)
        gold += g * (len(cols) >= 2 and "Land" not in types)
        pips = [x for x in syms if x in "WUBRG"]
        if pips:
            colored += g; heavy += g * (max(pips.count(x) for x in "WUBRG") >= 2)
    def wr(pred):
        ks = [k for k in grp if pred(k) and cr.get(k)]
        w = sum(grp[k] for k in ks)
        return sum(cr[k] * grp[k] for k in ks) / w if w else float("nan")
    three = sum(v for k, v in grp.items() if len(k) >= 3) / sum(grp.values())
    return {"three_share": three, "fixing_play": fix / tot, "fix_lands_play": fixland / tot,
            "hybrid_play": hyb / tot, "gold_play": gold / tot, "double_pip": heavy / colored,
            "wr3_minus_wr2": wr(lambda k: len(k) >= 3) - wr(lambda k: len(k) == 2)}

rows = {s: features(s) for s in comb}
names = list(next(iter(rows.values())))
print("set | softer (SE) runs | " + " | ".join(names))
for s in sorted(comb, key=lambda s: comb[s][0]):
    print(f"{s} | {comb[s][0]:+.4f} ({comb[s][1]:.4f}) {comb[s][2]} | " + " | ".join(f"{rows[s][n]:.3f}" for n in names))
y = np.array([comb[s][0] for s in comb]); w = np.array([1 / comb[s][1] ** 2 for s in comb])
def wcorr(x, m):
    x, yy, ww = x[m], y[m], w[m]
    mx, my = np.average(x, weights=ww), np.average(yy, weights=ww)
    return np.sum(ww*(x-mx)*(yy-my)) / np.sqrt(np.sum(ww*(x-mx)**2) * np.sum(ww*(yy-my)**2))
sets = list(comb)
allm = np.ones(len(sets), bool)
low = np.array([rows[s]["three_share"] < 0.3 for s in sets])
print("\nweighted correlation with softer's change (negative: more of it, softer helps more)")
print("feature | all %d sets | the %d sets under 30%% share" % (len(sets), low.sum()))
for n in names:
    x = np.array([rows[s][n] for s in sets])
    print(f"{n} | {wcorr(x, allm):+.2f} | {wcorr(x, low):+.2f}")
json.dump({"softer": comb, "features": rows}, open(f"{HERE}/features.json", "w"), indent=1)
