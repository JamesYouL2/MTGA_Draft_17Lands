# What can the regret measure detect?

Written before any result of this run was seen.

## Why

Every verdict on the pick replay is read from the change in regret slope: how much
more strongly a drafter's distance from the advisor's top choice goes with losing.
[The error-bars test](../2026-11-16-error-bars/RESULTS.md) nudged every card's score
by up to 10% at random. That changed 9% of top picks and the measure saw no loss.

So "no objection" may mean little. This run finds how much damage it takes before the
measure objects, and whether the report's other two measures do better.

## The heads

Each replaces or distorts the advisor's final score for every card.

| head | what the advisor does | what I expect it to be |
|---|---|---|
| `noise20-a`, `noise20-b` | a fixed nudge of up to 20% a card, by a hash of its name | mildly worse |
| `noise40-a`, `noise40-b` | up to 40% | clearly worse |
| `random-a`, `random-b` | the score is a fixed random number for each card | the floor: an advisor that knows nothing |
| `worst` | the advisor's order turned upside down | below the floor |
| `gihwr-only` | the card's overall GIH win rate, no rules at all | what every rule together adds |
| `alsa-only` | cards other drafters take earlier score higher; no win rates | the crowd's order |

Two draws of each noise level, because one fixed draw has its own luck.

## What runs

The Advisor heads workflow: ten sets, 3,000 drafts a set and salt, the salts `power1`
and `power2`, new. Held-out ratings, pools in pick order, base upstream main at
`d25398c`. The change in regret slope is the corrected one, with regret scaled within
each set.

## How it is read

For each head: the change in regret slope in SEs, the change in agreement with
drafters' picks (top-1), and event wins per swapped pick.

| what the regret slope does | reading |
|---|---|
| flags `random` and `worst` at 2+ SEs worse, and both `noise40` | it sees large damage. The smallest noise level it flags in both draws is its floor |
| flags `noise20` in both draws too | "no objection" is worth something for a change of that size or larger |
| misses `noise40` in either draw | a removal that changes many picks can pass while doing real harm. Removals over 3% of picks need a second measure before they count as safe |
| misses `random` or `worst` | the measure is not fit to decide anything, and every verdict read from it is reopened |

A second measure qualifies if it orders the heads as damage does: `worst` below
`random` below `noise40` below `noise20`, each flagged at 2+ SEs.

`gihwr-only` and `alsa-only` are not damage. They say how much of the advisor is the
ratings and how much is the rules on top.

## Predictions

- `random` and `worst` are flagged by a wide margin, over 10 SEs.
- `noise40` is flagged in both draws. `noise20` is flagged in one of two.
- Top-1 orders all the damage heads correctly.
- `gihwr-only` is worse than the app by 2+ SEs, and `alsa-only` is worse than
  `gihwr-only`.

## What it can't show

Random noise is one kind of damage. A rule that is wrong in a systematic way, such as
always overrating one color, may be easier or harder to see. And regret is measured in
each head's own scores, so a head that flattens its scores changes what regret means.
