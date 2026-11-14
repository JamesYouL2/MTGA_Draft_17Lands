# Auto lands and Auto optimize at `505a0a0`

857818 decks in 19 sets. Skipped: {'not 40 cards': 71078, 'card not in dataset': 10577, 'no basics': 15}.

## Auto lands: the simulation against the rule it starts from

The simulation's basics differ from the rule's in 80.3% of decks, by one land in 43.9% of those.

| basics chosen by | lands from the drafter's | same as the drafter's |
|---|---|---|
| the app's rule | 1.104 | 28.8% |
| Auto lands' simulation | 1.320 | 19.5% |
| share of pips | 1.633 | 14.9% |

- Simulation less rule, in lands from the drafter's: +0.216 [+0.146, +0.286]. Negative is nearer the drafter.
- Rule less pips: -0.529 [-0.672, -0.387].

Outcome, a full move from the rule's basics to the simulation's, in win rate points at the same card quality: +0.10 [-0.02, +0.22], on 689209 decks (40.2% played the rule's, 24.5% the simulation's).

## Auto optimize

It changes 96.5% of 857818 decks. Deck score change in win rate points, with the swaps of a spell for a land counted as zero (deciding): +0.077 [+0.047, +0.108].

| swap | decks | deck score change, win rate points |
|---|---|---|
| Curve Lower | 33.8% | -0.029 [-0.090, +0.032] |
| Optimize Mana | 21.1% | +0.000 [+0.000, +0.000] |
| Play 18 Lands | 13.7% | +0.041 [-0.730, +0.812] |
| Power Up | 12.0% | +0.804 [+0.752, +0.856] |
| Fix Mana Base | 9.1% | -0.100 [-0.141, -0.060] |
| Play 16 Lands | 6.8% | +0.809 [-0.195, +1.813] |
| Base Deck | 3.5% | +0.000 [+0.000, +0.000] |

Land count change: -1 in 6.8%, +0 in 79.5%, +1 in 13.7%.

## Verdicts

| feature | verdict |
|---|---|
| Auto lands' simulation | remove |
| Auto optimize | keep |
