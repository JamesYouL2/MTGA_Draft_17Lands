"""Per-card pick features, and the training rows for one set.

The features are computed from the card dicts the app holds (17Lands ratings
plus card data) and the pool taken so far, without the app's advisor, so the
same function serves the training rows and the replay heads:

    python Tools/LearnedPick/features.py --drafts drafts.json.gz \
        --dataset FRA_PremierDraft_All_Data.json.gz --set FRA --out FRA.npz

Rarity and play counts are left out on purpose: strong drafters take rares
more than their win rates justify, and play counts track what people pick, so
both would teach the model human habits rather than card value.
"""

import argparse
import gzip
import json
import os
import re
import sys

COLORS = "WUBRG"
FEATURES = [
    "quality",  # overall GIH WR, in SDs of the set's GIH WR (NaN if unrated)
    "lane_fit",  # GIH WR in the pool's top two colors minus overall, in SDs
    "color_share",  # the pool's share of the card's thinnest color
    "off_pips",  # the card's mana symbols outside the pool's top two colors
    "pack",
    "pick",
    "iwd",  # improvement when drawn, in points (NaN if missing)
    "mana_value",
    "creature",
    "alsa",  # average last seen at, a wheel signal (NaN if missing)
    "n_colors",
]
NAN = float("nan")
MIN_PAIR_SAMPLES = 10  # the advisor's own gate on pair win rates
TOKEN = re.compile(r"\{([^}]*)\}")


def _stats(card, deck="All Decks"):
    return (card.get("deck_colors") or {}).get(deck) or {}


def _float(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return NAN
    return x


def lane(pool):
    """The pool's top two colors by non-land cards, most first (fewer if fewer)."""
    counts = color_counts(pool)
    ranked = sorted((c for c in COLORS if counts[c] > 0), key=lambda c: -counts[c])
    return ranked[:2]


def color_counts(pool):
    counts = {c: 0 for c in COLORS}
    for card in pool:
        if "Land" in (card.get("types") or []):
            continue
        for c in card.get("colors") or []:
            if c in counts:
                counts[c] += 1
    return counts


def off_pips(card, lane_colors):
    """Colored mana symbols the lane can't pay; 0 before the pool has a color.

    Hybrid symbols count only if no option is in the lane. Phyrexian and
    two-brid symbols can be paid without the color and don't count."""
    if not lane_colors:
        return 0
    cost = card.get("mana_cost") or ""
    if not cost:
        return sum(c not in lane_colors for c in card.get("colors") or [])
    off = 0
    for token in TOKEN.findall(cost.upper()):
        if "P" in token or any(ch.isdigit() for ch in token):
            continue
        options = {ch for ch in token if ch in COLORS}
        if options and not options & set(lane_colors):
            off += 1
    return off


def card_features(card, pool_counts, lane_colors, pack_no, pick_no, mean, sd):
    """One row of FEATURES for a card."""
    stats = _stats(card)
    gihwr = _float(stats.get("gihwr"))
    rated = gihwr > 0
    quality = (gihwr - mean) / sd if rated else NAN

    lane_fit = NAN
    if rated and len(lane_colors) == 2:
        pair = "".join(c for c in COLORS if c in lane_colors)
        pair_stats = _stats(card, pair)
        pair_wr = _float(pair_stats.get("gihwr"))
        samples = _float(pair_stats.get("samples"))
        if pair_wr > 0 and samples >= MIN_PAIR_SAMPLES:
            lane_fit = (pair_wr - gihwr) / sd

    colors = [c for c in card.get("colors") or [] if c in COLORS]
    total = sum(pool_counts.values())
    if not colors:
        share = 1.0
    elif total == 0:
        share = NAN
    else:
        share = min(pool_counts[c] for c in colors) / total

    alsa = _float(stats.get("alsa"))
    return [
        quality,
        lane_fit,
        share,
        float(off_pips(card, lane_colors)),
        float(pack_no),
        float(pick_no),
        _float(stats.get("iwd")),
        _float(card.get("cmc")),
        float("Creature" in (card.get("types") or [])),
        alsa if alsa > 0 else NAN,
        float(len(colors)),
    ]


def pack_features(pack, pool, pack_no, pick_no, mean, sd):
    """{card name: feature row} for each distinct card in the pack."""
    counts = color_counts(pool)
    lane_colors = lane(pool)
    rows = {}
    for card in pack:
        name = card.get("name")
        if name not in rows:
            rows[name] = card_features(
                card, counts, lane_colors, pack_no, pick_no, mean, sd
            )
    return rows


def set_scale(metrics):
    """The set's GIH WR mean and SD, with the advisor's fallbacks."""
    mean, sd = metrics.get_metrics("All Decks", "gihwr")
    return (mean if mean > 0 else 54.0), (sd if sd > 0 else 4.0)


def training_rows(app, drafts):
    """Arrays for the drafts' picks: one group of rows (distinct pack cards) a pick.

    app is Tools/AdvisorReplay/replay.App for the set."""
    mean, sd = set_scale(app.metrics)
    X, label, group, wins, strong, weak, in_strong, in_all, draft_of = (
        [], [], [], [], [], [], [], [], []
    )
    for d_index, draft in enumerate(drafts):
        pool_names = []
        for pack_no, pick_no, taken, pack_names, by_card in draft["picks"]:
            pool_names = by_card
            taken_cards = app.cards([taken])
            if not taken_cards:
                continue
            taken_name = taken_cards[0]["name"]
            pack = app.cards(pack_names)
            rows = pack_features(pack, app.cards(pool_names), pack_no, pick_no, mean, sd)
            if len(rows) < 2 or taken_name not in rows:
                continue
            for name, row in rows.items():
                X.append(row)
                label.append(int(name == taken_name))
            group.append(len(rows))
            wins.append(draft.get("wins") or 0.0)
            strong.append(bool(draft.get("strong")))
            weak.append(bool(draft.get("weak")))
            in_strong.append("strong" in draft.get("samples", ["strong", "all"]))
            in_all.append("all" in draft.get("samples", ["strong", "all"]))
            draft_of.append(d_index)
    import numpy as np

    return {
        "X": np.asarray(X, dtype=np.float32).reshape(-1, len(FEATURES)),
        "label": np.asarray(label, dtype=np.int8),
        "group": np.asarray(group, dtype=np.int32),
        "wins": np.asarray(wins, dtype=np.float32),
        "strong": np.asarray(strong, dtype=bool),
        "weak": np.asarray(weak, dtype=bool),
        "in_strong": np.asarray(in_strong, dtype=bool),
        "in_all": np.asarray(in_all, dtype=bool),
        "draft": np.asarray(draft_of, dtype=np.int32),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--drafts", required=True, help="drafts.py output")
    parser.add_argument("--dataset", required=True, help="The app's dataset")
    parser.add_argument("--set", required=True, help="Set code")
    parser.add_argument("--src", default=".", help="Folder holding the app's src/")
    parser.add_argument("--out", required=True, help="Where to write (.npz)")
    args = parser.parse_args(argv)

    import numpy as np

    sys.path[:0] = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "AdvisorReplay"),
        os.path.abspath(args.src),
    ]
    from replay import App

    app = App(args.dataset)
    with gzip.open(args.drafts, "rt", encoding="utf-8") as f:
        drafts = json.load(f)
    data = training_rows(app, drafts)
    np.savez_compressed(args.out, set=np.array(args.set), features=np.array(FEATURES), **data)
    print(
        f"{args.set}: {len(data['group'])} picks, {len(data['label'])} rows "
        f"from {len(drafts)} drafts; unmatched {dict(app.unmatched.most_common(5))}"
    )


if __name__ == "__main__":
    main()
