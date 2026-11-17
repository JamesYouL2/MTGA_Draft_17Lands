# Splash price at `7fefad9`

914650 decks, 4133840 games, 20 sets.

## The groups

| group | decks | game win rate | mean card quality (SDs) |
|---|---|---|---|
| two colors or fewer, no splash | 49.9% | 56.5% | +0.21 |
| two main colors and a splash | 30.1% | 54.7% | +0.24 |
| three main colors, no splash | 11.2% | 53.1% | +0.22 |
| three main colors and a splash, or four or more | 8.7% | 54.0% | +0.28 |

## Q0. Today's single weight, refit

3+ colors against two or fewer: -2.99 ± 0.24 (-12.4 SEs) points (the app's two_colors weight is +3.1, so -3.1 here).

## Q1. Splash against three main colors

Each group against decks of two colors or fewer, in score points.

| group | weight |
|---|---|
| two main colors and a splash | -2.47 ± 0.20 (-12.2 SEs) |
| three main colors, no splash | -3.28 ± 0.31 (-10.5 SEs) |
| three main colors and a splash, or four or more | -4.94 ± 0.41 (-12.0 SEs) |

Splash less three main colors: **+0.81 ± 0.27 (+3.0 SEs)**.

## Q2. Does a bigger splash cost more?

Two main colors and a splash, by how many spells need the splash, against decks of two colors or fewer.

| spells needing the splash | decks (share of splash decks) | weight |
|---|---|---|
| 0 or 1 | 33.2% | -1.82 ± 0.17 (-10.5 SEs) |
| 2 | 28.6% | -2.43 ± 0.20 (-11.9 SEs) |
| 3 | 22.7% | -2.82 ± 0.24 (-11.9 SEs) |
| 4+ | 15.5% | -3.56 ± 0.29 (-12.3 SEs) |

Per spell needing the splash, as a straight line: -0.43 ± 0.05 (-9.3 SEs).

## Q3. On sets the fit didn't see

Log loss per game of the single weight less the split weights, in units of 1e-5 (positive: the split predicts better).

| BLB | Cube_-_Powered | DFT | DMU | DSK | EOE | FDN | FIN | FRA | HOB | LTR | MH3 | MSH | NEO | OTJ | PIO | SOS | TDM | TLA | TMT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| +5.6 | +118.1 | -2.0 | +15.7 | +10.0 | +4.1 | +2.2 | +8.4 | +5.7 | +4.6 | -4.2 | +21.3 | -2.3 | +2.5 | +6.4 | +13.0 | +7.4 | +39.6 | +12.3 | +5.9 |

Weighted by games: +7.93. Better on 17 of 20 sets. Mean +13.71, SE across sets 5.90.

## Q4. Each set alone

Splash and three-main weights fit on each set by itself (model SEs). `–` where a group has fewer than 300 decks.

| set | splash | three main | splash less three |
|---|---|---|---|
| BLB | -2.4 ± 0.2 | -5.5 ± 0.6 | +3.1 ± 0.6 |
| Cube_-_Powered | – | – | – |
| DFT | -3.4 ± 0.2 | -4.3 ± 0.4 | +0.9 ± 0.4 |
| DMU | -2.0 ± 0.2 | -2.9 ± 0.3 | +0.9 ± 0.2 |
| DSK | -1.9 ± 0.2 | -2.6 ± 0.2 | +0.8 ± 0.2 |
| EOE | -1.9 ± 0.2 | -2.7 ± 0.3 | +0.8 ± 0.3 |
| FDN | -2.2 ± 0.2 | -3.2 ± 0.4 | +1.0 ± 0.4 |
| FIN | -2.0 ± 0.2 | -3.4 ± 0.3 | +1.3 ± 0.3 |
| FRA | -3.3 ± 0.2 | -3.3 ± 0.3 | +0.1 ± 0.3 |
| HOB | -2.1 ± 0.2 | -4.1 ± 0.5 | +2.0 ± 0.6 |
| LTR | -2.8 ± 0.3 | -4.0 ± 0.5 | +1.1 ± 0.5 |
| MH3 | -1.5 ± 0.2 | -2.5 ± 0.2 | +1.0 ± 0.2 |
| MSH | -1.2 ± 0.3 | -1.6 ± 0.5 | +0.5 ± 0.5 |
| NEO | -3.4 ± 0.2 | -4.7 ± 0.4 | +1.3 ± 0.4 |
| OTJ | -1.9 ± 0.2 | -2.8 ± 0.3 | +0.9 ± 0.3 |
| PIO | -4.9 ± 0.4 | -6.4 ± 0.6 | +1.5 ± 0.6 |
| SOS | -3.4 ± 0.2 | -4.4 ± 0.3 | +1.1 ± 0.3 |
| TDM | -3.5 ± 0.5 | -2.7 ± 0.4 | -0.8 ± 0.3 |
| TLA | -0.8 ± 0.2 | -2.2 ± 0.3 | +1.3 ± 0.3 |
| TMT | -2.7 ± 0.3 | -4.4 ± 0.5 | +1.7 ± 0.5 |

Same sign as the pooled difference in 18 of 19 sets.

## Verdict by the rule

- Split the weight: **yes** (difference +3.0 SEs, held-out +7.93, same sign in 18/19).
- Price the splash's size: **yes** (slope -9.3 SEs; reported only, see PROTOCOL.md).

Fitted split weights, for the record: {"splash": -2.5, "three": -3.3, "more": -4.9}.
