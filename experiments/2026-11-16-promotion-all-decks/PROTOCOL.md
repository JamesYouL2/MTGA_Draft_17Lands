# Safe-deck promotion, on every deck the data has

Written before any result of this run was seen.

## Why

The deck builder moves the safe deck to the top when it is within 6 points of the best
one. That changes the first deck in 16.67% of pools, the most of any rule left in the
builder, and two runs gave no verdict: drafters who played the safe deck's colors did
-0.01 [-0.75, +0.73] and -0.09 [-0.68, +0.50] win rate points against those who
played the unpromoted top's.

Those runs sampled up to 50,000 pools a set. This one takes up to 100,000, which for
most sets is every deck in the dump. So it is the most this method can say. If it has
no verdict, more runs won't find one.

## What runs

The Deck builds workflow, unchanged in its builder part: 19 sets, up to 100,000 pools a
set, salt `three`, held-out ratings. Source is upstream main at `6b6dba9`. The 20-point
second promotion has since been removed on main (#269); the 6-point rule is the same.

This sample overlaps the two earlier ones heavily, so it is read alone, not pooled
with them.

## The measure and the rule

The earlier protocol's, unchanged (`deck_variants.py`): among pools where promotion
changes the top deck's colors, drafters in the safe colors against the top's, with
card quality, set and the player's buckets held equal.

| | verdict |
|---|---|
| favors promotion by 2+ SEs | keep |
| against it by 2+ SEs | remove |
| neither | no verdict, and the question is closed for this method: the rule stays, as the maintainer's choice of which deck a user sees first |

## Predictions

- The outcome is within 2 SEs of zero again, with an interval about 0.7 as wide as the
  second run's.

## What it can't show

As before: it's observational, and drafters who chose the safe colors differ from
those who didn't in ways the controls may miss.
