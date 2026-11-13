# Should Needs Fixing be bigger than 1.4x?

Written before any result of this run was seen, and after the needs sweep
(`experiments/2026-11-12-needs-sweep`), which is why it exists. There, every value
below 1.4 read worse than 1.4, in order: +0.0005 at 1.3, +0.0012 at 1.2, +0.0022 at
1.1 and +0.0034 at 1.0. The trend doesn't stop at the base, and nothing above it was
run.

## The heads

Each changes the one number in `_calculate_composition_bonus()`: 1.5, 1.6, 1.8 and 2.0
in place of 1.4. The patches are in [heads/](heads/).

## What runs

The Advisor heads workflow, as in the needs sweep: ten sets, 3,000 drafts a set, the
salts `""` and `arch2`, on held-out ratings only, and the same base (`main` at
`03f5007` with #265 and #266).

## How it is read

The measure is the change in regret slope, head minus base, pooled over both samples,
with a paired bootstrap SE. Negative is better for the head.

1. A head **qualifies** if it is better than the base by 2 SEs or more and both samples
   agree in sign.
2. If any qualifies, the app takes the smallest qualifying value, unless a larger one
   is better than it by more than its own 2 SEs against the base would cover. In
   practice: the smallest, unless the numbers plainly keep improving.
3. Otherwise nothing changes.

The smallest is preferred because the rule also boosts basic lands, which drafters
almost never take, so the replay barely sees what a big multiplier does to them. A
larger value is a larger bet on something unmeasured.

These drafts are the ones the needs sweep used, so this isn't fresh data: the trend
that prompted the run and its result share noise. If a value qualifies, it should be
confirmed on other drafts (another salt) before a PR.

## Predictions

- 1.5 and 1.6 read better than the base, by less than 2 SEs each.
- The slope turns back up by 2.0.
- Top-1 falls at every value, by more as the multiplier grows.

## What it can't show

As before: slopes are associations among drafters who chose freely, and regret says
whether drafters who followed an advisor won, not what its users would win. Event wins
per swapped pick disagreed with the slope throughout the needs sweep, and that isn't
explained.
