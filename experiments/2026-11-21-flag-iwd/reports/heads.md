# Advisor heads at `ab7d3a8`

Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| no-iwd-premium | -0.0007 (0.0001), -4.7 | +0.048 (0.042), +1.1 | adopt | +0.0003 / -0.084 | 0.56% | -0.04 | 75.0% to 75.1% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| no-iwd-premium | -0.0007 (0.0001), -6.2 | no objection | +0.046 (0.035), +1.3 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**no-iwd-premium** (152000 drafts, 117872 complete events)

- regret slope: r32s1: -0.0006 (0.0003), r32s2: -0.0006 (0.0004), r32s3: -0.0004 (0.0003), r32s4: -0.0006 (0.0004), r32s5: -0.0011 (0.0004), r32s6: -0.0009 (0.0003), r32s7: -0.0004 (0.0003), r32s8: -0.0009 (0.0003). tau 0.0000; phi 0.74 (0.49 to 1.50); corrected SE 0.0001, bootstrap only 0.0001
- swap: r32s1: +0.175 (0.099), r32s2: +0.034 (0.099), r32s3: +0.007 (0.094), r32s4: +0.019 (0.100), r32s5: +0.137 (0.097), r32s6: -0.013 (0.106), r32s7: -0.063 (0.101), r32s8: +0.072 (0.099). tau 0.000; phi 0.79 (0.52 to 1.62); corrected SE 0.035, bootstrap only 0.035
- both on-lane: 35.5% of changes; drafters took base's 45.3%, head's 25.3%
- base on, head off: 6.3% of changes; drafters took base's 49.2%, head's 12.3%
- base off, head on: 27.5% of changes; drafters took base's 18.0%, head's 41.0%
- both off-lane: 30.7% of changes; drafters took base's 28.8%, head's 18.3%

