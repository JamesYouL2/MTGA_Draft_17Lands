# The off-color rules, one by one: results

Protocol: `PROTOCOL.md`. Report: `heads.md`. 60,000 drafts from ten sets, 45,409
complete events, held-out ratings, pools in pick order.

## The verdicts

| head | regret slope change (SE) | SEs | top card changes | by the rule |
|---|---|---|---|---|
| `no-bomb-splash` | +0.0020 (0.0008) | +2.6 | 0.28% | **keep** |
| `no-greedy-bomb` | +0.0011 (0.0003) | +3.3 | 0.00% | **keep** |
| `no-premium-removal` | +0.0005 (0.0004) | +1.3 | 0.08% | can go; does almost nothing |
| `no-splashable` | +0.0011 (0.0016) | +0.7 | 0.60% | can go |
| `no-double-pip` | -0.0001 (0.0002) | -0.6 | 0.01% | **can go; does nothing** |
| `no-pack1-pressure` | -0.0001 (0.0015) | -0.1 | 3.19% | **can go** |
| `no-gold-pressure` | -0.0001 (0.0011) | -0.1 | 2.38% | can go (part of the one above) |

Positive is worse for the head.

- **The bomb splash earns its place.** Removing the three bomb and premium-removal
  splashes together is worse by 2.6 SEs, in both samples.
- **Greedy Bomb Splash never changes the advisor's first choice** (0.00% of picks),
  yet removing it is worse by 3.3 SEs. The measure counts how far below the top the
  drafter's own pick was scored, and drafters who took these cards won. So the rule
  ranks them rightly further down the list. Keep.
- **Pack 1's off-color penalty can go.** Removing it changes the top card on 3.19% of
  picks, with no change in the regret slope (-0.0001, SE 0.0015) in either sample. I
  predicted it would be kept. Pack 1 picks 1 to 8 already have no penalty; this is
  picks 9 to 14. The gold-card part is the same story.
- **"Uncastable (Double Pip)" does nothing:** 0.01% of picks. The rules after it give
  such a card 0.05 or 0.01 anyway. This agrees with the single-pip run.
- **"Splashable" and the premium-removal splash can go by the rule,** but both are on
  the worse side (0.7 and 1.3 SEs). They are under the 1.5 SEs at which I said I would
  recommend keeping. I would still take them last, and only after the joint check
  below.

## What follows

Two removals are clean, each its own pull request: the double-pip rule
(`simplify/no-double-pip`) and pack 1's off-color penalty
(`simplify/no-pack1-off-color`).

Nothing here was tested together. Before removing Splashable and the premium-removal
splash as well, one head with all four removals should run, as `no-three` did for the
composition rules.

## The predictions

| | predicted | found |
|---|---|---|
| `no-pack1-pressure` | keep | no objection: wrong |
| `no-splashable` | keep | no objection: wrong |
| `no-greedy-bomb` | under 0.1% of picks | 0.00%: right, though it is a keep |
| `no-gold-pressure`, `no-double-pip`, `no-premium-removal` | no objection | all three: right |
| `no-bomb-splash` | inconclusive | keep: wrong |
