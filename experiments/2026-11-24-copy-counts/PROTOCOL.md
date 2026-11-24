# Do the card-rating verdicts hold with copy-counted win rates? (written before running)

## Why

`games.py` counts a card once per game it was in hand. 17Lands counts copies
(found in the review of upstream PR 284). The deck score's weights don't read
those counts: `fit.py` fits on the app's dataset, which is 17Lands' own. The
card-rating comparison (`quality.py`, `horse.py`,
`experiments/2026-11-03-rating-parts`) does read them, and its verdicts on
shrinkage, the IWD premium, the archetype weight and the power bonus were drawn
from once-per-game win rates.

## Test

The Card ratings workflow, twice at the same commit, on the same decks (every
set, 50,000 decks per set, salt `copies1`): once as it is, and once with
`copies` on, which makes `games.py` count each copy in hand, and each copy left
in the deck that was neither in hand nor tutored.

## Reading

For each version against `engine`, horse.py gives a held-out log loss
difference with a 98.33% interval. A version's verdict is better, worse or no
difference, by whether that interval excludes zero.

- **holds:** every version has the same verdict in both runs.
- **changes:** some version's verdict differs. Name it; the decision that rested
  on it needs its own look.

The size of each difference is reported for both runs either way.
