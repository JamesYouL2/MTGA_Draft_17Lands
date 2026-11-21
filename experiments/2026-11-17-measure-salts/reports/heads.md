# Advisor heads, run 44122837249, at `61021a0`

Combined over 8 salts. Regret slope change: positive is worse for the head. Event wins per swapped pick: negative is worse. Each figure is estimate (scaled SE), SEs. The scaled SE counts the spread between salts and is widened for few salts (SE times t / 1.96, t on salts - 1 df), so 2 of them is about 95%. Adopt: 2+ better on one measure and not 2 worse on either. Smallest harm: what 2 scaled SEs worse is, the least harm the run could have seen.

| head | regret slope change | event wins per swapped pick | decision | smallest harm, regret / swap | top card changes | top-1 change | on-lane, base to head |
|---|---|---|---|---|---|---|---|
| lane-share-0.10 | -0.0012 (0.0011), -1.1 | +0.034 (0.015), +2.3 | adopt | +0.0022 / -0.031 | 2.19% | +0.01 | 74.6% to 75.4% |
| no-needs-2drops | -0.0003 (0.0002), -1.8 | +0.090 (0.045), +2.0 | adopt | +0.0004 / -0.089 | 0.33% | -0.01 | 74.6% to 74.6% |
| noise20 | +0.0025 (0.0014), +1.8 | -0.037 (0.006), -6.3 | worse (swap) | +0.0027 / -0.012 | 17.33% | -1.84 | 74.6% to 73.8% |
| wheel-0.15 | -0.0004 (0.0001), -2.9 | +0.056 (0.029), +1.9 | adopt | +0.0003 / -0.058 | 1.04% | +0.28 | 74.6% to 74.5% |
| wheel-0.15 against lane-share-0.10 | +0.0008 (0.0011), +0.7 | -0.014 (0.015), -0.9 | no objection | +0.0022 / -0.031 | 3.10% | +0.27 | 75.4% to 74.5% |

## Bootstrap only, over all salts at once

As read before 2026-11-17: these SEs leave out the spread between salts. The verdict is PROTOCOL.md's, on the regret slope.

| head | regret slope change (SE), SEs | verdict | event wins per swapped pick (SE), SEs |
|---|---|---|---|
| lane-share-0.10 | -0.0012 (0.0009), -1.4 | no objection | +0.035 (0.012), +2.8 |
| no-needs-2drops | -0.0003 (0.0002), -2.2 | no objection | +0.093 (0.038), +2.4 |
| noise20 | +0.0026 (0.0011), +2.4 | keep | -0.037 (0.005), -7.7 |
| wheel-0.15 | -0.0004 (0.0001), -3.3 | no objection | +0.058 (0.022), +2.7 |
| wheel-0.15 against lane-share-0.10 | +0.0008 (0.0009), +0.9 | no objection | -0.013 (0.011), -1.2 |

## By salt

Each salt's estimate (bootstrap SE). tau is the SD between salts beyond the bootstrap's; phi = sqrt(Q / (salts - 1)) is how many times the bootstrap SEs the salts spread, with its 95% interval.

**lane-share-0.10** (240000 drafts, 182002 complete events)

- regret slope: ms1: -0.0010 (0.0026), ms2: -0.0015 (0.0026), ms3: -0.0024 (0.0023), ms4: -0.0042 (0.0026), ms5: -0.0034 (0.0028), ms6: +0.0025 (0.0027), ms7: +0.0017 (0.0025), ms8: -0.0013 (0.0026). tau 0.0000; phi 0.88 (0.59 to 1.80); corrected SE 0.0009, bootstrap only 0.0009
- swap: ms1: +0.051 (0.034), ms2: +0.001 (0.036), ms3: +0.001 (0.031), ms4: +0.025 (0.035), ms5: +0.098 (0.035), ms6: +0.003 (0.034), ms7: +0.028 (0.036), ms8: +0.069 (0.032). tau 0.011; phi 1.05 (0.70 to 2.15); corrected SE 0.013, bootstrap only 0.012
- both on-lane: 86.0% of changes; drafters took base's 28.9%, head's 30.3%
- base on, head off: 5.5% of changes; drafters took base's 39.8%, head's 19.1%
- base off, head on: 7.2% of changes; drafters took base's 25.7%, head's 33.6%
- both off-lane: 1.2% of changes; drafters took base's 39.9%, head's 22.7%

**no-needs-2drops** (240000 drafts, 182002 complete events)

- regret slope: ms1: -0.0003 (0.0004), ms2: -0.0005 (0.0004), ms3: -0.0006 (0.0004), ms4: -0.0005 (0.0004), ms5: -0.0001 (0.0004), ms6: -0.0006 (0.0004), ms7: +0.0000 (0.0004), ms8: +0.0001 (0.0004). tau 0.0000; phi 0.68 (0.45 to 1.39); corrected SE 0.0001, bootstrap only 0.0001
- swap: ms1: -0.012 (0.102), ms2: +0.206 (0.115), ms3: +0.061 (0.099), ms4: +0.171 (0.102), ms5: +0.037 (0.104), ms6: +0.155 (0.103), ms7: +0.152 (0.107), ms8: -0.035 (0.109). tau 0.000; phi 0.85 (0.56 to 1.73); corrected SE 0.037, bootstrap only 0.037
- both on-lane: 85.5% of changes; drafters took base's 29.9%, head's 27.5%
- base on, head off: 7.0% of changes; drafters took base's 30.4%, head's 14.9%
- base off, head on: 5.6% of changes; drafters took base's 22.4%, head's 26.8%
- both off-lane: 1.8% of changes; drafters took base's 20.0%, head's 23.4%

**noise20** (240000 drafts, 182002 complete events)

- regret slope: ms1: +0.0070 (0.0031), ms2: -0.0017 (0.0030), ms3: +0.0001 (0.0033), ms4: +0.0074 (0.0033), ms5: +0.0015 (0.0031), ms6: +0.0020 (0.0031), ms7: +0.0008 (0.0032), ms8: +0.0035 (0.0032). tau 0.0006; phi 1.02 (0.67 to 2.07); corrected SE 0.0011, bootstrap only 0.0011
- swap: ms1: -0.056 (0.013), ms2: -0.030 (0.013), ms3: -0.033 (0.014), ms4: -0.037 (0.014), ms5: -0.040 (0.014), ms6: -0.034 (0.014), ms7: -0.015 (0.015), ms8: -0.051 (0.015). tau 0.000; phi 0.92 (0.61 to 1.87); corrected SE 0.005, bootstrap only 0.005
- both on-lane: 56.4% of changes; drafters took base's 37.5%, head's 27.1%
- base on, head off: 14.4% of changes; drafters took base's 46.9%, head's 12.1%
- base off, head on: 10.1% of changes; drafters took base's 17.7%, head's 40.1%
- both off-lane: 19.1% of changes; drafters took base's 26.2%, head's 15.8%

**wheel-0.15** (240000 drafts, 182002 complete events)

- regret slope: ms1: +0.0001 (0.0003), ms2: -0.0008 (0.0003), ms3: -0.0004 (0.0004), ms4: -0.0002 (0.0003), ms5: -0.0003 (0.0003), ms6: -0.0008 (0.0003), ms7: -0.0004 (0.0003), ms8: -0.0005 (0.0003). tau 0.0000; phi 0.90 (0.59 to 1.82); corrected SE 0.0001, bootstrap only 0.0001
- swap: ms1: +0.045 (0.061), ms2: +0.012 (0.072), ms3: +0.040 (0.071), ms4: +0.140 (0.069), ms5: +0.019 (0.068), ms6: +0.157 (0.069), ms7: -0.011 (0.069), ms8: +0.046 (0.069). tau 0.000; phi 0.87 (0.58 to 1.77); corrected SE 0.024, bootstrap only 0.024
- both on-lane: 74.1% of changes; drafters took base's 10.1%, head's 41.2%
- base on, head off: 12.9% of changes; drafters took base's 19.0%, head's 20.4%
- base off, head on: 4.6% of changes; drafters took base's 4.4%, head's 43.4%
- both off-lane: 8.3% of changes; drafters took base's 8.4%, head's 30.8%

**wheel-0.15 against lane-share-0.10** (240000 drafts, 182002 complete events)

- regret slope: ms1: +0.0011 (0.0027), ms2: +0.0007 (0.0026), ms3: +0.0020 (0.0024), ms4: +0.0040 (0.0026), ms5: +0.0031 (0.0028), ms6: -0.0033 (0.0027), ms7: -0.0021 (0.0025), ms8: +0.0007 (0.0026). tau 0.0000; phi 0.92 (0.61 to 1.88); corrected SE 0.0009, bootstrap only 0.0009
- swap: ms1: -0.034 (0.029), ms2: +0.008 (0.032), ms3: +0.006 (0.029), ms4: +0.018 (0.030), ms5: -0.073 (0.030), ms6: +0.036 (0.032), ms7: -0.022 (0.034), ms8: -0.043 (0.030). tau 0.019; phi 1.18 (0.78 to 2.40); corrected SE 0.013, bootstrap only 0.011
- both on-lane: 81.9% of changes; drafters took base's 24.5%, head's 32.9%
- base on, head off: 9.2% of changes; drafters took base's 27.2%, head's 23.2%
- base off, head on: 5.3% of changes; drafters took base's 15.0%, head's 41.5%
- both off-lane: 3.7% of changes; drafters took base's 11.8%, head's 33.1%

