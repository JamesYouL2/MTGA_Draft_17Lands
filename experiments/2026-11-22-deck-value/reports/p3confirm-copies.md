# Phase 3-lite confirmation (P3CONFIRM.md)

19 sets. Process hours: blend-1 115.5, gihwr-only 0.8, main 0.8

## blend-1 minus main

Drafts simulated by both: 9468; with a judge grade for both: 9439 (the rest fell back to the quick build).

| reading | win-rate points (SE) |
|---|---|
| **primary: judged on half B, 19 sets** | **+0.810 (0.017), +46.4 SE** |
| judged on half B, 16 non-tuning sets | +0.806 (0.019), +42.7 SE |
| judged on half A (the advisor's own ratings), same drafts | +0.788 (0.017), +47.4 SE |
| judged on half A, all drafts | +0.790 (0.018), +44.6 SE |

Share of the half-A gain that survives on half B: 103%.

| deck score, points | half A | half B |
|---|---|---|
| score difference | +0.651 (0.014), +47.7 SE | +0.667 (0.014), +46.7 SE |
| card quality term | +0.672 (0.014), +48.4 SE | +0.687 (0.014), +47.5 SE |

| regret measure (positive is worse) | change (SE), z |
|---|---|
| **rank regret (guard)** | +0.0018 (0.0101), +0.2 |
| missed top | +0.0036 (0.0132), +0.3 |
| SD regret (the old guard's measure) | +0.0194 (0.0128), +1.5 |

7352 complete events, 283903 picks.

| deck fact | head minus main (SE) |
|---|---|
| colors | +0.015 (0.003) |
| splash | +0.046 (0.008) |
| spells | -0.001 (0.002) |
| creatures | -0.043 (0.024) |
| removal | +0.046 (0.022) |
| cheap | -0.031 (0.022) |
| mana_value | +0.007 (0.003) |
| pool_quality | -0.002 (0.001) |
| pool_on_color | +0.570 (0.034) |
| pool_spells | +0.898 (0.014) |

## gihwr-only minus main

Drafts simulated by both: 9468; with a judge grade for both: 9439 (the rest fell back to the quick build).

| reading | win-rate points (SE) |
|---|---|
| **primary: judged on half B, 19 sets** | **-0.129 (0.026), -4.9 SE** |
| judged on half B, 16 non-tuning sets | -0.077 (0.027), -2.8 SE |
| judged on half A (the advisor's own ratings), same drafts | -0.145 (0.025), -5.7 SE |
| judged on half A, all drafts | -0.144 (0.025), -5.7 SE |

Share of the half-A gain that survives on half B: 89%.

| deck score, points | half A | half B |
|---|---|---|
| score difference | -0.118 (0.021), -5.7 SE | -0.105 (0.021), -4.9 SE |
| card quality term | +1.206 (0.027), +44.8 SE | +1.219 (0.027), +44.5 SE |

| regret measure (positive is worse) | change (SE), z |
|---|---|
| **rank regret (guard)** | +0.0711 (0.0217), +3.3 |
| missed top | +0.0887 (0.0221), +4.0 |
| SD regret (the old guard's measure) | +0.1259 (0.0245), +5.1 |

7352 complete events, 283903 picks.

| deck fact | head minus main (SE) |
|---|---|
| colors | +0.928 (0.013) |
| splash | +3.512 (0.049) |
| spells | -0.275 (0.006) |
| creatures | +0.061 (0.028) |
| removal | -0.045 (0.025) |
| cheap | -0.302 (0.025) |
| mana_value | +0.036 (0.003) |
| pool_quality | +0.217 (0.001) |
| pool_on_color | -1.682 (0.081) |
| pool_spells | +0.752 (0.015) |

## Decision

Primary +0.810 (0.017), +46.4 SE; rank regret +0.0018 (0.0101), +0.2 SE.

**Registered reading: confirmed.**

Power check: gihwr-only reads +3.3 SEs worse on rank regret.

### blend-1 per set (win-rate points)

| set | half B | half A | drafts |
|---|---|---|---|
| BLB | +0.695 | +0.697 | 496 |
| DFT | +0.872 | +0.860 | 492 |
| DMU | +0.758 | +0.713 | 498 |
| DSK | +0.814 | +0.709 | 495 |
| EOE | +0.729 | +0.604 | 500 |
| FDN | +0.588 | +0.643 | 496 |
| FIN | +0.895 | +0.888 | 500 |
| FRA | +0.819 | +0.827 | 500 |
| HOB | +0.724 | +0.577 | 500 |
| KTK | +0.795 | +1.006 | 498 |
| LTR | +0.553 | +0.494 | 492 |
| MSH | +0.683 | +0.754 | 500 |
| NEO | +0.517 | +0.521 | 493 |
| OTJ | +0.982 | +1.039 | 493 |
| SNC | +1.322 | +1.207 | 486 |
| SOS | +0.708 | +0.728 | 500 |
| TDM | +1.363 | +1.197 | 500 |
| TLA | +0.667 | +0.627 | 500 |
| TMT | +0.909 | +0.878 | 500 |

