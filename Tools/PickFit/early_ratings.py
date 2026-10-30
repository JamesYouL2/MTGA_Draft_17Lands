"""The app's dataset as it would have looked after the format's first days.

    python Tools/PickFit/early_ratings.py --games game_data.csv.gz \
        --dataset FRA_PremierDraft_All_Data.json.gz --days 1 2 3 --out early

17Lands no longer serves ratings for custom date ranges, so they are rebuilt
from the public game data. For each card and deck color group, GIH WR is the
win rate of games where the card was in the opening hand or drawn, among
drafts started in the format's first N days. As on 17Lands, a card with fewer
than 500 such games has no GIH WR. Other win rates are cleared.

Writes early/dayN.json.gz for each N, and early/start.txt, the format's first
day: the first with 1,000 or more games.
"""

import argparse
import datetime
import gzip
import json
import os

import numpy as np
import pandas as pd

MIN_SAMPLES = 500
MIN_GAMES_FIRST_DAY = 1000
CLEARED = ("ohwr", "gpwr", "gnswr", "gdwr", "iwd")


def normalize(colors):
    return "".join(sorted(colors, key="WUBRG".index)) if colors else ""


def count_games(path, last_date, chunksize=100_000):
    """For drafts started on or before last_date: {(date, main colors):
    [games, games each card was seen in, games won with it seen]}, and the
    card names."""
    header = pd.read_csv(path, nrows=0).columns
    names = [c[len("opening_hand_") :] for c in header if c.startswith("opening_hand_")]
    hand_cols = [f"opening_hand_{n}" for n in names]
    drawn_cols = [f"drawn_{n}" for n in names]
    cols = ["draft_time", "main_colors", "won"] + hand_cols + drawn_cols
    counts = {}
    for chunk in pd.read_csv(path, usecols=cols, chunksize=chunksize):
        date = chunk["draft_time"].astype(str).str[:10]
        chunk = chunk[date <= last_date]
        if chunk.empty:
            continue
        seen = (
            chunk[hand_cols].fillna(0).to_numpy()
            + chunk[drawn_cols].fillna(0).to_numpy()
        ) > 0
        won = chunk["won"].astype(str).str.lower().eq("true").to_numpy()
        colors = chunk["main_colors"].fillna("").astype(str).map(normalize)
        groups = pd.Series(0, index=chunk.index).groupby(
            [date[chunk.index].to_numpy(), colors.to_numpy()]
        )
        for key, rows in groups.indices.items():
            c = counts.setdefault(key, [0, np.zeros(len(names)), np.zeros(len(names))])
            c[0] += len(rows)
            c[1] += seen[rows].sum(0)
            c[2] += seen[rows][won[rows]].sum(0)
    return counts, names


def build(dataset, counts, names, cutoff):
    """A copy of dataset with GIH WR from drafts started before cutoff."""
    index = {n: i for i, n in enumerate(names)}
    k = len(names)
    by_colors = {}
    for (date, colors), (_, g, w) in counts.items():
        if date < cutoff:
            G, W = by_colors.get(colors, (np.zeros(k), np.zeros(k)))
            by_colors[colors] = (G + g, W + w)
    all_g = sum((g for g, _ in by_colors.values()), np.zeros(k))
    all_w = sum((w for _, w in by_colors.values()), np.zeros(k))
    out = json.loads(json.dumps(dataset))
    for card in out["card_ratings"].values():
        i = index.get(card["name"].split(" // ")[0], index.get(card["name"]))
        for key, stats in card.get("deck_colors", {}).items():
            if i is None:
                g = w = 0.0
            elif key == "All Decks":
                g, w = all_g[i], all_w[i]
            else:
                G, W = by_colors.get(normalize(key), (np.zeros(k), np.zeros(k)))
                g, w = G[i], W[i]
            stats["samples"] = int(g)
            stats["gihwr"] = round(100.0 * w / g, 2) if g >= MIN_SAMPLES else 0.0
            for field in CLEARED:
                stats[field] = 0.0
    out["meta"]["end_date"] = cutoff
    out["meta"]["game_count"] = int(
        sum(n for (date, _), (n, _, _) in counts.items() if date < cutoff)
    )
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--games", required=True, help="17Lands game data (.csv.gz)")
    parser.add_argument("--dataset", required=True, help="The app's dataset")
    parser.add_argument("--days", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args(argv)

    opener = gzip.open if args.dataset.endswith(".gz") else open
    with opener(args.dataset, "rt", encoding="utf-8") as f:
        dataset = json.load(f)
    # The app's dataset starts at the format's release; allow a few days of
    # slack either way to find the first real day.
    release = datetime.date.fromisoformat(dataset["meta"]["start_date"])
    last = release + datetime.timedelta(days=max(args.days) + 7)
    counts, names = count_games(args.games, last.isoformat())

    games_per_day = {}
    for (date, _), (n, _, _) in counts.items():
        games_per_day[date] = games_per_day.get(date, 0) + n
    start = min(d for d, n in games_per_day.items() if n >= MIN_GAMES_FIRST_DAY)
    start_day = datetime.date.fromisoformat(start)
    print("games per day:", dict(sorted(games_per_day.items())))

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "start.txt"), "w") as f:
        f.write(start + "\n")
    for n in args.days:
        cutoff = (start_day + datetime.timedelta(days=n)).isoformat()
        early = build(dataset, counts, names, cutoff)
        rated = sum(
            c["deck_colors"]["All Decks"]["gihwr"] > 0
            for c in early["card_ratings"].values()
        )
        with gzip.open(os.path.join(args.out, f"day{n}.json.gz"), "wt") as f:
            json.dump(early, f)
        print(
            f"day {n} (drafts before {cutoff}): {rated} cards rated, "
            f"{early['meta']['game_count']} games"
        )


if __name__ == "__main__":
    main()
