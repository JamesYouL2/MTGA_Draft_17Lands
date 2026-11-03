"""Sequential one-factor replays on frozen drafts and ratings.

Prepare baseline traces once, then run each ablation to completion before the
next. The fast scoring path is checked against independently compiled edited
engine source on real packs, and synthetic tests cover composition fallthrough.
"""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import statistics
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "AdvisorReplay"), str(HERE.parents[1])]
from replay import App
from variants import (BASE_SHA, ENGINE, PICK_VARIANTS, advisor_class, traced_class,
                      scores_from_trace, variant_source, assert_baseline)


def read_gz(path):
    with gzip.open(path, "rt") as f:
        return json.load(f)


def write_gz(path, value):
    def convert(value):
        if isinstance(value, set):
            return sorted(value)
        raise TypeError(f"Unsupported experiment value: {type(value).__name__}")
    temporary = path.with_suffix(path.suffix + ".partial")
    with gzip.open(temporary, "wt") as f:
        json.dump(value, f, separators=(",", ":"), default=convert, allow_nan=False)
    temporary.replace(path)


def score_map(recs):
    scores = {}
    for r in recs:
        scores.setdefault(r.card_name, r.contextual_score)
    return scores


def build_traces(folder, source):
    target = folder / "traces.json.gz"
    if target.exists():
        return
    app = App(str(folder / "dataset.json.gz"))
    Trace = traced_class(source)
    classes = {v: advisor_class(variant_source(v, source)[1]) for v in PICK_VARIANTS}
    rows, skipped, validations = [], Counter(), 0
    for d in read_gz(folder / "drafts.json.gz"):
        picks = []
        for pack_no, pick_no, taken, pack_names, pool_names in d["picks"]:
            pack, pool = app.cards(pack_names), app.cards(pool_names)
            took = app.cards([taken])
            if not took or len({c["name"] for c in pack}) < 2:
                skipped["unmatched taken or trivial pack"] += 1
                continue
            taken = took[0]["name"]
            advisor = Trace(app.metrics, pool)
            advisor._trace, advisor._pick = [], pick_no
            baseline = score_map(advisor.evaluate_pack(pack, pick_no, pack_no))
            if taken not in baseline:
                skipped["missing advice"] += 1
                continue
            fast_base = scores_from_trace(advisor, "baseline", Trace, pack_no)
            assert fast_base == baseline, (folder.name, "baseline", baseline, fast_base)
            if validations < 40:
                for v, cls in classes.items():
                    other = object.__new__(cls)
                    other.__dict__.update(advisor.__dict__)
                    actual = score_map(other.evaluate_pack(pack, pick_no, pack_no))
                    fast = scores_from_trace(advisor, v, cls, pack_no)
                    assert fast == actual, (folder.name, v, actual, fast)
                validations += 1
            state = {k: advisor.__dict__[k] for k in (
                "global_mean", "global_std", "main_colors", "main_archetype", "pool_metrics")}
            state["pool_size"] = len(pool)
            trace = [[row[0]["name"], *row[1:]] for row in advisor._trace]
            picks.append([pack_no, pick_no, taken, state, trace])
        rows.append({k: d[k] for k in ("id", "skill", "games", "wins", "losses")} | {"picks": picks})
    write_gz(target, {"base_sha": BASE_SHA, "drafts": rows, "skipped": dict(skipped),
                      "real_packs_checked_per_variant": validations})
    print(f"TRACES {folder.name}: {len(rows)} drafts; {validations} reference packs per variant", flush=True)


def summarize_pick(scores, taken, base, by_gih):
    order = sorted(scores, key=lambda n: -scores[n])
    rank = order.index(taken)
    gap = max(scores.values()) - scores[taken]
    sd = statistics.pstdev(scores.values()) or 1.0
    base_sd = statistics.pstdev(base.values()) or 1.0
    return [int(rank == 0), int(rank < 3), gap / sd, gap / base_sd,
            int(order[0] != max(base, key=base.get)), int(taken == max(by_gih, key=by_gih.get))]


def run_variant(variant, folders, output, source):
    target = output / f"{variant}.json.gz"
    if target.exists():
        print(f"REUSE {variant}", flush=True)
        return
    cls = advisor_class(variant_source(variant, source)[1]) if variant != "baseline" else advisor_class(source)
    baseline_cls = advisor_class(source)
    result = []
    start = time.time()
    for folder in folders:
        app = App(str(folder / "dataset.json.gz"))
        names = {card["name"]: card for card in app.dataset.get_card_ratings().values()}
        for draft in read_gz(folder / "traces.json.gz")["drafts"]:
            sums = [0.0] * 6
            strong = (draft["skill"] or 0) >= 0.60 and (draft["games"] or 0) >= 50
            early = [0, 0]
            n = 0
            for pack_no, pick_no, taken, state, rows in draft["picks"]:
                advisor = object.__new__(baseline_cls)
                advisor.__dict__.update(state)
                advisor.pool = [None] * state["pool_size"]
                advisor._pick = pick_no
                advisor._trace = [(names[row[0]], *row[1:]) for row in rows]
                base = scores_from_trace(advisor, "baseline", baseline_cls, pack_no)
                scores = scores_from_trace(advisor, variant, cls, pack_no)
                gih = {name: app.gihwr(names[name]) for name in scores}
                values = summarize_pick(scores, taken, base, gih)
                sums = [a + b for a, b in zip(sums, values)]
                n += 1
                if strong and pick_no <= 4:
                    early[0] += values[0]
                    early[1] += 1
            result.append({k: draft[k] for k in ("id", "skill", "games", "wins", "losses")} | {
                "set": folder.name, "n": n, "top1": sums[0], "top3": sums[1],
                "regret": sums[2] / n if n else None, "fixed_regret": sums[3] / n if n else None,
                "changed": sums[4], "gih_top1": sums[5], "strong": strong, "early": early})
        print(f"{variant}: {folder.name} complete", flush=True)
    write_gz(target, {"variant": variant, "base_sha": BASE_SHA, "seconds": time.time() - start, "drafts": result})
    print(f"COMPLETE {variant}: {len(result)} drafts in {time.time()-start:.1f}s", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--variants", nargs="+", default=["baseline", *PICK_VARIANTS])
    a = p.parse_args()
    assert_baseline()
    a.out.mkdir(parents=True, exist_ok=True)
    source = (HERE.parents[1] / ENGINE).read_text()
    folders = sorted(folder for folder in a.data.iterdir() if (folder / "receipt.json").exists())
    if len(folders) != 10:
        raise SystemExit(f"Expected 10 frozen sets, got {len(folders)}")
    for folder in folders:
        build_traces(folder, source)
    for variant in a.variants:
        run_variant(variant, folders, a.out, source)
