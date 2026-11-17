# Does the app's land count win?

Written before any result of this run was seen.

## The app's rule

There is no curve in it. Every suggested deck takes 23 spells
(`build_variant_consistency` and the other builds in `src/advisor/deck_builder.py`
take `candidates[:23]`) and fills the other 17 slots with lands. The Tempo build
takes 24 spells and plays 16 lands; its removal is open as #275. Auto lands in the
Custom Deck window fills 40 less the user's own spell count, so it follows the user.
Auto optimize can offer "Play 16 Lands" or "Play 18 Lands" when its simulation likes
them.

So the question is whether a flat 17 is right, and if not, whether the best count
depends on the curve.

## The data

The Deck score fit's features step: 50,000 decks from each of the twenty sets with
Premier Draft game data and ratings, salt `land-count-2026-11-16`, which no earlier
run used. `features.py` now also records each deck's card count, land count and how
many of its lands are spell // land modal double-faced cards (MDFCs).

Decided before the run:

- **Only decks of exactly 40 cards.** Others are counted and left out.
- **MDFCs count as lands**, as the app counts them: a card with "Land" among its
  types is a land, in the deck builder and the deck score alike. A second report,
  not part of the rule, counts them as spells, to show whether the answer rests on
  this.
- **Land counts**: 15 or fewer, 16, 17, 18, 19 or more, each against 17.
- **Curve bands**: the mean mana value of the deck's spells (`get_functional_cmc`,
  as `extra.mean_mana_value`), cut at the quintiles of all decks pooled.

## The model

Logistic regression of games won, as `fit.py` does it, on: indicators for each land
count against 17; card quality; `missing_fixing`; the deck's color group (splash,
three main colors, more, as in `experiments/2026-11-16-splash-price`); mean mana
value as a straight line and as band indicators; the set; the player's win rate and
experience buckets. Results in game win rate points. SEs are the larger of the
model's (dispersion-widened) and the set-clustered one. Script: `lands.py`.

Pooled over all decks, then the same model within each curve band, then each set
alone.

## The decision rule

A land count **beats 17** if:

1. it won more than 17 by 2 SEs or more, pooled, and
2. its estimate has the same sign as the pooled one in at least 70% of the sets
   with 300 or more decks at that count.

| result | what I propose |
|---|---|
| 16 or 18 beats 17 pooled | change the flat count |
| a count beats 17 only within some curve bands | a curve-dependent count, its breakpoints set from the bands, as a follow-up change with its own Deck builds check |
| nothing beats 17 | the flat 17 stays |

A count that does worse than 17 is not a reason to change anything: it supports 17.

Within bands there are twenty tests (five bands, four counts). A band result that
passes the rule at under 3 SEs is reported as possibly chance, and I'd want it to
repeat on a new salt before proposing a change.

## Predictions

- Pooled: nothing beats 17. 16 and 18 within 0.5 points of 17.
- In the lowest curve band, 16 is on the better side of 17 but doesn't pass.
- In the highest band, 18 is on the better side of 17 but doesn't pass.
- 15 or fewer and 19 or more do worse than 17.

## What it can't show

Drafters choose their land count knowing their deck. A drafter on 16 lands has a
reason, often a low curve, which is held equal, but sometimes card draw, mana sinks
or a plan the model doesn't see. So a weight here is "what decks at this count won",
not "what one more land does to a deck". A deck built by the app has no such reason,
so a gap here is a hint about the rule, not proof.

MDFCs are half a land and half a spell. Counting them as lands makes a deck with
16 basics and two MDFCs an 18-land deck, which is why the second report exists.
