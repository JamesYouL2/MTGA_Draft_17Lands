# The three open removals, on both measures

Written before any result of this run was seen.

## Why

[The measure-power test](../2026-11-16-measure-power/RESULTS.md) found that the regret
slope misses 20% random noise on card scores, which changes 17% of top picks. Event
wins per swapped pick sees it (3.7 SEs). From then on removals are read on both. Three
removals are proposed and were read on the regret slope only, or on runs where the
second measure was not yet a judge:

| head | the change | where |
|---|---|---|
| `on-lane-flat` | the on-lane bonus is 1.1x throughout, never 1.3x for a short pack 3 | #273, open |
| `pack1` | no off-color penalty in pack 1 | #274, open |
| `no-iwd-premium` | no 1.15x power bonus for high-IWD bombs | fork `simplify/no-iwd-premium`, link handed over |
| `all-three` | the three together | |

Each head is its branch's own diff to `src/`, taken from the fork. `all-three` is the
three applied in turn.

## Already seen, so said here

Earlier runs put numbers on the second measure for two of these, before it qualified
as a judge:

- `pack1`, run 43814769088 (salts `joint1`, `joint2`): event wins per swapped pick
  -0.039 (0.011), 3.5 SEs worse. Regret slope there, read within sets: no loss.
- `no-iwd-premium`, run of the bomb-bonus test: -0.032 (0.051).

So `pack1` comes in under suspicion. This run is a fresh look on new drafts, and its
verdict stands on its own drafts; the earlier one is reported beside it, not pooled.

## What runs

The Advisor heads workflow, base this branch's `src/` (upstream main's advisor), all
19 sets (BLB DFT DMU DSK EOE FDN FIN FRA HOB KTK LTR MSH NEO OTJ SNC SOS TDM TLA TMT),
6,000 drafts a set and salt, salts `both1` and `both2`, not used before. Held-out
ratings, pools in pick order. `heads.py` gives the regret slope change (within-set
z-scores) and event wins per swapped pick; `by_set.py` the four high-share sets
against the other fifteen.

## The decision rule

For each removal head:

| reading | verdict |
|---|---|
| regret slope change worse by 2+ SEs, or event wins per swapped pick worse by 2+ SEs | flagged: the removal is withdrawn (PR closed or link not used) |
| neither | stays proposed |

"Worse" is a positive regret slope change or a negative event wins figure. A measure
whose SE is so wide that it can't flag a change the size of 40% noise (event wins
-0.05 a swapped pick) is reported as "can't judge" for that head. Then the head rests
on the other measure alone, and the write-up says so.

`all-three` is read by the same rule. If it is flagged while no single head is, the
removals are not to be merged together until a larger run says which pair interacts.

## Predictions

- `on-lane-flat` changes about 0.01% of top cards: event wins can't judge it; regret
  slope no objection. Stays.
- `pack1` is flagged on event wins again, about -0.03, 2 to 3 SEs. Withdrawn.
- `no-iwd-premium` changes about 0.5% of top cards: event wins can't judge it; regret
  slope no objection. Stays.
- `all-three` looks like `pack1`.

## What it can't show

As in the held-out replay, and as measure-power says: on 228,000 drafts neither
measure can show that a removal changing under 1% of picks is harmless, only that it
is not large harm.
