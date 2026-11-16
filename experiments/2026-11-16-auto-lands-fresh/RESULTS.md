# Auto lands on decks not seen before: results

Run [43918276362](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43918276362):
548,462 decks from 18 sets, none used by an earlier run. Full report in
[buttons.md](buttons.md). The rule is in [PROTOCOL.md](PROTOCOL.md), written before
the run.

## The answer

#270 stands. On fresh decks the simulation's basics are worth +0.04 win rate points
over the rule's, with a range of -0.12 to +0.20. That is 0.5 SEs. The +0.18 seen on
11-16 did not repeat.

## The three readings

A full move from the rule's basics to the simulation's, among decks where they differ,
at the same card quality:

| run | effect, win rate points | SEs |
|---|---|---|
| 11-13 | +0.10 [-0.02, +0.22] | 1.6 |
| 11-16, sharing decks with the first | +0.18 [+0.04, +0.32] | 2.5 |
| this run, fresh decks | +0.04 [-0.12, +0.20] | 0.5 |

This run's figure is from the 441,971 decks where the two differ.

By the rule, "neither": the simulation is not ahead by 2 SEs and not behind by 2.

The rule also still sits nearer what drafters played: 1.10 lands away on average
against the simulation's 1.33, and the same basics as the drafter in 29.5% of decks
against 19.4%.

## Predictions

| prediction | result |
|---|---|
| effect between +0.03 and +0.15, under 2 SEs | right: +0.04, 0.5 SEs |
| the simulation differs from the rule in about 80% of decks | right: 80.6% |

## What this does not settle

All three readings are positive, so a small real edge for the simulation, around 0.1
points, is still possible. Nothing here can tell 0.1 from zero. The decision was that
an edge that small, if real, does not buy back a slow simulation, and that holds.

One set, TMT, had no decks left after the earlier samples were set aside.
