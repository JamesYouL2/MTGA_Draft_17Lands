"""Compute the app's pick features for sampled drafts.

    python Tools/PickFit/features.py --src . --drafts drafts.json.gz \
        --dataset FRA_PremierDraft_All_Data.json.gz --set FRA --out FRA.json.gz

Every pick goes through DraftAdvisor.pick_features() in the copy of the app at
--src, with that copy's card data, so the fit uses the same features as the
app. A pick is one row per distinct card in the pack; basic lands are left
out, as the app scores them 0.
"""

import argparse
import gzip
import json
import os
import shutil
import sys
import tempfile
from collections import Counter

RARITY = {"common": 0, "uncommon": 1, "rare": 2, "mythic": 3}


class App:
    """The pick advisor and card data, from the src/ on sys.path."""

    def __init__(self, dataset_path):
        from src.advisor import engine
        from src.dataset import Dataset
        from src.set_metrics import SetMetrics

        self.engine = engine
        self.dataset = Dataset()
        with tempfile.TemporaryDirectory() as tmp:
            # Dataset.open_file reads plain JSON only.
            plain = os.path.join(tmp, "dataset.json")
            opener = gzip.open if dataset_path.endswith(".gz") else open
            with opener(dataset_path, "rb") as src, open(plain, "wb") as dst:
                shutil.copyfileobj(src, dst)
            self.dataset.open_file(plain)
        if not self.dataset.get_card_ratings():
            raise SystemExit(f"Could not load dataset {dataset_path}")
        self.metrics = SetMetrics(self.dataset)

        # The dump names double-faced cards by their front face only.
        self.by_name = {}
        for card in self.dataset.get_card_ratings().values():
            name = card.get("name", "")
            self.by_name.setdefault(name.split(" // ")[0], card)
            self.by_name.setdefault(name, card)
        self.unmatched = Counter()

    def cards(self, names):
        """Card dicts for dump names; names missing from the dataset are dropped."""
        out = []
        for name in names:
            card = self.by_name.get(name)
            if card is None:
                self.unmatched[name] += 1
            else:
                out.append(card)
        return out


def extra(advisor, card, pack, pick):
    """Plain facts that aren't features, for the LightGBM yardstick."""
    strength = sorted(advisor.color_strength.values(), reverse=True)
    colors = card.get("colors", [])
    return [
        pack,
        pick,
        len(advisor.pool),
        strength[0],
        strength[1],
        sum(advisor.color_strength.get(c, 0.0) for c in colors),
        len(colors),
        float("Creature" in card.get("types", [])),
        float(card.get("cmc") or 0.0),
        RARITY.get(str(card.get("rarity", "")).lower(), 0),
        float("removal" in card.get("tags", [])),
    ]


EXTRA_NAMES = [
    "pack",
    "pick",
    "pool_size",
    "strongest_color",
    "second_color",
    "card_color_strength",
    "card_colors",
    "creature",
    "mana_value",
    "rarity",
    "removal",
]


def situations(app, drafts):
    """One entry per pick with at least two cards to choose from."""
    names = list(app.engine.WEIGHTS)
    out, skipped = [], Counter()
    for d, draft in enumerate(drafts):
        for pack_no, pick_no, taken, pack, pool in draft["picks"]:
            advisor = app.engine.DraftAdvisor(app.metrics, app.cards(pool))
            rows, chosen = [], None
            for card in app.cards(dict.fromkeys(pack)):
                features = advisor.pick_features(card)
                if features is None:
                    continue
                if card["name"].split(" // ")[0] == taken.split(" // ")[0]:
                    chosen = len(rows)
                rows.append((card, [features[k] for k in names]))
            if chosen is None:
                skipped["took a basic land or an unknown card"] += 1
            elif len(rows) < 2:
                skipped["one card to choose from"] += 1
            else:
                out.append(
                    {
                        "draft": d,
                        "pack": pack_no,
                        "pick": pick_no,
                        "chosen": chosen,
                        "x": [x for _, x in rows],
                        "extra": [extra(advisor, c, pack_no, pick_no) for c, _ in rows],
                    }
                )
    return out, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--src", required=True, help="Root of the app's checkout")
    parser.add_argument("--drafts", required=True, help="drafts.py output")
    parser.add_argument("--dataset", required=True, help="The app's set dataset")
    parser.add_argument("--set", required=True, help="Set code, for the report")
    parser.add_argument("--out", required=True, help="Where to write (.json.gz)")
    args = parser.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.src))
    app = App(args.dataset)
    with gzip.open(args.drafts, "rt", encoding="utf-8") as f:
        drafts = json.load(f)
    rows, skipped = situations(app, drafts)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump(
            {
                "set": args.set,
                "names": list(app.engine.WEIGHTS),
                "weights": app.engine.WEIGHTS,
                "log_odds_per_point": app.engine.PICK_LOG_ODDS_PER_POINT,
                "extra_names": EXTRA_NAMES,
                "drafts": len(drafts),
                "skipped": dict(skipped),
                "unmatched": dict(app.unmatched.most_common(20)),
                "situations": rows,
            },
            f,
        )
    print(
        f"{args.set}: {len(rows)} picks from {len(drafts)} drafts; "
        f"skipped {dict(skipped)}; unmatched {sum(app.unmatched.values())}"
    )


if __name__ == "__main__":
    main()
