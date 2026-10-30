"""Summarize compare.py results: a report, and examples of the biggest differences.

    python summarize.py --examples examples.md results/*.json > report.md
"""

import argparse
import json
from collections import defaultdict

STRONG = 0.6


def overlap(suggested, actual):
    """Of the drafter's non-basic cards, how many the suggestion also plays."""
    return sum(min(k, suggested.get(n, 0)) for n, k in actual.items())


def cards_diff(a, b):
    return 40 - sum(min(k, b.get(n, 0)) for n, k in a.items())


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", required=True)
    parser.add_argument("--n-examples", type=int, default=12)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args(argv)

    decks = []
    for path in args.files:
        with open(path, encoding="utf-8") as f:
            decks.extend(d for d in json.load(f) if all(d["suggested"].values()))
    scorers = list(decks[0]["suggested"])
    basics = {"Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"}
    for d in decks:
        d["actual"] = {n: k for n, k in d["deck"].items() if n not in basics}
        d["actual_colors"] = set(d["main_colors"]) | set(d["splash_colors"])

    out = []
    p = out.append
    sets = sorted({d["set"] for d in decks})
    strong = [d for d in decks if d["wr_bucket"] >= STRONG]
    p(
        f"{len(decks):,} real pools from 17Lands Premier Draft game data "
        f"({', '.join(sets)}); {len(strong):,} from strong drafters "
        f"(game win rate ≥ {STRONG:.0%})."
    )
    p("")
    p("For each pool, the deck builder's top suggestion under each scorer, ")
    p("compared with the deck the drafter actually built from the same pool.")
    p("")

    def row(name, group, get):
        n = len(group)
        three = sum(len(get(d)["colors"]) >= 3 for d in group)
        greedy = sum(get(d)["missing_fixers"] > 0 for d in group)
        same_main = sum(set(get(d)["identity"]) == set(d["main_colors"]) for d in group)
        ov = sum(overlap(get(d)["cards"], d["actual"]) for d in group) / n
        p(
            f"| {name} | {100 * three / n:.1f}% | {100 * greedy / n:.1f}% | "
            f"{100 * same_main / n:.1f}% | {ov:.1f} |"
        )

    for title, group in [("All drafters", decks), ("Strong drafters", strong)]:
        p(f"## {title}")
        p("")
        p(
            "| deck | 3+ colors | 3+ colors short of fixing | same main colors as "
            "the drafter | cards in common with the drafter's deck |"
        )
        p("|---|---|---|---|---|")
        for s in scorers:
            row(f"suggested, {s} scorer", group, lambda d, s=s: d["suggested"][s])
        n = len(group)
        three = sum(len(d["actual_colors"]) >= 3 for d in group)
        greedy = sum(d["actual_missing_fixers"] > 0 for d in group)
        p(
            f"| the drafter's own deck | {100 * three / n:.1f}% | "
            f"{100 * greedy / n:.1f}% | - | - |"
        )
        p("")

    p("## How often the top suggestion changes")
    p("")
    p("| from | to | different colors | 10+ cards different |")
    p("|---|---|---|---|")
    for a, b in [(scorers[0], s) for s in scorers[1:]] + [(scorers[1], s) for s in scorers[2:]]:
        col = sum(
            set(d["suggested"][a]["colors"]) != set(d["suggested"][b]["colors"])
            for d in decks
        )
        big = sum(
            cards_diff(d["suggested"][a]["cards"], d["suggested"][b]["cards"]) >= 10
            for d in decks
        )
        p(f"| {a} | {b} | {100 * col / len(decks):.1f}% | {100 * big / len(decks):.1f}% |")
    p("")

    p("## Game win rate of the drafter's deck, by whether its main colors match the suggestion's")
    p("")
    p("| scorer | matches: decks, game win rate | doesn't: decks, game win rate |")
    p("|---|---|---|")
    for s in scorers:
        cells = []
        for match in (True, False):
            g = [
                d
                for d in decks
                if (set(d["suggested"][s]["identity"]) == set(d["main_colors"])) == match
            ]
            games = sum(d["games"] for d in g)
            wins = sum(d["wins"] for d in g)
            cells.append(f"{len(g):,}, {100 * wins / max(games, 1):.1f}%")
        p(f"| {s} | " + " | ".join(cells) + " |")
    p("")

    by_set = defaultdict(list)
    for d in decks:
        by_set[d["set"]].append(d)
    p("## By set: greedy suggestions (3+ colors short of fixing)")
    p("")
    p("| set | pools | " + " | ".join(scorers) + " | the drafter's own |")
    p("|---|---|" + "---|" * (len(scorers) + 1))
    for s, g in sorted(by_set.items()):
        cells = [
            f"{100 * sum(d['suggested'][k]['missing_fixers'] > 0 for d in g) / len(g):.1f}%"
            for k in scorers
        ]
        own = 100 * sum(d["actual_missing_fixers"] > 0 for d in g) / len(g)
        p(f"| {s} | {len(g)} | " + " | ".join(cells) + f" | {own:.1f}% |")
    print("\n".join(out))

    # Examples: the pools whose top suggestion changed the most, old to new.
    def fmt_cards(cards):
        return ", ".join(f"{k} {n}" if k > 1 else n for n, k in sorted(cards.items()))

    ranked = sorted(
        decks,
        key=lambda d: -cards_diff(
            d["suggested"][scorers[0]]["cards"], d["suggested"][scorers[1]]["cards"]
        ),
    )
    ex = []
    e = ex.append
    e("# Deck builder suggestions before and after the deck score refit")
    e("")
    e(
        "Real 17Lands Premier Draft pools where the builder's top suggestion "
        "changed the most between the old scorer and the new one. Each shows "
        "what the drafter actually built and how it did, then the builder's top "
        "suggestion under each scorer: its label, score, notes, and cards."
    )
    e("")
    for i, d in enumerate(ranked[: args.n_examples], 1):
        splash = f" splash {d['splash_colors']}" if d["splash_colors"] else ""
        e(f"## {i}. {d['set']}, the drafter played {d['main_colors']}{splash}")
        e("")
        e(
            f"Record with that deck: {d['wins']}–{d['games'] - d['wins']} in games. "
            f"Drafter's game win rate bucket: {d['wr_bucket']:.2f}. "
            f"17Lands deck {d['id']}."
        )
        e("")
        e(f"- **Drafter's deck**: {fmt_cards(d['actual'])}")
        for s in scorers:
            g = d["suggested"][s]
            e(
                f"- **{s} scorer**: {g['label']}. Notes: {g['breakdown'] or 'none'}. "
                f"Cards: {fmt_cards(g['cards'])}"
            )
        e("")
    with open(args.examples, "w", encoding="utf-8") as f:
        f.write("\n".join(ex) + "\n")


if __name__ == "__main__":
    main()
