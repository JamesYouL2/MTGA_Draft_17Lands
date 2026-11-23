"""Phase 3-lite heads: pick by value to the deck, with no learned model.

    python experiments/2026-11-22-deck-value/p3_heads.py --src . \
        --drafts drafts.json.gz --dataset heldout.json.gz --set FDN \
        --heads marginal blend-1 --out results/ --simulate [--limit N]

Writes results/<head>.json in replay.py's format, so the files sit beside the
base's and gihwr-only's from replay.py and read the same way. Each head is
replay.App with advise() replaced (PHASE3LITE.md has the rules):

- marginal: each card in the pack scores V(pool + card) − V(pool), where V is
  the best of replay.App.deck_score's quick builds, scored as the registered
  Phase 2a V: deck score − 0.229 × splash-color spells (per copy). V(pool) is
  the same for every card of a pick, so the head ranks by V(pool + card).
- blend-L: main's score + L × SD(main's scores in the pack) × z(marginal),
  z taken over the pack's distinct cards.

The pool is padded with F filler cards before it is built:
F = max(0, round(23 × (41 − cards taken so far) / 42)). A filler is a
colorless 3-mana creature rated at the set's mean GIH WR (z = 0), so the
builds have about 23 spells to choose from at every pick: early picks reduce
to quality plus color fit, and the padding fades to none by the last pick.
Ties (cards no build would play) keep main's order.

No src/ change: the heads live here and call the app's own builders.
"""

import argparse
import gzip
import json
import os
import statistics
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Tools", "AdvisorReplay"))
import replay  # noqa: E402

SPLASH_POINTS = 0.229  # Phase 2a registered V: points per splash-color spell
PICKS = 42  # deck_scorer.deck_features' full pool


def fillers_for(pool_size):
    return max(0, round(23 * (PICKS - 1 - pool_size) / PICKS))


class HeadApp(replay.App):
    """replay.App whose advise() is one of the Phase 3-lite heads (mode)."""

    def __init__(self, dataset_path):
        super().__init__(dataset_path)
        self.mode, self.lam = "main", 0.0
        self.cache = {}
        mean, _ = self.metrics.get_metrics("All Decks", "gihwr")
        self.filler_wr = mean or 54.0
        self.fillers = [
            {
                "name": f"Filler {i}",
                "types": ["Creature"],
                "colors": [],
                "mana_cost": "{3}",
                "cmc": 3,
                "tags": [],
                "deck_colors": {"All Decks": {"gihwr": self.filler_wr}},
            }
            for i in range(23)
        ]
        self.builds = Counter()

    def set_head(self, head):
        if head == "marginal":
            self.mode, self.lam = "marginal", 0.0
        elif head.startswith("blend-"):
            self.mode, self.lam = "blend", float(head.split("-", 1)[1])
        elif head == "main":
            self.mode, self.lam = "main", 0.0
        else:
            raise ValueError(head)

    def splash_spells(self, deck, colors, soup):
        """Spell copies with a color outside the build's main two colors: the
        pair for a pair build (only build_variant_greedy splashes), the two
        most common colors of its spells for the soup."""
        c = self.constants
        spells = [x for x in deck if c.CARD_TYPE_LAND not in x.get("types", [])]
        if soup:
            by = Counter()
            for x in spells:
                for col in x.get("colors", []) or []:
                    by[col] += x.get("count", 1)
            main = {col for col, _ in by.most_common(2)}
        elif len(colors) <= 2:
            return 0
        else:
            main = set(colors[:2])
        return sum(x.get("count", 1) for x in spells if not set(x.get("colors", []) or []) <= main)

    def value(self, pool, n_fill):
        """V in deck-score points: the best quick build of pool + fillers."""
        key = (n_fill, tuple(sorted(c[self.constants.DATA_FIELD_NAME] for c in pool)))
        if key in self.cache:
            return self.cache[key]
        cl, m = self.card_logic, self.metrics
        full = pool + self.fillers[:n_fill]
        builds = []
        for pair in cl.identify_top_pairs(full, m):
            builds.append((cl.build_variant_consistency(full, pair, m), pair, False))
            builds.append((cl.build_variant_curve(full, pair, m), pair, False))
            deck, splash = cl.build_variant_greedy(full, pair, m)
            builds.append((deck, pair + [splash] if splash else pair, False))
        deck, colors = cl.build_variant_soup(full, m)
        builds.append((deck, colors[:3] if colors else ["All Decks"], True))
        best = 0.0
        for deck, colors, soup in builds:
            if not deck:
                continue
            score = cl.calculate_holistic_score(deck, colors, len(full), m)[0]
            best = max(best, score - SPLASH_POINTS * self.splash_spells(deck, colors, soup))
        self.builds["V"] += 1
        self.cache[key] = best
        return best

    def marginal(self, pack, pool, names):
        by_name = {}
        for c in pack:
            by_name.setdefault(c[self.constants.DATA_FIELD_NAME], c)
        n_fill = fillers_for(len(pool))
        return {n: self.value(pool + [by_name[n]], n_fill) for n in names if n in by_name}

    def advise(self, pack, pool, pack_no, pick_no):
        main = super().advise(pack, pool, pack_no, pick_no)
        if self.mode == "main" or len(main) < 2:
            return main
        marg = self.marginal(pack, pool, list(main))
        if self.mode == "marginal":
            # Ties keep main's order: a tiny step down main's ranking.
            order = sorted(main, key=lambda n: -main[n])
            return {n: marg.get(n, -1e9) - 1e-9 * i for i, n in enumerate(order)}
        sd_m = statistics.pstdev(marg.values()) if len(marg) > 1 else 0.0
        mean_m = statistics.fmean(marg.values()) if marg else 0.0
        sd_main = statistics.pstdev(main.values()) or 1.0
        z = {n: (marg[n] - mean_m) / sd_m if sd_m > 0 else 0.0 for n in marg}
        return {n: s + self.lam * sd_main * z.get(n, 0.0) for n, s in main.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--src", default=".")
    ap.add_argument("--drafts", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--set", default="")
    ap.add_argument("--heads", nargs="+", required=True)
    ap.add_argument("--out", required=True, help="Folder for <head>.json")
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--no-replay", action="store_true",
                    help="Simulate only: skip the pick replay on the drafter's pool")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--first", type=int, default=0, help="Skip the first N drafts")
    args = ap.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.src))
    app = HeadApp(args.dataset)
    with gzip.open(args.drafts, "rt", encoding="utf-8") as f:
        drafts = json.load(f)
    drafts = drafts[args.first:]
    if args.limit:
        drafts = drafts[: args.limit]

    results = {h: [] for h in args.heads}
    skipped = {h: Counter() for h in args.heads}
    sims = {h: Counter() for h in args.heads}
    seconds = Counter()
    start = time.time()
    for d in drafts:
        app.cache = {}  # one draft's builds are shared by every head
        for h in args.heads:
            t = time.time()
            app.set_head(h)
            if args.no_replay:
                import simulate
                out = {k: d[k] for k in ("id", "skill", "games", "wins", "losses")} | {
                    "picks": [], "deck_score": None, "pool_gihwr": None,
                    "sim": simulate.simulate_draft(app, d, sims[h]) if args.simulate else None}
            else:
                out = replay.replay_draft(app, d, skipped[h], sims[h] if args.simulate else None)
            results[h].append(out)
            seconds[h] += time.time() - t
    total = time.time() - start
    os.makedirs(args.out, exist_ok=True)
    for h in args.heads:
        with open(os.path.join(args.out, f"{h}.json"), "w", encoding="utf-8") as f:
            json.dump({
                "set": args.set, "label": h, "seconds": round(seconds[h]),
                "skipped": dict(skipped[h]),
                "simulation": dict(sims[h]) if args.simulate else None,
                "unmatched": dict(app.unmatched.most_common(10)),
                "drafts": results[h],
            }, f)
    print(f"{len(drafts)} drafts, heads {args.heads}: {total:.0f}s "
          f"({total / max(1, len(drafts)):.1f}s per draft), V builds {app.builds['V']}, "
          f"per head {dict((h, round(s)) for h, s in seconds.items())}")


if __name__ == "__main__":
    main()
