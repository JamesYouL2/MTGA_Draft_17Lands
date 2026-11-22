# Advisor heads at `f816b13`

Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| gihwr-only | +0.1089 (0.0099), +11.0 | -0.050 (0.006), -8.9 | worse (regret, swap) | +0.0198 / -0.011 | 40.45% | -10.18 | 74.6% to 45.8% |
| lane-share-0.10 | -0.0047 (0.0020), -2.3 | +0.056 (0.028), +2.0 | adopt | +0.0040 / -0.055 | 2.18% | +0.01 | 74.6% to 75.4% |
| no-needs-2drops | -0.0002 (0.0003), -0.5 | -0.031 (0.096), -0.3 | no objection | +0.0006 / -0.193 | 0.33% | -0.01 | 74.6% to 74.6% |
| noise10 | +0.0003 (0.0012), +0.3 | -0.022 (0.014), -1.6 | no objection | +0.0023 / -0.028 | 9.15% | -0.49 | 74.6% to 74.5% |
| noise20-a | +0.0022 (0.0022), +1.0 | -0.038 (0.010), -3.7 | worse (swap) | +0.0044 / -0.021 | 17.30% | -1.89 | 74.6% to 73.8% |
| noise40-a | +0.0132 (0.0041), +3.3 | -0.054 (0.008), -6.7 | worse (regret, swap) | +0.0081 / -0.016 | 29.49% | -4.82 | 74.6% to 73.0% |
| random-a | +0.2294 (0.0144), +15.9 | -0.076 (0.004), -17.8 | worse (regret, swap) | +0.0288 / -0.008 | 80.69% | -27.56 | 74.6% to 46.2% |
| scale | -0.0040 (0.0021), -1.9 | -0.067 (0.095), -0.7 | no objection | +0.0042 / -0.190 | 0.16% | -0.04 | 74.6% to 74.6% |
| wheel-0.15 | -0.0007 (0.0002), -2.9 | +0.097 (0.050), +2.0 | adopt | +0.0005 / -0.099 | 1.04% | +0.28 | 74.6% to 74.5% |
| worst | +0.4593 (0.0193), +23.8 | -0.077 (0.004), -19.8 | worse (regret, swap) | +0.0385 / -0.008 | 96.73% | -37.61 | 74.6% to 25.5% |

## Simulated draft deck win rate

The advisor drafts each draft's packs itself; the first deck Suggest Deck builds from its pool, as an expected game win rate. Head minus base in win rate points, combined over salts like the others: estimate (scaled SE), SEs. Positive is better for the head. Not part of the decision: it grades advisors by the deck score's own beliefs (experiments/2026-11-21-simulated-draft).

| head | simulated deck win rate change | SD per draft | drafts | decks changed |
|---|---|---|---|---|
| gihwr-only | -0.049 (0.010), -5.0 | 2.288 | 79904 | 99.9% |
| lane-share-0.10 | +0.095 (0.002), +40.3 | 0.516 | 79904 | 27.8% |
| no-needs-2drops | -0.000 (0.000), -0.3 | 0.095 | 79904 | 3.3% |
| noise10 | -0.148 (0.008), -19.2 | 1.247 | 79904 | 93.7% |
| noise20-a | -0.522 (0.009), -56.1 | 1.551 | 79904 | 99.3% |
| noise40-a | -1.420 (0.012), -120.9 | 1.909 | 79904 | 99.9% |
| random-a | -12.306 (0.018), -685.2 | 3.720 | 79904 | 100.0% |
| scale | +0.000 (0.001), +0.3 | 0.128 | 79904 | 2.0% |
| wheel-0.15 | +0.053 (0.002), +22.4 | 0.438 | 79904 | 27.3% |
| worst | -21.240 (0.021), -1013.1 | 4.798 | 79904 | 100.0% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| gihwr-only | +0.1102 (0.0092), +12.0 | keep | -0.050 (0.005), -9.8 |
| lane-share-0.10 | -0.0045 (0.0015), -3.0 | no objection | +0.057 (0.022), +2.6 |
| no-needs-2drops | -0.0002 (0.0003), -0.7 | no objection | -0.034 (0.061), -0.6 |
| noise10 | +0.0004 (0.0010), +0.4 | no objection | -0.021 (0.012), -1.8 |
| noise20-a | +0.0023 (0.0019), +1.2 | no objection | -0.038 (0.009), -4.3 |
| noise40-a | +0.0134 (0.0038), +3.6 | keep | -0.054 (0.007), -8.2 |
| random-a | +0.2297 (0.0131), +17.6 | keep | -0.076 (0.004), -20.4 |
| scale | -0.0040 (0.0015), -2.8 | no objection | -0.068 (0.083), -0.8 |
| wheel-0.15 | -0.0007 (0.0002), -3.1 | no objection | +0.102 (0.040), +2.6 |
| worst | +0.4589 (0.0173), +26.6 | keep | -0.076 (0.003), -22.7 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**gihwr-only** (80000 drafts, 60667 complete events)

- regret slope: r33s1: +0.1490 (0.0244), r33s2: +0.1251 (0.0226), r33s3: +0.1149 (0.0228), r33s4: +0.0980 (0.0245), r33s5: +0.1122 (0.0233), r33s6: +0.0762 (0.0212), r33s7: +0.1038 (0.0238), r33s8: +0.0996 (0.0233). tau 0.0000; phi 0.93 (0.62 to 1.90); corrected SE 0.0082, bootstrap only 0.0082
- swap: r33s1: -0.058 (0.013), r33s2: -0.063 (0.012), r33s3: -0.058 (0.015), r33s4: -0.042 (0.013), r33s5: -0.051 (0.013), r33s6: -0.038 (0.013), r33s7: -0.051 (0.014), r33s8: -0.040 (0.013). tau 0.000; phi 0.72 (0.48 to 1.47); corrected SE 0.005, bootstrap only 0.005
- both on-lane: 18.6% of changes; drafters took base's 31.6%, head's 36.2%
- base on, head off: 72.6% of changes; drafters took base's 45.3%, head's 9.4%
- base off, head on: 1.6% of changes; drafters took base's 15.9%, head's 43.7%
- both off-lane: 7.2% of changes; drafters took base's 26.4%, head's 21.0%

**lane-share-0.10** (80000 drafts, 60667 complete events)

- regret slope: r33s1: -0.0085 (0.0040), r33s2: -0.0032 (0.0047), r33s3: +0.0010 (0.0044), r33s4: -0.0040 (0.0046), r33s5: +0.0013 (0.0045), r33s6: -0.0079 (0.0051), r33s7: -0.0117 (0.0040), r33s8: -0.0028 (0.0041). tau 0.0018; phi 1.08 (0.71 to 2.19); corrected SE 0.0017, bootstrap only 0.0015
- swap: r33s1: +0.048 (0.060), r33s2: +0.122 (0.068), r33s3: -0.019 (0.061), r33s4: +0.094 (0.057), r33s5: +0.005 (0.058), r33s6: +0.134 (0.064), r33s7: +0.106 (0.054), r33s8: -0.032 (0.058). tau 0.026; phi 1.09 (0.72 to 2.22); corrected SE 0.023, bootstrap only 0.021
- both on-lane: 85.8% of changes; drafters took base's 29.0%, head's 30.2%
- base on, head off: 5.6% of changes; drafters took base's 39.3%, head's 18.9%
- base off, head on: 7.3% of changes; drafters took base's 25.1%, head's 34.0%
- both off-lane: 1.3% of changes; drafters took base's 39.5%, head's 23.6%

**no-needs-2drops** (80000 drafts, 60667 complete events)

- regret slope: r33s1: -0.0005 (0.0007), r33s2: +0.0002 (0.0008), r33s3: -0.0010 (0.0008), r33s4: -0.0001 (0.0007), r33s5: +0.0005 (0.0007), r33s6: +0.0002 (0.0007), r33s7: +0.0002 (0.0007), r33s8: -0.0009 (0.0007). tau 0.0000; phi 0.76 (0.50 to 1.55); corrected SE 0.0003, bootstrap only 0.0003
- swap: r33s1: +0.252 (0.169), r33s2: -0.143 (0.199), r33s3: +0.102 (0.167), r33s4: -0.257 (0.176), r33s5: -0.201 (0.154), r33s6: -0.248 (0.154), r33s7: -0.056 (0.170), r33s8: +0.293 (0.161). tau 0.151; phi 1.35 (0.89 to 2.74); corrected SE 0.080, bootstrap only 0.059
- both on-lane: 85.4% of changes; drafters took base's 29.9%, head's 27.3%
- base on, head off: 7.4% of changes; drafters took base's 30.2%, head's 17.4%
- base off, head on: 5.5% of changes; drafters took base's 25.2%, head's 25.9%
- both off-lane: 1.7% of changes; drafters took base's 19.5%, head's 26.4%

**noise10** (80000 drafts, 60667 complete events)

- regret slope: r33s1: -0.0000 (0.0028), r33s2: -0.0003 (0.0027), r33s3: -0.0008 (0.0028), r33s4: -0.0031 (0.0027), r33s5: +0.0005 (0.0027), r33s6: +0.0024 (0.0025), r33s7: +0.0034 (0.0028), r33s8: +0.0006 (0.0029). tau 0.0000; phi 0.74 (0.49 to 1.50); corrected SE 0.0010, bootstrap only 0.0010
- swap: r33s1: -0.022 (0.034), r33s2: +0.037 (0.034), r33s3: -0.047 (0.031), r33s4: +0.019 (0.031), r33s5: -0.043 (0.031), r33s6: -0.056 (0.033), r33s7: -0.031 (0.031), r33s8: -0.028 (0.033). tau 0.005; phi 1.01 (0.67 to 2.06); corrected SE 0.011, bootstrap only 0.011
- both on-lane: 56.6% of changes; drafters took base's 34.9%, head's 29.2%
- base on, head off: 12.6% of changes; drafters took base's 45.3%, head's 13.4%
- base off, head on: 11.8% of changes; drafters took base's 16.1%, head's 41.2%
- both off-lane: 19.0% of changes; drafters took base's 23.5%, head's 17.8%

**noise20-a** (80000 drafts, 60667 complete events)

- regret slope: r33s1: +0.0026 (0.0057), r33s2: +0.0000 (0.0046), r33s3: +0.0017 (0.0052), r33s4: +0.0050 (0.0053), r33s5: +0.0033 (0.0055), r33s6: +0.0054 (0.0050), r33s7: +0.0092 (0.0053), r33s8: -0.0082 (0.0051). tau 0.0000; phi 0.99 (0.65 to 2.02); corrected SE 0.0018, bootstrap only 0.0018
- swap: r33s1: -0.013 (0.025), r33s2: -0.057 (0.023), r33s3: -0.045 (0.024), r33s4: -0.027 (0.024), r33s5: -0.043 (0.023), r33s6: -0.078 (0.025), r33s7: -0.027 (0.025), r33s8: -0.010 (0.025). tau 0.000; phi 0.93 (0.62 to 1.90); corrected SE 0.009, bootstrap only 0.009
- both on-lane: 56.5% of changes; drafters took base's 37.7%, head's 27.0%
- base on, head off: 14.3% of changes; drafters took base's 47.3%, head's 11.9%
- base off, head on: 10.0% of changes; drafters took base's 17.8%, head's 40.0%
- both off-lane: 19.1% of changes; drafters took base's 26.3%, head's 15.6%

**noise40-a** (80000 drafts, 60667 complete events)

- regret slope: r33s1: +0.0127 (0.0099), r33s2: +0.0214 (0.0092), r33s3: +0.0122 (0.0094), r33s4: +0.0153 (0.0098), r33s5: +0.0046 (0.0098), r33s6: +0.0183 (0.0094), r33s7: +0.0230 (0.0102), r33s8: +0.0006 (0.0088). tau 0.0000; phi 0.83 (0.55 to 1.70); corrected SE 0.0034, bootstrap only 0.0034
- swap: r33s1: -0.021 (0.018), r33s2: -0.068 (0.017), r33s3: -0.048 (0.017), r33s4: -0.050 (0.017), r33s5: -0.048 (0.017), r33s6: -0.087 (0.018), r33s7: -0.062 (0.019), r33s8: -0.050 (0.019). tau 0.007; phi 1.08 (0.72 to 2.20); corrected SE 0.007, bootstrap only 0.006
- both on-lane: 57.2% of changes; drafters took base's 40.9%, head's 24.3%
- base on, head off: 15.1% of changes; drafters took base's 50.0%, head's 11.1%
- base off, head on: 9.7% of changes; drafters took base's 19.6%, head's 37.6%
- both off-lane: 18.0% of changes; drafters took base's 29.5%, head's 14.4%

**random-a** (80000 drafts, 60667 complete events)

- regret slope: r33s1: +0.2303 (0.0350), r33s2: +0.2209 (0.0321), r33s3: +0.2612 (0.0333), r33s4: +0.2245 (0.0326), r33s5: +0.2007 (0.0320), r33s6: +0.1984 (0.0347), r33s7: +0.2689 (0.0350), r33s8: +0.2364 (0.0360). tau 0.0000; phi 0.75 (0.49 to 1.52); corrected SE 0.0119, bootstrap only 0.0119
- swap: r33s1: -0.070 (0.010), r33s2: -0.080 (0.010), r33s3: -0.084 (0.009), r33s4: -0.068 (0.009), r33s5: -0.075 (0.010), r33s6: -0.074 (0.010), r33s7: -0.077 (0.011), r33s8: -0.076 (0.011). tau 0.000; phi 0.54 (0.36 to 1.10); corrected SE 0.004, bootstrap only 0.004
- both on-lane: 31.9% of changes; drafters took base's 47.1%, head's 15.7%
- base on, head off: 43.4% of changes; drafters took base's 52.0%, head's 4.3%
- base off, head on: 8.3% of changes; drafters took base's 23.0%, head's 25.9%
- both off-lane: 16.3% of changes; drafters took base's 32.5%, head's 10.0%

**scale** (80000 drafts, 60667 complete events)

- regret slope: r33s1: -0.0014 (0.0040), r33s2: +0.0050 (0.0039), r33s3: -0.0038 (0.0036), r33s4: -0.0105 (0.0037), r33s5: -0.0063 (0.0041), r33s6: -0.0042 (0.0041), r33s7: -0.0092 (0.0039), r33s8: -0.0019 (0.0038). tau 0.0031; phi 1.28 (0.84 to 2.60); corrected SE 0.0017, bootstrap only 0.0014
- swap: r33s1: -0.037 (0.216), r33s2: -0.167 (0.230), r33s3: -0.007 (0.219), r33s4: +0.151 (0.220), r33s5: -0.115 (0.239), r33s6: -0.112 (0.201), r33s7: -0.076 (0.242), r33s8: -0.190 (0.224). tau 0.000; phi 0.49 (0.32 to 0.99); corrected SE 0.079, bootstrap only 0.079
- both on-lane: 29.6% of changes; drafters took base's 35.1%, head's 30.0%
- base on, head off: 8.1% of changes; drafters took base's 52.2%, head's 15.2%
- base off, head on: 17.5% of changes; drafters took base's 61.8%, head's 21.5%
- both off-lane: 44.8% of changes; drafters took base's 57.4%, head's 22.6%

**wheel-0.15** (80000 drafts, 60667 complete events)

- regret slope: r33s1: -0.0010 (0.0006), r33s2: +0.0001 (0.0006), r33s3: -0.0002 (0.0005), r33s4: -0.0015 (0.0005), r33s5: -0.0011 (0.0006), r33s6: -0.0004 (0.0006), r33s7: -0.0007 (0.0006), r33s8: -0.0006 (0.0006). tau 0.0000; phi 0.92 (0.61 to 1.88); corrected SE 0.0002, bootstrap only 0.0002
- swap: r33s1: +0.016 (0.116), r33s2: +0.006 (0.129), r33s3: +0.240 (0.119), r33s4: +0.057 (0.107), r33s5: +0.173 (0.122), r33s6: +0.165 (0.117), r33s7: +0.141 (0.121), r33s8: +0.009 (0.104). tau 0.000; phi 0.77 (0.51 to 1.57); corrected SE 0.041, bootstrap only 0.041
- both on-lane: 74.8% of changes; drafters took base's 10.1%, head's 40.7%
- base on, head off: 12.6% of changes; drafters took base's 18.5%, head's 21.0%
- base off, head on: 4.4% of changes; drafters took base's 4.6%, head's 43.8%
- both off-lane: 8.2% of changes; drafters took base's 9.6%, head's 30.8%

**worst** (80000 drafts, 60667 complete events)

- regret slope: r33s1: +0.4720 (0.0462), r33s2: +0.5098 (0.0454), r33s3: +0.4941 (0.0434), r33s4: +0.4418 (0.0431), r33s5: +0.4149 (0.0474), r33s6: +0.4377 (0.0429), r33s7: +0.4575 (0.0465), r33s8: +0.4433 (0.0476). tau 0.0000; phi 0.69 (0.46 to 1.41); corrected SE 0.0160, bootstrap only 0.0160
- swap: r33s1: -0.077 (0.009), r33s2: -0.085 (0.009), r33s3: -0.084 (0.009), r33s4: -0.070 (0.009), r33s5: -0.074 (0.009), r33s6: -0.077 (0.009), r33s7: -0.072 (0.010), r33s8: -0.071 (0.010). tau 0.000; phi 0.63 (0.42 to 1.29); corrected SE 0.003, bootstrap only 0.003
- both on-lane: 16.9% of changes; drafters took base's 50.2%, head's 12.6%
- base on, head off: 58.4% of changes; drafters took base's 51.5%, head's 3.2%
- base off, head on: 7.6% of changes; drafters took base's 24.3%, head's 19.7%
- both off-lane: 17.2% of changes; drafters took base's 33.0%, head's 9.4%

