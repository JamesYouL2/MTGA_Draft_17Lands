# Card ratings at `f25b449`

714281 decks and 3288430 games from 20 sets; held-out log loss per game, 5 folds. Intervals are 98.33%.

Card quality is worth 1.62 [1.55, 1.69] millinats a game: the engine's version against no card quality at all.

## Primary results

Gain: how much better the engine's version predicts than the ablation, in millinats a game (positive: the engine's is better) and as a share of what card quality is worth.

| what the engine does | ablation | gain (millinats a game) | share of card quality's worth | verdict |
|---|---|---|---|---|
| Archetype weighting | `no-archetype` | -0.457 [-0.492, -0.422] | -28.2% [-30.3%, -26.0%] | ablation predicts better |
| Shrinkage | `no-shrinkage` | +0.005 [+0.003, +0.006] | +0.3% [+0.2%, +0.4%] | engine's predicts better |
| IWD premium | `no-iwd` | +0.033 [+0.032, +0.035] | +2.1% [+2.0%, +2.2%] | engine's predicts better |

## Other versions

Not used for a verdict. Gain of the engine's version over each.

| version | gain (millinats a game) | share of card quality's worth |
|---|---|---|
| blend weight 0.65 (engine's at pick 1) | -0.177 [-0.186, -0.168] | -10.9% |
| blend weight 1.3 (engine's from pick 15) | +0.187 [+0.179, +0.196] | +11.6% |
| no power bonus | +0.295 [+0.282, +0.307] | +18.2% |
| overall GIH WR alone | -0.272 [-0.306, -0.238] | -16.8% |
| the deck score's blend (0.7 pair, 0.3 overall) | +0.136 [+0.127, +0.144] | +8.4% |

## By set

Gain of the engine's version over each ablation, in millinats a game (± SE).

| set | decks | card quality's worth | `no-archetype` | `no-shrinkage` | `no-iwd` |
|---|---|---|---|---|---|
| BLB | 46322 | 1.72 | -0.457 ± 0.055 | +0.003 ± 0.001 | +0.025 ± 0.002 |
| Cube_-_Powered | 130 | -0.07 | +3.185 ± 1.041 | -0.197 ± 0.126 | +0.033 ± 0.040 |
| DFT | 42493 | 1.45 | -0.466 ± 0.058 | +0.003 ± 0.001 | +0.038 ± 0.002 |
| DMU | 26463 | 1.95 | -0.253 ± 0.094 | +0.005 ± 0.003 | +0.035 ± 0.003 |
| DSK | 43224 | 2.37 | -0.701 ± 0.061 | +0.006 ± 0.002 | +0.050 ± 0.003 |
| EOE | 44991 | 1.47 | -0.656 ± 0.062 | +0.008 ± 0.002 | +0.032 ± 0.002 |
| FDN | 45468 | 1.74 | -0.698 ± 0.051 | +0.007 ± 0.002 | +0.030 ± 0.002 |
| FIN | 41378 | 1.58 | -0.635 ± 0.056 | +0.002 ± 0.002 | +0.039 ± 0.002 |
| FRA | 37431 | 1.07 | -0.315 ± 0.061 | +0.011 ± 0.003 | +0.036 ± 0.003 |
| HOB | 46567 | 1.66 | -0.454 ± 0.060 | +0.004 ± 0.002 | +0.038 ± 0.003 |
| LTR | 43869 | 1.33 | -0.398 ± 0.054 | -0.002 ± 0.001 | +0.028 ± 0.003 |
| MH3 | 25691 | 2.12 | -0.555 ± 0.087 | +0.001 ± 0.002 | +0.038 ± 0.004 |
| MSH | 42057 | 1.13 | -0.491 ± 0.055 | +0.002 ± 0.002 | +0.030 ± 0.003 |
| NEO | 43810 | 1.81 | -0.661 ± 0.063 | +0.008 ± 0.002 | +0.041 ± 0.003 |
| OTJ | 37773 | 1.81 | -0.405 ± 0.056 | +0.003 ± 0.002 | +0.034 ± 0.003 |
| PIO | 32895 | 1.11 | +0.275 ± 0.075 | +0.011 ± 0.004 | -0.004 ± 0.003 |
| SOS | 38685 | 1.99 | -0.223 ± 0.057 | -0.002 ± 0.002 | +0.040 ± 0.002 |
| TDM | 10435 | 1.63 | +0.627 ± 0.178 | +0.017 ± 0.008 | +0.021 ± 0.005 |
| TLA | 37959 | 1.34 | -0.600 ± 0.057 | +0.006 ± 0.002 | +0.035 ± 0.003 |
| TMT | 26640 | 1.64 | -0.566 ± 0.086 | +0.008 ± 0.004 | +0.036 ± 0.003 |
