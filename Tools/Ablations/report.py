"""Paired draft bootstrap for sequential ablations; observational diagnostics."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run import read_gz
from variants import BASE_SHA, PICK_VARIANTS, DECK_VARIANTS, variant_source

spec = importlib.util.spec_from_file_location("replay_report", HERE.parent / "AdvisorReplay" / "report.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


def load(out, names):
    runs = {name: read_gz(out / f"{name}.json.gz")["drafts"] for name in names}
    ids = lambda rows: [(r["set"], r["id"]) for r in rows]
    reference = ids(runs[names[0]])
    assert all(ids(rows) == reference for rows in runs.values()), "unpaired drafts"
    return runs


def slopes(x, wins, controls):
    sd = x.std(axis=0)
    scaled = x / np.where(sd > 0, sd, 1)
    values = np.column_stack([wins, scaled])
    residual = values - controls @ np.linalg.lstsq(controls, values, rcond=None)[0]
    denom = (residual[:, 1:] ** 2).sum(axis=0)
    return (residual[:, 1:] * residual[:, :1]).sum(axis=0) / np.where(denom > 0, denom, np.nan)


def outcomes(runs, names, fields, bootstraps=200):
    rows = runs[names[0]]
    keep = [i for i, r in enumerate(rows) if (r["wins"] == 7 or r["losses"] == 3)
            and all(runs[v][i].get(f) is not None for v in names for f in fields)]
    selected = [rows[i] for i in keep]
    wins = np.array([r["wins"] for r in selected], dtype=float)
    ctrl = old.controls(selected, [r["set"] for r in selected])
    columns = [(v, f) for f in fields for v in names]
    x = np.array([[runs[v][i][f] for v, f in columns] for i in keep], dtype=float)
    coef = slopes(x, wins, ctrl)
    rng = np.random.default_rng(20261103)
    boots = []
    for _ in range(bootstraps):
        idx = rng.integers(0, len(wins), len(wins))
        boots.append(slopes(x[idx], wins[idx], ctrl[idx]))
    boots = np.array(boots)
    result = {}
    for field in fields:
        b = columns.index((names[0], field))
        for variant in names:
            h = columns.index((variant, field))
            result[variant, field] = {"events": len(wins), "base": float(coef[b]),
                "head": float(coef[h]), "difference": float(coef[h]-coef[b]),
                "paired_se": float((boots[:, h] - boots[:, b]).std())}
    return result


def agreement(rows, strong=False):
    rows = [r for r in rows if not strong or r["strong"]]
    n = sum(r["n"] for r in rows)
    return {"picks": n, "top1": 100*sum(r["top1"] for r in rows)/n,
            "top3": 100*sum(r["top3"] for r in rows)/n}


def pick_reports(out, destination):
    names = ["baseline", *PICK_VARIANTS]
    runs = load(out, names)
    effects = outcomes(runs, names, ["regret", "fixed_regret"])
    rng = np.random.default_rng(20261103)
    n = np.array([r["n"] for r in runs["baseline"]], dtype=float)
    counts = np.array([[runs[v][i]["top1"] for v in names] for i in range(len(n))])
    bootstrap = []
    for _ in range(200):
        idx = rng.integers(0, len(n), len(n))
        top1 = 100 * counts[idx].sum(axis=0) / n[idx].sum()
        bootstrap.append(top1-top1[0])
    ses = np.array(bootstrap).std(axis=0)
    summaries = []
    for j, variant in enumerate(PICK_VARIANTS, 1):
        rows = runs[variant]
        b, h = agreement(runs["baseline"]), agreement(rows)
        sb, sh = agreement(runs["baseline"], True), agreement(rows, True)
        per_set = []
        for code in sorted({r["set"] for r in rows}):
            before = agreement([r for r in runs["baseline"] if r["set"] == code])
            after = agreement([r for r in rows if r["set"] == code])
            per_set.append({"set": code, "base_top1": before["top1"], "head_top1": after["top1"],
                            "difference": after["top1"]-before["top1"]})
        summary = {"variant": variant, "kind": "pick", "base_sha": BASE_SHA,
            "drafts": len(rows), "base": b, "head": h, "strong_base": sb, "strong_head": sh,
            "top1_difference": h["top1"]-b["top1"], "top1_paired_se": float(ses[j]),
            "changed_top_pick_percent": 100*sum(r["changed"] for r in rows)/h["picks"],
            "outcomes": {f: effects[variant, f] for f in ("regret", "fixed_regret")}, "per_set": per_set}
        write_result(destination, summary)
        summaries.append(summary)
    return summaries


def deck_reports(out, destination):
    names = ["deck-baseline", *DECK_VARIANTS]
    runs = load(out, names)
    effects = outcomes(runs, names, ["rating"])
    summaries = []
    for variant in DECK_VARIANTS:
        def metrics(rows):
            return {"unsupported_fixing_percent": 100*np.mean([r["missing_fixing"] > 0 for r in rows]),
                    "mean_quality": np.mean([r["quality"] for r in rows]),
                    "mean_colors": np.mean([r["colors"] for r in rows]),
                    **{stat: np.mean([r["stats"][stat] for r in rows])
                       for stat in ("color_screw_t3", "screw_t3", "flood_t5")}}
        rows = runs[variant]
        summary = {"variant": variant, "kind": "deck", "base_sha": BASE_SHA,
            "pools": len(rows), "changed_top_build_percent": 100*np.mean([r["changed"] for r in rows]),
            "base": metrics(runs["deck-baseline"]), "head": metrics(rows),
            "outcomes": {"rating": effects[variant, "rating"]}}
        write_result(destination, summary)
        summaries.append(summary)
    return summaries


def write_result(destination, summary):
    variant = summary["variant"]
    folder = destination / variant
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    lines = [f"# Ablation: {variant}", "", f"Frozen application baseline: `{BASE_SHA}`.",
             "One factor removed; all other source and inputs are held fixed.", ""]
    if variant in ("no-artifact-synergy", "no-graveyard-synergy", "no-counters-synergy"):
        lines += ["**Coverage limit:** none of the ten frozen rating snapshots contains `synergy_*` tags. This screen therefore does not exercise this rule; an unchanged result is not evidence that synergy never matters.", ""]
    if summary["kind"] == "pick":
        lines += [f"{summary['drafts']:,} drafts; {summary['head']['picks']:,} scored choices across ten sets.", "",
                  "| Metric | Baseline | Ablation | Difference (paired SE) |",
                  "|---|---:|---:|---:|",
                  f"| Top-1 agreement, all (%) | {summary['base']['top1']:.3f} | {summary['head']['top1']:.3f} | {summary['top1_difference']:+.3f} ({summary['top1_paired_se']:.3f}) |",
                  f"| Top-1 agreement, strong (%) | {summary['strong_base']['top1']:.3f} | {summary['strong_head']['top1']:.3f} | {summary['strong_head']['top1']-summary['strong_base']['top1']:+.3f} |",
                  f"| Top-3 agreement, all (%) | {summary['base']['top3']:.3f} | {summary['head']['top3']:.3f} | {summary['head']['top3']-summary['base']['top3']:+.3f} |"]
        for field, effect in summary["outcomes"].items():
            lines.append(f"| Wins per SD {field} | {effect['base']:+.4f} | {effect['head']:+.4f} | {effect['difference']:+.4f} ({effect['paired_se']:.4f}) |")
        lines += ["", f"Changed top recommendation: {summary['changed_top_pick_percent']:.3f}% of choices.", "",
                  "More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.",
                  "`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.", "",
                  "| Set | Top-1 difference (points) |", "|---|---:|"]
        lines += [f"| {r['set']} | {r['difference']:+.3f} |" for r in summary["per_set"]]
    else:
        lines += [f"{summary['pools']:,} real final pools. Every baseline ranking was checked against live `suggest_deck()` output.", "",
                  f"Changed first displayed build: {summary['changed_top_build_percent']:.2f}%.", "",
                  "| Metric | Baseline | Ablation |", "|---|---:|---:|"]
        lines += [f"| {name} | {summary['base'][name]:.4f} | {summary['head'][name]:.4f} |" for name in summary["base"]]
        e = summary["outcomes"]["rating"]
        lines += ["", f"Wins per SD displayed score: {e['base']:+.4f} → {e['head']:+.4f}; difference {e['difference']:+.4f} (paired SE {e['paired_se']:.4f}).",
                  "This describes observational score association and selection behavior, not wins gained by following a build."]
    lines += ["", "## Reproduction and limits", "",
              "Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.",
              "Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.",
              "Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.",
              "Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.", ""]
    (folder / "RESULTS.md").write_text("\n".join(lines))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--reports", type=Path, required=True)
    a = p.parse_args()
    summaries = pick_reports(a.out, a.reports) + deck_reports(a.out, a.reports)
    (a.reports / "summary.json").write_text(json.dumps(summaries, indent=2, allow_nan=False)+"\n")
    print(f"Wrote {len(summaries)} paired experiment reports", flush=True)
