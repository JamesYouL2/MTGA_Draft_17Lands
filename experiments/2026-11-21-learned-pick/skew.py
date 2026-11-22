"""DIAGNOSE.md check 8: do the replay head's features equal the training pipeline's?

    python experiments/2026-11-21-learned-pick/skew.py --drafts drafts.json.gz \
        --dataset KTK.json.gz --set KTK --models MODELS [--json out.json]

drafts.json.gz is Tools/LearnedPick/drafts.py's output; MODELS holds <SET>/ from a
Learned pick models run. Each pick's feature rows are computed two ways, on the
same dataset:

- training: features.training_rows, one draft at a time, as features.py runs it;
- serving: replay.replay_draft through a copy of src/ with the noalsa head's
  patch, catching the rows learned_head hands to the model.

They are compared card by card (NaN equal to NaN). Training stores its rows as
float32 and the head scores float64, so the set's noalsa model also scores both
versions of each serving row, for the largest score change and how often the
top card changes.
"""

import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TOOL = os.path.join(ROOT, "Tools", "LearnedPick")
PATCH = os.path.join(HERE, "confirm-heads", "lgbm-strong-noalsa.patch")
HEAD = "lgbm-strong-noalsa"


def same(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    return (a == b) | (np.isnan(a) & np.isnan(b))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--drafts", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--set", required=True)
    parser.add_argument("--models", required=True)
    parser.add_argument("--json")
    args = parser.parse_args(argv)

    tmp = tempfile.mkdtemp()
    shutil.copytree(os.path.join(ROOT, "src"), os.path.join(tmp, "src"))
    subprocess.run(
        ["git", "apply", "--unsafe-paths", f"--directory={tmp}", PATCH], check=True, cwd=ROOT
    )
    os.environ.update(SET=args.set, LEARNED_MODELS=os.path.abspath(args.models), LEARNED_PICK_TOOL=TOOL)
    sys.path[:0] = [TOOL, os.path.join(ROOT, "Tools", "AdvisorReplay"), tmp]
    import features
    import model
    import replay

    app = replay.App(args.dataset)
    with gzip.open(args.drafts, "rt", encoding="utf-8") as f:
        drafts = json.load(f)

    caught = {"train": {}, "serve": {}}
    where = {"side": None, "draft": None}
    real = features.pack_features

    def catching(pack, pool, pack_no, pick_no, mean, sd):
        rows = real(pack, pool, pack_no, pick_no, mean, sd)
        key = (where["draft"], int(pack_no), int(pick_no))
        caught[where["side"]][key] = (rows, mean, sd, sorted(c["name"] for c in pool))
        return rows

    features.pack_features = catching  # training_rows' name
    model.pack_features = catching  # score_pack's name

    skipped = Counter()
    for i, d in enumerate(drafts):
        where.update(side="train", draft=i)
        features.training_rows(app, [d])
        where.update(side="serve")
        replay.replay_draft(app, d, skipped)

    booster = model.load(args.models, args.set, HEAD)
    train, serve = caught["train"], caught["serve"]
    both = sorted(set(train) & set(serve))
    out = {
        "set": args.set,
        "drafts": len(drafts),
        "picks_train": len(train),
        "picks_serve": len(serve),
        "picks_compared": len(both),
        "cards_compared": 0,
        "row_mismatches": Counter(),
        "card_set_mismatches": 0,
        "scale_mismatches": 0,
        "pool_mismatches": 0,
        "float32_max_score_change": 0.0,
        "float32_top_changes": 0,
    }
    names = features.FEATURES
    for key in both:
        (t_rows, t_mean, t_sd, t_pool), (s_rows, s_mean, s_sd, s_pool) = train[key], serve[key]
        out["scale_mismatches"] += (t_mean, t_sd) != (s_mean, s_sd)
        out["pool_mismatches"] += t_pool != s_pool
        if list(t_rows) != list(s_rows):
            out["card_set_mismatches"] += 1
        cards = [n for n in t_rows if n in s_rows]
        out["cards_compared"] += len(cards)
        for n in cards:
            ok = same(t_rows[n], s_rows[n])
            for f, good in zip(names, ok):
                if not good:
                    out["row_mismatches"][f] += 1
        # What training saw (float32) against what the head scores (float64).
        X64 = np.array([s_rows[n] for n in s_rows], dtype=np.float64)
        X32 = X64.astype(np.float32).astype(np.float64)
        a, b = booster.score(X64), booster.score(X32)
        out["float32_max_score_change"] = max(out["float32_max_score_change"], float(np.max(np.abs(a - b))))
        out["float32_top_changes"] += int(np.argmax(a) != np.argmax(b))
    out["only_train"] = len(set(train) - set(serve))
    out["only_serve"] = len(set(serve) - set(train))
    out["replay_skipped"] = dict(skipped)
    out["row_mismatches"] = dict(out["row_mismatches"])
    shutil.rmtree(tmp)
    print(json.dumps(out))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
