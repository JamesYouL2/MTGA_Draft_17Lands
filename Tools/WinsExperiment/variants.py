"""Compare main, main with parts of its score switched off, and the pick score
refitted with and without castability, on agreement with drafters and on
event wins.

    python Tools/WinsExperiment/variants.py --eval features/*.eval.json.gz \
        --train features/*.train.json.gz --replay replay/ > report.md

--replay holds the advisor replay's SET.base.json (main) and SET.head.json
(this branch) for the same drafts as the --eval features, and SET.LABEL.json
from ablate.py.
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
NAMES = [
    "quality",
    "lane",
    "color_support",
    "color_gap",
    "unrated",
    "off_pips",
    "late_off_pips",
]
CASTABILITY = ["off_pips", "late_off_pips"]
FITTED = {
    "quality": 15.0,
    "lane": 11.1,
    "color_support": 0.9,
    "color_gap": -2.0,
    "unrated": -10.9,
}
ABLATIONS = [
    ("nocast", "main without castability"),
    ("nocomp", "main without composition"),
    ("nocastcomp", "main without either"),
]
BOOTSTRAP = 200


def vec(w):
    return np.array([w.get(k, 0.0) for k in NAMES])


class Picks:
    """Every pick of some drafts, as flat arrays: one row per distinct pack card."""

    def __init__(self, paths):
        X, basic, sizes, taken, owner = [], [], [], [], []
        self.drafts, self.keys = [], []
        for path in sorted(paths):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            assert data["names"] == NAMES, data["names"]
            fx, fb, fs, ft, fo = [], [], [], [], []
            for draft in data["drafts"]:
                d = len(self.drafts)
                self.drafts.append(
                    {k: draft[k] for k in ("id", "skill", "games", "wins", "losses")}
                    | {"set": data["set"]}
                )
                for pack, pick, t, rows in draft["picks"]:
                    fs.append(len(rows))
                    ft.append(t)
                    fo.append(d)
                    self.keys.append((d, pack, pick))
                    for r in rows:
                        fb.append(r is None)
                        fx.append(r or [0.0] * len(NAMES))
            X.append(np.array(fx, dtype=float).reshape(-1, len(NAMES)))
            basic.append(np.array(fb, dtype=bool))
            sizes.append(np.array(fs, dtype=int))
            taken.append(np.array(ft, dtype=int))
            owner.append(np.array(fo, dtype=int))
            del data, fx, fb
        self.X, self.basic = np.vstack(X), np.concatenate(basic)
        self.sizes, self.taken = np.concatenate(sizes), np.concatenate(taken)
        self.owner = np.concatenate(owner)
        self.starts = np.concatenate([[0], np.cumsum(self.sizes)[:-1]]).astype(int)
        self.row_pick = np.repeat(np.arange(len(self.sizes)), self.sizes)
        self.set = np.array([d["set"] for d in self.drafts])
        self.complete = np.array([R.is_complete(d) for d in self.drafts])
        self.strong = np.array([R.is_strong(d) for d in self.drafts])
        self.n_picks = np.bincount(self.owner, minlength=len(self.drafts))

    def per_pick(self, w, rows=None):
        """(top-1, regret) per pick, as replay.py computes them for score weights w."""
        s = np.round(BASE + self.X @ vec(w), 1)
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
        pick_set = self.set[self.owner]
        for code in np.unique(self.set):
            t, r = self.per_pick(weights_for(code))
            mask = pick_set == code
            top1[mask], regret[mask] = t[mask], r[mask]
        return top1, regret


# --- Refits -------------------------------------------------------------------


def logit_fit(train, names):
    """For each set, conditional logit weights for the features names, fitted to
    strong drafters' picks on the other sets, in points (quality 15); and the
    fit on all sets."""
    cols = [NAMES.index(k) for k in names]
    pick_ok = train.strong[train.owner].copy()
    chosen_row = train.starts + train.taken
    pick_ok &= ~train.basic[chosen_row]
    nonbasic = np.add.reduceat((~train.basic).astype(int), train.starts)
    pick_ok &= nonbasic >= 2
    pick_set = train.set[train.owner]

    def fit(mask):
        picks = np.flatnonzero(mask)
        keep_row = np.repeat(mask, train.sizes) & ~train.basic
        before = np.cumsum(keep_row) - keep_row  # kept rows before each row
        sizes = np.add.reduceat(keep_row.astype(int), train.starts)[picks]
        starts = np.concatenate([[0], np.cumsum(sizes)[:-1]]).astype(int)
        offset = before[chosen_row[picks]] - before[train.starts[picks]]
        data = SimpleNamespace(
            sizes=sizes,
            starts=starts,
            chosen=starts + offset,
            draft=train.owner[picks],
        )
        X = train.X[np.flatnonzero(keep_row)][:, cols]
        beta, _ = fit_logit(X, data)
        points = beta / beta[0] * 15.0
        return dict(zip(names, np.round(points, 1))), len(picks)

    out = {"all": fit(pick_ok)}
    for code in sorted(np.unique(train.set)):
        out[code] = fit(pick_ok & (pick_set != code))
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
    return ", ".join(f"{w.get(k, 0.0):+g}" for k in NAMES[1:])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--eval", nargs="+", required=True)
    parser.add_argument("--train", nargs="+", required=True)
    parser.add_argument("--replay", required=True)
    args = parser.parse_args(argv)

    ev = Picks(args.eval)
    out = []

    # Main, main with parts switched off, and this branch, as the replay scored them.
    variants = {}
    for label, title in [("base", "main")] + ABLATIONS + [("head", "this PR (replay)")]:
        t, n, r, missing = load_replay(args.replay, label, ev)
        out.append(f"<!-- {label}: {missing} eval drafts missing from the replay -->")
        if missing < len(ev.drafts):
            variants[title] = (t, n, r, None)

    def offline(title, w_for, shown):
        top1, regret = ev.by_set(w_for)
        variants[title] = (
            np.bincount(ev.owner, top1, len(ev.drafts)),
            ev.n_picks.astype(float),
            ev.per_draft(regret),
            shown,
        )

    offline("this PR", lambda s: FITTED, fmt_w(FITTED))

    # The offline scoring should reproduce the replay of this branch.
    rep_t, rep_n, rep_r, _ = variants.pop("this PR (replay)")
    off_t, off_n, off_r, _ = variants["this PR"]
    same_n = np.mean(rep_n == off_n)
    ok = (rep_n > 0) & (off_n > 0)
    out.append(
        f"Check: offline scoring matches the replay of this PR on {100 * same_n:.2f}% of "
        f"drafts' pick counts, {100 * np.mean(rep_t[ok] == off_t[ok]):.2f}% of drafts' "
        f"top-1 counts, and drafts' mean regret to within "
        f"{np.nanmax(np.abs(rep_r[ok] - off_r[ok])):.4f}.\n"
    )

    train = Picks(args.train)
    out.append(
        f"Training sample (a different salt): {len(train.drafts):,} drafts, "
        f"{int(train.strong.sum()):,} by strong drafters, {len(train.sizes):,} picks.\n"
    )
    refits = {
        "refit, no castability": logit_fit(train, NAMES[:5]),
        "refit with castability": logit_fit(train, NAMES),
    }
    del train
    for title, fits in refits.items():
        offline(
            title,
            lambda s, fits=fits: fits[s][0],
            fmt_w(fits["all"][0]) + f" ({fits['all'][1]:,} picks)",
        )

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
        "Weights are " + ", ".join(NAMES[1:]) + " (quality is 15). Refits are "
        "scored on each set with weights fitted to strong drafters' picks on the "
        "other nine.",
        "",
        "| variation | weights | top-1 all | top-1 strong | regret → wins "
        "(more negative is better) | top-1 share → wins (more positive is better) |",
        "|---|---|---|---|---|---|",
    ]
    for title, (t, n, r, shown) in variants.items():
        all_top1 = 100 * t.sum() / n.sum()
        strong_top1 = 100 * t[strong].sum() / n[strong].sum()
        share = t / np.where(n > 0, n, 1)
        cells = []
        for x, base in [(r, main_r), (share, main_share)]:
            s = slope(x)
            if title == "main":
                cells.append(f"{s:+.3f}")
                continue
            se = R.bootstrap(
                lambda i: slope(x, i) - slope(base, i), len(idx), samples=BOOTSTRAP
            )
            cells.append(f"{s:+.3f} ({s - slope(base):+.3f} ± {se:.3f})")
        out.append(
            f"| {title} | {shown or '-'} | {all_top1:.1f} | {strong_top1:.1f} | "
            + " | ".join(cells)
            + " |"
        )

    out += ["", "## Weights fitted on the other nine sets", ""]
    out += ["| left out | " + " | ".join(refits) + " |", "|---|---|---|"]
    for code in sorted(k for k in refits["refit with castability"] if k != "all"):
        out.append(
            f"| {code} | "
            + " | ".join(fmt_w(fits[code][0]) for fits in refits.values())
            + " |"
        )
    print("\n".join(out))


if __name__ == "__main__":
    main()
