# Phase 3-lite decomposition (P3DECOMP.md)

19 sets. Job seconds per head: blend-1 59.9 h, main 0.3 h, marginal 33.4 h

## Reproduction check against run 45187839933

| head | drafts matching the eval's score | flag |
|---|---|---|
| main | 9469 / 9469 (100.0%) | ok |
| blend-1 | 9469 / 9469 (100.0%) | ok |
| marginal | 9469 / 9469 (100.0%) | ok |

## blend-1 minus main, 19 sets

Drafts with parts for both: 9438; dropped (a quick build, no parts): 31.

| term | points (SE) | share of the score difference |
|---|---|---|
| **score difference** | +0.637 (0.013), +48.1 SE | 100% |
| card_quality | +0.665 (0.013), +49.5 SE | 104% |
| two_colors | -0.026 (0.003), -7.7 SE | -4% |
| missing_fixing | -0.001 (0.001), -1.9 SE | -0% |
| missing_spells | +0.000 (0.000), +0.0 SE | 0% |
| residual | +0.000 (0.000), +0.2 SE | 0% |

Q (card quality share) = 104%; C (two_colors + missing_fixing) = -4%.

**Registered reading: quality-led.**

Descriptive, head minus main:

| fact | difference (SE) |
|---|---|
| colors | +0.021 (0.003) |
| splash | +0.066 (0.009) |
| spells | -0.001 (0.002) |
| creatures | -0.021 (0.025) |
| removal | +0.013 (0.022) |
| cheap | +0.005 (0.023) |
| mana_value | +0.006 (0.003) |
| pool_quality | -0.001 (0.001) |
| pool_on_color | +0.703 (0.034) |
| pool_spells | +0.957 (0.014) |

## blend-1 minus main, 16 non-tuning sets

Drafts with parts for both: 7950; dropped (a quick build, no parts): 25.

| term | points (SE) | share of the score difference |
|---|---|---|
| **score difference** | +0.650 (0.014), +45.6 SE | 100% |
| card_quality | +0.675 (0.014), +47.0 SE | 104% |
| two_colors | -0.024 (0.004), -6.7 SE | -4% |
| missing_fixing | -0.000 (0.000), -1.0 SE | -0% |
| missing_spells | +0.000 (0.000), +0.0 SE | 0% |
| residual | +0.000 (0.000), +0.1 SE | 0% |

Q (card quality share) = 104%; C (two_colors + missing_fixing) = -4%.

Descriptive, head minus main:

| fact | difference (SE) |
|---|---|
| colors | +0.019 (0.003) |
| splash | +0.060 (0.009) |
| spells | -0.000 (0.001) |
| creatures | -0.025 (0.028) |
| removal | +0.064 (0.023) |
| cheap | +0.055 (0.025) |
| mana_value | +0.004 (0.003) |
| pool_quality | -0.002 (0.001) |
| pool_on_color | +0.751 (0.037) |
| pool_spells | +0.966 (0.015) |

### blend-1: per set (points)

| set | score | card quality | two colors | fixing | spells | residual |
|---|---|---|---|---|---|---|
| BLB | +0.537 | +0.572 | -0.025 | -0.010 | +0.000 | +0.000 |
| DFT | +0.698 | +0.774 | -0.076 | +0.000 | +0.000 | -0.000 |
| DMU | +0.745 | +0.751 | -0.006 | +0.000 | +0.000 | -0.000 |
| DSK | +0.372 | +0.464 | -0.081 | -0.010 | +0.000 | +0.000 |
| EOE | +0.352 | +0.352 | +0.000 | +0.000 | +0.000 | -0.000 |
| FDN | +0.576 | +0.595 | -0.019 | +0.000 | +0.000 | +0.000 |
| FIN | +0.713 | +0.762 | -0.050 | +0.000 | +0.000 | +0.000 |
| FRA | +0.707 | +0.701 | +0.006 | +0.000 | +0.000 | -0.000 |
| HOB | +0.519 | +0.537 | -0.019 | +0.000 | +0.000 | +0.000 |
| KTK | +0.623 | +0.666 | -0.038 | -0.005 | +0.000 | -0.000 |
| LTR | +0.347 | +0.347 | +0.000 | +0.000 | +0.000 | -0.000 |
| MSH | +0.724 | +0.730 | -0.006 | +0.000 | +0.000 | +0.000 |
| NEO | +0.418 | +0.418 | +0.000 | +0.000 | +0.000 | -0.000 |
| OTJ | +0.786 | +0.793 | -0.006 | +0.000 | +0.000 | -0.000 |
| SNC | +1.174 | +1.174 | +0.000 | +0.000 | +0.000 | +0.000 |
| SOS | +0.548 | +0.653 | -0.105 | +0.000 | +0.000 | +0.000 |
| TDM | +0.940 | +0.946 | -0.006 | +0.000 | +0.000 | +0.000 |
| TLA | +0.573 | +0.610 | -0.037 | +0.000 | +0.000 | +0.000 |
| TMT | +0.751 | +0.782 | -0.031 | +0.000 | +0.000 | +0.000 |

## marginal minus main, 19 sets

Drafts with parts for both: 9438; dropped (a quick build, no parts): 31.

| term | points (SE) | share of the score difference |
|---|---|---|
| **score difference** | +0.480 (0.016), +29.2 SE | 100% |
| card_quality | +0.697 (0.017), +41.7 SE | 145% |
| two_colors | -0.187 (0.008), -24.4 SE | -39% |
| missing_fixing | -0.022 (0.003), -7.1 SE | -5% |
| missing_spells | -0.009 (0.003), -2.8 SE | -2% |
| residual | +0.000 (0.000), +1.2 SE | 0% |

Q (card quality share) = 145%; C (two_colors + missing_fixing) = -43%.

**Registered reading: quality-led.**

Descriptive, head minus main:

| fact | difference (SE) |
|---|---|
| colors | +0.154 (0.007) |
| splash | +0.493 (0.021) |
| spells | -0.035 (0.003) |
| creatures | +0.007 (0.027) |
| removal | -0.060 (0.024) |
| cheap | -0.067 (0.025) |
| mana_value | +0.013 (0.003) |
| pool_quality | +0.001 (0.001) |
| pool_on_color | +0.595 (0.044) |
| pool_spells | +0.806 (0.016) |

## marginal minus main, 16 non-tuning sets

Drafts with parts for both: 7950; dropped (a quick build, no parts): 25.

| term | points (SE) | share of the score difference |
|---|---|---|
| **score difference** | +0.509 (0.017), +29.2 SE | 100% |
| card_quality | +0.703 (0.018), +39.8 SE | 138% |
| two_colors | -0.175 (0.008), -21.7 SE | -34% |
| missing_fixing | -0.011 (0.002), -5.1 SE | -2% |
| missing_spells | -0.008 (0.003), -2.5 SE | -1% |
| residual | +0.000 (0.000), +0.3 SE | 0% |

Q (card quality share) = 138%; C (two_colors + missing_fixing) = -37%.

Descriptive, head minus main:

| fact | difference (SE) |
|---|---|
| colors | +0.147 (0.007) |
| splash | +0.473 (0.023) |
| spells | -0.029 (0.002) |
| creatures | +0.018 (0.030) |
| removal | +0.015 (0.025) |
| cheap | -0.004 (0.027) |
| mana_value | +0.010 (0.004) |
| pool_quality | -0.001 (0.001) |
| pool_on_color | +0.664 (0.047) |
| pool_spells | +0.814 (0.017) |

### marginal: per set (points)

| set | score | card quality | two colors | fixing | spells | residual |
|---|---|---|---|---|---|---|
| BLB | +0.118 | +0.538 | -0.263 | -0.157 | +0.000 | +0.000 |
| DFT | +0.508 | +0.959 | -0.416 | -0.036 | +0.000 | -0.000 |
| DMU | +0.521 | +0.708 | -0.132 | -0.015 | -0.040 | -0.000 |
| DSK | +0.077 | +0.544 | -0.351 | -0.076 | -0.040 | +0.000 |
| EOE | +0.298 | +0.334 | -0.031 | -0.005 | +0.000 | -0.000 |
| FDN | +0.447 | +0.656 | -0.194 | -0.015 | +0.000 | +0.000 |
| FIN | +0.656 | +0.848 | -0.192 | +0.000 | +0.000 | -0.000 |
| FRA | +0.519 | +0.655 | -0.136 | +0.000 | +0.000 | +0.000 |
| HOB | +0.427 | +0.604 | -0.167 | -0.010 | +0.000 | +0.000 |
| KTK | +0.251 | +0.645 | -0.313 | -0.040 | -0.040 | +0.000 |
| LTR | +0.223 | +0.292 | -0.044 | -0.005 | -0.020 | -0.000 |
| MSH | +0.804 | +0.828 | -0.025 | +0.000 | +0.000 | +0.000 |
| NEO | +0.322 | +0.357 | -0.025 | -0.010 | +0.000 | -0.000 |
| OTJ | +0.782 | +0.913 | -0.131 | +0.000 | +0.000 | +0.000 |
| SNC | +1.196 | +1.305 | -0.109 | +0.000 | +0.000 | +0.000 |
| SOS | +0.330 | +0.883 | -0.508 | -0.025 | -0.020 | +0.000 |
| TDM | +0.980 | +1.035 | -0.056 | +0.000 | +0.000 | -0.000 |
| TLA | +0.217 | +0.529 | -0.298 | -0.015 | +0.000 | +0.000 |
| TMT | +0.443 | +0.603 | -0.155 | -0.005 | +0.000 | -0.000 |

