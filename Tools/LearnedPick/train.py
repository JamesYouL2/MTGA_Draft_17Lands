"""Fit the learned pick models without one set, and check them on it.

    python Tools/LearnedPick/train.py --rows rows/ --heldout FRA --out models/

rows/ holds features.py's <SET>.npz for every set. Nothing from --heldout is
used to fit or tune its models: its rows are only read for the held-out check.

- lgbm-strong: picks by strong drafters (either sample).
- lgbm-wins: the all-drafter sample's picks, each pick weighted by its draft's
  event match wins (0 to 7; drafts with 0 wins drop out).
- lgbm-strong-noalsa: as lgbm-strong, with ALSA hidden (crowd pick order).
- lgbm-weak: as lgbm-strong-noalsa, on weak drafters' picks (a placebo).
- logit-simple: strong drafters' picks, as lgbm-strong.

--heads fits only the named models.

LightGBM's leaves are picked from a small grid, and its rounds by early
stopping, on validation sets: four of the training sets, by a hash. The pick
is the lowest validation pick log-loss after one fitted temperature (ranking
scores aren't probabilities). The models are then refitted on all training
sets with the chosen settings.

    python Tools/LearnedPick/train.py --report models/ > report.md

writes the summary of every held-out set's fit.
"""

import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import FEATURES  # noqa: E402
from model import (  # noqa: E402
    LGBM_HEADS,
    LOGIT_INPUTS,
    QUALITY_POINTS,
    logit_inputs,
    masked,
)

LEAVES = (15, 63)
LEARNING_RATE = 0.05
MAX_ROUNDS = 1500
PATIENCE = 50
VALIDATION_SETS = 4


class Picks:
    """Rows grouped by pick: rows of a pick are contiguous."""

    def __init__(self, X, label, group, weight, sets):
        self.X, self.label, self.group = X, label, group
        self.weight = weight  # per pick
        self.sets = sets  # per pick
        self.start = np.concatenate([[0], np.cumsum(group)[:-1]]).astype(np.int64)

    def take(self, keep):
        """The picks where keep (per pick) is true."""
        keep = np.asarray(keep, dtype=bool)
        rows = np.repeat(keep, self.group)
        return Picks(
            self.X[rows],
            self.label[rows],
            self.group[keep],
            self.weight[keep],
            self.sets[keep],
        )

    def row_weight(self):
        return np.repeat(self.weight, self.group)

    def __len__(self):
        return len(self.group)


def load_rows(paths):
    """{set: dict of arrays} from features.py's .npz files."""
    out = {}
    for path in paths:
        with np.load(path, allow_pickle=False) as z:
            if list(z["features"]) != FEATURES:
                raise SystemExit(f"{path}: features differ from features.py")
            out[str(z["set"])] = {k: z[k] for k in z.files}
    return out


def hide(picks, hidden):
    """Picks with the hidden features missing."""
    if not hidden:
        return picks
    return Picks(masked(picks.X, hidden), picks.label, picks.group, picks.weight, picks.sets)


def picks_of(rows, sets, which):
    """Picks of the given sets: which is "strong", "weak", "wins" or "all".

    "all" is the all-drafter sample unweighted, for checking agreement."""
    parts = []
    for s in sets:
        r = rows[s]
        keep = r[which] if which in ("strong", "weak") else r["in_all"]
        weight = r["wins"] if which == "wins" else np.ones(len(r["group"]))
        if which == "wins":
            keep = keep & (weight > 0)
        p = Picks(r["X"], r["label"], r["group"], weight.astype(np.float64),
                  np.array([s] * len(r["group"])))
        parts.append(p.take(keep))
    return Picks(
        np.concatenate([p.X for p in parts]),
        np.concatenate([p.label for p in parts]),
        np.concatenate([p.group for p in parts]),
        np.concatenate([p.weight for p in parts]),
        np.concatenate([p.sets for p in parts]),
    )


def group_softmax(picks, scores):
    """Each row's softmax probability within its pick."""
    gid = np.repeat(np.arange(len(picks)), picks.group)
    top = np.maximum.reduceat(scores, picks.start)
    e = np.exp(scores - top[gid])
    return e / np.add.reduceat(e, picks.start)[gid]


def pick_log_loss(picks, scores, temperature=1.0):
    """Mean (pick-weighted) negative log chance of the card taken."""
    p = group_softmax(picks, scores / temperature)
    taken = np.log(np.maximum(p[picks.label == 1], 1e-300))
    return float(-(taken * picks.weight).sum() / picks.weight.sum())


def calibrated_log_loss(picks, scores):
    """pick_log_loss at its best temperature (searched on a log grid)."""
    grid = np.exp(np.linspace(np.log(0.05), np.log(20.0), 61))
    losses = [pick_log_loss(picks, scores, t) for t in grid]
    i = int(np.argmin(losses))
    return losses[i], float(grid[i])


def agreement(picks, scores, weighted=False):
    """(top-1, top-3) in percent: how often the card taken scores best, top 3."""
    gid = np.repeat(np.arange(len(picks)), picks.group)
    taken = scores[picks.label == 1]
    # Rank of the card taken: rows of the same pick scoring higher (ties count half).
    higher = np.zeros(len(picks))
    ties = np.zeros(len(picks))
    np.add.at(higher, gid, scores > taken[gid])
    np.add.at(ties, gid, scores == taken[gid])
    rank = higher + (ties - 1) / 2.0
    w = picks.weight if weighted else np.ones(len(picks))
    return (
        float(100 * (w * (rank < 0.5)).sum() / w.sum()),
        float(100 * (w * (rank < 2.5)).sum() / w.sum()),
    )


def lgbm_dataset(lightgbm, picks, reference=None):
    return lightgbm.Dataset(
        picks.X,
        label=picks.label,
        group=picks.group,
        weight=picks.row_weight(),
        feature_name=FEATURES,
        reference=reference,
        free_raw_data=False,
    )


def lgbm_params(leaves):
    return {
        "objective": "lambdarank",
        "metric": "ndcg",
        "eval_at": [3],
        "learning_rate": LEARNING_RATE,
        "num_leaves": leaves,
        "min_data_in_leaf": 200,
        "feature_fraction": 0.9,
        "verbosity": -1,
        "seed": 1,
        "deterministic": True,
        "num_threads": os.cpu_count() or 2,
    }


def fit_lgbm(train, valid):
    """The chosen settings, their grid, and the model refitted on train + valid."""
    import lightgbm

    grid = []
    for leaves in LEAVES:
        dtrain = lgbm_dataset(lightgbm, train)
        dvalid = lgbm_dataset(lightgbm, valid, reference=dtrain)
        booster = lightgbm.train(
            lgbm_params(leaves),
            dtrain,
            num_boost_round=MAX_ROUNDS,
            valid_sets=[dvalid],
            callbacks=[lightgbm.early_stopping(PATIENCE, verbose=False)],
        )
        rounds = booster.best_iteration or MAX_ROUNDS
        scores = booster.predict(valid.X, num_iteration=rounds)
        loss, temp = calibrated_log_loss(valid, scores)
        grid.append(
            {
                "leaves": leaves,
                "rounds": rounds,
                "valid_log_loss": round(loss, 5),
                "temperature": round(temp, 4),
                "valid_top1": round(agreement(valid, scores, True)[0], 2),
            }
        )
    best = min(grid, key=lambda g: g["valid_log_loss"])
    both = concat(train, valid)
    booster = lightgbm.train(
        lgbm_params(best["leaves"]),
        lgbm_dataset(lightgbm, both),
        num_boost_round=best["rounds"],
    )
    return best, grid, booster


def concat(a, b):
    return Picks(
        np.concatenate([a.X, b.X]),
        np.concatenate([a.label, b.label]),
        np.concatenate([a.group, b.group]),
        np.concatenate([a.weight, b.weight]),
        np.concatenate([a.sets, b.sets]),
    )


def fit_logit(picks, iterations=50):
    """Conditional logit coefficients on logit_inputs (Newton's method)."""
    Z = logit_inputs(picks.X)
    gid = np.repeat(np.arange(len(picks)), picks.group)
    w = picks.weight[gid]
    beta = np.zeros(Z.shape[1])
    for _ in range(iterations):
        p = group_softmax(picks, Z @ beta)
        grad = ((picks.label - p) * w) @ Z
        mean = np.add.reduceat(p[:, None] * Z, picks.start)  # per pick
        centered = Z - mean[gid]
        hess = (centered * (p * w)[:, None]).T @ centered
        step = np.linalg.solve(hess, grad)
        beta += step
        if np.max(np.abs(step)) < 1e-9:
            break
    return beta, np.linalg.inv(hess)


def logit_points(beta, cov):
    """Points per unit of each input, quality fixed at QUALITY_POINTS, with SEs."""
    scale = QUALITY_POINTS / beta[0]
    points = beta * scale
    # Delta method for points_j = 15 * b_j / b_0.
    ses = []
    for j in range(len(beta)):
        g = np.zeros(len(beta))
        if j == 0:
            ses.append(0.0)
            continue
        g[0] = -QUALITY_POINTS * beta[j] / beta[0] ** 2
        g[j] = QUALITY_POINTS / beta[0]
        ses.append(float(np.sqrt(g @ cov @ g)))
    return {k: float(v) for k, v in zip(LOGIT_INPUTS, points)}, dict(
        zip(LOGIT_INPUTS, ses)
    )


def validation_sets(train_sets, heldout, n=VALIDATION_SETS):
    key = lambda s: hashlib.md5(f"{heldout}:{s}".encode()).hexdigest()
    return sorted(sorted(train_sets, key=key)[:n])


def quality_scores(picks):
    """GIH WR alone, for reference (unrated cards last)."""
    return np.nan_to_num(picks.X[:, FEATURES.index("quality")], nan=-99.0)


def train(rows, heldout, out_dir, n_valid=VALIDATION_SETS, heads=None):
    if heads is None:
        # Every model whose training picks the rows have (older rows lack "weak").
        heads = [
            h for h, (which, _) in LGBM_HEADS.items()
            if which not in ("weak",) or all(which in r for r in rows.values())
        ] + ["logit-simple"]
    train_sets = sorted(s for s in rows if s != heldout)
    valid_sets = validation_sets(train_sets, heldout, n_valid)
    fit_sets = [s for s in train_sets if s not in valid_sets]
    folder = os.path.join(out_dir, heldout)
    os.makedirs(folder, exist_ok=True)
    summary = {
        "heldout": heldout,
        "train_sets": train_sets,
        "validation_sets": valid_sets,
        "models": {},
    }
    test_strong = picks_of(rows, [heldout], "strong")
    test_all = picks_of(rows, [heldout], "all")
    summary["heldout_picks"] = {"strong": len(test_strong), "all": len(test_all)}
    summary["gihwr"] = {
        "strong": agreement(test_strong, quality_scores(test_strong)),
        "all": agreement(test_all, quality_scores(test_all)),
    }

    for head, (which, hidden) in LGBM_HEADS.items():
        if heads is not None and head not in heads:
            continue
        best, grid, booster = fit_lgbm(
            hide(picks_of(rows, fit_sets, which), hidden),
            hide(picks_of(rows, valid_sets, which), hidden),
        )
        booster.save_model(os.path.join(folder, f"{head}.txt"))
        gain = booster.feature_importance(importance_type="gain")
        summary["models"][head] = {
            "chosen": best,
            "grid": grid,
            "gain_share": {
                f: round(float(g / gain.sum()), 4) for f, g in zip(FEATURES, gain)
            },
            "heldout": {
                "strong": agreement(
                    test_strong, booster.predict(masked(test_strong.X, hidden))
                ),
                "all": agreement(test_all, booster.predict(masked(test_all.X, hidden))),
            },
            "picks": len(picks_of(rows, train_sets, which)),
        }

    if heads is not None and "logit-simple" not in heads:
        with open(os.path.join(folder, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1)
        return summary
    picks = picks_of(rows, train_sets, "strong")
    beta, cov = fit_logit(picks)
    points, ses = logit_points(beta, cov)
    with open(os.path.join(folder, "logit-simple.json"), "w", encoding="utf-8") as f:
        json.dump({"weights": points, "ses": ses}, f, indent=1)
    from model import Logit

    logit = Logit(points)
    summary["models"]["logit-simple"] = {
        "weights": points,
        "ses": ses,
        "heldout": {
            "strong": agreement(test_strong, logit.score(test_strong.X)),
            "all": agreement(test_all, logit.score(test_all.X)),
        },
        "picks": len(picks),
    }
    with open(os.path.join(folder, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    return summary


def report(models_dir):
    """Markdown summary of every held-out set's fit."""
    summaries = []
    for path in sorted(glob.glob(os.path.join(models_dir, "*", "summary.json"))):
        with open(path, encoding="utf-8") as f:
            summaries.append(json.load(f))
    if not summaries:
        return "No fits found.\n"
    fitted = set(summaries[0]["models"])
    lgbm = [h for h in LGBM_HEADS if h in fitted]
    heads = lgbm + [h for h in ["logit-simple"] if h in fitted]
    out = ["# Learned pick models: fits", ""]
    out.append(
        "Each set scored by models fitted without it, on its own full ratings "
        "(not the replay's held-out ratings). Top-1 / top-3 agreement with the "
        "card taken, in percent."
    )
    out.append("")
    out.append("| set | picks (strong) | GIH WR only | " + " | ".join(heads) + " |")
    out.append("|---" * (3 + len(heads)) + "|")
    totals = {h: np.zeros(2) for h in ["gihwr"] + heads}
    n_total = 0
    for s in summaries:
        n = s["heldout_picks"]["strong"]
        n_total += n
        cells = [f"{s['gihwr']['strong'][0]:.1f} / {s['gihwr']['strong'][1]:.1f}"]
        totals["gihwr"] += n * np.array(s["gihwr"]["strong"])
        for h in heads:
            a = s["models"][h]["heldout"]["strong"]
            totals[h] += n * np.array(a)
            cells.append(f"{a[0]:.1f} / {a[1]:.1f}")
        out.append(f"| {s['heldout']} | {n} | " + " | ".join(cells) + " |")
    cells = [
        f"{totals[h][0] / n_total:.1f} / {totals[h][1] / n_total:.1f}"
        for h in ["gihwr"] + heads
    ]
    out.append(f"| **all** | {n_total} | " + " | ".join(f"**{c}**" for c in cells) + " |")
    out.append("")
    out.append("## Chosen LightGBM settings")
    out.append("")
    out.append("Leaves / rounds.")
    out.append("")
    out.append("| set | " + " | ".join(lgbm) + " |")
    out.append("|---" * (1 + len(lgbm)) + "|")
    for s in summaries:
        c = [s["models"][h]["chosen"] for h in lgbm]
        out.append(
            f"| {s['heldout']} | "
            + " | ".join(f"{x['leaves']} / {x['rounds']}" for x in c)
            + " |"
        )
    out.append("")
    out.append("## Feature importance (share of gain, mean over fits)")
    out.append("")
    out.append("| feature | " + " | ".join(lgbm) + " |")
    out.append("|---" * (1 + len(lgbm)) + "|")
    for f in FEATURES:
        vals = [
            np.mean([s["models"][h]["gain_share"][f] for s in summaries]) for h in lgbm
        ]
        out.append(f"| {f} | " + " | ".join(f"{100 * v:.1f}%" for v in vals) + " |")
    if "logit-simple" not in heads:
        return "\n".join(out) + "\n"
    out.append("")
    out.append("## logit-simple weights (points; quality fixed at 15)")
    out.append("")
    out.append("| set | " + " | ".join(LOGIT_INPUTS[1:]) + " |")
    out.append("|---" * len(LOGIT_INPUTS) + "|")
    for s in summaries:
        m = s["models"]["logit-simple"]
        out.append(
            f"| {s['heldout']} | "
            + " | ".join(
                f"{m['weights'][k]:+.2f} ± {m['ses'][k]:.2f}" for k in LOGIT_INPUTS[1:]
            )
            + " |"
        )
    return "\n".join(out) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--rows", help="Folder of features.py's <SET>.npz")
    parser.add_argument("--heldout", help="The set to leave out")
    parser.add_argument("--out", help="Models folder")
    parser.add_argument("--validation-sets", type=int, default=VALIDATION_SETS)
    parser.add_argument("--report", help="Summarize a models folder instead")
    parser.add_argument("--heads", default="", help="Comma-separated models to fit (default: all)")
    args = parser.parse_args(argv)
    if args.report:
        sys.stdout.write(report(args.report))
        return
    rows = load_rows(sorted(glob.glob(os.path.join(args.rows, "*.npz"))))
    if args.heldout not in rows:
        raise SystemExit(f"No rows for {args.heldout}")
    heads = [h for h in args.heads.split(",") if h] or None
    summary = train(rows, args.heldout, args.out, args.validation_sets, heads)
    print(json.dumps({h: m["heldout"] for h, m in summary["models"].items()}))


if __name__ == "__main__":
    main()
