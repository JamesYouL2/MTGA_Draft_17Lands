# The bomb bonus and the IWD premium

Written before any result of this run was seen.

## Why

`evaluate_pack()` adds a power bonus to a card rated above the pack: 10 points per SD
of GIH WR above the pack's mean, from half an SD up. A card more than 1 SD up with an
IWD over 4.5 gets 1.15 times that, and the reason "TRUE BOMB (High IWD)".

Both were switched off in October in an exploratory ablation, on ratings that included
the replayed drafts' games, before the held-out harness and the pool-order fix. Neither
has been tested since, and the bonus's size (10 a SD) is hand-set.

## The heads

| head | what changes |
|---|---|
| `no-iwd-premium` | no 1.15x, and no "TRUE BOMB" reason |
| `no-power-bonus` | no power bonus at all |
| `half-power-bonus` | 5 points a SD |
| `double-power-bonus` | 20 points a SD |

## What runs

The Advisor heads workflow: ten sets, 3,000 drafts a set and salt, the salts `""` and
`arch2`, held-out ratings, pools in pick order, base upstream main at `d25398c`.

## How it is read

The pick-multipliers reading, on the change in regret slope, positive worse for the
head.

- `no-iwd-premium` and `no-power-bonus` are removals: "keep" at 2+ SEs worse,
  "inconclusive" if the change plus 2 SEs is above +0.0063, otherwise "no objection"
  and the rule can go. Between 1.5 and 2 SEs worse, I recommend keeping.
- `half-power-bonus` and `double-power-bonus` say whether 10 is the right size. Neither
  is a simplification, so only one better by 2+ SEs would mean a retune, as its own
  test on new drafts.

## Predictions

- `no-power-bonus`: keep, by a wide margin.
- `no-iwd-premium`: no objection, under 1% of picks.
- Half and double are both worse or within 2 SEs: 10 is about right.

## What it can't show

As in the held-out replay. Drafters take bombs whatever an advisor says, so top-1
favors any bonus.
