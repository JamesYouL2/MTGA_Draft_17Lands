# Do the off-color rules earn their place, one by one?

Written before any result of this run was seen.

## Why

`_calculate_castability_v5()` in `src/advisor/engine.py` decides what an off-color card
costs. It is the largest block of hand-set rules left in the advisor, and none of its
branches has been tested alone. The off-color tests of 2026-11-15 moved all of its
multipliers together. Each branch is a rule to explain and maintain.

## The heads

Each removes one branch. A card that loses it falls through to the rules after it, as
it would in the app. Patches in [heads/](heads/).

| head | what it removes | the card then gets |
|---|---|---|
| `no-pack1-pressure` | pack 1's off-color penalty: none for picks 1 to 8, then 0.05 a pick down to 0.7 at pick 14; gold cards 0.2 lower | no penalty in pack 1 |
| `no-gold-pressure` | the extra 0.2 for an off-color gold card in pack 1 | the penalty of any off-color card |
| `no-double-pip` | "Uncastable (Double Pip)": 0.01 for two or more off-color pips from pack 2, with under two fixing cards | the later rules: usually 0.05 in pack 2, 0.01 in pack 3 |
| `no-bomb-splash` | "Bomb Splash", "Premium Removal Splash" (0.45, 0.35 in pack 3) and "Greedy Bomb Splash" (0.30) | "Splashable" 0.3 with fixing for its color, else 0.05 or 0.01 |
| `no-premium-removal` | the splash for removal 1 SD above the pack; bombs keep theirs | the same |
| `no-greedy-bomb` | "Greedy Bomb Splash": 0.30 for a two-pip bomb of mana value 5+ with four fixing cards | 0.05 or 0.01 |
| `no-splashable` | "Splashable": 0.3 for one off-color pip with fixing for it | 0.05 or 0.01 |

`no-premium-removal` and `no-greedy-bomb` are parts of `no-bomb-splash`.

## What runs

The Advisor heads workflow: ten sets, 3,000 drafts a set and salt, the salts `""` and
`arch2`, held-out ratings, pools in pick order, base upstream main at `6b6dba9`.

## How it is read

As in the pick-multipliers protocol, unchanged: the change in regret slope, head minus
base, positive is worse for the head.

1. **Keep:** worse by 2+ SEs.
2. **Inconclusive:** otherwise, if the change plus 2 SEs is above +0.0063. Stays.
3. **No objection:** otherwise. The branch can go.

A head better by 2+ SEs is "no objection" with a stronger case. A branch that changes
the top card on under 0.1% of picks is reported as doing nothing, whatever its label.
Between 1.5 and 2 SEs worse, I will recommend keeping, as before. No correction for
seven heads: a false "keep" leaves a rule in place.

If `no-bomb-splash` gets "no objection", it decides for its two parts as well.

## Predictions

- `no-pack1-pressure`: keep. It is the rule that stops early drift.
- `no-splashable`: keep.
- `no-greedy-bomb`: changes under 0.1% of picks.
- `no-gold-pressure`, `no-double-pip`, `no-premium-removal`: no objection.
- `no-bomb-splash`: inconclusive.

## What it can't show

As in the held-out replay. Splashing bombs is rare and matters in few picks, so a rule
can be right and too rare for the replay to see.
