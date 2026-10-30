"""Sample strong drafters' drafts from a 17Lands public draft dump.

    python Tools/PickFit/drafts.py \
        --dump draft_data_public.FRA.PremierDraft.csv.gz \
        --drafts 3000 --out drafts.json.gz

Keeps drafts by drafters whose game win rate bucket is at least --min-skill
over a games bucket of at least --min-games. Drafts are chosen by a hash of
their draft_id, so the same dump, size and salt always give the same drafts.
Drafts with a second pick (pick_2, from formats that take two cards a pick)
are left out.
"""

import argparse
import csv
import gzip
import hashlib
import heapq
import json


def draft_priority(draft_id, salt=""):
    """A draft's place in the sample order; the lowest values are kept."""
    return int(hashlib.sha1((salt + draft_id).encode("utf-8")).hexdigest()[:15], 16)


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _names(row, columns):
    """Card names from count columns: [(index, name)] -> name repeated count times."""
    return [
        name
        for i, name in columns
        if row[i] not in ("", "0")
        for _ in range(int(row[i]))
    ]


def _split(line):
    # Card names with commas are quoted; numbers never are.
    if '"' in line:
        return next(csv.reader([line]))
    return line.rstrip("\r\n").split(",")


def sample_drafts(lines, n_drafts, min_skill=0.6, min_games=50, salt="", dates=None):
    """The n_drafts strong drafters' drafts with the lowest priority, in
    draft_id order.

    lines is the dump's CSV text, one line per pick. Each draft has its "id"
    and its "picks": [pack, pick, taken card, cards in the pack, cards already
    taken], with pack and pick from 1. If dates is given, only drafts started
    from dates[0] (ISO) up to but not including dates[1] are kept.
    """
    lines = iter(lines)
    header = next(csv.reader([next(lines)]))
    col = {name: i for i, name in enumerate(header)}
    pack_cols = [
        (i, c[len("pack_card_") :])
        for i, c in enumerate(header)
        if c.startswith("pack_card_")
    ]
    pool_cols = [
        (i, c[len("pool_") :]) for i, c in enumerate(header) if c.startswith("pool_")
    ]
    pick_2 = col.get("pick_2")

    # Max-heap of the kept drafts' priorities, as (-priority, draft_id).
    kept, drafts, two_picks = [], {}, set()
    current_id, keep = None, False
    for line in lines:
        row = _split(line)
        if len(row) != len(header):
            continue
        draft_id = row[col["draft_id"]]
        if draft_id != current_id:
            current_id = draft_id
            skill = _number(row[col["user_game_win_rate_bucket"]])
            games = _number(row[col["user_n_games_bucket"]])
            strong = (
                skill is not None
                and games is not None
                and skill >= min_skill
                and games >= min_games
            )
            if dates:
                date = row[col["draft_time"]][:10]
                strong = strong and dates[0] <= date < dates[1]
            priority = draft_priority(draft_id, salt)
            keep = strong and (
                draft_id in drafts or len(kept) < n_drafts or priority < -kept[0][0]
            )
            if keep and draft_id not in drafts:
                if len(kept) == n_drafts:
                    drafts.pop(heapq.heappop(kept)[1])
                heapq.heappush(kept, (-priority, draft_id))
                drafts[draft_id] = {"id": draft_id, "picks": []}
        if keep:
            if pick_2 is not None and row[pick_2]:
                two_picks.add(draft_id)
            drafts[draft_id]["picks"].append(
                [
                    int(row[col["pack_number"]]) + 1,
                    int(row[col["pick_number"]]) + 1,
                    row[col["pick"]],
                    _names(row, pack_cols),
                    _names(row, pool_cols),
                ]
            )
    return [drafts[d] for d in sorted(drafts) if d not in two_picks]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dump", required=True, help="17Lands draft dump (.csv.gz)")
    parser.add_argument("--drafts", type=int, required=True, help="Drafts to keep")
    parser.add_argument("--min-skill", type=float, default=0.6)
    parser.add_argument("--min-games", type=float, default=50)
    parser.add_argument("--salt", default="", help="Changes which drafts are kept")
    parser.add_argument("--from-date", help="First draft date (ISO)")
    parser.add_argument("--to-date", help="Day after the last draft date (ISO)")
    parser.add_argument("--out", required=True, help="Where to write (.json.gz)")
    args = parser.parse_args(argv)

    opener = gzip.open if args.dump.endswith(".gz") else open
    with opener(args.dump, "rt", newline="", encoding="utf-8") as f:
        drafts = sample_drafts(
            f,
            args.drafts,
            args.min_skill,
            args.min_games,
            args.salt,
            (args.from_date, args.to_date) if args.from_date else None,
        )
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump(drafts, f)
    print(f"Sampled {len(drafts)} drafts from {args.dump}")


if __name__ == "__main__":
    main()
