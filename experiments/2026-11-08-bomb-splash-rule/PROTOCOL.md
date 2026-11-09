# Testing Enables Bomb Splash on game results: protocol

Written before any run. It goes with the replay test of the same rule in
`experiments/2026-11-08-pick-multipliers` (branch `exp/pick-multipliers`).

## The rule

From `_calculate_composition_bonus()` in `src/advisor/engine.py`: a land or fixing
card gets 1.3x if a card in the pool rated 1.5 SDs above the format's mean needs a
color it makes, unless the 1.4x Needs Fixing rule fires first.

## The test

`Tools/DeckScoreFit/splash_rule.py` uses `rules.py`'s logistic regression and its
controls: card quality, the app's other deck features (without `missing_fixing`, as
in the fixing rule's test), the set, and the player's buckets. It adds to the fixing
rule's terms the count of off-lane bombs in the deck, and a separate slope for fixing
in decks with at least one.

**Tested claim:** a fixing card is worth more in a deck that plays an off-lane bomb
than in other decks with off-color cards. Bombs and castability are counted the way
the engine counts them, with a deck's main colors as its lane.

Decided before the first run:

- **Primary result:** that difference in slope, per fixing card, in game win rate
  points, with a 95% interval. The SE is the larger of the model's, widened for
  overdispersion, and the set-clustered sandwich.
- **Verdict:** *supported* if the interval excludes zero in the rule's direction,
  *contradicted* if it excludes zero the other way, otherwise *not established*.
- **For the rule's removal:** with the replay, as that protocol says. *Supported*
  keeps the rule. Otherwise the replay decides.
- **Prediction:** not established, as with Needs Fixing, whose interval included zero
  in `experiments/2026-11-03-rule-targets`.

Reported, not deciding: the rule's size against the effect in rating SDs, per-set
fits, added counts as controls, strong drafters only, and what a fixing card is worth
in a deck with an off-lane bomb.

## What it can't show

- It sees decks, not pools. The rule fires on a bomb in the pool, but only a bomb
  that was played counts here, so decks that passed on the splash are in the
  comparison group only if they play other off-color cards.
- It's observational, and drafters who splash a bomb may differ in ways the skill
  buckets don't capture.
- It values a fixing card in a finished deck, not the pick-order effect of taking it
  over another card. The replay covers that.

Synergy 1.2x has no test on results: no card in any set's data has a `synergy_*` tag.
Premium Fixing's pack 1 gate and the on-lane multiplier's lane don't exist in a
finished deck.
