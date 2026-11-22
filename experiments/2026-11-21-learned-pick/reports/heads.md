# Advisor heads at `da02bd1`

Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| gihwr-only | +0.0973 (0.0070), +13.8 | -0.050 (0.004), -11.9 | worse (regret, swap) | +0.0141 / -0.008 | 40.68% | -9.84 | 75.5% to 46.6% |
| lgbm-strong | +0.0305 (0.0065), +4.7 | +0.034 (0.004), +7.7 | worse (regret) | +0.0129 / -0.009 | 40.28% | +13.69 | 75.5% to 79.2% |
| lgbm-strong-noalsa | +0.0089 (0.0053), +1.7 | +0.037 (0.005), +7.7 | adopt | +0.0107 / -0.010 | 33.90% | +7.75 | 75.5% to 80.6% |
| lgbm-wins | +0.0327 (0.0067), +4.9 | +0.028 (0.004), +7.0 | worse (regret) | +0.0135 / -0.008 | 43.10% | +14.01 | 75.5% to 80.1% |
| logit-simple | +0.0145 (0.0044), +3.3 | +0.022 (0.008), +2.6 | worse (regret) | +0.0088 / -0.016 | 22.45% | +1.36 | 75.5% to 74.5% |

## Simulated draft deck win rate

The advisor drafts each draft's packs itself; the first deck Suggest Deck builds from its pool, as an expected game win rate. Head minus base in win rate points, combined over salts like the others: estimate (scaled SE), SEs. Positive is better for the head. Not part of the decision: it grades advisors by the deck score's own beliefs (experiments/2026-11-21-simulated-draft).

| head | simulated deck win rate change | SD per draft | drafts | decks changed |
|---|---|---|---|---|
| gihwr-only | -0.240 (0.008), -31.0 | 2.518 | 151370 | 99.7% |
| lgbm-strong | -0.989 (0.007), -135.2 | 2.370 | 151370 | 99.8% |
| lgbm-strong-noalsa | -0.157 (0.007), -23.1 | 1.976 | 151370 | 99.4% |
| lgbm-wins | -1.503 (0.008), -184.3 | 2.616 | 151370 | 99.9% |
| logit-simple | +0.451 (0.005), +91.5 | 1.539 | 151370 | 95.9% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| gihwr-only | +0.0980 (0.0056), +17.4 | keep | -0.050 (0.003), -14.6 |
| lgbm-strong | +0.0304 (0.0049), +6.2 | keep | +0.034 (0.003), +10.2 |
| lgbm-strong-noalsa | +0.0087 (0.0044), +2.0 | inconclusive | +0.037 (0.004), +9.7 |
| lgbm-wins | +0.0324 (0.0053), +6.1 | keep | +0.028 (0.003), +9.3 |
| logit-simple | +0.0147 (0.0032), +4.7 | keep | +0.022 (0.005), +4.6 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**gihwr-only** (152000 drafts, 117805 complete events)

- regret slope: r35s1: +0.0956 (0.0162), r35s2: +0.0950 (0.0159), r35s3: +0.1104 (0.0179), r35s4: +0.0820 (0.0159), r35s5: +0.0976 (0.0174), r35s6: +0.1095 (0.0173), r35s7: +0.0934 (0.0161), r35s8: +0.0993 (0.0158). tau 0.0000; phi 0.54 (0.36 to 1.10); corrected SE 0.0058, bootstrap only 0.0058
- swap: r35s1: -0.045 (0.009), r35s2: -0.057 (0.009), r35s3: -0.063 (0.010), r35s4: -0.038 (0.009), r35s5: -0.053 (0.010), r35s6: -0.053 (0.010), r35s7: -0.040 (0.010), r35s8: -0.048 (0.010). tau 0.000; phi 0.88 (0.58 to 1.79); corrected SE 0.003, bootstrap only 0.003
- both on-lane: 19.3% of changes; drafters took base's 31.6%, head's 35.9%
- base on, head off: 72.5% of changes; drafters took base's 44.4%, head's 9.6%
- base off, head on: 1.5% of changes; drafters took base's 15.6%, head's 43.4%
- both off-lane: 6.7% of changes; drafters took base's 25.5%, head's 22.0%

**lgbm-strong** (152000 drafts, 117805 complete events)

- regret slope: r35s1: +0.0246 (0.0162), r35s2: +0.0328 (0.0155), r35s3: +0.0333 (0.0136), r35s4: +0.0276 (0.0146), r35s5: +0.0032 (0.0154), r35s6: +0.0401 (0.0148), r35s7: +0.0426 (0.0165), r35s8: +0.0395 (0.0153). tau 0.0000; phi 0.82 (0.54 to 1.67); corrected SE 0.0054, bootstrap only 0.0054
- swap: r35s1: +0.027 (0.010), r35s2: +0.028 (0.010), r35s3: +0.037 (0.009), r35s4: +0.038 (0.011), r35s5: +0.048 (0.011), r35s6: +0.026 (0.011), r35s7: +0.040 (0.010), r35s8: +0.024 (0.010). tau 0.000; phi 0.82 (0.54 to 1.67); corrected SE 0.004, bootstrap only 0.004
- both on-lane: 52.6% of changes; drafters took base's 20.3%, head's 52.3%
- base on, head off: 12.3% of changes; drafters took base's 21.9%, head's 43.6%
- base off, head on: 21.5% of changes; drafters took base's 12.4%, head's 57.8%
- both off-lane: 13.6% of changes; drafters took base's 16.3%, head's 51.3%

**lgbm-strong-noalsa** (152000 drafts, 117805 complete events)

- regret slope: r35s1: +0.0025 (0.0139), r35s2: +0.0028 (0.0136), r35s3: +0.0137 (0.0110), r35s4: +0.0030 (0.0119), r35s5: +0.0088 (0.0122), r35s6: +0.0223 (0.0123), r35s7: +0.0102 (0.0135), r35s8: +0.0042 (0.0127). tau 0.0000; phi 0.56 (0.37 to 1.14); corrected SE 0.0044, bootstrap only 0.0044
- swap: r35s1: +0.028 (0.011), r35s2: +0.042 (0.010), r35s3: +0.039 (0.011), r35s4: +0.043 (0.013), r35s5: +0.051 (0.012), r35s6: +0.022 (0.011), r35s7: +0.042 (0.011), r35s8: +0.028 (0.011). tau 0.000; phi 0.84 (0.56 to 1.72); corrected SE 0.004, bootstrap only 0.004
- both on-lane: 49.8% of changes; drafters took base's 24.3%, head's 43.5%
- base on, head off: 11.4% of changes; drafters took base's 24.4%, head's 37.1%
- base off, head on: 26.5% of changes; drafters took base's 14.8%, head's 49.5%
- both off-lane: 12.3% of changes; drafters took base's 20.0%, head's 41.5%

**lgbm-wins** (152000 drafts, 117805 complete events)

- regret slope: r35s1: +0.0307 (0.0167), r35s2: +0.0378 (0.0163), r35s3: +0.0340 (0.0142), r35s4: +0.0310 (0.0154), r35s5: +0.0009 (0.0165), r35s6: +0.0415 (0.0155), r35s7: +0.0422 (0.0168), r35s8: +0.0413 (0.0156). tau 0.0000; phi 0.83 (0.55 to 1.68); corrected SE 0.0056, bootstrap only 0.0056
- swap: r35s1: +0.015 (0.009), r35s2: +0.024 (0.009), r35s3: +0.030 (0.009), r35s4: +0.030 (0.010), r35s5: +0.043 (0.010), r35s6: +0.024 (0.010), r35s7: +0.036 (0.009), r35s8: +0.020 (0.009). tau 0.000; phi 0.95 (0.63 to 1.93); corrected SE 0.003, bootstrap only 0.003
- both on-lane: 53.7% of changes; drafters took base's 21.4%, head's 51.4%
- base on, head off: 11.1% of changes; drafters took base's 21.7%, head's 44.5%
- base off, head on: 21.7% of changes; drafters took base's 13.5%, head's 56.7%
- both off-lane: 13.5% of changes; drafters took base's 17.5%, head's 51.0%

**logit-simple** (152000 drafts, 117805 complete events)

- regret slope: r35s1: +0.0334 (0.0095), r35s2: +0.0087 (0.0091), r35s3: +0.0123 (0.0092), r35s4: +0.0081 (0.0089), r35s5: +0.0037 (0.0093), r35s6: +0.0219 (0.0093), r35s7: +0.0062 (0.0090), r35s8: +0.0240 (0.0094). tau 0.0047; phi 1.12 (0.74 to 2.29); corrected SE 0.0037, bootstrap only 0.0032
- swap: r35s1: +0.007 (0.013), r35s2: +0.013 (0.013), r35s3: +0.016 (0.014), r35s4: +0.042 (0.014), r35s5: +0.026 (0.014), r35s6: +0.001 (0.014), r35s7: +0.059 (0.014), r35s8: +0.013 (0.015). tau 0.013; phi 1.38 (0.91 to 2.82); corrected SE 0.007, bootstrap only 0.005
- both on-lane: 46.2% of changes; drafters took base's 27.1%, head's 36.9%
- base on, head off: 24.2% of changes; drafters took base's 38.2%, head's 18.2%
- base off, head on: 19.8% of changes; drafters took base's 17.1%, head's 46.8%
- both off-lane: 9.8% of changes; drafters took base's 23.3%, head's 29.0%

