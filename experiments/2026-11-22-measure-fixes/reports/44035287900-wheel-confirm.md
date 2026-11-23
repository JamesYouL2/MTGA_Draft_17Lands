# Advisor heads at `9f26e1c`

Combined over 2 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| wheel-015 | -0.0007 (0.0015), -0.5 | +0.107 (0.304), +0.4 | no objection | +0.0029 / -0.608 | 1.08% | +0.29 | 76.0% to 75.9% |
| wheel-030 | -0.0013 (0.0029), -0.5 | +0.083 (0.235), +0.4 | no objection | +0.0058 / -0.469 | 1.97% | +0.52 | 76.0% to 75.8% |

## The order alone

A second reading, not the decision above. Rank regret (how many cards the advisor ranked above the drafter's pick) and missed top (the share of picks that weren't its top card) read the advisor's order, where SD regret also reads how it spaces its scores within a pack: slope change per SD of each, positive is worse. The unconstrained swap lets a changed pick that the drafter settled with neither top card count for what it does, where the swap above holds it halfway between the two; share is unconstrained over constrained. Order-only reading: the decision's rule on rank regret and the unconstrained swap.

| head | rank regret change | missed top change | event wins per swapped pick, unconstrained | share of constrained | order-only reading | decision above |
|---|---|---|---|---|---|---|
| wheel-015 | +0.000 (0.005), +0.0 | -0.001 (0.007), -0.2 | +0.059 (0.320), +0.2 | 55% | no objection | no objection |
| wheel-030 | +0.000 (0.007), +0.1 | -0.001 (0.010), -0.1 | +0.034 (0.246), +0.1 | 41% | no objection | no objection |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope. The last two columns are the order alone's rank regret and unconstrained swap, read the same way.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs | rank regret change (SE), SEs | unconstrained swap (SE), SEs |
|---|---|---|---|---|---|
| wheel-015 | -0.0007 (0.0002), -3.3 | no objection | +0.105 (0.046), +2.3 | +0.000 (0.001), +0.5 | +0.058 (0.051), +1.1 |
| wheel-030 | -0.0013 (0.0004), -3.2 | no objection | +0.081 (0.033), +2.5 | +0.001 (0.001), +0.5 | +0.033 (0.037), +0.9 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**wheel-015** (60000 drafts, 45494 complete events)

- regret slope: wheelconfirm1: -0.0009 (0.0003), wheelconfirm2: -0.0005 (0.0003). tau 0.0000; phi 0.97 (0.43 to 30.82); corrected SE 0.0002, bootstrap only 0.0002
- swap: wheelconfirm1: +0.127 (0.063), wheelconfirm2: +0.083 (0.070). tau 0.000; phi 0.46 (0.20 to 14.62); corrected SE 0.047, bootstrap only 0.047
- unconstrained swap: wheelconfirm1: +0.080 (0.068), wheelconfirm2: +0.034 (0.072). tau 0.000; phi 0.47 (0.21 to 14.85); corrected SE 0.049, bootstrap only 0.049
- both on-lane: 72.3% of changes; drafters took base's 10.2%, head's 41.0%
- base on, head off: 13.1% of changes; drafters took base's 17.8%, head's 20.7%
- base off, head on: 4.5% of changes; drafters took base's 5.0%, head's 41.2%
- both off-lane: 10.1% of changes; drafters took base's 7.1%, head's 33.9%

**wheel-030** (60000 drafts, 45494 complete events)

- regret slope: wheelconfirm1: -0.0017 (0.0006), wheelconfirm2: -0.0010 (0.0006). tau 0.0000; phi 0.83 (0.37 to 26.61); corrected SE 0.0004, bootstrap only 0.0004
- swap: wheelconfirm1: +0.099 (0.049), wheelconfirm2: +0.063 (0.054). tau 0.000; phi 0.49 (0.22 to 15.52); corrected SE 0.036, bootstrap only 0.036
- unconstrained swap: wheelconfirm1: +0.052 (0.052), wheelconfirm2: +0.014 (0.055). tau 0.000; phi 0.49 (0.22 to 15.70); corrected SE 0.038, bootstrap only 0.038
- both on-lane: 71.6% of changes; drafters took base's 10.6%, head's 40.9%
- base on, head off: 14.0% of changes; drafters took base's 18.1%, head's 20.6%
- base off, head on: 4.4% of changes; drafters took base's 4.8%, head's 42.2%
- both off-lane: 10.1% of changes; drafters took base's 6.5%, head's 33.9%

