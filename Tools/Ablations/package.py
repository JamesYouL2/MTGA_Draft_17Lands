"""Validate receipts and assemble branch-ready reports/source edits."""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run import read_gz
from variants import BASE_SHA, ALL_VARIANTS, variant_source, assert_baseline


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--reports", type=Path, required=True)
    p.add_argument("--payloads", type=Path, required=True)
    a = p.parse_args()
    assert_baseline()
    a.payloads.mkdir(parents=True, exist_ok=True)
    summaries = json.loads((a.reports / "summary.json").read_text())
    assert {s["variant"] for s in summaries} == set(ALL_VARIANTS)
    receipts, coverage, verification = [], {}, {}
    for folder in sorted(a.data.iterdir()):
        if not (folder / "receipt.json").exists():
            continue
        receipt = json.loads((folder / "receipt.json").read_text())
        assert sha(folder / "dataset.json.gz") == receipt["sha256"]["dataset.json.gz"]
        assert sha(folder / "drafts.json.gz") == receipt["sample_sha256"]
        receipts.append(receipt)
        with gzip.open(folder / "dataset.json.gz", "rt") as f:
            cards = json.load(f)["card_ratings"].values()
        tags = Counter(t for card in cards for t in card.get("tags", []))
        coverage[folder.name] = dict(tags)
        traces = read_gz(folder / "traces.json.gz")
        decks = read_gz(folder / "deck-candidates.json.gz")["drafts"]
        verification[folder.name] = {"real_pack_parity_checks_per_variant": traces["real_packs_checked_per_variant"],
            "skipped": traces["skipped"], "deck_candidate_sha256": sha(folder / "deck-candidates.json.gz"),
            "deck_pools_requested": len(decks), "deck_pools_evaluated": sum("error" not in d for d in decks),
            "deck_pool_errors": [{"id": d["id"], "error": d["error"]} for d in decks if "error" in d]}
    assert len(receipts) == 10
    manifest = {"base_sha": BASE_SHA, "requested_drafts": 10000, "requested_deck_pools": 1000,
        "input_receipts": receipts, "tag_coverage": coverage, "verification": verification,
        "python": sys.version, "platform": platform.platform(),
        "packages": {p: importlib.metadata.version(p) for p in ("numpy", "scipy", "numba", "requests", "ttkbootstrap")},
        "raw_output_sha256": {p.name: sha(p) for p in sorted(a.out.glob("*.json.gz"))}}
    (a.reports / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    lines = ["# One-factor ablation results — November 3, 2026", "",
        f"Baseline application: `{BASE_SHA}` (cache, format and hybrid fixes).",
        "18 pick ablations on 10,000 drafts; 7 deck-score ablations on 1,000 final pools; ten sets, frozen inputs, one factor at a time.", "",
        "## Pick scoring", "",
        "Differences are percentage points for agreement and event wins per SD for regret. Parentheses show paired bootstrap SEs.", "",
        "| Variant / result branch | Δ top-1 (SE) | Δ strong top-1 | Δ regret slope (SE) | Δ fixed-normalizer slope (SE) |",
        "|---|---:|---:|---:|---:|"]
    for s in summaries:
        v = s["variant"]
        if s["kind"] != "pick":
            continue
        e, f = s["outcomes"]["regret"], s["outcomes"]["fixed_regret"]
        link = f"https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-{v}-20261103"
        lines.append(f"| [{v}]({link}) | {s['top1_difference']:+.3f} ({s['top1_paired_se']:.3f}) | {s['strong_head']['top1']-s['strong_base']['top1']:+.3f} | {e['difference']:+.4f} ({e['paired_se']:.4f}) | {f['difference']:+.4f} ({f['paired_se']:.4f}) |")
    lines += ["", "## Live deck ranking", "",
        "Every baseline first displayed build was checked against live suggest_deck(). The variants reuse the same candidate builds and MC draws.", "",
        "Of 1,000 sampled pools, 998 produced decks and enter the paired screen. Two produced no builds and are recorded in manifest.json.", "",
        "| Variant / result branch | First build changed | Fixing-deficit builds, base → head | Δ score/wins slope (SE) |",
        "|---|---:|---:|---:|"]
    for s in summaries:
        if s["kind"] != "deck":
            continue
        v = s["variant"]
        e = s["outcomes"]["rating"]
        link = f"https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-{v}-20261103"
        lines.append(f"| [{v}]({link}) | {s['changed_top_build_percent']:.2f}% | {s['base']['unsupported_fixing_percent']:.2f}% → {s['head']['unsupported_fixing_percent']:.2f}% | {e['difference']:+.4f} ({e['paired_se']:.4f}) |")
    lines += ["", "## Interpretation and coverage", "",
        "- No synergy_* tags occur in any frozen snapshot. The three synergy-rule ablations are therefore unexercised, not evidence against synergy as a concept.",
        "- Own-pack and fixed-baseline-pack regret normalizations can disagree. Treat such disagreements as sensitivity, not proof of a wins gain.",
        "- This is an exploratory paired screen using format-wide ratings, not causal evaluation or a chronological holdout. No variant is automatically approved for merging.",
        "- Confirm promising simplifications on fresh data. A neutral small-sample result is not an equivalence test.",
        "- Generated-deck results do not establish effects on arbitrary manual deck builds or on other event formats.", "",
        "Each experiment branch contains its single application-source edit, EXPERIMENT_RESULT.md and experiment-result.json. Shared harness, all reports and provenance remain in this index branch.", "",
        "Reproduce with Tools/Ablations/README.md. Raw input snapshots and output rows are archived separately; exact input/output hashes and validation counts are in manifest.json.",
        "Public data: 17Lands, CC BY 4.0, https://www.17lands.com/public_datasets.", ""]
    (a.reports / "RESULTS.md").write_text("\n".join(lines))
    for s in summaries:
        v = s["variant"]
        path, source = variant_source(v)
        payload = {"variant": v, "branch": f"exp/ablate-{v}-20261103",
            "files": [
                {"path": path, "mode": "100644", "type": "blob", "content": source},
                {"path": "EXPERIMENT_RESULT.md", "mode": "100644", "type": "blob", "content": (a.reports/v/"RESULTS.md").read_text()},
                {"path": "experiment-result.json", "mode": "100644", "type": "blob", "content": (a.reports/v/"summary.json").read_text()},
            ]}
        (a.payloads / f"{v}.json").write_text(json.dumps(payload))
    print(f"Prepared {len(summaries)} result branches with validated receipts", flush=True)
