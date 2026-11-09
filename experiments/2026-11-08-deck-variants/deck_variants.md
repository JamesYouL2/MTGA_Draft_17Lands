# Deck variants at `8acc28c`

928062 pools in 19 sets; 4199344 games. Skipped: {'pool under 35 cards': 19, 'card not in dataset': 11407}.

## How often it changes what's shown, against today's

With the simulator off on every pool, and on for the first pools of each set. **Top 2** counts either of the first two changing.

| version | pools | top deck | top 2 | list shown |
|---|---|---|---|---|
| no-tempo | 928062 | 0.12% | 34.55% | 71.43% |
| no-promotion | 928062 | 10.30% | 11.63% | 0.00% |
| neither | 928062 | 10.40% | 46.17% | 71.43% |
| sim-no-tempo | 9397 | 65.56% | 87.34% | 92.05% |
| sim-no-promotion | 9397 | 5.88% | 6.89% | 0.00% |
| sim-neither | 9397 | 68.63% | 91.28% | 92.05% |

## Which build comes first

Share of pools, on the pools each ran on. `sim` is today's app.

| version | build | pools |
|---|---|---|
| blend | Safe Core | 90.0% |
| blend | Splash | 7.3% |
| blend | Good Stuff (Soup) | 2.7% |
| sim | Safe Tempo | 60.6% |
| sim | Safe Core | 28.3% |
| sim | Splash | 8.2% |
| sim | Good Stuff (Soup) | 2.9% |

On the 9397 pools run both ways, the simulator's penalties change the top deck in 71.5% and its pair in 10.2%.

### By set, top deck, simulator off

| set | no-tempo | no-promotion |
|---|---|---|
| BLB | 0.15% | 3.53% |
| DFT | 0.06% | 8.01% |
| DMU | 0.02% | 28.96% |
| DSK | 0.03% | 6.25% |
| EOE | 0.12% | 4.59% |
| FDN | 0.27% | 4.46% |
| FIN | 0.21% | 7.68% |
| FRA | 0.03% | 12.01% |
| HOB | 0.26% | 2.48% |
| LTR | 0.10% | 5.60% |
| MH3 | 0.02% | 14.62% |
| MSH | 0.10% | 8.92% |
| NEO | 0.19% | 3.60% |
| OTJ | 0.04% | 11.31% |
| PIO | 0.22% | 14.64% |
| SOS | 0.00% | 17.04% |
| TDM | 0.00% | 25.09% |
| TLA | 0.34% | 6.71% |
| TMT | 0.05% | 10.76% |

## Tempo: playing nearer its cards

Among two-color decks where the pair's Tempo and Consistent builds differ, a full move from Consistent's cards to Tempo's, in win rate points, within the pair in the set, with the player controlled.

- At the same card quality (deciding): +0.34 [+0.11, +0.57], on 707816 decks.
- Without controlling for it: -1.27 [-1.49, -1.05].

## Promotion: drafters in the safe deck's colors against the top's

Promotion changes the top deck's colors in 93993 pools. 7767 decks played the safe colors at 52.2%, and 51796 the top's at 54.4%.

Effect in win rate points, safe over the top's, set and player controlled: -0.28 [-1.00, +0.44].

## Verdicts

Top deck change is with the simulator off. A remove that rests on it holds once the mana penalties are gone: see the protocol's amendment.

| feature | top deck changes | outcome | verdict |
|---|---|---|---|
| Tempo build | 0.12% | +0.34 [+0.11, +0.57] | keep |
| Safe-deck promotion | 10.30% | -0.28 [-1.00, +0.44] | no verdict |
