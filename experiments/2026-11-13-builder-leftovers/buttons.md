# Auto lands and Auto optimize at `505a0a0`

86712 decks in 19 sets. Skipped: {'not 40 cards': 7150, 'card not in dataset': 1138}.

## Auto lands: the simulation against the rule it starts from

The simulation's basics differ from the rule's in 80.1% of decks, by one land in 44.4% of those.

| basics chosen by | lands from the drafter's | same as the drafter's |
|---|---|---|
| the app's rule | 1.106 | 28.9% |
| Auto lands' simulation | 1.318 | 19.7% |
| share of pips | 1.635 | 14.9% |

- Simulation less rule, in lands from the drafter's: +0.212 [+0.141, +0.283]. Negative is nearer the drafter.
- Rule less pips: -0.528 [-0.671, -0.386].

Outcome, a full move from the rule's basics to the simulation's, in win rate points at the same card quality: +0.22 [+0.00, +0.44], on 69413 decks (40.2% played the rule's, 24.7% the simulation's).

## Auto optimize

It changes 96.6% of 86712 decks. Deck score change in win rate points, with the swaps of a spell for a land counted as zero (deciding): +0.079 [+0.048, +0.110].

| swap | decks | deck score change, win rate points |
|---|---|---|
| Curve Lower | 33.7% | -0.023 [-0.085, +0.039] |
| Optimize Mana | 21.3% | +0.000 [+0.000, +0.000] |
| Play 18 Lands | 13.7% | +0.058 [-0.682, +0.798] |
| Power Up | 12.1% | +0.792 [+0.735, +0.849] |
| Fix Mana Base | 9.0% | -0.097 [-0.140, -0.055] |
| Play 16 Lands | 6.8% | +0.869 [-0.189, +1.927] |
| Base Deck | 3.4% | +0.000 [+0.000, +0.000] |

Land count change: -1 in 6.8%, +0 in 79.5%, +1 in 13.7%.

## Verdicts

| feature | verdict |
|---|---|
| Auto lands' simulation | remove |
| Auto optimize | keep |
