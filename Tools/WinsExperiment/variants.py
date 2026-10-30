"""Compare lane and off_pips against the pool's two main colors with the same
terms against 17lands' color groups (mono to five colors, splashes folded in),
weighted by how often decks are in each group: averaged over P(group | pool)
("soft") or for the most likely group ("map"), for several K.

    python Tools/WinsExperiment/variants.py --eval features/*.eval.json.gz \
        --train features/*.train.json.gz --replay replay/ > report.md

--replay holds the advisor replay's SET.base.json (main) and SET.head.json
(this branch) for the same drafts as the --eval features.
"""

import argparse
import glob
import gzip
import json
import os
import sys
from types import SimpleNamespace

import numpy as np

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "AdvisorReplay"))
sys.path.insert(0, os.path.join(HERE, "..", "PickFit"))

import report as R  # noqa: E402
from fit import fit_logit  # noqa: E402

BASE = 50.0
SHARE_BINS = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 40), (40, 1000)]
COUNT_BINS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 9), (9, 1000)]
PSHARE = [f"pshare_{lo}_{hi}" for lo, hi in SHARE_BINS]
CSHARE = [f"cshare_{lo}_{hi}" for lo, hi in SHARE_BINS]
COUNT = [f"count_{lo}_{hi}" for lo, hi in COUNT_BINS]
EXTRAS = [
    "ata",
    "alsa",
    "ohwr",
    "gdwr",
    "gpwr",
    "gnswr",
    "iwd",
    "play_rate",
    "log_games",
    "take_rate",
    "rare",
    "mythic",
]
NAMES = (
    ["quality", "lane", "color_support", "color_gap", "unrated", "off_pips"]
    + ["pip_gap"]
    + PSHARE
    + CSHARE
    + COUNT
    + EXTRAS
)
KS = ["k025", "k05", "k1", "k2", "k4"]
GROUP = [f"{f}_{m}_{k}" for k in KS for m in ["soft", "map"] for f in ["lane", "off"]]
# The engine's features come first, in WEIGHTS order; then EXTRAS.
NAMES = NAMES[: -len(EXTRAS)] + GROUP + EXTRAS
FITTED = {
    "quality": 15.0,
    "lane": 11.1,
    "color_support": 0.9,
    "color_gap": -2.0,
    "unrated": -10.9,
}
# Pool sizes (cards taken before the pick) for off_pips as a curve.
BINS = [(0, 6), (7, 13), (14, 20), (21, 27), (28, 34), (35, 99)]
CURVE = [f"off_pips@{lo}-{hi}" for lo, hi in BINS]
LATE = 14  # pack 2 on, for the harsher late penalty
NO_COLOR = ["quality", "lane", "unrated"]
CORE = NO_COLOR + ["color_support"]
# Pool sizes for bins by timing: early pack 1, late pack 1, packs 2-3.
PHASES = [(0, 6), (7, 13), (14, 99)]


def timed(names):
    return [f"{k}@{lo}-{hi}" for lo, hi in PHASES for k in names]


CANDIDATE = "off_pips, two main colors (this PR)"
SUPPORT = ["quality", "unrated", "color_support"]
FITS = {
    CANDIDATE: CORE + ["off_pips"],
    "groups map K=0.5": SUPPORT + ["lane_map_k05", "off_map_k05"],
    "groups soft K=1": SUPPORT + ["lane_soft_k1", "off_soft_k1"],
    "two-color lane + groups off soft K=1": CORE + ["off_soft_k1"],
}
HARSHER = [2, 4, 8]
BOOTSTRAP = 200


class Picks:
    """Every pick of some drafts, as flat arrays: one row per distinct pack card."""

    def __init__(self, paths, strong_only=False):
        X, basic, sizes, taken, owner, pool = [], [], [], [], [], []
        self.drafts = []
        for path in sorted(paths):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            assert data["names"] == NAMES, data["names"]
            fx, fb, fs, ft, fo, fp = [], [], [], [], [], []
            for draft in data["drafts"]:
                if strong_only and not R.is_strong(draft):
                    continue
                d = len(self.drafts)
                self.drafts.append(
                    {k: draft[k] for k in ("id", "skill", "games", "wins", "losses")}
                    | {"set": data["set"]}
                )
                for _pack, _pick, t, rows, pool_size in draft["picks"]:
                    fs.append(len(rows))
                    ft.append(t)
                    fo.append(d)
                    fp.append(pool_size)
                    for r in rows:
                        fb.append(r is None)
                        fx.append(r or [0.0] * len(NAMES))
            X.append(np.array(fx, dtype=np.float32).reshape(-1, len(NAMES)))
            basic.append(np.array(fb, dtype=bool))
            sizes.append(np.array(fs, dtype=int))
            taken.append(np.array(ft, dtype=int))
            owner.append(np.array(fo, dtype=int))
            pool.append(np.array(fp, dtype=int))
            del data, fx, fb
        self.X, self.basic = np.vstack(X), np.concatenate(basic)
        self.sizes, self.taken = np.concatenate(sizes), np.concatenate(taken)
        self.owner, self.pool = np.concatenate(owner), np.concatenate(pool)
        self.starts = np.concatenate([[0], np.cumsum(self.sizes)[:-1]]).astype(int)
        self.row_pick = np.repeat(np.arange(len(self.sizes)), self.sizes)
        self.set = np.array([d["set"] for d in self.drafts])
        self.complete = np.array([R.is_complete(d) for d in self.drafts])
        self.strong = np.array([R.is_strong(d) for d in self.drafts])
        self.n_picks = np.bincount(self.owner, minlength=len(self.drafts))
        self.pick_set = self.set[self.owner]
        # Strong drafters' picks of a non-basic card from 2+ non-basic cards.
        chosen = self.starts + self.taken
        nonbasic = np.add.reduceat((~self.basic).astype(int), self.starts)
        self.fit_pick = self.strong[self.owner] & ~self.basic[chosen] & (nonbasic >= 2)

    def column(self, name):
        """A feature per row: a raw feature, NAME@LO-HI (the feature when the
        pool has LO to HI cards, else 0) or off_pips*pool (off_pips times the
        pool's size over 42)."""
        off = self.X[:, NAMES.index("off_pips")]
        if name in NAMES:
            return self.X[:, NAMES.index(name)]
        pool = np.repeat(self.pool, self.sizes)
        if "@" in name:
            raw, span = name.split("@")
            lo, hi = map(int, span.split("-"))
            return self.X[:, NAMES.index(raw)] * ((pool >= lo) & (pool <= hi))
        assert name == "off_pips*pool", name
        return off * pool / 42.0

    def scores(self, w):
        s = np.full(len(self.X), BASE)
        for k, v in w.items():
            if v:
                s += v * self.column(k)
        return s

    def per_pick(self, w):
        """(top-1, regret) per pick, as replay.py computes them for score weights w."""
        s = np.round(self.scores(w), 1)
        s[self.basic] = 0.0
        top = np.maximum.reduceat(s, self.starts)
        mean = np.add.reduceat(s, self.starts) / self.sizes
        sd = np.sqrt(
            np.add.reduceat((s - np.repeat(mean, self.sizes)) ** 2, self.starts)
            / self.sizes
        )
        sd[sd == 0] = 1.0
        chosen = self.starts + self.taken
        regret = (top - s[chosen]) / sd
        # Ties go to the card that comes first in the pack.
        at_top = np.flatnonzero(s == np.repeat(top, self.sizes))
        _, first = np.unique(self.row_pick[at_top], return_index=True)
        top1 = at_top[first] == chosen
        return top1, regret

    def per_draft(self, values):
        """The mean of a per-pick value in each draft (NaN for drafts with no picks)."""
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.bincount(self.owner, values, len(self.drafts)) / self.n_picks

    def by_set(self, weights_for):
        """(top-1, regret) per pick, with each set scored by weights_for(set)."""
        top1 = np.zeros(len(self.sizes), dtype=bool)
        regret = np.zeros(len(self.sizes))
        for code in np.unique(self.set):
            t, r = self.per_pick(weights_for(code))
            mask = self.pick_set == code
            top1[mask], regret[mask] = t[mask], r[mask]
        return top1, regret

    def subset(self, mask):
        """Data for fit_logit: the non-basic rows of the picks in mask."""
        picks = np.flatnonzero(mask)
        keep_row = np.repeat(mask, self.sizes) & ~self.basic
        before = np.cumsum(keep_row) - keep_row  # kept rows before each row
        sizes = np.add.reduceat(keep_row.astype(int), self.starts)[picks]
        starts = np.concatenate([[0], np.cumsum(sizes)[:-1]]).astype(int)
        chosen = self.starts[picks] + self.taken[picks]
        offset = before[chosen] - before[self.starts[picks]]
        data = SimpleNamespace(
            sizes=sizes, starts=starts, chosen=starts + offset, draft=self.owner[picks]
        )
        return np.flatnonzero(keep_row), data

    def log_lik(self, weights_for, scale_for):
        """Mean log-likelihood of strong drafters' picks, each set scored by
        weights_for(set) in points times scale_for(set) log-odds per point."""
        total, n = 0.0, 0
        for code in np.unique(self.set):
            rows, data = self.subset(self.fit_pick & (self.pick_set == code))
            w = weights_for(code)
            u = scale_for(code) * (self.scores(w)[rows] - BASE)
            top = np.maximum.reduceat(u, data.starts)
            e = np.exp(u - np.repeat(top, data.sizes))
            lse = top + np.log(np.add.reduceat(e, data.starts))
            total += float(np.sum(u[data.chosen] - lse))
            n += len(data.sizes)
        return total / n


def logit_fit(train, names):
    """For each set, conditional logit weights for names fitted to strong
    drafters' picks on the other sets: (points with quality 15, log-odds per
    point, picks); and the fit on all sets."""
    every, _ = train.subset(train.fit_pick)
    X = np.column_stack([train.column(k)[every] for k in names]).astype(float)
    where = np.full(len(train.X), -1)
    where[every] = np.arange(len(every))

    def fit(mask):
        rows, data = train.subset(mask)
        beta, _ = fit_logit(X[where[rows]], data)
        # Quality is +15 points, or -15 if other terms turn its weight negative.
        points = beta / abs(beta[0]) * 15.0
        return (
            dict(zip(names, np.round(points, 2))),
            abs(beta[0]) / 15.0,
            len(data.sizes),
        )

    out = {"all": fit(train.fit_pick)}
    for code in sorted(np.unique(train.set)):
        out[code] = fit(train.fit_pick & (train.pick_set != code))
    return out


# --- Report -------------------------------------------------------------------


def load_replay(folder, label, ev):
    """Per eval draft: (top-1 count, picks, mean regret) from the replay's label."""
    found = {}
    for path in glob.glob(os.path.join(folder, f"*.{label}.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for d in data["drafts"]:
            found[(data["set"], d["id"])] = d
    top1, n, regret = (np.zeros(len(ev.drafts)) for _ in range(3))
    missing = 0
    for i, d in enumerate(ev.drafts):
        r = found.get((d["set"], d["id"]))
        if r is None:
            missing += 1
            n[i] = 0
            continue
        n[i] = len(r["picks"])
        top1[i] = sum(p[2] == 0 for p in r["picks"])
        regret[i] = np.mean([p[3] for p in r["picks"]]) if r["picks"] else np.nan
    return top1, n, regret, missing


def fmt_w(w):
    return ", ".join(
        f"{k} {v:+.1f}" for k, v in w.items() if k != "quality" or v != 15.0
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--eval", nargs="+", required=True)
    parser.add_argument("--train", nargs="+", required=True)
    parser.add_argument("--replay", required=True)
    args = parser.parse_args(argv)

    ev = Picks(args.eval)
    out = []

    variants = {}
    for label, title in [("base", "main"), ("head", "this PR (replay)")]:
        t, n, r, missing = load_replay(args.replay, label, ev)
        out.append(f"<!-- {label}: {missing} eval drafts missing from the replay -->")
        variants[title] = (t, n, r, None)

    def offline(title, w_for, ll=None):
        top1, regret = ev.by_set(w_for)
        variants[title] = (
            np.bincount(ev.owner, top1, len(ev.drafts)),
            ev.n_picks.astype(float),
            ev.per_draft(regret),
            ll,
        )

    offline("this PR", lambda s: FITTED)

    # The offline scoring should reproduce the replay of this branch.
    rep_t, rep_n, rep_r, _ = variants.pop("this PR (replay)")
    off_t, off_n, off_r, _ = variants["this PR"]
    ok = (rep_n > 0) & (off_n > 0)
    out.append(
        f"Check: offline scoring matches the replay of this PR on "
        f"{100 * np.mean(rep_n == off_n):.2f}% of drafts' pick counts, "
        f"{100 * np.mean(rep_t[ok] == off_t[ok]):.2f}% of drafts' top-1 counts, "
        f"and drafts' mean regret to within "
        f"{np.nanmax(np.abs(rep_r[ok] - off_r[ok])):.4f}.\n"
    )
    del variants["this PR"]

    train = Picks(args.train, strong_only=True)
    out.append(
        f"Training sample (a different salt): {len(train.drafts):,} drafts, "
        f"{int(train.strong.sum()):,} by strong drafters, "
        f"{int(train.fit_pick.sum()):,} of their picks fitted.\n"
    )
    fits = {title: logit_fit(train, names) for title, names in FITS.items()}
    del train

    for title, f in fits.items():
        ll = ev.log_lik(lambda s, f=f: f[s][0], lambda s, f=f: f[s][1])
        offline(title, lambda s, f=f: f[s][0], ll)
    keep = ev.complete & (ev.n_picks > 0)
    for t, n, r, _ in variants.values():
        keep &= (n > 0) & ~np.isnan(r)
    idx = np.flatnonzero(keep)
    sub = [ev.drafts[i] for i in idx]
    wins = np.array([d["wins"] for d in sub], dtype=float)
    ctrl = R.controls(sub, [d["set"] for d in sub])
    strong = ev.strong

    def slope(x, i=slice(None)):
        return R.wins_slope(x[idx][i], wins[i], ctrl[i])

    main_t, main_n, main_r, _ = variants["main"]
    main_share = main_t / np.where(main_n > 0, main_n, 1)

    out += [
        f"{len(ev.drafts):,} replay drafts; {len(idx):,} complete events for the win "
        "columns. Win columns are Δevent wins per +1 SD, controlling for set and the "
        "drafter's win rate and games buckets, as in the replay report; in brackets, "
        "the difference from main and its paired bootstrap SE.",
        "",
        "Every fitted row is scored on each set with weights fitted to strong "
        "drafters' picks on the other nine. Log-likelihood is per strong drafter's "
        "pick on the replay drafts (higher is better; the fit's own objective).",
        "",
        "| variation | log-lik | top-1 all | top-1 strong | regret → wins "
        "(more negative is better) | top-1 share → wins (more positive is better) |",
        "|---|---|---|---|---|---|",
    ]
    for title, (t, n, r, ll) in variants.items():
        all_top1 = 100 * t.sum() / n.sum()
        strong_top1 = 100 * t[strong].sum() / n[strong].sum()
        share = t / np.where(n > 0, n, 1)
        cells = []
        for x, b in [(r, main_r), (share, main_share)]:
            s = slope(x)
            if title == "main":
                cells.append(f"{s:+.3f}")
                continue
            se = R.bootstrap(
                lambda i: slope(x, i) - slope(b, i), len(idx), samples=BOOTSTRAP
            )
            cells.append(f"{s:+.3f} ({s - slope(b):+.3f} ± {se:.3f})")
        ll_cell = "-" if ll is None else f"{ll:.4f}"
        out.append(
            f"| {title} | {ll_cell} | {all_top1:.1f} | {strong_top1:.1f} | "
            + " | ".join(cells)
            + " |"
        )

    out += ["", "## Weights fitted on all ten sets", ""]
    out += ["| variation | picks | weights (points; quality is 15) |", "|---|---|---|"]
    for title, f in fits.items():
        out.append(f"| {title} | {f['all'][2]:,} | {fmt_w(f['all'][0])} |")

    out += ["", "## By set: top-1 strong % / log-lik, each set held out", ""]
    titles = [t for t in variants if t != "main"]
    out += ["| set | main | " + " | ".join(titles) + " |"]
    out += ["|---|---|" + "---|" * len(titles)]
    for code in sorted(np.unique(ev.set)):
        mask = strong & (ev.set == code)
        cells = []
        for title in ["main"] + titles:
            t, n, _r, _ll = variants[title]
            cell = f"{100 * t[mask].sum() / n[mask].sum():.1f}"
            if title in fits:
                f = fits[title]
                rows, data = ev.subset(ev.fit_pick & (ev.pick_set == code))
                u = f[code][1] * (ev.scores(f[code][0])[rows] - BASE)
                top = np.maximum.reduceat(u, data.starts)
                e = np.exp(u - np.repeat(top, data.sizes))
                lse = top + np.log(np.add.reduceat(e, data.starts))
                cell += f" / {np.mean(u[data.chosen] - lse):.4f}"
            cells.append(cell)
        out.append(f"| {code} | " + " | ".join(cells) + " |")
    print("\n".join(out))


if __name__ == "__main__":
    main()
