# Auto lands and Auto optimize at `f690897`

548462 decks in 18 sets. Skipped: {'not 40 cards': 44133, 'no basics': 2, 'card not in dataset': 3590}.

## Auto lands: the simulation against the rule it starts from

The simulation's basics differ from the rule's in 80.6% of decks, by one land in 43.5% of those.

| basics chosen by | lands from the drafter's | same as the drafter's |
|---|---|---|
| the app's rule | 1.100 | 29.5% |
| Auto lands' simulation | 1.329 | 19.4% |
| share of pips | 1.604 | 15.4% |

- Simulation less rule, in lands from the drafter's: +0.228 [+0.147, +0.310]. Negative is nearer the drafter.
- Rule less pips: -0.504 [-0.673, -0.334].

Outcome, a full move from the rule's basics to the simulation's, in win rate points at the same card quality: +0.04 [-0.12, +0.20], on 441971 decks (40.4% played the rule's, 23.8% the simulation's).

## Auto optimize

It changes 96.4% of 548462 decks. Deck score change in win rate points, with the swaps of a spell for a land counted as zero (deciding): +0.065 [+0.035, +0.095].

| swap | decks | deck score change, win rate points |
|---|---|---|
| Curve Lower | 33.5% | -0.052 [-0.114, +0.009] |
| Optimize Mana | 21.7% | +0.000 [+0.000, +0.000] |
| Play 18 Lands | 13.4% | +0.140 [-0.687, +0.967] |
| Power Up | 11.7% | +0.788 [+0.739, +0.838] |
| Fix Mana Base | 9.2% | -0.108 [-0.158, -0.059] |
| Play 16 Lands | 6.8% | +0.709 [-0.456, +1.874] |
| Base Deck | 3.6% | +0.000 [+0.000, +0.000] |

Land count change: -1 in 6.8%, +0 in 79.8%, +1 in 13.4%.

## Verdicts

| feature | verdict |
|---|---|
| Auto lands' simulation | remove |
| Auto optimize | keep |
