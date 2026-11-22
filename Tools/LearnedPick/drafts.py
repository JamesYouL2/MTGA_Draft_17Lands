"""Sample training drafts from a 17Lands public draft dump, in one pass.

    python Tools/LearnedPick/drafts.py --dump draft_data_public.FRA.PremierDraft.csv.gz \
        --strong 2000 --all 2000 --out drafts.json.gz

Two samples, each the drafts with the lowest hash of their draft_id:

- "strong": drafters with a game win rate bucket of 0.6 or more over a games
  bucket of 50 or more.
- "all": any drafter.

A draft can be in both. Each draft has the same fields as
Tools/AdvisorReplay/sample.py's, plus "strong" (true or false) and "samples"
(which of the two samples it was drawn for).
"""

import argparse
import csv
import gzip
import heapq
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "AdvisorReplay"))
from sample import _names, _number, draft_priority  # noqa: E402

STRONG_SKILL, STRONG_GAMES = 0.6, 50


def is_strong(skill, games):
    return (
        skill is not None
        and games is not None
        and skill >= STRONG_SKILL
        and games >= STRONG_GAMES
    )


def _split(line):
    # Card names with commas are quoted; numbers never are.
    if '"' in line:
        return next(csv.reader([line]))
    return line.rstrip("\r\n").split(",")


def sample_two(lines, n_strong, n_all, salt=""):
    """The strong and all-drafter samples, merged, in draft_id order."""
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
    sizes = {"strong": n_strong, "all": n_all}
    heaps = {"strong": [], "all": []}  # max-heaps of (-priority, draft_id)
    members = {"strong": set(), "all": set()}
    drafts = {}
    current_id, keep = None, False
    for line in lines:
        row = _split(line)
        if len(row) != len(header):
            continue
        draft_id = row[col["draft_id"]]
        if draft_id != current_id:
            current_id = draft_id
            if draft_id in drafts:
                keep = True
            else:
                skill = _number(row[col["user_game_win_rate_bucket"]])
                games = _number(row[col["user_n_games_bucket"]])
                priority = draft_priority(draft_id, salt)
                wanted = ["all"] + (["strong"] if is_strong(skill, games) else [])
                joined = []
                for name in wanted:
                    heap = heaps[name]
                    if len(heap) < sizes[name] or (heap and priority < -heap[0][0]):
                        if len(heap) == sizes[name]:
                            _, out = heapq.heappop(heap)
                            members[name].discard(out)
                            if not any(out in m for m in members.values()):
                                drafts.pop(out, None)
                        heapq.heappush(heap, (-priority, draft_id))
                        members[name].add(draft_id)
                        joined.append(name)
                keep = bool(joined)
                if keep:
                    drafts[draft_id] = {
                        "id": draft_id,
                        "skill": skill,
                        "games": games,
                        "wins": _number(row[col["event_match_wins"]]),
                        "losses": _number(row[col["event_match_losses"]]),
                        "strong": is_strong(skill, games),
                        "picks": [],
                    }
        if keep and draft_id in drafts:
            drafts[draft_id]["picks"].append(
                [
                    int(row[col["pack_number"]]) + 1,
                    int(row[col["pick_number"]]) + 1,
                    row[col["pick"]],
                    _names(row, pack_cols),
                    _names(row, pool_cols),
                ]
            )
    out = []
    for draft_id in sorted(drafts):
        d = drafts[draft_id]
        d["samples"] = [n for n in ("strong", "all") if draft_id in members[n]]
        if d["samples"]:
            out.append(d)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dump", required=True, help="17Lands draft dump (.csv.gz)")
    parser.add_argument("--strong", type=int, default=2000, help="Strong drafts")
    parser.add_argument("--all", type=int, default=2000, help="Drafts by anyone")
    parser.add_argument("--salt", default="learned", help="Changes which drafts")
    parser.add_argument("--out", required=True, help="Where to write (.json.gz)")
    args = parser.parse_args(argv)
    opener = gzip.open if args.dump.endswith(".gz") else open
    with opener(args.dump, "rt", newline="", encoding="utf-8") as f:
        drafts = sample_two(f, args.strong, args.all, args.salt)
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump(drafts, f)
    strong = sum("strong" in d["samples"] for d in drafts)
    print(f"Sampled {len(drafts)} drafts ({strong} strong) from {args.dump}")


if __name__ == "__main__":
    main()
