# Learned pick models: fits

Each set scored by models fitted without it, on its own full ratings (not the replay's held-out ratings). Top-1 / top-3 agreement with the card taken, in percent.

| set | picks (strong) | GIH WR only | lgbm-weak |
|---|---|---|---|
| BLB | 71560 | 36.9 / 74.5 | 58.4 / 89.7 |
| DFT | 77408 | 40.4 / 77.1 | 59.1 / 90.2 |
| DMU | 77611 | 35.0 / 72.4 | 50.3 / 84.8 |
| DSK | 77674 | 39.6 / 75.6 | 60.5 / 90.3 |
| EOE | 72000 | 40.0 / 77.2 | 59.2 / 89.9 |
| FDN | 77537 | 41.1 / 77.1 | 61.7 / 91.4 |
| FIN | 78000 | 38.9 / 75.8 | 59.0 / 89.9 |
| FRA | 77997 | 42.3 / 78.1 | 56.9 / 88.8 |
| HOB | 78000 | 41.6 / 78.5 | 59.1 / 90.1 |
| KTK | 77591 | 41.9 / 78.3 | 51.7 / 85.0 |
| LTR | 77416 | 42.3 / 77.9 | 58.9 / 89.5 |
| MSH | 78000 | 43.2 / 78.2 | 58.6 / 89.6 |
| NEO | 83437 | 40.0 / 75.3 | 56.3 / 87.2 |
| OTJ | 77750 | 40.5 / 75.9 | 57.1 / 89.0 |
| SNC | 76430 | 40.8 / 76.5 | 55.7 / 88.2 |
| SOS | 78000 | 40.2 / 76.6 | 59.5 / 90.1 |
| TDM | 78000 | 39.4 / 75.9 | 54.1 / 86.2 |
| TLA | 76000 | 40.2 / 76.1 | 57.2 / 88.3 |
| TMT | 75667 | 41.8 / 78.4 | 58.9 / 89.7 |
| **all** | 1466078 | **40.3 / 76.6** | **57.5 / 88.8** |

## Chosen LightGBM settings

Leaves / rounds.

| set | lgbm-weak |
|---|---|
| BLB | 15 / 225 |
| DFT | 63 / 114 |
| DMU | 15 / 238 |
| DSK | 63 / 109 |
| EOE | 15 / 341 |
| FDN | 63 / 114 |
| FIN | 15 / 217 |
| FRA | 15 / 220 |
| HOB | 15 / 263 |
| KTK | 63 / 147 |
| LTR | 15 / 138 |
| MSH | 15 / 247 |
| NEO | 63 / 119 |
| OTJ | 63 / 163 |
| SNC | 63 / 119 |
| SOS | 15 / 228 |
| TDM | 15 / 403 |
| TLA | 15 / 257 |
| TMT | 63 / 107 |

## Feature importance (share of gain, mean over fits)

| feature | lgbm-weak |
|---|---|
| quality | 29.7% |
| lane_fit | 20.5% |
| color_share | 25.6% |
| off_pips | 0.7% |
| pack | 1.9% |
| pick | 5.1% |
| iwd | 6.4% |
| mana_value | 2.5% |
| creature | 0.7% |
| alsa | 0.0% |
| n_colors | 6.9% |
