# Advisor heads at `8fbdf5e`

More positive is worse for the head. Verdicts follow PROTOCOL.md.

| head | regret slope change (SE) | SEs | verdict | top card changes | top-1 change | on-lane, base to head | event wins per swapped pick (SE) |
|---|---|---|---|---|---|---|---|
| alsa-only | +0.0872 (0.0123) | +7.1 | keep | 62.23% | -6.32 | 76.0% to 45.4% | -0.027 (0.004) |
| gihwr-only | +0.0971 (0.0097) | +10.0 | keep | 43.16% | -10.29 | 76.0% to 45.7% | -0.051 (0.005) |
| noise20-a | +0.0022 (0.0022) | +1.0 | inconclusive | 17.28% | -1.80 | 76.0% to 75.1% | -0.034 (0.009) |
| noise20-b | +0.0007 (0.0021) | +0.3 | no objection | 17.82% | -1.92 | 76.0% to 75.8% | -0.037 (0.010) |
| noise40-a | +0.0106 (0.0039) | +2.7 | keep | 29.38% | -4.67 | 76.0% to 74.2% | -0.049 (0.007) |
| noise40-b | +0.0077 (0.0039) | +2.0 | keep | 30.67% | -5.24 | 76.0% to 75.3% | -0.048 (0.007) |
| random-a | +0.2396 (0.0142) | +16.9 | keep | 80.75% | -27.61 | 76.0% to 46.2% | -0.077 (0.004) |
| random-b | +0.2281 (0.0141) | +16.1 | keep | 78.44% | -27.37 | 76.0% to 48.6% | -0.077 (0.004) |
| worst | +0.4582 (0.0207) | +22.1 | keep | 96.75% | -37.71 | 76.0% to 24.3% | -0.080 (0.004) |

## By sample and kind of change

**alsa-only** (60000 drafts, 45530 complete events). power1: +0.1033 (0.0171), power2: +0.0708 (0.0177)

- both on-lane: 25.9% of changes; drafters took base's 30.2%, head's 44.8%
- base on, head off: 54.3% of changes; drafters took base's 45.6%, head's 12.9%
- base off, head on: 5.1% of changes; drafters took base's 11.7%, head's 56.2%
- both off-lane: 14.7% of changes; drafters took base's 20.6%, head's 31.1%

**gihwr-only** (60000 drafts, 45530 complete events). power1: +0.1086 (0.0130), power2: +0.0857 (0.0140)

- both on-lane: 17.9% of changes; drafters took base's 31.6%, head's 36.4%
- base on, head off: 71.4% of changes; drafters took base's 45.3%, head's 10.0%
- base off, head on: 1.4% of changes; drafters took base's 15.6%, head's 44.2%
- both off-lane: 9.3% of changes; drafters took base's 23.1%, head's 24.4%

**noise20-a** (60000 drafts, 45530 complete events). power1: +0.0013 (0.0031), power2: +0.0032 (0.0031)

- both on-lane: 57.3% of changes; drafters took base's 37.3%, head's 27.3%
- base on, head off: 14.7% of changes; drafters took base's 46.0%, head's 12.5%
- base off, head on: 9.9% of changes; drafters took base's 18.0%, head's 39.1%
- both off-lane: 18.1% of changes; drafters took base's 26.0%, head's 16.0%

**noise20-b** (60000 drafts, 45530 complete events). power1: +0.0007 (0.0032), power2: +0.0007 (0.0032)

- both on-lane: 57.9% of changes; drafters took base's 38.4%, head's 25.9%
- base on, head off: 12.8% of changes; drafters took base's 46.5%, head's 12.5%
- base off, head on: 11.9% of changes; drafters took base's 17.3%, head's 37.4%
- both off-lane: 17.4% of changes; drafters took base's 25.6%, head's 16.8%

**noise40-a** (60000 drafts, 45530 complete events). power1: +0.0094 (0.0056), power2: +0.0118 (0.0050)

- both on-lane: 58.1% of changes; drafters took base's 40.7%, head's 24.4%
- base on, head off: 15.4% of changes; drafters took base's 48.6%, head's 11.6%
- base off, head on: 9.4% of changes; drafters took base's 19.2%, head's 36.9%
- both off-lane: 17.0% of changes; drafters took base's 28.9%, head's 14.8%

**noise40-b** (60000 drafts, 45530 complete events). power1: +0.0097 (0.0059), power2: +0.0059 (0.0057)

- both on-lane: 58.3% of changes; drafters took base's 42.1%, head's 22.7%
- base on, head off: 13.7% of changes; drafters took base's 49.5%, head's 11.2%
- base off, head on: 11.6% of changes; drafters took base's 19.6%, head's 33.7%
- both off-lane: 16.4% of changes; drafters took base's 28.6%, head's 15.2%

**random-a** (60000 drafts, 45530 complete events). power1: +0.2572 (0.0202), power2: +0.2221 (0.0187)

- both on-lane: 32.3% of changes; drafters took base's 46.7%, head's 15.9%
- base on, head off: 44.4% of changes; drafters took base's 51.9%, head's 4.5%
- base off, head on: 7.5% of changes; drafters took base's 23.0%, head's 24.8%
- both off-lane: 15.8% of changes; drafters took base's 31.8%, head's 10.5%

**random-b** (60000 drafts, 45530 complete events). power1: +0.2481 (0.0200), power2: +0.2078 (0.0172)

- both on-lane: 33.9% of changes; drafters took base's 47.3%, head's 15.0%
- base on, head off: 42.8% of changes; drafters took base's 52.6%, head's 4.5%
- base off, head on: 8.0% of changes; drafters took base's 23.2%, head's 22.6%
- both off-lane: 15.2% of changes; drafters took base's 32.0%, head's 10.6%

**worst** (60000 drafts, 45530 complete events). power1: +0.4976 (0.0283), power2: +0.4191 (0.0271)

- both on-lane: 16.9% of changes; drafters took base's 49.6%, head's 12.8%
- base on, head off: 59.8% of changes; drafters took base's 51.3%, head's 3.4%
- base off, head on: 6.4% of changes; drafters took base's 24.1%, head's 18.5%
- both off-lane: 16.9% of changes; drafters took base's 32.3%, head's 10.2%

