# Should a splash cost the same as three colors in the deck score?

Written before any result of this run was seen.

## Why

The deck score gives +3.1 points (`two_colors`) to a deck of two colors or fewer,
which is the same as docking 3.1 points from every other deck. A deck with two main
colors and two splash cards loses exactly as much as a real three-color deck.

The [land swaps test](https://github.com/JamesYouL2/MTGA_Draft_17Lands/blob/exp/lands-recheck/experiments/2026-11-16-land-swaps/RESULTS.md)
found that three-color and splashing decks win less than their card quality says.
It held card quality equal but not the deck score, so it can't say whether the 3.1
already covers that. What it does suggest is that the two kinds of deck may differ.
The deck builder makes both kinds (a "Splash X" build and a three-color build) and
ranks them by this score, so a wrong price moves the suggested deck.

## The data

The Deck score fit's features step (`deck-score-features.yml`): 50,000 decks from
each of the twenty sets with Premier Draft game data and ratings, salt
`splash-price-2026-11-16`, which no earlier run used. `features.py` now also records
17Lands' main and splash colors for each deck and how many of its spells need a
splash color.

The groups, from 17Lands' registered colors:

| group | |
|---|---|
| two | two colors or fewer, no splash: exactly the decks with `two_colors` today |
| splash | two main colors (or one) and a splash |
| three | three main colors, no splash |
| more | three main colors and a splash, or four or more |

## The models

All are `fit.py`'s: logistic regression of games won on card quality,
`missing_fixing`, the color terms, the set and the player's buckets. Weights in score
points. SEs are the larger of the model's (dispersion-widened) and the set-clustered
one. The script is `colors.py`.

- **single**: one term for every group but "two". This is today's score.
- **split**: one term each for splash, three and more.

## Questions

- **Q0.** Today's single weight, refit on new decks. For the record.
- **Q1.** Splash weight less three-main weight, pooled.
- **Q2.** Within splash decks, does a bigger splash (more spells needing it) cost more?
- **Q3.** On each set held out, log loss per game of split against single, both fit
  on the other nineteen sets.
- **Q4.** The split weights fit on each set alone.

## The decision rule

**Split the weight** if all three hold:

1. Q1's difference is 2 SEs or more from zero.
2. Q3: the split model's held-out log loss, weighted by games, is better.
3. Q4: the difference has the same sign as the pooled one in at least 70% of the
   sets where both splash and three-main groups have 300 decks or more.

Otherwise the single weight stays, and I don't retest this without a new reason.

If it passes, the next step is its own change: `deck_features()` needs to know which
colors are a splash (the deck builder knows), and a Deck builds run measures how
often the first suggested deck changes before anything is proposed.

**Q2 is reported only.** A weight per splash card would be a second change. I'll
suggest one only if the slope is 2 SEs or more and the four size bins run in order.

## Predictions

- Q0: about -3.1, as at the last refit.
- Q1: a splash costs less than three main colors: splash about -2, three main about
  -4.5. The rule passes.
- Q2: bigger splashes cost a little more, under 2 SEs.
- "more" costs the most.

## What it can't show

These are drafters' own decks, and drafters choose when to splash: often to play a
bomb out of a weak pool. Card quality is held equal, but a pool's shape isn't, so a
weight here is "what decks like this won", not "what splashing does to a deck".
That is the right question for ranking builds of one pool only if the reason a
drafter splashed doesn't itself predict losing.

17Lands decides what counts as a splash color; the app's splash builds hold two or
three splash spells, close to but not the same as 17Lands' rule. Q2's bins show how
many spells 17Lands' splash decks hold.
