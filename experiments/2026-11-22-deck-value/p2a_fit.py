"""PHASE2A.md's per-set fits: within-deck effects of the cards seen in a game.

    python experiments/2026-11-22-deck-value/p2a_fit.py --src . --set FDN \
        --games game_data_public.FDN.PremierDraft.csv.gz --dataset dataset.json.gz \
        --out p2a-FDN.json

Two passes over the game data. Pass 1 counts, per fold of drafts, each card's
games and wins with it in the opening hand or drawn. Pass 2 rates each game's
cards from the other fold and builds the per-game terms; then each model is a
linear probability fit with deck fixed effects and deck-clustered SEs. Writes
each model's coefficients and covariance, for p2a_report.py.
"""

import argparse
import csv
import gzip
import json
import os
import sys
import time
import zlib

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "DeckScoreFit"))
import features as F  # noqa: E402

META = 18
PREFIXES = ("opening_hand_", "drawn_", "deck_")
COLOR_BITS = {c: 1 << i for i, c in enumerate("WUBRG")}
MIN_RATED_COPIES = 10  # a deck needs this many rated spell copies to be used
CHUNK = 4000


def mask(colors):
    m = 0
    for c in colors or ():
        m |= COLOR_BITS.get(c, 0)
    return m


class Layout:
    def __init__(self, header):
        self.meta = {name: i for i, name in enumerate(header[:META])}
        cards = header[META:-2]
        idx = {p: [] for p in PREFIXES}
        names = {p: [] for p in PREFIXES}
        for j, col in enumerate(cards):
            for p in PREFIXES:
                if col.startswith(p):
                    idx[p].append(j)
                    names[p].append(col[len(p):])
        assert names["opening_hand_"] == names["drawn_"] == names["deck_"], "card columns out of order"
        self.names = names["deck_"]
        self.oh, self.dr, self.dk = (np.array(idx[p]) for p in PREFIXES)
        self.width = len(cards)


def chunks(path, limit=None):
    """(layout, meta rows, card int matrix) per chunk of lines."""
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        header = next(csv.reader([f.readline()]))
        lay = Layout(header)
        meta, body, read = [], [], 0
        for line in f:
            if '"' in line:
                fields = next(csv.reader([line]))
                meta.append(fields[:META])
                body.append(",".join(fields[META:-2]))
            else:
                parts = line.split(",", META)
                meta.append(parts[:META])
                body.append(parts[META].rsplit(",", 2)[0])
            read += 1
            if len(meta) == CHUNK or (limit and read >= limit):
                yield lay, meta, parse(body, lay.width)
                meta, body = [], []
                if limit and read >= limit:
                    return
        if meta:
            yield lay, meta, parse(body, lay.width)


def parse(body, width):
    flat = np.array(",".join(body).split(","), dtype=np.int16)
    return flat.reshape(len(body), width)


def fold_of(draft_ids):
    return np.array([zlib.crc32(d.encode()) & 1 for d in draft_ids], dtype=np.int8)


class Cards:
    """Per-column card properties from the app's dataset."""

    def __init__(self, app, names):
        n = len(names)
        self.spell, self.creature, self.removal = np.zeros(n, bool), np.zeros(n, bool), np.zeros(n, bool)
        self.cheap, self.two_drop = np.zeros(n, bool), np.zeros(n, bool)
        self.cmask = np.zeros(n, np.int64)
        self.app_z = np.full(n, np.nan)
        mean, sd = app.metrics.get_metrics("All Decks", "gihwr")
        self.mean, self.sd = (mean or 54.0), (sd or 4.0)
        self.unmatched = []
        for j, name in enumerate(names):
            found = app.deck({name: 1})
            if not found:
                self.unmatched.append(name)
                self.spell[j] = True  # unknown: an unrated spell with no type
                continue
            c = found[0]
            types = c.get("types") or []
            if "Land" in types:
                continue
            self.spell[j] = True
            cmc = float(c.get("cmc", 0) or 0)
            self.creature[j] = "Creature" in types
            self.removal[j] = "removal" in (c.get("tags") or [])
            self.cheap[j] = (self.creature[j] or self.removal[j]) and cmc <= 2
            self.two_drop[j] = self.creature[j] and cmc <= 2
            self.cmask[j] = mask(c.get("colors"))
            r = app.gihwr(c)
            if r > 30.0:
                self.app_z[j] = (r - self.mean) / self.sd


def ranks(z, D, top=True, k=5):
    """Per row, the share of each card's copies among the deck's k best (or
    worst) rated spell copies; D is the deck's rated spell copies."""
    s = z if top else -z
    key = np.where(D > 0, -s, np.inf)
    order = np.argsort(key, axis=1)[:, :k]
    cnt = np.take_along_axis(D, order, axis=1).astype(float)
    cum = np.cumsum(cnt, axis=1)
    full = cum[:, -1] >= k
    pos = np.argmax(cum >= k, axis=1)
    thr = np.where(full, np.take_along_axis(s, order, axis=1)[np.arange(len(s)), pos], -np.inf)
    # Copies above the k-th copy's rating count whole; copies tied with it
    # share the remaining places evenly.
    above = (D > 0) & (s > thr[:, None])
    at = (D > 0) & (s == thr[:, None])
    n_above = (D * above).sum(1)
    n_at = (D * at).sum(1)
    share = np.divide(k - n_above, n_at, out=np.zeros(len(s)), where=n_at > 0)
    return above + at * share[:, None]


def terms(X, z, zbar, wtop, wlow, rated, cards, splash, outside):
    """{term: per-row value} for seen counts X (rows x cards)."""
    Xs = X * cards.spell
    Xr = Xs * rated
    dev = np.where(rated, z - zbar[:, None], 0.0)
    return {
        "Q": (Xr * dev).sum(1),
        "Q2": (Xr * dev**2).sum(1),
        "B5": (Xr * wtop).sum(1),
        "T": (Xr * wtop * dev).sum(1),
        "L": (Xr * wlow * dev).sum(1),
        "C": X @ cards.creature,
        "R": X @ cards.removal,
        "K": X @ cards.cheap,
        "S": (Xs * splash).sum(1),
        "O": (Xs * outside).sum(1),
        "U": (Xs * ~rated).sum(1),
        "lands": X.sum(1) - Xs.sum(1),
        "seen": X.sum(1),
        "F": (X * cards.two_drop).sum(1) > 0,
    }


def deck_part(z, D, cards):
    rated = ~np.isnan(z)
    Dr = D * (cards.spell & rated)
    zz = np.where(rated, z, 0.0)
    n = Dr.sum(1)
    zbar = (Dr * zz).sum(1) / np.maximum(n, 1)
    return rated, zz, Dr, zbar, n


def build(path, app, limit=None):
    t0 = time.time()
    # Pass 1: per-fold GIH games and wins.
    games = wins = None
    lay = None
    rows = 0
    for lay, meta, M in chunks(path, limit):
        if games is None:
            games = np.zeros((2, len(lay.names)))
            wins = np.zeros((2, len(lay.names)))
        fold = fold_of([m[lay.meta["draft_id"]] for m in meta])
        won = np.array([m[lay.meta["won"]] == "True" for m in meta])
        seen = (M[:, lay.oh] + M[:, lay.dr]) > 0
        for f in (0, 1):
            games[f] += seen[fold == f].sum(0)
            wins[f] += seen[(fold == f) & won].sum(0)
        rows += len(meta)
    t1 = time.time()
    cards = Cards(app, lay.names)
    gih = np.where(games > 0, 100.0 * wins / np.maximum(games, 1), np.nan)
    z_fold = np.where(games >= ARGS.min_games, (gih - cards.mean) / cards.sd, np.nan)
    z_fold[:, ~cards.spell] = np.nan
    both = ~np.isnan(z_fold).any(0)
    r = float(np.corrcoef(z_fold[0, both], z_fold[1, both])[0, 1]) if both.sum() > 2 else float("nan")
    info = dict(rows=rows, spells=int(cards.spell.sum()), rated=[int((~np.isnan(z_fold[f])).sum()) for f in (0, 1)],
                app_rated=int((~np.isnan(cards.app_z)).sum()), reliability=r, rated_both=int(both.sum()),
                unmatched=cards.unmatched[:20], n_unmatched=len(cards.unmatched), mean=cards.mean, sd=cards.sd)

    # Pass 2: per-game terms.
    out = {k: [] for k in ("deck", "won", "on_play", "mull")}
    feats = {}
    deck_ids = {}
    for lay, meta, M in chunks(path, limit):
        g = lay.meta
        fold = fold_of([m[g["draft_id"]] for m in meta])
        z = z_fold[1 - fold]  # rows x cards: the other fold's ratings
        D = M[:, lay.dk].astype(float)
        O = M[:, lay.oh].astype(float)
        S = O + M[:, lay.dr]
        main = np.array([mask(m[g["main_colors"]]) for m in meta])
        spl = np.array([mask(m[g["splash_colors"]]) for m in meta])
        splash = (cards.cmask[None, :] & spl[:, None]) != 0
        outside = (cards.cmask[None, :] & ~(main | spl)[:, None]) != 0
        cols = {}
        for tag, zz_in in (("", z), ("app_", np.broadcast_to(cards.app_z, z.shape))):
            rated, zz, Dr, zbar, n = deck_part(zz_in, D, cards)
            wtop, wlow = ranks(zz, Dr, True), ranks(zz, Dr, False)
            for which, X in (("o_", O), ("d_", S)):
                if tag and which == "d_":
                    continue
                for k, v in terms(X, zz, zbar, wtop, wlow, rated, cards, splash, outside).items():
                    cols[tag + which + k] = v
            cols[tag + "nrated"] = n
        for k, v in cols.items():
            feats.setdefault(k, []).append(np.asarray(v, dtype=np.float32))
        keys = [m[g["draft_id"]] + "|" + m[g["build_index"]] for m in meta]
        out["deck"].append(np.array([deck_ids.setdefault(k, len(deck_ids)) for k in keys], dtype=np.int64))
        out["won"].append(np.array([m[g["won"]] == "True" for m in meta], dtype=np.float32))
        out["on_play"].append(np.array([m[g["on_play"]] == "True" for m in meta], dtype=np.float32))
        out["mull"].append(np.array([int(m[g["num_mulligans"]] or 0) for m in meta], dtype=np.float32))
    data = {k: np.concatenate(v) for k, v in out.items()} | {k: np.concatenate(v) for k, v in feats.items()}
    info.update(pass1_s=round(t1 - t0, 1), pass2_s=round(time.time() - t1, 1), decks=len(deck_ids))
    return data, info


def demean(x, deck, keep):
    """x demeaned within deck over the kept rows (kept rows only)."""
    d = deck[keep]
    n = np.bincount(d)
    if x.ndim == 1:
        return x[keep] - (np.bincount(d, x[keep]) / np.maximum(n, 1))[d]
    return np.column_stack([demean(x[:, j], deck, keep) for j in range(x.shape[1])])


def fe_fit(y, X, names, deck, keep):
    """LPM with deck fixed effects; deck-clustered covariance."""
    d = deck[keep]
    multi = np.bincount(d)[d] > 1
    sub = keep.copy()
    sub[np.flatnonzero(keep)[~multi]] = False
    d = deck[sub]
    yt = demean(y, deck, sub)
    Xt = demean(X, deck, sub)
    live = Xt.std(0) > 1e-9
    k = X.shape[1]
    beta = np.zeros(k)
    V = np.eye(k) * 1e12
    Xl = Xt[:, live]
    A = Xl.T @ Xl
    Ainv = np.linalg.inv(A)
    b = Ainv @ (Xl.T @ yt)
    e = yt - Xl @ b
    _, inv = np.unique(d, return_inverse=True)
    G = inv.max() + 1
    Sc = np.column_stack([np.bincount(inv, Xl[:, j] * e, minlength=G) for j in range(Xl.shape[1])])
    Vl = Ainv @ (Sc.T @ Sc) @ Ainv * G / max(1, G - 1)
    beta[live] = b
    li = np.flatnonzero(live)
    V[np.ix_(li, li)] = Vl
    return dict(names=names, beta=beta.tolist(), cov=V.tolist(), games=int(sub.sum()), decks=int(G),
                means={n: float(X[sub, j].mean()) for j, n in enumerate(names)})


def models(data):
    deck, won = data["deck"], data["won"].astype(float)
    ok = data["nrated"] >= MIN_RATED_COPIES
    okapp = data["app_nrated"] >= MIN_RATED_COPIES
    m0 = (data["mull"] == 0)
    c = lambda name: data[name].astype(float)  # noqa: E731
    lands = c("o_lands")
    land_d = {"lands<=1": lands <= 1, "lands=2": lands == 2, "lands=4": lands == 4, "lands>=5": lands >= 5}
    land_cols = [v.astype(float) for v in land_d.values()]
    base = ["Q", "B5", "C", "R", "K", "S", "O"]
    ctrl = [c("o_U"), c("on_play")]
    ctrl_names = ["U", "on_play"]
    res = {}

    def run(key, names, cols, keep):
        res[key] = fe_fit(won, np.column_stack(cols), names, deck, keep)

    o = lambda t: c("o_" + t)  # noqa: E731
    run("M0", ["Q"] + ctrl_names, [o("Q")] + ctrl, ok & m0)
    run("M1", base + list(land_d) + ctrl_names, [o(t) for t in base] + land_cols + ctrl, ok & m0)
    m2 = ["Q", "T", "L", "C", "R", "K", "S", "O"]
    run("M2", m2 + list(land_d) + ctrl_names, [o(t) for t in m2] + land_cols + ctrl, ok & m0)
    m3 = ["Q", "Q2", "C", "R", "K", "S", "O"]
    run("M3", m3 + list(land_d) + ctrl_names, [o(t) for t in m3] + land_cols + ctrl, ok & m0)
    run("M4", base + ["F"] + list(land_d) + ctrl_names,
        [o(t) for t in base] + [o("F")] + land_cols + ctrl, ok & m0)
    # In-sample (app) ratings, M1's form.
    al = c("app_o_lands")
    app_land = [(al <= 1), (al == 2), (al == 4), (al >= 5)]
    run("S1", base + list(land_d) + ctrl_names,
        [c("app_o_" + t) for t in base] + [v.astype(float) for v in app_land] + [c("app_o_U"), c("on_play")],
        okapp & m0)
    # Draws: all games, mulligan dummies, lands seen; D1 adds seen-count dummies.
    mull = data["mull"]
    mcols = [(mull == 1).astype(float), (mull >= 2).astype(float)]
    d = lambda t: c("d_" + t)  # noqa: E731
    dnames = base + ["lands", "U", "on_play", "mull=1", "mull>=2"]
    dcols = [d(t) for t in base] + [d("lands"), d("U"), c("on_play")] + mcols
    run("D0", dnames, dcols, ok)
    seen = np.clip(c("d_seen"), 7, 25)
    levels = [v for v in np.unique(seen) if v != 7]
    run("D1", dnames + [f"seen={int(v)}" for v in levels], dcols + [(seen == v).astype(float) for v in levels], ok)
    return res


def main(argv=None):
    global ARGS
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--src", required=True)
    parser.add_argument("--set", required=True)
    parser.add_argument("--games", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--min-games", type=int, default=500)
    parser.add_argument("--limit", type=int, help="Read only this many games (smoke tests)")
    ARGS = parser.parse_args(argv)
    sys.path.insert(0, os.path.abspath(ARGS.src))
    app = F.App(ARGS.dataset)
    data, info = build(ARGS.games, app, ARGS.limit)
    t = time.time()
    res = models(data)
    info["fit_s"] = round(time.time() - t, 1)
    share = {}
    for tag in ("", "app_"):
        seen = data[tag + "o_seen"] - data[tag + "o_lands"]
        share[tag or "heldout"] = float(1 - data[tag + "o_U"].sum() / max(1, seen.sum()))
    info["rated_share_open"] = share
    os.makedirs(os.path.dirname(ARGS.out) or ".", exist_ok=True)
    with open(ARGS.out, "w", encoding="utf-8") as f:
        json.dump({"set": ARGS.set, "info": info, "models": res}, f)
    m1 = res["M1"]
    print(f"{ARGS.set}: {info['rows']} games, {m1['games']} in M1 over {m1['decks']} decks; r {info['reliability']:.3f}; "
          f"rated share {share}; pass1 {info['pass1_s']}s pass2 {info['pass2_s']}s fit {info['fit_s']}s")
    for j, n in enumerate(m1["names"]):
        b, s = m1["beta"][j], np.sqrt(m1["cov"][j][j])
        print(f"  {n:10s} {b:+.5f} ({s:.5f}) {b / s:+.1f}")


if __name__ == "__main__":
    main()
