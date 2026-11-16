# The on-lane bonus, on the fixed harness

Written before any result of this run was seen.

## Why

`experiments/2026-11-08-pick-multipliers` tested removing the on-lane bonus (1.1x for a
card the lane can cast, 1.3x in pack 3 when the pool is short of playables). Removing it
was worse by 0.0017 (SE 0.0009), 1.975 SEs: under the 2 SE bar, so the label was "no
objection", and I recommended keeping it against the label. It is the closest call of
any rule tested.

That run gave the advisor each pool in the dump's column order. The lane's pair differs
from the app's on 9.4% of picks that way
(`experiments/2026-11-15-lane-accuracy`), and this rule depends on the lane more than
any other. The harness now feeds pools in pick order. The app has also changed since:
nine rules have been removed.

## The heads

| head | what changes |
|---|---|
| `no-on-lane` | no bonus at all. The 11-08 patch, unchanged |
| `on-lane-flat` | 1.1x always: no 1.3x when pack 3 is short of playables |

## What runs

The Advisor heads workflow, ten sets, 3,000 drafts a set and salt, held-out ratings,
pools in pick order, base upstream main at `6b6dba9`. Four salts: `""` and `arch2`,
the drafts of the 11-08 run, and `lane1` and `lane2`, which are new.

## How it is read

As in the pick-multipliers protocol, on all four samples together: the change in regret
slope, head minus base, positive is worse for the head.

| verdict | means | here |
|---|---|---|
| keep | worse by 2+ SEs | the bonus (or its 1.3x) stays, and the 11-08 call is confirmed |
| inconclusive | the change plus 2 SEs is above +0.0063 | stays |
| no objection | otherwise | can go |

For `no-on-lane`, between 1.5 and 2 SEs worse I will again recommend keeping it, and
say the question is as open as before. The two old samples and the two new ones are
reported apart.

## Predictions

- `no-on-lane` is worse by 2+ SEs: a truer lane makes the bonus worth more.
- `on-lane-flat` gets "no objection", and changes the top card on under 1% of picks.

## What it can't show

As in the held-out replay. Top-1 favors the base here, since drafters themselves draft
by lane.
