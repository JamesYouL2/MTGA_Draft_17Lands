# Card ratings at `f25b449`

714281 decks and 3288430 games from 20 sets; held-out log loss per game, 5 folds. Intervals are 98.33%.

Card quality is worth 1.56 [1.49, 1.63] millinats a game: the engine's version against no card quality at all.

## Primary results

Gain: how much better the engine's version predicts than the ablation, in millinats a game (positive: the engine's is better) and as a share of what card quality is worth.

| what the engine does | ablation | gain (millinats a game) | share of card quality's worth | verdict |
|---|---|---|---|---|
| Archetype weighting | `no-archetype` | -0.421 [-0.454, -0.387] | -27.0% [-29.2%, -24.9%] | ablation predicts better |
| Shrinkage | `no-shrinkage` | +0.004 [+0.003, +0.005] | +0.2% [+0.2%, +0.3%] | engine's predicts better |
| IWD premium | `no-iwd` | +0.029 [+0.028, +0.031] | +1.9% [+1.8%, +2.0%] | engine's predicts better |

## Other versions

Not used for a verdict. Gain of the engine's version over each.

| version | gain (millinats a game) | share of card quality's worth |
|---|---|---|
| blend weight 0.65 (engine's at pick 1) | -0.164 [-0.173, -0.156] | -10.5% |
| blend weight 1.3 (engine's from pick 15) | +0.176 [+0.168, +0.184] | +11.3% |
| no power bonus | +0.267 [+0.255, +0.279] | +17.1% |
| overall GIH WR alone | -0.272 [-0.305, -0.239] | -17.5% |
| the deck score's blend (0.7 pair, 0.3 overall) | +0.114 [+0.106, +0.122] | +7.3% |

## By set

Gain of the engine's version over each ablation, in millinats a game (± SE).

| set | decks | card quality's worth | `no-archetype` | `no-shrinkage` | `no-iwd` |
|---|---|---|---|---|---|
| BLB | 46322 | 1.65 | -0.435 ± 0.053 | +0.002 ± 0.001 | +0.024 ± 0.002 |
| Cube_-_Powered | 130 | -0.08 | +3.006 ± 1.000 | -0.175 ± 0.119 | +0.037 ± 0.039 |
| DFT | 42493 | 1.44 | -0.515 ± 0.055 | +0.004 ± 0.001 | +0.037 ± 0.002 |
| DMU | 26463 | 1.91 | -0.142 ± 0.090 | +0.007 ± 0.004 | +0.033 ± 0.003 |
| DSK | 43224 | 2.36 | -0.652 ± 0.056 | +0.006 ± 0.002 | +0.046 ± 0.003 |
| EOE | 44991 | 1.40 | -0.633 ± 0.060 | +0.007 ± 0.002 | +0.028 ± 0.002 |
| FDN | 45468 | 1.67 | -0.649 ± 0.049 | +0.005 ± 0.002 | +0.026 ± 0.002 |
| FIN | 41378 | 1.51 | -0.598 ± 0.054 | +0.002 ± 0.002 | +0.036 ± 0.002 |
| FRA | 37431 | 0.93 | -0.271 ± 0.058 | +0.010 ± 0.003 | +0.021 ± 0.003 |
| HOB | 46567 | 1.34 | -0.230 ± 0.058 | +0.002 ± 0.002 | +0.016 ± 0.003 |
| LTR | 43869 | 1.27 | -0.364 ± 0.053 | -0.002 ± 0.001 | +0.027 ± 0.003 |
| MH3 | 25691 | 2.06 | -0.561 ± 0.081 | +0.002 ± 0.002 | +0.018 ± 0.003 |
| MSH | 42057 | 1.16 | -0.493 ± 0.053 | +0.001 ± 0.002 | +0.039 ± 0.002 |
| NEO | 43810 | 1.81 | -0.653 ± 0.060 | +0.008 ± 0.002 | +0.041 ± 0.003 |
| OTJ | 37773 | 1.82 | -0.423 ± 0.053 | +0.004 ± 0.002 | +0.035 ± 0.002 |
| PIO | 32895 | 1.08 | +0.190 ± 0.071 | +0.014 ± 0.004 | -0.012 ± 0.003 |
| SOS | 38685 | 1.96 | -0.234 ± 0.054 | -0.005 ± 0.002 | +0.036 ± 0.002 |
| TDM | 10435 | 1.59 | +0.648 ± 0.162 | +0.001 ± 0.008 | +0.014 ± 0.005 |
| TLA | 37959 | 1.24 | -0.568 ± 0.055 | +0.003 ± 0.002 | +0.029 ± 0.003 |
| TMT | 26640 | 1.54 | -0.333 ± 0.085 | +0.005 ± 0.004 | +0.040 ± 0.003 |
