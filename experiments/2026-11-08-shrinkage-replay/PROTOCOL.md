# Can the archetype rate's shrinkage go?

Written before any result was seen.

## Why

`_calculate_weighted_score()` in `src/advisor/engine.py` moves a card's pair win rate
toward its overall win rate when the pair has under 1,000 games in hand. The whole-deck
rating test (`experiments/2026-11-03-rating-parts`) put its worth at 1.0% of card
quality's worth [+0.5, +1.6]. Now that a rate needs 500 games, the most it can pull a
rate is halfway. That test measures finished decks, so removal needs a check on picks
too.

## What runs

The head `no-shrinkage` uses the pair's rate as it is ([the patch](heads/no-shrinkage.patch)),
still only with 10 or more games. It runs with the other heads in
[the pick multipliers test](../2026-11-08-pick-multipliers/PROTOCOL.md), in the same
Advisor heads run: ten sets, 3,000 drafts a set, the salts `""` and `arch2`, on
held-out ratings. Both datasets keep `samples` from the whole dump, so the base's
shrinkage sees no results.

## How it is read

The measure and verdict are that protocol's, from the change in regret slope, head
minus base, with a paired bootstrap SE:

1. **Keep:** worse by 2 SEs or more.
2. **Inconclusive:** otherwise, if the change plus 2 SEs is above +0.0063.
3. **No objection:** otherwise. Shrinkage can go on this evidence.

## Prediction

"No objection", with the top card changing on under 1% of picks. Shrinkage only
matters for pair rates with 500-999 games, and those cards are the ones drafters of
the pair rarely see.

Reported, not deciding: how often the top card changes, top-1, the on-lane share, the
change in each sample, and event wins per pick swapped to the head's top card.

## What it can't show

As in the held-out replay. Also, 17Lands data with thin pair rates, such as a new set
in its first days, may gain more from shrinkage than these full-format ratings. The
dumps are from whole formats, so this test doesn't cover the early days of a set.
