"""Add the three-color share to an app dataset made before datasets recorded it.

    python Tools/PickFit/three_color_share.py --src . \
        --dataset FRA_PremierDraft_All_Data.json.gz --set FRA

The share of games played by decks of three or more colors is taken from
17Lands' color ratings over the dataset's own dates, as the app and the server
record it for new datasets. A dataset that already has it is left alone.
"""

import argparse
import gzip
import json
import sys

import requests


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--src", required=True, help="the app's checkout")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--set", required=True)
    parser.add_argument("--event", default="PremierDraft")
    args = parser.parse_args(argv)

    sys.path.insert(0, args.src)
    from src.seventeenlands import Seventeenlands
    from src.utils import three_color_share

    opener = gzip.open if args.dataset.endswith(".gz") else open
    with opener(args.dataset, "rt", encoding="utf-8") as f:
        data = json.load(f)
    meta = data["meta"]
    if meta.get("three_color_share") is not None:
        print(f"{args.set}: already has {meta['three_color_share']}")
        return

    response = requests.get(
        f"{Seventeenlands.URL_BASE}/color_ratings/data",
        params={
            "expansion": args.set,
            "event_type": args.event,
            "start_date": meta["start_date"],
            "end_date": meta["end_date"],
            "combine_splash": "true",
        },
        headers=Seventeenlands.HEADERS,
        timeout=60,
    )
    response.raise_for_status()
    share = three_color_share(response.json())
    if share is None:
        raise SystemExit(f"{args.set}: 17Lands has no color ratings")
    meta["three_color_share"] = round(share, 4)
    with opener(args.dataset, "wt", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"{args.set}: {share:.4f} ({meta['start_date']} to {meta['end_date']})")


if __name__ == "__main__":
    main()
