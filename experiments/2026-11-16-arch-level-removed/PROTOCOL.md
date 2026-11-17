# The archetype weight with the pair's level taken out

Written before any result of this run was seen.

## Why

`_calculate_weighted_score()` scores a card at its overall GIH WR plus the
archetype weight (0.65 at pick 1, up to 1.3) times its GIH WR in the lane's pair
less its overall one. That difference has two parts:

- **level**: how much better the pair's cards do in the pair than the format's cards
  do overall, the same for every card with pair data;
- **fit**: how much better this card does in the pair than the pair's cards do.

On 2026-11-08 the weight won on held-out picks (removing it is 3.6 SEs worse on the
corrected measure, flat 0.65 is 2.7). The whole-deck test seemed to object, and
[the pair-parts split](https://github.com/JamesYouL2/MTGA_Draft_17Lands/blob/exp/pair-parts/experiments/2026-11-08-pair-parts/RESULTS.md)
showed why: within a pair, fit predicts decks' wins (+1.29); the loss came from the
level (-0.23). No pick replay has tried fit without level.

Level isn't a constant shift on a pick. Cards with no pair data (mostly off-color
ones, or those under 10 samples in the pair) get their overall rate and no level, so
in a strong pair level pushes the on-lane cards up against the off-lane ones, and in
a weak pair down. In the MKM test dataset the levels run from -0.93 (BR) to +1.78
(UG) points of GIH WR, up to about 0.45 SD, or up to 6.8 score points times the weight.

## The head

| head | what changes |
|---|---|
| `arch-level-removed` | the pair rate used is the card's pair GIH WR less the pair's level |

The pair's level is `SetMetrics.get_metrics(pair, "gihwr")` mean less
`get_metrics("All Decks", "gihwr")` mean: the plain mean over distinct cards with a
rate, in the pair and overall. Nothing else changes. With no pair yet ("All Decks")
the level is zero.

**Why this mean and not the alternatives.** It is the same estimator as the format
mean the score is already centred on, so a pair whose cards do exactly as the
format's do has zero level, and the app already computes it; no new data or
constants. A game-weighted mean would weight the commons drafters play most, on a
different footing from the format mean. The pair's deck win rate from
`color_ratings` is on another scale (deck, not games-in-hand) and would need its own
centring; it also sees only the pair's overall strength, not how its cards' GIH WR
runs, which is what the subtraction has to cancel.

## What runs

The Advisor heads workflow on all 19 sets: 6,000 drafts a set and salt, the salts
`archlvl1` and `archlvl2`, new. Held-out ratings, pools in pick order, base this
branch (`exp/after-landing` plus the head, upstream main `d25398c` in `src/`).

## How it is read

Two measures, as decided in
[the measure power test](../2026-11-16-measure-power/RESULTS.md):

- change in regret slope, regret scaled within each set (`heads.py`'s corrected
  figure), positive worse for the head;
- event wins per swapped pick, positive better for the head.

Both all-sets, and for the four sets over a 20% first-day three-color share (DMU,
TDM, SNC, KTK) against the other fifteen (`by_set.py`, `within_set.py`).

## The decision rule

| result | verdict |
|---|---|
| better by 2+ SEs on either measure, and not worse by 2+ SEs on the other | **adopt**: the level comes out, as its own PR |
| worse by 2+ SEs on either measure, and not better by 2+ SEs on the other | **today's stays**, and the level is earning its place in picks |
| anything else | **today's stays**, no verdict |

All-sets figures decide. The high and low groups are reported, not used for the
verdict.

## Predictions

- Top card changes on 3% to 6% of picks.
- No verdict: within 2 SEs on both measures.
- If anything, leans worse: level is the part that keeps a drafter in a strong pair.

## What it can't show

As in the held-out replay. The power test showed neither measure can prove a change
of this size harmless on this many drafts; "no verdict" means not large harm either
way.
