# Advisor heads at `4b5a75d`

Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| lgbm-weak | +0.0269 (0.0060), +4.5 | +0.022 (0.005), +4.6 | worse (regret) | +0.0120 / -0.010 | 37.36% | +7.84 | 75.5% to 82.5% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| lgbm-weak | +0.0272 (0.0048), +5.7 | keep | +0.022 (0.004), +6.0 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**lgbm-weak** (152000 drafts, 117904 complete events)

- regret slope: r36s1: +0.0081 (0.0122), r36s2: +0.0380 (0.0132), r36s3: +0.0118 (0.0133), r36s4: +0.0160 (0.0131), r36s5: +0.0290 (0.0130), r36s6: +0.0348 (0.0139), r36s7: +0.0472 (0.0134), r36s8: +0.0347 (0.0135). tau 0.0051; phi 1.07 (0.71 to 2.18); corrected SE 0.0050, bootstrap only 0.0047
- swap: r36s1: +0.034 (0.010), r36s2: +0.015 (0.010), r36s3: +0.036 (0.010), r36s4: +0.031 (0.010), r36s5: +0.022 (0.012), r36s6: +0.020 (0.011), r36s7: +0.007 (0.010), r36s8: +0.010 (0.011). tau 0.004; phi 1.07 (0.71 to 2.18); corrected SE 0.004, bootstrap only 0.004
- both on-lane: 51.4% of changes; drafters took base's 25.3%, head's 42.3%
- base on, head off: 8.9% of changes; drafters took base's 23.9%, head's 38.7%
- base off, head on: 27.6% of changes; drafters took base's 16.4%, head's 47.4%
- both off-lane: 12.1% of changes; drafters took base's 21.3%, head's 40.9%

