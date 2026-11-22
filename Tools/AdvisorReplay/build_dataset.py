"""Build the app's dataset for a set the daily ETL no longer covers.

    python Tools/AdvisorReplay/build_dataset.py --set SNC --out SNC.json.gz

The ETL only builds sets on Arena's calendar, so an older set with 17Lands dumps
may have no dataset to replay with. This runs the server's own steps for one
set (Premier Draft, all users, all time) and writes the dataset it would
publish. It asks 17Lands for one page per deck color group, with the server's
delay between them, so it takes a few minutes.
"""

import argparse
import gzip
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from server import config  # noqa: E402
from server.extract import (  # noqa: E402
    extract_17lands_data,
    extract_basic_lands,
    extract_color_ratings,
    extract_scryfall_by_names,
    extract_scryfall_data,
    extract_scryfall_tags,
)
from server.transform import transform_payload  # noqa: E402
from server.utils import APIClient  # noqa: E402

FORMAT, USERS = "PremierDraft", "All"


def build(set_code, start_date=""):
    client = APIClient()
    period = config.default_time_period(set_code)
    cards = extract_scryfall_data(client, set_code)
    tags = extract_scryfall_tags(client, set_code)
    for name, land in extract_basic_lands(client).items():
        cards.setdefault(name, land)
    color_ratings, games, total_games = extract_color_ratings(
        client, set_code, FORMAT, USERS, period
    )
    groups = ["All Decks"] + [
        g
        for g in config.ARCHETYPES
        if g != "All Decks" and games.get(g, 0) >= config.MIN_GAMES_THRESHOLD
    ]
    ratings = extract_17lands_data(client, set_code, FORMAT, groups, USERS, period)
    if not ratings.get("All Decks"):
        raise SystemExit(f"17Lands has no {FORMAT} card ratings for {set_code}")
    missing = [name for name in ratings["All Decks"] if name not in cards]
    if missing:
        cards.update(extract_scryfall_by_names(client, missing))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return transform_payload(
        set_code, FORMAT, cards, ratings, tags, color_ratings,
        start_date or today, today, total_games,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--set", required=True, help="17Lands set code")
    parser.add_argument("--out", required=True, help="Where to write it (.json.gz)")
    args = parser.parse_args(argv)
    dataset = build(args.set)
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump(dataset, f)
    rated = sum(
        1
        for card in dataset["card_ratings"].values()
        if card.get("deck_colors", {}).get("All Decks", {}).get("gihwr")
    )
    print(f"{args.set}: {len(dataset['card_ratings'])} cards, {rated} rated")


if __name__ == "__main__":
    main()
