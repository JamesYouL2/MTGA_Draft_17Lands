# Is Suggest Deck's "X wins" calibrated? Results

Data: the features of Splash price run
[44007932871](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44007932871),
914,650 decks and 4,133,840 games from 20 sets. Full report:
[calibration.md](calibration.md). The rule is in [PROTOCOL.md](PROTOCOL.md), written
before the run.

## The answer

By the rule, the record is calibrated. No score band or color group with 2% or more of
the decks is off by more than 0.3 expected wins, and the slope is 1 within its error. The
app's constants pass as they are, so there is nothing to refit.

## Held out: constants fit on the other 19 sets

Actual less predicted, in expected Premier Draft wins (positive: decks did better than
the record said). SEs clustered by set.

| decks | share | predicted game WR | actual game WR | actual less predicted |
|---|---|---|---|---|
| 70-75 | 11.1% | 47.6% | 48.3% | +0.07 ± 0.09 |
| 75-80 | 46.0% | 53.4% | 53.1% | -0.03 ± 0.05 |
| 80-85 | 38.2% | 58.7% | 58.6% | -0.01 ± 0.05 |
| 85-90 | 4.0% | 63.7% | 65.0% | +0.15 ± 0.08 |
| two colors or fewer | 49.9% | 57.2% | 56.5% | -0.08 ± 0.05 |
| two main colors and a splash | 30.1% | 53.3% | 54.7% | +0.14 ± 0.07 |
| three main colors | 11.2% | 53.1% | 53.1% | -0.00 ± 0.13 |
| three and a splash, or four or more | 8.7% | 54.2% | 54.0% | -0.02 ± 0.07 |

The bands under 70 and from 90 up hold under 1% of decks together. Calibration slope
0.971 ± 0.072, intercept +0.007 ± 0.029. The app's own constants give slope 1.000 ± 0.065
and the same table within 0.02 wins.

## Two things outside the rule

**The set matters more than the band.** The record doesn't know which set it is in,
and for a whole set it is off by up to 0.4 wins: TDM +0.41, Cube +0.39, LTR -0.33,
FDN -0.27. Every set's 17Lands users win about 55% of games, but the mean deck score
moves from set to set. In TDM, a three-color set, the 3+ color weight pulls the whole set
down. This doesn't change which deck is suggested first within a pool, only the number
shown. The rule didn't ask about sets, so it is not a verdict. A per-set offset, or
scoring against the set's own mean, would fix it if wanted.

**Splash decks beat their record by 0.14 wins (2.0 SEs), two-color decks fall short by
0.08.** This is under the rule's 0.3, but it agrees with the question the splash price
experiment asks: the shared 3+ color weight may overcharge a splash.

## Predictions

| prediction | result |
|---|---|
| slope a little under 1 (about 0.9) | right in direction, within error: 0.97 ± 0.07 |
| no band off by 0.3 wins except perhaps 90 and over | right: none fails; 90 and over is +0.53 ± 0.48 on almost no decks |
| three main colors and "more" predicted too high, by under 0.3 | wrong: both within 0.02 wins; splash decks are the ones off, the other way |

## What it can't show

- Bo3 (Traditional Draft): there is no Traditional data, so `3 × P(win a match)` is not
  checked.
- The record is for 17Lands users, who win about 55% of games.
- The deck score's weights were fit to games from these sets, so this is out of sample for
  the two constants only.
