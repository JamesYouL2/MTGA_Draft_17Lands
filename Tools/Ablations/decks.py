"""Cache the live builder's candidates/MC draws, then ablate final rankings."""
import argparse
import copy
import hashlib
import inspect
import json
from pathlib import Path
import sys
import textwrap
import time

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1])]
from run import App, read_gz, write_gz
from variants import BASE_SHA, MC, FEATURES, DECK_VARIANTS, assert_baseline
from src.advisor import deck_builder as db, deck_scorer as ds
from src.configuration import Configuration


def signature(deck):
    return tuple(sorted((c["name"], c.get("count", 1)) for c in deck))


def ranking_function():
    """Use the actual app's filtering, deduplication and safe-core promotion."""
    source = inspect.getsource(db.suggest_deck)
    body = source[source.index("        # Incomplete (land-padded)"):source.index("        GLOBAL_DECK_CACHE[cache_key]")]
    body = textwrap.dedent(body)
    prefix = '''def select(candidates):
    sorted_decks = {}
    all_variants = [(label, data) for label, data in candidates if "Incomplete Deck" not in data["breakdown"]]
    incomplete_variants = [(label, data) for label, data in candidates if "Incomplete Deck" in data["breakdown"]]
'''
    scope = dict(vars(db))
    exec(prefix + textwrap.indent(body, "    ") + "\n    return sorted_decks\n", scope)
    return scope["select"]


SELECT = ranking_function()


def rescored(candidates, variant):
    result = copy.deepcopy(candidates)
    for index, (label, data) in enumerate(result):
        raw = ds.BASE_SCORE
        for name, weight in ds.WEIGHTS.items():
            if FEATURES.get(variant) != name:
                raw += weight * data["features"][name]
        score = max(0.0, raw)
        if data["stats"]:
            for key, (stat, threshold, weight) in MC.items():
                if variant not in (key, "no-mc-all"):
                    score -= max(0.0, data["stats"][stat] - threshold) * weight
        data["rating"] = max(0.0, score)
        data["record"] = ds.estimate_record(data["rating"], False)
        prefix = label.split(" [Est:", 1)[0]
        result[index][0] = f"{prefix} [Est: {data['record']}] (Power: {data['rating']:.0f})"
    return result


def collect(folder, limit):
    target = folder / "deck-candidates.json.gz"
    if target.exists():
        assert read_gz(target)["requested_pools"] == limit
        return
    app = App(str(folder / "dataset.json.gz"))
    drafts = sorted(read_gz(folder / "drafts.json.gz"), key=lambda d: hashlib.sha256(("deck-ablation"+d["id"]).encode()).hexdigest())[:limit]
    records = []
    for index, draft in enumerate(drafts):
        if not draft["picks"]:
            continue
        _, _, taken, _, pool_names = draft["picks"][-1]
        pool = app.cards(pool_names + [taken])
        candidates = []

        def progress(message):
            if "variant_data" in message:
                data = copy.deepcopy(message["variant_data"])
                data["features"] = ds.deck_features(data["deck_cards"], data["colors"], len(pool), app.metrics)
                # Ranking only needs inventory, labels, scores and diagnostics;
                # do not repeat the entire ratings table on every card copy.
                data["deck_cards"] = [{"name": c["name"], "count": c.get("count", 1)} for c in data["deck_cards"]]
                data.pop("sideboard_cards", None)
                candidates.append([message["variant_label"], data])

        db.clear_deck_cache()
        builds = db.suggest_deck(pool, app.metrics, Configuration(), progress_callback=progress,
                                 dataset_name=f"frozen-{folder.name}-{draft['id']}")
        if not builds:
            records.append({"id": draft["id"], "error": "builder produced no decks"})
            continue
        live = next(iter(builds.values()))
        replay = next(iter(SELECT(rescored(candidates, "baseline")).values()))
        assert signature(live["deck_cards"]) == signature(replay["deck_cards"]), draft["id"]
        assert abs(live["rating"] - replay["rating"]) < 1e-8, draft["id"]
        for _, data in candidates:
            assert sum(c.get("count", 1) for c in data["deck_cards"]) == 40
        records.append({k: draft[k] for k in ("id", "skill", "games", "wins", "losses")} | {
            "set": folder.name, "candidates": candidates})
        if (index+1) % 10 == 0:
            print(f"CANDIDATES {folder.name}: {index+1}/{len(drafts)}", flush=True)
    write_gz(target, {"base_sha": BASE_SHA, "requested_pools": limit, "drafts": records})
    print(f"CANDIDATES COMPLETE {folder.name}: {len(records)}", flush=True)


def run_variant(variant, folders, output):
    target = output / f"{variant}.json.gz"
    if target.exists():
        return
    result = []
    for folder in folders:
        for draft in read_gz(folder / "deck-candidates.json.gz")["drafts"]:
            if "error" in draft:
                continue
            builds = SELECT(rescored(draft["candidates"], variant))
            baseline = SELECT(rescored(draft["candidates"], "baseline"))
            original = SELECT(copy.deepcopy(draft["candidates"]))
            assert signature(next(iter(original.values()))["deck_cards"]) == signature(next(iter(baseline.values()))["deck_cards"])
            chosen, base = next(iter(builds.values())), next(iter(baseline.values()))
            result.append({k: draft[k] for k in ("id", "set", "skill", "games", "wins", "losses")} | {
                "rating": chosen["rating"], "changed": signature(chosen["deck_cards"]) != signature(base["deck_cards"]),
                "missing_fixing": chosen["features"]["missing_fixing"],
                "quality": chosen["features"]["card_quality"],
                "colors": len(chosen["colors"]),
                "stats": {stat: chosen["stats"][stat] for stat, _, _ in MC.values()},
            })
    write_gz(target, {"base_sha": BASE_SHA, "variant": variant, "drafts": result})
    print(f"COMPLETE {variant}: {len(result)} end-to-end builds", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--pools", type=int, default=100)
    p.add_argument("--collect-only", action="store_true")
    a = p.parse_args()
    assert_baseline()
    a.out.mkdir(parents=True, exist_ok=True)
    folders = sorted(f for f in a.data.iterdir() if (f / "receipt.json").exists())
    for folder in folders:
        collect(folder, a.pools)
    if not a.collect_only:
        assert len(folders) == 10
        for variant in ["deck-baseline", *DECK_VARIANTS]:
            run_variant(variant, folders, a.out)
