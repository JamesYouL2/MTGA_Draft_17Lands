# Auto lands and Auto optimize at `c4253e2`

346299 decks in 19 sets. Skipped: {'not 40 cards': 28900, 'card not in dataset': 4800, 'no basics': 1}.

## Auto lands: the simulation against the rule it starts from

The simulation's basics differ from the rule's in 80.2% of decks, by one land in 43.9% of those.

| basics chosen by | lands from the drafter's | same as the drafter's |
|---|---|---|
| the app's rule | 1.108 | 28.7% |
| Auto lands' simulation | 1.321 | 19.5% |
| share of pips | 1.636 | 14.9% |

- Simulation less rule, in lands from the drafter's: +0.213 [+0.143, +0.283]. Negative is nearer the drafter.
- Rule less pips: -0.529 [-0.670, -0.387].

Outcome, a full move from the rule's basics to the simulation's, in win rate points at the same card quality: +0.18 [+0.04, +0.32], on 277852 decks (40.0% played the rule's, 24.6% the simulation's).

## Auto optimize

It changes 96.4% of 346299 decks. Deck score change in win rate points, with the swaps of a spell for a land counted as zero (deciding): +0.076 [+0.045, +0.108].

| swap | decks | deck score change, win rate points |
|---|---|---|
| Curve Lower | 33.8% | -0.031 [-0.094, +0.031] |
| Optimize Mana | 21.2% | +0.000 [+0.000, +0.000] |
| Play 18 Lands | 13.8% | +0.052 [-0.704, +0.807] |
| Power Up | 11.9% | +0.808 [+0.758, +0.858] |
| Fix Mana Base | 9.1% | -0.096 [-0.132, -0.061] |
| Play 16 Lands | 6.8% | +0.805 [-0.193, +1.803] |
| Base Deck | 3.6% | +0.000 [+0.000, +0.000] |

Land count change: -1 in 6.8%, +0 in 79.5%, +1 in 13.8%.

## Verdicts

| feature | verdict |
|---|---|
| Auto lands' simulation | keep |
| Auto optimize | keep |
