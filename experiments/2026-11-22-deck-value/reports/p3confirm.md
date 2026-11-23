# Phase 3-lite confirmation (P3CONFIRM.md)

19 sets. Process hours: blend-1 117.7, gihwr-only 0.8, main 0.8

## blend-1 minus main

Drafts simulated by both: 9468; with a judge grade for both: 9439 (the rest fell back to the quick build).

| reading | win-rate points (SE) |
|---|---|
| **primary: judged on half B, 19 sets** | **+0.791 (0.017), +46.3 SE** |
| judged on half B, 16 non-tuning sets | +0.790 (0.018), +43.2 SE |
| judged on half A (the advisor's own ratings), same drafts | +0.783 (0.016), +47.9 SE |
| judged on half A, all drafts | +0.786 (0.017), +45.0 SE |

Share of the half-A gain that survives on half B: 101%.

| deck score, points | half A | half B |
|---|---|---|
| score difference | +0.646 (0.013), +48.2 SE | +0.650 (0.014), +46.6 SE |
| card quality term | +0.669 (0.014), +49.3 SE | +0.673 (0.014), +47.7 SE |

| regret measure (positive is worse) | change (SE), z |
|---|---|
| **rank regret (guard)** | +0.0042 (0.0104), +0.4 |
| missed top | -0.0040 (0.0136), -0.3 |
| SD regret (the old guard's measure) | +0.0256 (0.0133), +1.9 |

7352 complete events, 283903 picks.

| deck fact | head minus main (SE) |
|---|---|
| colors | +0.017 (0.003) |
| splash | +0.052 (0.008) |
| spells | -0.002 (0.002) |
| creatures | -0.001 (0.025) |
| removal | +0.032 (0.022) |
| cheap | +0.001 (0.023) |
| mana_value | +0.005 (0.003) |
| pool_quality | -0.001 (0.001) |
| pool_on_color | +0.583 (0.034) |
| pool_spells | +0.951 (0.014) |

## gihwr-only minus main

Drafts simulated by both: 9468; with a judge grade for both: 9439 (the rest fell back to the quick build).

| reading | win-rate points (SE) |
|---|---|
| **primary: judged on half B, 19 sets** | **-0.204 (0.026), -7.9 SE** |
| judged on half B, 16 non-tuning sets | -0.155 (0.027), -5.7 SE |
| judged on half A (the advisor's own ratings), same drafts | -0.216 (0.025), -8.6 SE |
| judged on half A, all drafts | -0.215 (0.025), -8.6 SE |

Share of the half-A gain that survives on half B: 95%.

| deck score, points | half A | half B |
|---|---|---|
| score difference | -0.175 (0.020), -8.6 SE | -0.165 (0.021), -7.9 SE |
| card quality term | +1.146 (0.026), +43.6 SE | +1.156 (0.027), +43.2 SE |

| regret measure (positive is worse) | change (SE), z |
|---|---|
| **rank regret (guard)** | +0.0669 (0.0219), +3.1 |
| missed top | +0.0732 (0.0222), +3.3 |
| SD regret (the old guard's measure) | +0.1258 (0.0247), +5.1 |

7352 complete events, 283903 picks.

| deck fact | head minus main (SE) |
|---|---|
| colors | +0.940 (0.013) |
| splash | +3.546 (0.050) |
| spells | -0.269 (0.006) |
| creatures | +0.070 (0.028) |
| removal | -0.080 (0.025) |
| cheap | -0.306 (0.025) |
| mana_value | +0.035 (0.003) |
| pool_quality | +0.211 (0.001) |
| pool_on_color | -1.659 (0.081) |
| pool_spells | +0.717 (0.016) |

## Decision

Primary +0.791 (0.017), +46.3 SE; rank regret +0.0042 (0.0104), +0.4 SE.

**Registered reading: confirmed.**

Power check: gihwr-only reads +3.1 SEs worse on rank regret.

### blend-1 per set (win-rate points)

| set | half B | half A | drafts |
|---|---|---|---|
| BLB | +0.600 | +0.619 | 496 |
| DFT | +0.844 | +0.847 | 492 |
| DMU | +0.781 | +0.756 | 498 |
| DSK | +0.862 | +0.754 | 495 |
| EOE | +0.660 | +0.550 | 500 |
| FDN | +0.571 | +0.645 | 496 |
| FIN | +0.893 | +0.872 | 500 |
| FRA | +0.894 | +0.894 | 500 |
| HOB | +0.741 | +0.637 | 500 |
| KTK | +0.558 | +0.861 | 498 |
| LTR | +0.583 | +0.502 | 492 |
| MSH | +0.826 | +0.891 | 500 |
| NEO | +0.429 | +0.489 | 493 |
| OTJ | +0.927 | +0.995 | 493 |
| SNC | +1.332 | +1.247 | 486 |
| SOS | +0.667 | +0.676 | 500 |
| TDM | +1.345 | +1.198 | 500 |
| TLA | +0.629 | +0.581 | 500 |
| TMT | +0.886 | +0.869 | 500 |

