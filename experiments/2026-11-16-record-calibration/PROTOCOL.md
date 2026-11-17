# Is Suggest Deck's "X wins" calibrated?

Written before any result of this run was seen.

## Why

Each suggested deck shows an expected record, from `estimate_record()` in
`src/advisor/deck_scorer.py`. It turns the deck score into a game win rate with two
constants (`WIN_LOG_ODDS_AT_BASE`, `WIN_LOG_ODDS_PER_POINT`), then into expected wins in
a Premier Draft event (7 wins or 3 losses). The constants were fit to all sets at once
(`fit.py`'s `record_curve`). Nobody has checked them on a set the fit didn't see, or by
the kind of deck. It is the number users read most.

## The data

The features artifacts of the Splash price run (run 44007932871): 50,000 decks from
each of twenty sets, salt `splash-price-2026-11-16`. Each deck's score is
`75 + sum(weight × feature)` with the app's current weights, which the features record.
Color groups are 17Lands' registered colors, as in `../2026-11-16-splash-price`: two
colors or fewer (no splash), two main colors and a splash, three main colors, three plus
a splash or four or more.

## The method (`calibrate.py`)

- **Held out:** for each set, the two constants are fit on the other nineteen (score
  alone, no player terms, as `record_curve` does), and give each of the set's decks a
  predicted game win rate.
- **Current:** the app's constants as they are, for every set.

For each, by score band (under 65, 65-70, 70-75, 75-80, 80-85, 85-90, 90 and over) and by
color group: the share of decks, the predicted and actual game win rate (weighted by
games), and the difference turned into expected Premier Draft wins. SEs are clustered by
set. Also the calibration slope and intercept: a logistic regression of games won on the
predicted log-odds, slope 1 and intercept 0 if calibrated.

17Lands decks' games are not whole events (a deck is one build, and it may be used in
part of an event), so the comparison is on game win rate, and expected wins are derived
from it.

## The decision rule

Propose refitting the constants (or changing how the record is computed) if, on the
held-out predictions:

1. any score band or color group with 2% or more of the decks is off by more than 0.3
   expected wins and by 2 SEs or more, or
2. the calibration slope differs from 1 by 2 SEs or more.

Otherwise the record stays as it is. The current-constants table is reported the same
way. If the held-out one passes but the current one fails, the constants are only stale,
and a refit on today's weights is enough.

## Predictions

- The slope is a little under 1 (about 0.9): constants fit to other sets overstate how
  far apart decks are on a new set.
- No band is off by 0.3 wins except perhaps 90 and over, which has few decks.
- Three main colors and "more" are predicted too high, by under 0.3 wins, because the
  single 3+ color weight is shared with splash decks.

## What it can't show

- Bo3 (Traditional Draft): there is no Traditional data here, so its record,
  `3 × P(win a match)`, is not checked.
- The record is for 17Lands users, who win more than the average player. The app says
  so; it is not a calibration fault.
- The deck score's weights were fit to games from these sets (other decks), so the
  held-out check is out of sample for the two constants only, not for the weights.
