# Advisor heads at `4b5a75d`

Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| gihwr-only | +0.0960 (0.0051), +18.9 | -0.049 (0.002), -20.5 | worse (regret, swap) | +0.0102 / -0.005 | 40.70% | -9.79 | 75.5% to 46.7% |
| lgbm-strong-noalsa | +0.0168 (0.0040), +4.2 | +0.027 (0.003), +10.0 | worse (regret) | +0.0080 / -0.005 | 33.92% | +7.73 | 75.5% to 80.6% |

## Simulated draft deck win rate

The advisor drafts each draft's packs itself; the first deck Suggest Deck builds from its pool, as an expected game win rate. Head minus base in win rate points, combined over salts like the others: estimate (scaled SE), SEs. Positive is better for the head. Not part of the decision: it grades advisors by the deck score's own beliefs (experiments/2026-11-21-simulated-draft).

| head | simulated deck win rate change | SD per draft | drafts | decks changed |
|---|---|---|---|---|
| gihwr-only | -0.236 (0.005), -52.3 | 2.501 | 454118 | 99.7% |
| lgbm-strong-noalsa | -0.155 (0.004), -43.5 | 1.968 | 454118 | 99.4% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| gihwr-only | +0.0966 (0.0032), +30.6 | keep | -0.049 (0.002), -23.7 |
| lgbm-strong-noalsa | +0.0168 (0.0023), +7.2 | keep | +0.027 (0.002), +12.5 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**gihwr-only** (456000 drafts, 353760 complete events)

- regret slope: r36s1: +0.0754 (0.0083), r36s2: +0.1078 (0.0095), r36s3: +0.0975 (0.0099), r36s4: +0.0964 (0.0099), r36s5: +0.1058 (0.0096), r36s6: +0.1081 (0.0091), r36s7: +0.0901 (0.0098), r36s8: +0.0903 (0.0094). tau 0.0073; phi 1.27 (0.84 to 2.58); corrected SE 0.0042, bootstrap only 0.0033
- swap: r36s1: -0.045 (0.005), r36s2: -0.054 (0.005), r36s3: -0.043 (0.005), r36s4: -0.043 (0.005), r36s5: -0.052 (0.006), r36s6: -0.055 (0.005), r36s7: -0.054 (0.005), r36s8: -0.043 (0.006). tau 0.002; phi 1.04 (0.69 to 2.12); corrected SE 0.002, bootstrap only 0.002
- both on-lane: 19.3% of changes; drafters took base's 31.6%, head's 36.0%
- base on, head off: 72.4% of changes; drafters took base's 44.3%, head's 9.7%
- base off, head on: 1.5% of changes; drafters took base's 15.2%, head's 44.3%
- both off-lane: 6.7% of changes; drafters took base's 25.6%, head's 21.9%

**lgbm-strong-noalsa** (456000 drafts, 353760 complete events)

- regret slope: r36s1: +0.0027 (0.0073), r36s2: +0.0321 (0.0069), r36s3: +0.0142 (0.0069), r36s4: +0.0134 (0.0074), r36s5: +0.0209 (0.0067), r36s6: +0.0240 (0.0073), r36s7: +0.0196 (0.0069), r36s8: +0.0071 (0.0069). tau 0.0062; phi 1.34 (0.88 to 2.72); corrected SE 0.0033, bootstrap only 0.0025
- swap: r36s1: +0.034 (0.006), r36s2: +0.018 (0.006), r36s3: +0.027 (0.007), r36s4: +0.031 (0.006), r36s5: +0.026 (0.007), r36s6: +0.031 (0.006), r36s7: +0.020 (0.006), r36s8: +0.030 (0.007). tau 0.000; phi 0.91 (0.60 to 1.85); corrected SE 0.002, bootstrap only 0.002
- both on-lane: 49.8% of changes; drafters took base's 24.3%, head's 43.5%
- base on, head off: 11.4% of changes; drafters took base's 24.5%, head's 37.0%
- base off, head on: 26.5% of changes; drafters took base's 14.8%, head's 49.5%
- both off-lane: 12.4% of changes; drafters took base's 20.2%, head's 41.5%

