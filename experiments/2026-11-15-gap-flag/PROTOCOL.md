# A flag by the win-rate gap, against the flag by the three-color share

Written before any result of this run was seen.

## Why

`experiments/2026-11-15-what-sorts-sets` found, after the fact, that the best single
explainer of where a softer off-color penalty helps is how far three-color decks'
win rate falls short of two-color decks'. With it in a fit, the three-color share adds
nothing.

A flag on that gap, cut at -2.2 points, turns on for six of the 19 sets. A flag on the
share, cut at 30%, turns on for four. The two differ in exactly two sets:

| set | gap | share | softer, earlier runs together (SE) |
|---|---|---|---|
| TMT | -0.60 | 23% | -0.0215 (0.0039) |
| FRA | -1.40 | 24% | +0.0029 (0.0038) |

In the other 17 sets the two flags do the same thing. So the choice between them is
the question of whether softening helps in TMT and FRA, which two runs have already
measured. This run measures it a third time, on new drafts, with the gap computed in
the app's own code.

## What this can and can't settle

The cut of -2.2 was chosen on these 19 sets, between TDM (-1.98) and DFT (-2.44). No
set is left that it wasn't chosen on. So a pass here shows the two sets' results
repeat, not that the gap is the right rule for the next set. That limit is the reason
this is the weaker of the two flags to ship, whatever the numbers.

## The heads

Patches in [heads/](heads/). `SetMetrics` gets the gap: the win rate of decks of three
or more colors minus that of two-color decks, from the dataset's color ratings,
weighting each color group by its games.

| head | the square root applies when |
|---|---|
| `flag-gap` | the gap is -2.2 or more |
| `flag-share` | the share is 30% or more. In these two sets that is never, so it is a control: its picks must be the base's |

## What runs

The Advisor heads workflow on TMT and FRA: 6,000 drafts a set and salt, the salts
`gap1` to `gap4`, held-out ratings, pools in pick order, base upstream main at
`6b6dba9`. TMT's dump is small, so its samples share drafts and its SE is understated.

## How it is read

Each set's change for `flag-gap`, from `by_set.py`, pooled by weighting each by its SE.

| | verdict |
|---|---|
| the two together are better by 2+ SEs, and FRA is not worse by 2+ SEs | the gap flag does better than the share flag on the sets tested. Which to ship is the maintainer's call, given the limit above |
| FRA is worse by 2+ SEs | the gap flag is rejected: it would hurt the current set |
| otherwise | no case for changing the flag |

## Predictions

- TMT is better by 2+ SEs again. FRA is within 2 SEs, on the worse side.
- The two together pass.

## What it can't show

As in the held-out replay, and the limit above.
