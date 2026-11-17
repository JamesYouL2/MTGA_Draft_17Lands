914650 decks, 4133840 games, 20 sets. Mean score 79.2.

## Held out (the rule's test)

### Constants fit on the other 19 sets

| decks | share | predicted game WR | actual game WR | actual less predicted, in expected wins |
|---|---|---|---|---|
| under 65 | 0.0% | 35.5% | 41.0% | +0.42 ± 0.31 |
| 65-70 | 0.7% | 41.4% | 45.2% | +0.33 ± 0.24 |
| 70-75 | 11.1% | 47.6% | 48.3% | +0.07 ± 0.09 |
| 75-80 | 46.0% | 53.4% | 53.1% | -0.03 ± 0.05 |
| 80-85 | 38.2% | 58.7% | 58.6% | -0.01 ± 0.05 |
| 85-90 | 4.0% | 63.7% | 65.0% | +0.15 ± 0.08 |
| 90 and over | 0.0% | 68.7% | 73.3% | +0.53 ± 0.48 |
| two colors or fewer, no splash | 49.9% | 57.2% | 56.5% | -0.08 ± 0.05 |
| two main colors and a splash | 30.1% | 53.3% | 54.7% | +0.14 ± 0.07 |
| three main colors, no splash | 11.2% | 53.1% | 53.1% | -0.00 ± 0.13 |
| three main colors and a splash, or four or more | 8.7% | 54.2% | 54.0% | -0.02 ± 0.07 |
| all | 100.0% | 55.4% | 55.4% | +0.00 ± 0.05 |

Calibration slope 0.971 ± 0.072, intercept +0.007 ± 0.029.

Held-out constants ranged: at base -0.0281 to -0.0031, per point 0.04998 to 0.05327. App: -0.0062, 0.05099.

Fit on all 20 sets: at base -0.0098, per point 0.05100.

## The app's current constants

### As in deck_scorer.py

| decks | share | predicted game WR | actual game WR | actual less predicted, in expected wins |
|---|---|---|---|---|
| under 65 | 0.0% | 36.1% | 41.0% | +0.38 ± 0.28 |
| 65-70 | 0.7% | 41.8% | 45.2% | +0.30 ± 0.21 |
| 70-75 | 11.1% | 47.8% | 48.3% | +0.05 ± 0.08 |
| 75-80 | 46.0% | 53.5% | 53.1% | -0.04 ± 0.05 |
| 80-85 | 38.2% | 58.7% | 58.6% | -0.01 ± 0.05 |
| 85-90 | 4.0% | 63.7% | 65.0% | +0.15 ± 0.07 |
| 90 and over | 0.0% | 68.6% | 73.3% | +0.54 ± 0.50 |
| two colors or fewer, no splash | 49.9% | 57.2% | 56.5% | -0.09 ± 0.05 |
| two main colors and a splash | 30.1% | 53.4% | 54.7% | +0.13 ± 0.06 |
| three main colors, no splash | 11.2% | 53.3% | 53.1% | -0.02 ± 0.12 |
| three main colors and a splash, or four or more | 8.7% | 54.3% | 54.0% | -0.04 ± 0.06 |
| all | 100.0% | 55.5% | 55.4% | -0.01 ± 0.05 |

Calibration slope 1.000 ± 0.065, intercept -0.004 ± 0.027.

## By set, held out

| set | predicted | actual | actual less predicted, expected wins |
|---|---|---|---|
| BLB | 52.3% | 54.7% | +0.26 |
| Cube_-_Powered | 53.3% | 56.9% | +0.39 |
| DFT | 54.4% | 54.9% | +0.06 |
| DMU | 53.4% | 56.3% | +0.32 |
| DSK | 54.9% | 54.3% | -0.07 |
| EOE | 57.2% | 55.3% | -0.21 |
| FDN | 57.2% | 54.8% | -0.27 |
| FIN | 56.7% | 55.8% | -0.10 |
| FRA | 54.9% | 55.1% | +0.02 |
| HOB | 57.9% | 56.2% | -0.19 |
| LTR | 58.5% | 55.5% | -0.33 |
| MH3 | 57.5% | 55.7% | -0.20 |
| MSH | 54.8% | 56.0% | +0.13 |
| NEO | 56.1% | 55.5% | -0.06 |
| OTJ | 55.2% | 54.2% | -0.11 |
| PIO | 56.4% | 55.6% | -0.09 |
| SOS | 56.0% | 55.4% | -0.06 |
| TDM | 51.2% | 55.0% | +0.41 |
| TLA | 53.3% | 55.8% | +0.26 |
| TMT | 54.1% | 57.0% | +0.32 |

## Verdict by the rule

- Held out: **calibrated** (failing rows: none; slope passes).
- Current constants: failing rows: none; slope passes.
