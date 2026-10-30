"""Record every pack card's pick features for sampled drafts, so any weights
can be scored offline the way Tools/AdvisorReplay/replay.py scores them.

    python Tools/WinsExperiment/extract.py --drafts drafts.json.gz \
        --dataset FRA_PremierDraft_All_Data.json.gz --set FRA --out FRA.eval.json.gz

Picks are filtered as replay.py filters them, and keep the pool's size. Each pick keeps the pack's
distinct cards in the order replay.py breaks ties by, with None for basic lands
(scored 0).
"""

import argparse
import gzip
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "AdvisorReplay"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from replay import App  # noqa: E402


def extract_draft(app, draft, skipped):
    name_field = app.constants.DATA_FIELD_NAME
    picks = []
    for pack_no, pick_no, taken, pack_names, pool_names in draft["picks"]:
        pack, pool = app.cards(pack_names), app.cards(pool_names)
        taken = app.cards([taken])
        if not taken:
            skipped["taken card not in dataset"] += 1
            continue
        taken = taken[0][name_field]
        if len({c[name_field] for c in pack}) < 2:
            skipped["fewer than 2 different cards in pack"] += 1
            continue
        advisor = app.DraftAdvisor(app.metrics, pool)
        names, rows = [], []
        for card in pack:
            if card[name_field] in names:
                continue
            features = advisor.pick_features(card)
            names.append(card[name_field])
            rows.append(
                None
                if features is None
                else [round(features[k], 5) for k in app.feature_names]
            )
        picks.append([pack_no, pick_no, names.index(taken), rows, len(pool)])
    return {k: draft[k] for k in ("id", "skill", "games", "wins", "losses")} | {
        "picks": picks
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--drafts", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--set", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    from src.advisor import engine

    app = App(args.dataset)
    app.feature_names = list(engine.WEIGHTS)
    with gzip.open(args.drafts, "rt", encoding="utf-8") as f:
        drafts = json.load(f)
    skipped = Counter()
    results = [extract_draft(app, d, skipped) for d in drafts]
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump(
            {
                "set": args.set,
                "names": app.feature_names,
                "skipped": dict(skipped),
                "drafts": results,
            },
            f,
        )
    print(f"{args.set}: {len(results)} drafts; skipped {dict(skipped)}")


if __name__ == "__main__":
    main()
