"""Test the advisor's Enables Bomb Splash rule on game results.

    python Tools/DeckScoreFit/splash_rule.py results/*.json > splash_rule.md

The rule scores a land or fixing card at 1.3x if a card in the pool, rated 1.5 SDs
above the format's mean, needs a color it makes. Tested: is a fixing card worth more
in a deck that plays an off-lane card of that rating than in other decks with
off-color cards? It reuses rules.py's model, sections and intervals, for this one
rule. See experiments/2026-11-08-bomb-splash-rule/PROTOCOL.md.

Needs NumPy.
"""

import rules


def splash_terms(r):
    has_bomb = (r["off_bomb"] > 0).astype(float)
    return dict(
        rules.fixing_terms(r),
        off_bomb=r["off_bomb"],
        fixing_with_off_bomb=r["fixing"] * has_bomb,
    )


SPLASH = rules.Rule(
    "bomb_splash",
    "Enables Bomb Splash (1.3x)",
    "a fixing card is worth more in a deck with an off-lane bomb than in other decks "
    "with off-color cards",
    splash_terms,
    {"fixing_with_off_bomb": 1},
    1,
    lambda r: r["off_bomb"] > 0,
    (1.3 - 1) * 50 / 15,
    drop=("missing_fixing",),
    secondary={
        "a fixing card in a deck with an off-lane bomb": {
            "fixing": 1,
            "fixing_in_off_color_deck": 1,
            "fixing_with_off_bomb": 1,
        },
    },
)


def main(argv=None):
    rules.RULES = [SPLASH]
    rules.Z = 1.96  # One rule: a plain 95% interval.
    rules.main(argv)


if __name__ == "__main__":
    main()
