
# Simulated draft deck score: validation

Salts: r33s1, r33s2, r33s3, r33s4, r33s5, r33s6, r33s7, r33s8. Criterion (a) is read on the first 6: r33s1, r33s2, r33s3, r33s4, r33s5, r33s6. Each cell: estimate (scaled SE), scaled SEs, signed so positive is the measure's own direction (regret: positive is worse; swap and simulated: positive is better).

## All salts

| head | regret slope change | event wins per swapped pick | simulated deck win rate | simulated drafts | decks changed |
|---|---|---|---|---|---|
| gihwr-only | +0.1089 (0.0099), +11.0 | -0.050 (0.006), -8.9 | -0.049 (0.010), -5.0 | 79904 | 99.9% |
| lane-share-0.10 | -0.0047 (0.0020), -2.3 | +0.056 (0.028), +2.0 | +0.095 (0.002), +40.3 | 79904 | 27.8% |
| no-needs-2drops | -0.0002 (0.0003), -0.5 | -0.031 (0.096), -0.3 | -0.000 (0.000), -0.3 | 79904 | 3.3% |
| noise10 | +0.0003 (0.0012), +0.3 | -0.022 (0.014), -1.6 | -0.148 (0.008), -19.2 | 79904 | 93.7% |
| noise20-a | +0.0022 (0.0022), +1.0 | -0.038 (0.010), -3.7 | -0.522 (0.009), -56.1 | 79904 | 99.3% |
| noise40-a | +0.0132 (0.0041), +3.3 | -0.054 (0.008), -6.7 | -1.420 (0.012), -120.9 | 79904 | 99.9% |
| random-a | +0.2294 (0.0144), +15.9 | -0.076 (0.004), -17.8 | -12.306 (0.018), -685.2 | 79904 | 100.0% |
| scale | -0.0040 (0.0021), -1.9 | -0.067 (0.095), -0.7 | +0.000 (0.001), +0.3 | 79904 | 2.0% |
| wheel-0.15 | -0.0007 (0.0002), -2.9 | +0.097 (0.050), +2.0 | +0.053 (0.002), +22.4 | 79904 | 27.3% |
| worst | +0.4593 (0.0193), +23.8 | -0.077 (0.004), -19.8 | -21.240 (0.021), -1013.1 | 79904 | 100.0% |

## First 6 salts

| head | regret slope change | event wins per swapped pick | simulated deck win rate | simulated drafts | decks changed |
|---|---|---|---|---|---|
| gihwr-only | +0.1114 (0.0133), +8.4 | -0.052 (0.007), -7.4 | -0.050 (0.012), -4.1 | 59933 | 99.9% |
| lane-share-0.10 | -0.0036 (0.0024), -1.5 | +0.061 (0.033), +1.8 | +0.096 (0.003), +30.5 | 59933 | 27.8% |
| no-needs-2drops | -0.0001 (0.0004), -0.3 | -0.084 (0.114), -0.7 | +0.000 (0.000), +0.5 | 59933 | 3.3% |
| noise10 | -0.0002 (0.0014), -0.1 | -0.019 (0.020), -0.9 | -0.154 (0.008), -19.3 | 59933 | 93.7% |
| noise20-a | +0.0029 (0.0028), +1.0 | -0.044 (0.013), -3.4 | -0.524 (0.013), -39.0 | 59933 | 99.3% |
| noise40-a | +0.0143 (0.0051), +2.8 | -0.053 (0.012), -4.6 | -1.425 (0.015), -93.4 | 59933 | 99.9% |
| random-a | +0.2225 (0.0178), +12.5 | -0.075 (0.005), -14.5 | -12.305 (0.026), -482.3 | 59933 | 100.0% |
| scale | -0.0035 (0.0028), -1.3 | -0.046 (0.118), -0.4 | +0.000 (0.001), +0.0 | 59933 | 2.0% |
| wheel-0.15 | -0.0007 (0.0003), -2.2 | +0.109 (0.063), +1.7 | +0.052 (0.003), +17.1 | 59933 | 27.3% |
| worst | +0.4620 (0.0239), +19.3 | -0.078 (0.005), -16.5 | -21.244 (0.029), -728.9 | 59933 | 100.0% |

## Relative power

z per root draft: scaled SEs toward 'head better' divided by the square root of the drafts (events, for regret and swap) the measure used, all salts. Drafts for 3 SEs: what the measure would need to put this head 3 scaled SEs from zero. The power ratio is (z per root draft, simulated / swap) squared: how many times as many drafts swap needs as the simulated measure for the same SEs.

| head | regret z/√n | swap z/√n | simulated z/√n | drafts for 3 SEs: regret / swap / simulated | power ratio, simulated to swap |
|---|---|---|---|---|---|
| gihwr-only | -0.0447 | -0.0361 | -0.0176 | 4,495 / 6,918 / 28,948 | 0.24 |
| lane-share-0.10 | +0.0094 | +0.0082 | +0.1425 | 102,647 / 135,386 / 443 | 305.66 |
| no-needs-2drops | +0.0022 | -0.0013 | -0.0010 | 1,890,890 / 5,258,539 / 9,352,655 | 0.56 |
| noise10 | -0.0012 | -0.0064 | -0.0679 | 6,557,050 / 218,823 / 1,950 | 112.20 |
| noise20-a | -0.0041 | -0.0150 | -0.1986 | 546,318 / 40,044 / 228 | 175.48 |
| noise40-a | -0.0132 | -0.0271 | -0.4278 | 51,586 / 12,289 / 49 | 249.83 |
| random-a | -0.0647 | -0.0722 | -2.4240 | 2,151 / 1,729 / 2 | 1128.67 |
| scale | +0.0078 | -0.0029 | +0.0011 | 148,895 / 1,094,449 / 7,899,172 | 0.14 |
| wheel-0.15 | +0.0117 | +0.0079 | +0.0792 | 65,429 / 143,169 / 1,436 | 99.71 |
| worst | -0.0968 | -0.0803 | -3.5841 | 961 / 1,395 / 1 | 1990.49 |

## Sign agreement

Direction each measure reads for the head, all salts: + better, − worse, and in brackets when under 2 scaled SEs.

| head | regret | swap | simulated | simulated agrees with swap |
|---|---|---|---|---|
| gihwr-only | − | − | − | yes |
| lane-share-0.10 | + | + | + | yes |
| no-needs-2drops | (+) | (−) | (−) | yes |
| noise10 | (−) | (−) | − | yes |
| noise20-a | (−) | − | − | yes |
| noise40-a | − | − | − | yes |
| random-a | − | − | − | yes |
| scale | (+) | (−) | (+) | no |
| wheel-0.15 | + | (+) | + | yes |
| worst | − | − | − | yes |

## Sanity check: deck score against event wins

60603 complete events, base replay. Correlation of the deck win rate with the event's wins, both centred within set (r, its SE, and the slope in event wins per deck win rate point). The base agrees with the drafter on 35.0% of its decided picks on average.

| pools | events | r (SE) | slope |
|---|---|---|---|
| advisor's draft, full agreement with the drafter | 6 | too few | |
| the drafter's own pool, Suggest Deck | 60603 | +0.212 (0.004) | +0.1384 |
| advisor's draft, all events | 60603 | +0.094 (0.004) | +0.0917 |
| advisor's draft, agreement share 0.00 to 0.28 | 23138 | +0.032 (0.007) | +0.0305 |
| advisor's draft, agreement share 0.28 to 0.41 | 22319 | +0.074 (0.007) | +0.0733 |
| advisor's draft, agreement share 0.41 to 1.00 | 20978 | +0.136 (0.007) | +0.1411 |

## What the simulation did

| copy | drafts | picks | wheel picks | wheel swaps applied | dropped | applied share | forced picks | quick builds | skipped |
|---|---|---|---|---|---|---|---|---|---|
| base | 79904 | 3336814 | 1436800 | 144817 | 854706 | 14.5% | 16031 | 83 | 96 |
| gihwr-only | 79904 | 3336814 | 1436800 | 84900 | 879094 | 8.8% | 16031 | 83 | 96 |
| lane-share-0.10 | 79904 | 3336814 | 1436800 | 143378 | 853548 | 14.4% | 16031 | 83 | 96 |
| no-needs-2drops | 79904 | 3336814 | 1436800 | 144938 | 854646 | 14.5% | 16031 | 83 | 96 |
| noise10 | 79904 | 3336814 | 1436800 | 149882 | 859583 | 14.8% | 16031 | 83 | 96 |
| noise20-a | 79904 | 3336814 | 1436800 | 161294 | 875914 | 15.6% | 16031 | 83 | 96 |
| noise40-a | 79904 | 3336814 | 1436800 | 186390 | 898546 | 17.2% | 16031 | 83 | 96 |
| random-a | 79904 | 3336814 | 1436800 | 368746 | 919453 | 28.6% | 16031 | 83 | 96 |
| scale | 79904 | 3336814 | 1436800 | 144791 | 854718 | 14.5% | 16031 | 83 | 96 |
| wheel-0.15 | 79904 | 3336814 | 1436800 | 137091 | 856790 | 13.8% | 16031 | 83 | 96 |
| worst | 79904 | 3336814 | 1436800 | 458043 | 888049 | 34.0% | 16031 | 83 | 96 |

