"""Phase 3-lite decomposition run (P3DECOMP.md): simulate main and the heads with
the parts of each deck's score saved.

    python p3_decomp.py --src . --drafts drafts.json.gz --dataset heldout.json.gz \
        --set FDN --heads main blend-1 marginal --first 0 --limit 125 --out out/part0

Writes <head>.json per head in replay.py's format, simulation only. Each draft's
"sim" has simulate.py's fields plus "parts" (simulate.deck_parts, with the
deck's spells and colors) and "pool" (facts about the simulated pool).
"""

import argparse
import gzip
import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p3_heads  # noqa: E402  (puts Tools/AdvisorReplay on the path)
import simulate  # noqa: E402

_deck_choice, _deck_parts = simulate.deck_choice, simulate.deck_parts
LAST = {}  # the pool and deck of the draft being simulated


def overall(card):
    return float(card.get("deck_colors", {}).get("All Decks", {}).get("gihwr") or 0.0)


def deck_choice(app, pool):
    LAST["pool"] = pool
    return _deck_choice(app, pool)


def deck_parts(app, deck, pool_size):
    out = _deck_parts(app, deck, pool_size)
    if out is None:
        return None
    land = app.constants.CARD_TYPE_LAND
    spells = [c for c in deck["deck_cards"] if land not in c.get("types", [])]
    colors = list(deck["colors"])
    out["deck_colors"] = colors
    out["cards"] = sorted(f'{c.get("count", 1)} {c[app.constants.DATA_FIELD_NAME]}' for c in spells)
    out["splash"] = app.splash_spells(deck["deck_cards"], colors, False)
    # The pool: its spells' mean overall rating in SDs from the format mean, and
    # how many of them are castable in the deck's colors.
    mean, sd = app.metrics.get_metrics("All Decks", "gihwr")
    mean, sd = mean or 54.0, sd or 4.0
    pool_spells = [c for c in LAST.get("pool", []) if land not in c.get("types", [])]
    rated = [overall(c) for c in pool_spells if overall(c) > 30.0]
    on = set(colors)
    out["pool_spells"] = len(pool_spells)
    out["pool_quality"] = round((sum(rated) / len(rated) - mean) / sd, 4) if rated else None
    out["pool_on_color"] = sum(1 for c in pool_spells if set(c.get("colors", []) or []) <= on)
    return out


simulate.deck_choice, simulate.deck_parts = deck_choice, deck_parts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--src", default=".")
    ap.add_argument("--drafts", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--set", default="")
    ap.add_argument("--heads", nargs="+", required=True)
    ap.add_argument("--out", required=True, help="Folder for <head>.json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--first", type=int, default=0, help="Skip the first N drafts")
    args = ap.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.src))
    app = p3_heads.HeadApp(args.dataset)
    with gzip.open(args.drafts, "rt", encoding="utf-8") as f:
        drafts = json.load(f)
    drafts = drafts[args.first:]
    if args.limit:
        drafts = drafts[: args.limit]

    results = {h: [] for h in args.heads}
    sims = {h: Counter() for h in args.heads}
    seconds = Counter()
    start = time.time()
    for d in drafts:
        app.cache = {}  # one draft's builds are shared by every head
        for h in args.heads:
            t = time.time()
            app.set_head(h)
            LAST.clear()
            out = {k: d[k] for k in ("id", "skill", "games", "wins", "losses")} | {
                "picks": [], "deck_score": None, "pool_gihwr": None,
                "sim": simulate.simulate_draft(app, d, sims[h], detail=True)}
            results[h].append(out)
            seconds[h] += time.time() - t
    total = time.time() - start
    os.makedirs(args.out, exist_ok=True)
    for h in args.heads:
        with open(os.path.join(args.out, f"{h}.json"), "w", encoding="utf-8") as f:
            json.dump({
                "set": args.set, "label": h, "seconds": round(seconds[h]),
                "skipped": {}, "simulation": dict(sims[h]),
                "unmatched": dict(app.unmatched.most_common(10)),
                "drafts": results[h],
            }, f)
    print(f"{len(drafts)} drafts, heads {args.heads}: {total:.0f}s "
          f"({total / max(1, len(drafts)):.1f}s per draft), per head "
          f"{dict((h, round(s)) for h, s in seconds.items())}")


if __name__ == "__main__":
    main()
