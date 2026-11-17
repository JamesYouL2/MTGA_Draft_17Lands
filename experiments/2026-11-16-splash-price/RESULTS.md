# Should a splash cost the same as three colors in the deck score? Results

Run [44007932871](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44007932871)
at `7fefad9`: 914,650 decks and 4.13M games from twenty sets, salt
`splash-price-2026-11-16`. The full report is [colors.md](colors.md). The rule is in
[PROTOCOL.md](PROTOCOL.md), written before the run.

## The answer

No. By the rule, the single weight should be split. A splash costs less than three main
colors, and how much less depends on how many spells need the splash.

| deck | weight today | fitted weight (points) |
|---|---|---|
| two colors or fewer | 0 | 0 |
| two main colors and a splash | -3.1 | -2.47 ± 0.20 |
| three main colors, no splash | -3.1 | -3.28 ± 0.31 |
| three main colors and a splash, or four or more | -3.1 | -4.94 ± 0.41 |

The three conditions:

| condition | result | passes |
|---|---|---|
| splash less three main colors, 2+ SEs | +0.81 ± 0.27, 3.0 SEs | yes |
| held-out log loss better | +7.9e-5 a game, better on 17 of 20 sets | yes |
| same sign in 70%+ of sets | 18 of 19 (Cube has too few of each) | yes |

## The size of the splash matters more

This was reported only, but it is the clearer finding. Splash decks, by how many
spells need the splash:

| spells needing the splash | share of splash decks | weight |
|---|---|---|
| 0 or 1 | 33.2% | -1.82 ± 0.17 |
| 2 | 28.6% | -2.43 ± 0.20 |
| 3 | 22.7% | -2.82 ± 0.24 |
| 4 or more | 15.5% | -3.56 ± 0.29 |

As a line: -0.43 ± 0.05 points a splash spell, 9.3 SEs, and the bins run in order. By
the protocol that is enough to suggest a weight per splash card. A splash of four or
more spells costs as much as three main colors, which is what such a deck is.

The app's splash builds hold two or three splash spells, so under these weights they
would lose about 2.4 to 2.8 points, not 3.1. Three-color builds would lose about 0.2
more than today, and four-color builds about 1.8 more.

## TDM again

TDM is the one set where a splash costs more than three main colors (-0.8 ± 0.3). It is
also the one high three-color set where softening the off-color penalty didn't help
(see `exp/flag-snc-ktk`). Its three-color decks are less of a stretch than a splash,
which fits a set built around three-color clans. That is a reading, not a test.

## Predictions

| prediction | result |
|---|---|
| Q0: about -3.1 | right: -2.99 ± 0.24 |
| Q1: a splash costs less, splash about -2, three main about -4.5, the rule passes | direction right and the rule passes; the gap is smaller (-2.5 and -3.3) |
| Q2: bigger splashes cost a little more, under 2 SEs | wrong: -0.43 a spell, 9.3 SEs |
| "more" costs the most | right: -4.9 |

## What's next

The app change, as its own step. `deck_features()` gets the splash colors from the deck
builder and replaces `two_colors` with weights for a splash (a base plus a weight per
splash spell), three main colors, and more. Fit that form directly before writing it
down: the bins above suggest roughly -1.4 plus -0.43 a spell. Then a Deck builds run
measures how often the first suggested deck changes, before anything is proposed.

## What this can't show

As the protocol says: drafters choose when to splash and how much, so these weights say
what decks like these won, not what splashing does to a given pool. A drafter who
splashes four spells may do so because the pool's two main colors are thin, and that
would show up here as a cost of the splash.
