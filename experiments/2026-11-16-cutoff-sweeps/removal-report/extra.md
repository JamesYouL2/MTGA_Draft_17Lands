
## no threshold against 0.05, head to head

lane-share-05 is the base here. Regret: positive is worse for no threshold. Event wins: positive is better for no threshold.

| regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs | top card changes |
|---|---|---|---|---|
| -0.0007 (0.0005) | -1.4 | +0.126 (0.062) | +2.0 | 0.31% |

By sample: removal1: -0.0012 (0.0007), removal2: -0.0001 (0.0006)

## The four high three-color sets against the other six

High: FRA, SOS, TDM, TLA. Regret: positive is worse for the head. Event wins: positive is better for the head.

| base | head | sets | events | regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs |
|---|---|---|---|---|---|---|---|
| 0.15 (today) | 0.05 | high four | 18030 | +0.0010 (0.0033) | +0.3 | +0.029 (0.034) | +0.9 |
| 0.15 (today) | 0.05 | other six | 27453 | +0.0036 (0.0033) | +1.1 | +0.036 (0.022) | +1.6 |
| 0.15 (today) | no threshold | high four | 18030 | +0.0000 (0.0034) | +0.0 | +0.042 (0.034) | +1.2 |
| 0.15 (today) | no threshold | other six | 27453 | +0.0030 (0.0034) | +0.9 | +0.043 (0.022) | +1.9 |
| 0.05 | no threshold | high four | 18030 | -0.0010 (0.0006) | -1.7 | +0.231 (0.122) | +1.9 |
| 0.05 | no threshold | other six | 27453 | -0.0006 (0.0007) | -0.8 | +0.095 (0.075) | +1.3 |

## What the threshold does

60000 drafts, picks all three replays scored. The threshold acts only from 15 cards in the pool.

Share of picks where the advisor's lane has three main colors:

| cards in pool | picks | 0.15 (today) | 0.05 | no threshold |
|---|---|---|---|---|
| 0 to 14 | 827434 | 42.1% | 42.1% | 42.1% |
| 15 to 19 | 299600 | 44.0% | 94.2% | 100.0% |
| 20 to 24 | 299503 | 38.8% | 87.3% | 100.0% |
| 25 to 29 | 239512 | 39.6% | 88.9% | 100.0% |
| 30 to 34 | 299360 | 37.8% | 92.0% | 100.0% |
| 35+ | 357964 | 35.3% | 92.4% | 100.0% |

Share of picks where the lane has more main colors than today's (it gains a third color):

| cards in pool | 0.05 | no threshold |
|---|---|---|
| 0 to 14 | 0.0% | 0.0% |
| 15 to 19 | 50.2% | 56.0% |
| 20 to 24 | 48.5% | 61.2% |
| 25 to 29 | 49.3% | 60.4% |
| 30 to 34 | 54.2% | 62.2% |
| 35+ | 57.0% | 64.7% |

- 0.05: 80.7% of drafts gain a third color at some pick; first at a median of 15 cards (quartiles 15 to 19).
- no threshold: 82.7% of drafts gain a third color at some pick; first at a median of 15 cards (quartiles 15 to 17).
## Thin colors in the lane, from 15 cards

Share of picks where the lane's thinnest color has no non-land cards, or under 5% or 10% of the non-land cards counted over all colors:

| threshold | picks | no cards | under 5% | under 10% | lane of three |
|---|---|---|---|---|---|
| 0.15 (today) | 1495939 | 0.00% | 0.01% | 0.20% | 38.9% |
| 0.05 | 1495939 | 0.00% | 0.01% | 30.77% | 91.1% |
| no threshold | 1495939 | 4.11% | 14.48% | 41.30% | 100.0% |

