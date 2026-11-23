"""PROTOCOL.md's E4 pilot: hindsight value labels for every card of every pack.

    python experiments/2026-11-22-deck-value/e4_hindsight.py --src . \
        --drafts drafts.json.gz --dataset heldout.json.gz --limit 1000 \
        --shard 0 --shards 4 --out e4.json.gz

label(card) = V(best quick build of final pool − taken + card)
              − V(best quick build of final pool),
V = WIN_LOG_ODDS_AT_BASE + WIN_LOG_ODDS_PER_POINT × (score − BASE_SCORE): the
deck's game win log-odds by the record constants. The quick builds are
replay.App.deck_score's. A label's "flip" is whether the swap changes the
best build's colors. Circular by construction: V is the app's own deck score.
"""

import argparse
import gzip
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "AdvisorReplay"))


def best_build(app, pool):
    """(score, colors) of the best quick build, as replay.App.deck_score."""
    cl = app.card_logic
    builds = []
    for pair in cl.identify_top_pairs(pool, app.metrics):
        builds.append((cl.build_variant_consistency(pool, pair, app.metrics), pair))
        builds.append((cl.build_variant_curve(pool, pair, app.metrics), pair))
        deck, splash = cl.build_variant_greedy(pool, pair, app.metrics)
        builds.append((deck, pair + [splash] if splash else pair))
    deck, colors = cl.build_variant_soup(pool, app.metrics)
    builds.append((deck, colors[:3] if colors else ["All Decks"]))
    best = (0.0, "")
    for deck, colors in builds:
        if deck:
            s = cl.calculate_holistic_score(deck, colors, len(pool), app.metrics)[0]
            if s > best[0]:
                best = (s, "".join(sorted(colors)))
    return best


def log_odds(app, score):
    s = app.scorer
    return s.WIN_LOG_ODDS_AT_BASE + s.WIN_LOG_ODDS_PER_POINT * (score - s.BASE_SCORE)


def label_draft(app, draft):
    """[[pack, pick, taken, {card: [label, flip]}]] in app names, or None."""
    if not draft["picks"]:
        return None
    last = draft["picks"][-1]
    final_names = list(last[4]) + [last[2]]
    name = app.constants.DATA_FIELD_NAME
    final = app.cards(final_names)
    if len(final) < 23:
        return None
    base_score, base_colors = best_build(app, final)
    v0 = log_odds(app, base_score)
    by_name = {}
    for c in final:
        by_name.setdefault(c[name], c)
    cache, out = {}, []
    for pack_no, pick_no, taken, pack_names, _ in draft["picks"]:
        taken_card = app.cards([taken])
        if not taken_card:
            continue
        taken = taken_card[0][name]
        pack = {c[name]: c for c in app.cards(pack_names)}
        if taken not in pack or len(pack) < 2:
            continue
        i = next(k for k, c in enumerate(final) if c[name] == taken)
        labels = {}
        for card_name, card in pack.items():
            if card_name == taken:
                labels[card_name] = [0.0, 0]
                continue
            key = (taken, card_name)
            if key not in cache:
                pool = final[:i] + final[i + 1:] + [card]
                score, colors = best_build(app, pool)
                cache[key] = [round(log_odds(app, score) - v0, 5), int(colors != base_colors)]
            labels[card_name] = cache[key]
        out.append([pack_no, pick_no, taken, labels])
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--src", default=".")
    parser.add_argument("--drafts", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--set", default="")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.src))
    import replay

    app = replay.App(args.dataset)
    with gzip.open(args.drafts, "rt", encoding="utf-8") as f:
        drafts = json.load(f)[: args.limit]
    drafts = drafts[args.shard :: args.shards]
    results, times = [], []
    for d in drafts:
        start = time.time()
        labels = label_draft(app, d)
        times.append(time.time() - start)
        results.append({"id": d["id"], "skill": d["skill"], "labels": labels})
    with gzip.open(args.out, "wt", encoding="utf-8") as f:
        json.dump({"set": args.set, "shard": args.shard, "seconds": times, "drafts": results}, f)
    print(f"{args.set} shard {args.shard}: {len(results)} drafts, "
          f"{sum(times):.0f}s ({sum(times) / max(1, len(times)):.1f}s per draft)")


if __name__ == "__main__":
    main()
