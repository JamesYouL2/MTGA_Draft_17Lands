Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| no-iwd-premium | +0.0005 (0.0003), +1.6 | +0.036 (0.143), +0.3 | no objection | +0.0006 / -0.286 | 0.59% | -0.07 | 70.2% to 70.3% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| no-iwd-premium | +0.0004 (0.0003), +1.7 | no objection | +0.039 (0.067), +0.6 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**no-iwd-premium** (32000 drafts, 26450 complete events)

- regret slope: r32s1: +0.0008 (0.0007), r32s2: +0.0013 (0.0006), r32s3: +0.0001 (0.0008), r32s4: +0.0008 (0.0006), r32s5: +0.0001 (0.0007), r32s6: +0.0007 (0.0007), r32s7: -0.0007 (0.0007), r32s8: +0.0003 (0.0007). tau 0.0000; phi 0.94 (0.62 to 1.91); corrected SE 0.0002, bootstrap only 0.0002
- swap: r32s1: +0.509 (0.193), r32s2: -0.208 (0.190), r32s3: +0.386 (0.192), r32s4: -0.062 (0.205), r32s5: -0.004 (0.213), r32s6: +0.142 (0.212), r32s7: -0.507 (0.190), r32s8: +0.042 (0.206). tau 0.268; phi 1.68 (1.11 to 3.41); corrected SE 0.118, bootstrap only 0.071
- both on-lane: 32.3% of changes; drafters took base's 44.8%, head's 22.0%
- base on, head off: 8.1% of changes; drafters took base's 46.6%, head's 10.5%
- base off, head on: 30.1% of changes; drafters took base's 23.5%, head's 30.0%
- both off-lane: 29.5% of changes; drafters took base's 33.0%, head's 19.5%

