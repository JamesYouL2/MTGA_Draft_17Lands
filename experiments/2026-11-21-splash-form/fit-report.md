# Deck score fit at `a7e60b6`

## Data

914655 decks and 4136676 games from 20 sets (BLB, Cube_-_Powered, DFT, DMU, DSK, EOE, FDN, FIN, FRA, HOB, LTR, MH3, MSH, NEO, OTJ, PIO, SOS, TDM, TLA, TMT). 16844 unfinished decks were left out.

## Weights

In score points. A weight within two SEs of 0 is marked ~0.

| feature | decks it applies to | app's weight | fitted weight |
|---|---|---|---|
| card_quality | 100.0% | +12.0 | +12.0 |
| splash | 30.9% | -1.4 | -1.5 ± 0.1 |
| splash_spells | 30.6% | -0.4 | -0.4 ± 0.0 |
| three_colors | 11.2% | -3.3 | -3.3 ± 0.1 |
| four_colors | 8.8% | -4.9 | -5.0 ± 0.1 |
| missing_fixing | 2.6% | -2.5 | -0.2 ± 0.1 ~0 (not used: the app's weight is kept) |

## Weights fit on each set alone

If these agree, one set of weights can serve every set.

| feature | BLB | Cube_-_Powered | DFT | DMU | DSK | EOE | FDN | FIN | FRA | HOB | LTR | MH3 | MSH | NEO | OTJ | PIO | SOS | TDM | TLA | TMT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| splash | -1.0 | -0.5 | -1.3 | -1.0 | -1.4 | -1.8 | -2.0 | -0.9 | -2.0 | -1.0 | -2.6 | -0.8 | -0.6 | -1.8 | -1.6 | -2.8 | -1.5 | -1.2 | -0.2 | -1.2 |
| splash_spells | -0.8 | +0.1 | -0.8 | -0.4 | -0.3 | -0.1 | +0.0 | -0.5 | -0.4 | -0.2 | +0.1 | -0.6 | -0.2 | -0.7 | -0.5 | -0.7 | -0.7 | -0.6 | -0.2 | -0.6 |
| three_colors | -4.8 | -5.4 | -3.7 | -2.9 | -2.7 | -2.5 | -3.7 | -3.4 | -3.4 | -3.6 | -3.6 | -2.7 | -2.1 | -4.2 | -3.1 | -6.3 | -4.3 | -3.1 | -1.9 | -4.4 |
| four_colors | -7.0 | -5.2 | -4.1 | -4.0 | -4.1 | -3.3 | -8.1 | -4.1 | -6.7 | -8.4 | -3.3 | -4.5 | -1.9 | -5.3 | -4.7 | -6.7 | -5.3 | -6.6 | -2.6 | -4.3 |
| missing_fixing | +0.4 | – | +0.1 | -0.3 | -2.0 | -0.9 | -1.8 | -0.8 | -1.7 | -3.4 | -0.4 | -0.5 | -0.6 | -0.5 | -1.7 | -2.5 | -1.0 | +0.3 | -0.1 | -0.7 |

## On sets the fit didn't see

Each set is scored by models fit on the other sets. *Spread*: the game win rate of the top fifth of decks by score, less the bottom fifth's; higher is better. *Log loss*: per game, lower is better.

| model | spread | log loss |
|---|---|---|
| card quality only | 12.8% | 0.67273 |
| app's current weights | 13.8% | 0.67220 |
| fitted weights | 13.9% | 0.67216 |
| LightGBM (yardstick) | 14.1% | 0.67203 |

Spread by set:

| model | BLB | Cube_-_Powered | DFT | DMU | DSK | EOE | FDN | FIN | FRA | HOB | LTR | MH3 | MSH | NEO | OTJ | PIO | SOS | TDM | TLA | TMT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| card quality only | 10.9% | 9.6% | 11.9% | 11.5% | 14.4% | 12.4% | 13.8% | 13.2% | 11.9% | 13.5% | 13.5% | 14.6% | 14.0% | 12.7% | 12.5% | 12.6% | 12.5% | 10.8% | 13.7% | 14.1% |
| app's current weights | 11.8% | 13.9% | 12.4% | 12.8% | 15.5% | 13.1% | 14.4% | 14.5% | 13.4% | 14.0% | 13.7% | 16.2% | 14.0% | 14.2% | 13.6% | 14.8% | 14.9% | 12.1% | 13.0% | 15.1% |
| fitted weights | 11.9% | 13.9% | 12.4% | 12.9% | 15.4% | 13.1% | 14.4% | 14.5% | 13.3% | 14.0% | 13.7% | 16.1% | 14.1% | 14.2% | 13.7% | 14.7% | 14.9% | 12.6% | 13.4% | 15.4% |
| LightGBM (yardstick) | 12.5% | 11.4% | 12.6% | 13.2% | 15.4% | 13.4% | 15.0% | 14.6% | 13.7% | 14.0% | 14.5% | 15.6% | 14.1% | 15.0% | 13.6% | 14.9% | 15.1% | 13.1% | 12.9% | 15.5% |

## Records

Game win rate by score, fit on the score alone (the app doesn't know the player), and the expected wins in a Premier Draft event.

| score | decks at or below | game win rate | expected wins |
|---|---|---|---|
| 55 | 0% | 29.7% | 1.3 |
| 60 | 0% | 35.3% | 1.6 |
| 65 | 0% | 41.2% | 2.1 |
| 70 | 5% | 47.5% | 2.6 |
| 75 | 37% | 53.8% | 3.3 |
| 80 | 87% | 59.9% | 3.9 |
| 85 | 100% | 65.8% | 4.6 |
| 90 | 100% | 71.3% | 5.3 |
| 95 | 100% | 76.1% | 5.8 |

## For deck_scorer.py

```python
WEIGHTS = {
    "card_quality": 12.0,
    "splash": -1.5,
    "splash_spells": -0.4,
    "three_colors": -3.3,
    "four_colors": -5.0,
    "missing_fixing": -2.5,
    "missing_spells": -10.0,
}
WIN_LOG_ODDS_AT_BASE = 0.1503
WIN_LOG_ODDS_PER_POINT = 0.05048
```
