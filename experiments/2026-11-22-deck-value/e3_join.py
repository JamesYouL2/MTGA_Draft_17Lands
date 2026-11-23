"""PROTOCOL.md's E3 join: each replayed draft's swap counts and the decks its
drafter played, for one set.

    python experiments/2026-11-22-deck-value/e3_join.py --src . --set FDN \
        --games games.csv.gz --dataset dataset.json.gz \
        --replays conf weak --out e3-FDN.json.gz

Each --replays folder holds one folder per salt (heads-SET-SALT, as
`gh run download` writes them) with base.json and one or more heads' results
from replay.py. A draft's row has, for each head, how many of its disagreements
with base the drafter settled with the head's top card, base's, or neither
(diagnose.py's "took"). Its decks are every (draft_id, build_index) in the game
data, with deckfacts.py's facts averaged over builds, weighted by games.

For the skill-confound control (PROTOCOL.md addendum, 2026-11-22), a row also
has "picks": for each head, its disagreement picks as [pack, pick, class (0 =
took the head's top card, 1 = base's, 2 = neither), head's top maindecked,
base's top maindecked], where maindecked means in any of the draft's played
builds (None when the draft has no game rows).
"""

import argparse
import csv
import gzip
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deckfacts as DF  # noqa: E402


def took(base, head):
    """{draft id: [a, b, c]} over the drafts both copies replayed."""
    theirs = {d["id"]: d for d in head["drafts"]}
    out = {}
    for d in base["drafts"]:
        o = theirs.get(d["id"])
        if o is None or not d["picks"] or not o["picks"]:
            continue
        head_picks = {(q[0], q[1]): q for q in o["picks"]}
        t = [0, 0, 0]
        for p in d["picks"]:
            q = head_picks.get((p[0], p[1]))
            if q is None or p[5] == q[5]:
                continue
            t[0 if q[2] == 0 else 1 if p[2] == 0 else 2] += 1
        out[d["id"]] = t
    return out


def took_picks(base, head):
    """{draft id: [[pack, pick, class, head's top, base's top], ...]}, the
    disagreements took() counts, one entry per pick."""
    theirs = {d["id"]: d for d in head["drafts"]}
    out = {}
    for d in base["drafts"]:
        o = theirs.get(d["id"])
        if o is None or not d["picks"] or not o["picks"]:
            continue
        head_picks = {(q[0], q[1]): q for q in o["picks"]}
        got = []
        for p in d["picks"]:
            q = head_picks.get((p[0], p[1]))
            if q is None or p[5] == q[5]:
                continue
            got.append([p[0], p[1], 0 if q[2] == 0 else 1 if p[2] == 0 else 2, q[5], p[5]])
        out[d["id"]] = got
    return out


def read_replays(roots):
    """{(salt, draft id): row} with each head's took."""
    rows = {}
    for root in roots:
        for name in sorted(os.listdir(root)):
            folder = os.path.join(root, name)
            base_path = os.path.join(folder, "base.json")
            if not os.path.exists(base_path):
                continue
            salt = name.rsplit("-", 1)[-1]
            with open(base_path, encoding="utf-8") as f:
                base = json.load(f)
            for d in base["drafts"]:
                row = rows.setdefault((salt, d["id"]), {
                    "salt": salt, "id": d["id"], "wins": d["wins"], "losses": d["losses"],
                    "skill": d["skill"], "games": d["games"], "took": {}, "picks": {},
                })
            for path in sorted(os.listdir(folder)):
                if path == "base.json" or not path.endswith(".json"):
                    continue
                with open(os.path.join(folder, path), encoding="utf-8") as f:
                    head = json.load(f)
                for draft_id, t in took(base, head).items():
                    rows[(salt, draft_id)]["took"][path[:-5]] = t
                for draft_id, got in took_picks(base, head).items():
                    rows[(salt, draft_id)]["picks"][path[:-5]] = got
                del head
            del base
    return rows


def read_played(lines, ids, vocab=None):
    """{draft id: {build index: deck}} from the game data, for drafts in ids.
    vocab, if given, is filled with the deck columns' card names."""
    lines = iter(lines)
    header = next(csv.reader([next(lines)]))
    col = {name: i for i, name in enumerate(header)}
    deck_cols = [(i, name[5:]) for i, name in enumerate(header) if name.startswith("deck_")]
    if vocab is not None:
        vocab.update(n for _, n in deck_cols)
    i_id, i_build, i_won = col["draft_id"], col["build_index"], col["won"]
    out = defaultdict(dict)
    for line in lines:
        # The draft_id is the first fields' business; skip unwanted rows cheaply.
        fields = next(csv.reader([line])) if '"' in line else line.rstrip("\r\n").split(",")
        draft_id = fields[i_id]
        if draft_id not in ids:
            continue
        deck = out[draft_id].get(fields[i_build])
        if deck is None:
            deck = out[draft_id][fields[i_build]] = {
                "main_colors": fields[col["main_colors"]],
                "splash_colors": fields[col["splash_colors"]],
                "cards": {n: c for i, n in deck_cols if fields[i] and (c := int(float(fields[i])))},
                "games": 0, "wins": 0,
            }
        deck["games"] += 1
        deck["wins"] += fields[i_won] == "True"
    return out


def combine(decks):
    """Facts averaged over a draft's scored builds, weighted by games, with the
    total games and wins."""
    sums, weights = defaultdict(float), defaultdict(float)
    games = sum(d["games"] for d in decks)
    for d in decks:
        if d["facts"] is None:
            continue
        for k, v in d["facts"].items():
            if v is not None:
                sums[k] += v * d["games"]
                weights[k] += d["games"]
    out = {k: round(sums[k] / weights[k], 4) for k in sums if weights[k]}
    return out, games, sum(d["wins"] for d in decks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--src", required=True)
    parser.add_argument("--set", required=True)
    parser.add_argument("--games", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--replays", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    rows = read_replays(args.replays)
    ids = {draft_id for _, draft_id in rows}
    with gzip.open(args.games, "rt", encoding="utf-8", newline="") as f:
        vocab = set()
        played = read_played(f, ids, vocab)

    sys.path.insert(0, os.path.abspath(args.src))
    app = DF.F.App(args.dataset)
    cache = {}
    for draft_id, builds in played.items():
        decks = []
        for deck in builds.values():
            facts = DF.facts(app, deck["cards"], deck["main_colors"], deck["splash_colors"])
            decks.append({"facts": facts, "games": deck["games"], "wins": deck["wins"]})
        cache[draft_id] = combine(decks) + (len(builds),)

    out = []
    names_seen = [0, 0]  # top-card names checked, and found among the deck columns
    for (salt, draft_id), row in sorted(rows.items()):
        got = cache.get(draft_id)
        row["deck"], row["deck_games"], row["deck_wins"], row["builds"] = got if got else (None, 0, 0, 0)
        builds = played.get(draft_id)
        main = set().union(*(b["cards"] for b in builds.values())) if builds else None
        for head, got_picks in row["picks"].items():
            for q in got_picks:
                names_seen[0] += 2
                names_seen[1] += (q[3] in vocab) + (q[4] in vocab)
            row["picks"][head] = [
                [q[0], q[1], q[2], None if main is None else int(q[3] in main),
                 None if main is None else int(q[4] in main)]
                for q in got_picks
            ]
        out.append(row)
    complete = [r for r in out if r["wins"] == 7 or r["losses"] == 3]
    matched = sum(1 for r in complete if r["builds"])
    scored = sum(1 for r in complete if r["deck"])
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump({"set": args.set, "rows": out, "unmatched": dict(app.unmatched.most_common(10))}, f)
    print(f"{args.set}: {len(out)} rows, {len(complete)} complete, "
          f"{matched} matched ({matched / max(1, len(complete)):.1%}), {scored} scored; "
          f"top-card names found among deck columns {names_seen[1]}/{names_seen[0]} "
          f"({names_seen[1] / max(1, names_seen[0]):.1%})")


if __name__ == "__main__":
    main()
