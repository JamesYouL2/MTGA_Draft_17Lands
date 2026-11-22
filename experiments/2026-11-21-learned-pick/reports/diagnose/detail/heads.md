# Advisor heads at `4b5a75d`

Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| lgbm-strong-noalsa | +0.0162 (0.0052), +3.1 | +0.031 (0.005), +6.5 | worse (regret) | +0.0104 / -0.009 | 33.97% | +7.77 | 75.5% to 80.6% |

## Simulated draft deck win rate

The advisor drafts each draft's packs itself; the first deck Suggest Deck builds from its pool, as an expected game win rate. Head minus base in win rate points, combined over salts like the others: estimate (scaled SE), SEs. Positive is better for the head. Not part of the decision: it grades advisors by the deck score's own beliefs (experiments/2026-11-21-simulated-draft).

| head | simulated deck win rate change | SD per draft | drafts | decks changed |
|---|---|---|---|---|
| lgbm-strong-noalsa | -0.158 (0.006), -25.6 | 1.964 | 151395 | 99.4% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| lgbm-strong-noalsa | +0.0165 (0.0044), +3.8 | keep | +0.031 (0.004), +8.1 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**lgbm-strong-noalsa** (152000 drafts, 117904 complete events)

- regret slope: r36s1: -0.0001 (0.0113), r36s2: +0.0234 (0.0118), r36s3: +0.0018 (0.0122), r36s4: +0.0140 (0.0125), r36s5: +0.0204 (0.0120), r36s6: +0.0237 (0.0128), r36s7: +0.0336 (0.0124), r36s8: +0.0163 (0.0125). tau 0.0000; phi 0.95 (0.63 to 1.93); corrected SE 0.0043, bootstrap only 0.0043
- swap: r36s1: +0.041 (0.011), r36s2: +0.028 (0.010), r36s3: +0.047 (0.011), r36s4: +0.034 (0.011), r36s5: +0.031 (0.012), r36s6: +0.023 (0.012), r36s7: +0.019 (0.011), r36s8: +0.022 (0.011). tau 0.000; phi 0.87 (0.58 to 1.77); corrected SE 0.004, bootstrap only 0.004
- both on-lane: 49.8% of changes; drafters took base's 24.3%, head's 43.6%
- base on, head off: 11.4% of changes; drafters took base's 24.5%, head's 37.1%
- base off, head on: 26.4% of changes; drafters took base's 14.8%, head's 49.5%
- both off-lane: 12.4% of changes; drafters took base's 20.1%, head's 41.6%

