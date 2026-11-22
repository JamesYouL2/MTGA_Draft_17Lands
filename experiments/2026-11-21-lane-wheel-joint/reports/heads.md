# Advisor heads at `547af95`

Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| lane-share-0.10 | -0.0014 (0.0018), -0.8 | +0.042 (0.027), +1.6 | no objection | +0.0037 / -0.054 | 2.19% | -0.00 | 74.6% to 75.5% |
| lane-wheel | -0.0019 (0.0019), -1.0 | +0.048 (0.023), +2.2 | adopt | +0.0038 / -0.045 | 3.13% | +0.26 | 74.6% to 75.4% |
| wheel-0.15 | -0.0004 (0.0002), -1.7 | +0.086 (0.049), +1.8 | no objection | +0.0005 / -0.098 | 1.03% | +0.28 | 74.6% to 74.5% |
| lane-wheel against lane-share-0.10 | -0.0005 (0.0002), -1.9 | +0.111 (0.050), +2.2 | adopt | +0.0005 / -0.101 | 1.00% | +0.26 | 75.5% to 75.4% |
| lane-wheel against wheel-0.15 | -0.0015 (0.0019), -0.8 | +0.044 (0.027), +1.6 | no objection | +0.0038 / -0.054 | 2.14% | -0.02 | 74.5% to 75.4% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| lane-share-0.10 | -0.0014 (0.0014), -0.9 | no objection | +0.043 (0.020), +2.1 |
| lane-wheel | -0.0018 (0.0015), -1.2 | no objection | +0.050 (0.018), +2.8 |
| wheel-0.15 | -0.0004 (0.0002), -1.9 | no objection | +0.093 (0.041), +2.3 |
| lane-wheel against lane-share-0.10 | -0.0005 (0.0002), -2.2 | no objection | +0.120 (0.042), +2.9 |
| lane-wheel against wheel-0.15 | -0.0014 (0.0015), -1.0 | no objection | +0.045 (0.020), +2.2 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**lane-share-0.10** (80000 drafts, 60823 complete events)

- regret slope: r31s1: +0.0009 (0.0042), r31s2: -0.0000 (0.0044), r31s3: +0.0063 (0.0044), r31s4: -0.0042 (0.0046), r31s5: -0.0020 (0.0043), r31s6: -0.0091 (0.0044), r31s7: -0.0027 (0.0040), r31s8: -0.0009 (0.0043). tau 0.0005; phi 1.01 (0.67 to 2.05); corrected SE 0.0015, bootstrap only 0.0015
- swap: r31s1: +0.066 (0.062), r31s2: +0.047 (0.062), r31s3: -0.034 (0.065), r31s4: +0.091 (0.061), r31s5: -0.020 (0.060), r31s6: +0.134 (0.064), r31s7: -0.033 (0.061), r31s8: +0.083 (0.059). tau 0.013; phi 1.02 (0.67 to 2.08); corrected SE 0.022, bootstrap only 0.022
- both on-lane: 85.9% of changes; drafters took base's 29.3%, head's 30.1%
- base on, head off: 5.6% of changes; drafters took base's 39.7%, head's 18.3%
- base off, head on: 7.2% of changes; drafters took base's 25.9%, head's 34.2%
- both off-lane: 1.2% of changes; drafters took base's 38.7%, head's 24.5%

**lane-wheel** (80000 drafts, 60823 complete events)

- regret slope: r31s1: +0.0006 (0.0042), r31s2: -0.0002 (0.0045), r31s3: +0.0059 (0.0044), r31s4: -0.0042 (0.0047), r31s5: -0.0021 (0.0044), r31s6: -0.0096 (0.0044), r31s7: -0.0041 (0.0041), r31s8: -0.0018 (0.0044). tau 0.0007; phi 1.01 (0.67 to 2.06); corrected SE 0.0016, bootstrap only 0.0015
- swap: r31s1: +0.053 (0.048), r31s2: +0.073 (0.055), r31s3: +0.023 (0.055), r31s4: +0.060 (0.053), r31s5: +0.013 (0.053), r31s6: +0.082 (0.051), r31s7: -0.021 (0.053), r31s8: +0.102 (0.054). tau 0.000; phi 0.76 (0.50 to 1.55); corrected SE 0.019, bootstrap only 0.019
- both on-lane: 82.2% of changes; drafters took base's 24.1%, head's 33.1%
- base on, head off: 7.8% of changes; drafters took base's 28.9%, head's 19.5%
- base off, head on: 6.4% of changes; drafters took base's 21.2%, head's 36.4%
- both off-lane: 3.6% of changes; drafters took base's 15.8%, head's 30.3%

**wheel-0.15** (80000 drafts, 60823 complete events)

- regret slope: r31s1: -0.0002 (0.0005), r31s2: -0.0001 (0.0006), r31s3: -0.0004 (0.0006), r31s4: -0.0002 (0.0006), r31s5: -0.0000 (0.0006), r31s6: -0.0002 (0.0005), r31s7: -0.0013 (0.0006), r31s8: -0.0009 (0.0006). tau 0.0000; phi 0.72 (0.48 to 1.47); corrected SE 0.0002, bootstrap only 0.0002
- swap: r31s1: +0.085 (0.106), r31s2: +0.172 (0.116), r31s3: +0.239 (0.116), r31s4: -0.032 (0.118), r31s5: +0.137 (0.113), r31s6: -0.060 (0.111), r31s7: +0.010 (0.114), r31s8: +0.156 (0.126). tau 0.000; phi 0.92 (0.61 to 1.88); corrected SE 0.041, bootstrap only 0.041
- both on-lane: 74.3% of changes; drafters took base's 10.2%, head's 40.6%
- base on, head off: 12.8% of changes; drafters took base's 17.6%, head's 21.0%
- base off, head on: 4.4% of changes; drafters took base's 4.1%, head's 42.5%
- both off-lane: 8.5% of changes; drafters took base's 9.0%, head's 31.8%

**lane-wheel against lane-share-0.10** (80000 drafts, 60823 complete events)

- regret slope: r31s1: -0.0002 (0.0005), r31s2: -0.0002 (0.0006), r31s3: -0.0004 (0.0006), r31s4: -0.0001 (0.0006), r31s5: -0.0001 (0.0006), r31s6: -0.0005 (0.0005), r31s7: -0.0015 (0.0006), r31s8: -0.0009 (0.0006). tau 0.0000; phi 0.84 (0.55 to 1.70); corrected SE 0.0002, bootstrap only 0.0002
- swap: r31s1: +0.030 (0.107), r31s2: +0.263 (0.119), r31s3: +0.274 (0.120), r31s4: -0.029 (0.117), r31s5: +0.155 (0.113), r31s6: -0.008 (0.114), r31s7: +0.061 (0.118), r31s8: +0.179 (0.129). tau 0.018; phi 1.01 (0.67 to 2.06); corrected SE 0.042, bootstrap only 0.041
- both on-lane: 74.8% of changes; drafters took base's 10.7%, head's 39.5%
- base on, head off: 12.3% of changes; drafters took base's 17.4%, head's 20.7%
- base off, head on: 4.2% of changes; drafters took base's 3.9%, head's 41.9%
- both off-lane: 8.7% of changes; drafters took base's 8.9%, head's 32.1%

**lane-wheel against wheel-0.15** (80000 drafts, 60823 complete events)

- regret slope: r31s1: +0.0009 (0.0042), r31s2: -0.0000 (0.0044), r31s3: +0.0063 (0.0044), r31s4: -0.0041 (0.0046), r31s5: -0.0020 (0.0043), r31s6: -0.0093 (0.0044), r31s7: -0.0028 (0.0040), r31s8: -0.0009 (0.0043). tau 0.0009; phi 1.02 (0.68 to 2.08); corrected SE 0.0016, bootstrap only 0.0015
- swap: r31s1: +0.049 (0.061), r31s2: +0.059 (0.063), r31s3: -0.023 (0.066), r31s4: +0.085 (0.062), r31s5: -0.026 (0.060), r31s6: +0.153 (0.065), r31s7: -0.024 (0.062), r31s8: +0.080 (0.059). tau 0.013; phi 1.02 (0.67 to 2.08); corrected SE 0.022, bootstrap only 0.022
- both on-lane: 85.6% of changes; drafters took base's 30.0%, head's 29.9%
- base on, head off: 5.7% of changes; drafters took base's 40.2%, head's 18.5%
- base off, head on: 7.4% of changes; drafters took base's 26.1%, head's 34.5%
- both off-lane: 1.2% of changes; drafters took base's 38.5%, head's 24.3%

