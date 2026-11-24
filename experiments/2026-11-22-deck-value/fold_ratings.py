"""Two independent rating sets from one game dump (P3CONFIRM.md).

    python fold_ratings.py --games games.csv.gz --drafts drafts.json.gz \
        --dataset dataset.json.gz --a ratings_a.json.gz --b ratings_b.json.gz

The games of the drafts in --drafts are left out of both, as holdout.py's
--heldout leaves them out. Every other draft goes to half A or half B by a hash
of its draft ID, so all builds of one pool land in the same half. Each output is
the app's dataset with win rates from its half only. As in holdout.py, a card is
rated where it has MIN_SAMPLES copies in hand in the whole dump, so both halves
rate the same cards. Copies are counted as 17Lands counts them (since the rerun
of 2026-11-24; run 45259059583 counted a card once per game).
"""

import argparse
import gzip
import json
import os
import sys

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Tools")
sys.path.insert(0, os.path.join(TOOLS, "AdvisorReplay"))
import holdout  # noqa: E402  (puts Tools/DeckScoreFit on the path)
from decks import deck_hash  # noqa: E402
from games import ALL, read_games  # noqa: E402

SALT = "p3fold"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games", required=True)
    ap.add_argument("--drafts", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    args = ap.parse_args(argv)

    with gzip.open(args.drafts, "rt", encoding="utf-8") as f:
        held = {d["id"] for d in json.load(f)}
    with gzip.open(args.dataset, "rt", encoding="utf-8") as f:
        data = json.load(f)

    def fold_of(key):
        draft = key.rsplit(":", 1)[0]
        return 0 if draft in held else 1 + deck_hash(draft, SALT) % 2

    with gzip.open(args.games, "rt", encoding="utf-8", newline="") as f:
        _, folds = read_games(f, set(), fold_of=fold_of, copies=True)
    whole = holdout.merged(holdout.merged(folds[0], folds[1]), folds[2])
    for path, counts in ((args.a, folds[1]), (args.b, folds[2])):
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(holdout.rebuilt(data, counts, whole), f)
    games = [sum(c[0] for c in folds[i].get(ALL, {}).values()) for i in range(3)]
    total = sum(games)
    print(f"Games in hand: sampled drafts {games[0] / total:.1%}, half A {games[1] / total:.1%}, "
          f"half B {games[2] / total:.1%}")


if __name__ == "__main__":
    main()
