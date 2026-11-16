# The pending advisor changes, together

Written before any result of this run was seen.

## Why

Three changes to the advisor are proposed, each tested alone against upstream main:

- `flag`: off-color multipliers at their square root from a 30% three-color share
  (`feat/three-color-off-color`, not yet opened);
- `pack1`: no off-color penalty in pack 1 (#274, open);
- `on-lane-flat`: the on-lane bonus is 1.1x throughout (#273, open).

They touch the same few lines. In a three-color set the flag was softening the pack-1
penalty that `pack1` removes, so the two were never tested as they would ship.

What has merged since the experiments' base (#268 to #272) is the harness fix, two deck
builder changes and two write-ups. None of it changes the advisor's picks, so there is
nothing of it for this harness to re-check.

## The heads

| head | what it has |
|---|---|
| `flag`, `pack1`, `on-lane-flat` | each alone, as tested before |
| `proposed` | all three |
| `proposed-more` | all three, and no "Splashable" and no premium-removal splash, the two removals that passed their rule on the worse side |

## What runs

The Advisor heads workflow on all 19 sets: 6,000 drafts a set and salt, the salts
`joint1` and `joint2`, new. Held-out ratings, pools in pick order, base upstream main
at `d25398c`.

## How it is read

From `heads.py` on all sets and `by_set.py` for the four sets over a 30% share and the
other fifteen. Positive is worse for the head.

| `proposed` | verdict |
|---|---|
| not worse by 2+ SEs on all sets or in the fifteen, and better by 2+ SEs in the four | the three hold together |
| worse by 2+ SEs anywhere | they don't. The single heads say which, and that pull request is held or reverted |
| not better by 2+ SEs in the four | the flag has lost its gain alongside `pack1`; the flag is held until that is understood |

`proposed-more` against `proposed`: if it is worse by more than 2 of its own SEs on
all sets, Splashable and the premium-removal splash stay. Otherwise they can go.

If the error-bars test (`experiments/2026-11-16-error-bars`) finds the SEs too small,
these bars are widened by its factor before the verdict.

## Predictions

- `proposed` holds: within 2 SEs on all sets, better by 2+ SEs in the four.
- In the four, `proposed` is a little less good than `flag` alone.
- `proposed-more` is within 2 SEs of `proposed`.

## What it can't show

As in the held-out replay.
