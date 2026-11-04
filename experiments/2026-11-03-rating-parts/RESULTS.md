# Which card rating predicts results

Run [41752671721](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/41752671721)
at `067c22f` (`269f8df` plus a push trigger; that workflow ran this test
and the mana-penalty test together), on the same decks as the rule
tests: 914,784 registered decks and 4.14M games from all 20 sets with
Premier Draft game data and Premier Draft ratings, up to 50,000 decks a set.

The protocol is in [Tools/DeckScoreFit/README.md](../../Tools/DeckScoreFit/README.md#which-rating-predicts-results).
It was written down before the first run. The full report is
[horse.md](horse.md), and the numbers are in [horse.json](horse.json).

The first run,
[41745035079](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/41745035079),
showed a problem in the data, fixed before this run:

- **Ratings.** The first run rated decks only from games played by decks
  outside the sample. TMT's whole dump is under 50,000 decks, so it was
  left with no ratings at all. PIO, FRA, HOB and MSH were left with a
  fraction of theirs, and noisy ratings favor shrinkage. Ratings are now
  cross-fitted: each deck is rated from the four fifths of its set's dump
  that it isn't in.

## Which rating predicts results

Each version of the engine's card rating gives a deck a quality: the average
of its spells' values. Each version was then compared on how well it
predicts held-out decks' results, using 914,784 decks from 20 sets. The
gain is the engine's version against the ablation, in held-out log loss
per game.
Positive means the engine's version predicts better. It is also given as a
share of what card quality is worth: 1.63 [1.57, 1.69] millinats a game,
measured against no card quality at all. The intervals are 98.33%, which is
95% familywise across the three comparisons.

| what the engine does | gain (millinats a game) | share of card quality's worth | verdict |
|---|---|---|---|
| Archetype weighting (`no-archetype`) | −0.434 [−0.472, −0.397] | −26.7% [−29.0%, −24.4%] | **drop** |
| Shrinkage (`no-shrinkage`) | +0.140 [+0.122, +0.158] | +8.6% [+7.5%, +9.7%] | **keep** |
| IWD premium (`no-iwd`) | +0.034 [+0.033, +0.036] | +2.1% [+2.0%, +2.2%] | **keep** (barely matters) |

**Archetype weighting makes the rating worse.**

- **The result.** Blending in the card's win rate in the deck's color pair
  at the engine's average weight (0.95) predicts results worse than the
  overall GIH WR alone. The loss is about a quarter of everything card
  quality adds.
- **Weight.** The less weight, the better. At 0.65 (the engine's pick-1
  weight) the rating predicts better than at 0.95. At 1.3 (its weight from
  pick 15) it predicts worse.
- **By set.** 18 of the 20 sets agree. The exceptions are PIO and the Cube,
  and the Cube rates only 240 decks.
- **Pair strength.** The model has no color-pair terms, so a pair's own
  strength was free to help the archetype version, and it still loses.
  Pair win rates, even shrunk, carry more noise and selection than signal
  about how good the card is.

Two caveats limit what this says about picks:

- **Lane.** The archetype here is the deck's final main colors, the best
  case. During a draft the engine has to guess the lane.
- **Within a pack.** The test ranks whole decks. Within a pack the pair's
  overall level cancels out, and what matters is whether pair win rates
  order the cards better. It shows that the blended rating is a worse
  measure of card strength. It doesn't directly test the pick-order
  effect.

**Shrinkage helps.** It is worth +8.6% of card quality. It helps in 16 of 20 sets;
in LTR, MH3, TDM and the Cube it makes no clear difference.
Since the archetype blend hurts anyway, shrinkage mainly limits the damage.

**The IWD premium** comes out "keep" because its interval excludes zero.
But it is worth 2.1% of card quality, right at the 2% "no difference"
margin. It is harmless and nearly irrelevant.

Other versions, not used for a verdict:

| version | gain of the engine's version | share of card quality's worth |
|---|---|---|
| blend weight 0.65 | −0.203 [−0.213, −0.194] | −12.5% |
| blend weight 1.3 | +0.214 [+0.206, +0.223] | +13.2% |
| no power bonus | +0.321 [+0.309, +0.333] | +19.7% |
| overall GIH WR alone (no blend, no bonus) | −0.257 [−0.294, −0.220] | −15.8% |
| the deck score's blend (0.7 pair, 0.3 overall, no shrinkage) | +0.264 [+0.244, +0.284] | +16.2% |

- **The power bonus** helps a lot: +19.7%. Even without it, the overall GIH
  WR alone beats the engine's blend.
- **The deck scorer's own blend** in `get_card_rating()` (0.7 pair, 0.3
  overall, unshrunk) is worse than the engine's. That makes it the weakest
  rating tested.

## What this suggests

These are suggestions, not part of the test:

- **Archetype weighting.** Cut it well below 0.6–1.3, or drop it from the
  card's value. A test of the pick-order effect, such as the replay
  harness, should come before removing it from pick ordering.
- **The deck scorer's blend.** Switch `get_card_rating()` to the overall
  GIH WR, or at least shrink its pair win rates.
