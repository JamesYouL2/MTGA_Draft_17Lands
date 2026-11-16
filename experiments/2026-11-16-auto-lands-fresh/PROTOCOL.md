# Auto lands: the simulation against the rule, on decks not seen before

Written before any result of this run was seen.

## Why

#270 (merged) made Auto lands use the mana base rule and dropped the simulation around
it. It rested on `experiments/2026-11-13-builder-leftovers`: among decks where the two
disagree, a full move from the rule's basics to the simulation's was worth
+0.10 [-0.02, +0.22] win rate points, short of 2 SEs, and the rule sat nearer what
drafters played.

On 11-16 the same measure on four times the decks came out at +0.18 [+0.04, +0.32],
2.5 SEs. By the 11-13 rule that would have kept the simulation. But that run was not
set up to re-decide it and shares decks with the first.

## What runs

The Deck builds workflow, buttons only, on decks none of the earlier runs used. The
sampler leaves out the 11-13 samples (salts `""` and `two`, 50,000 decks a set) and
the decks the 11-16 run put through the buttons (salt `three`, the first 20,000 of
100,000), then takes up to 40,000 of what is left in each set, salt `four`. Sets with
under about 60,000 decks will have few or none left.

Source is this branch, whose `src/` is upstream main at `6b6dba9`: it still has the
simulation, which is what lets the two be compared.

## The measure

`buttons_report.py`'s, unchanged: among decks where the simulation's basics differ
from the rule's, the effect of a full move from the rule's to the simulation's on win
rate, with card quality, set and the player held equal, SEs clustered by set.

## The decision rule

| the simulation over the rule | verdict |
|---|---|
| ahead by 2+ SEs | the simulation helps. #270 is reverted, and I prepare the pull request |
| behind by 2+ SEs | #270 stands, firmly |
| neither | #270 stands. Two readings near +0.1 to +0.2 and a third that doesn't confirm them is not enough to bring back a slow simulation |

This sample decides alone. It is not pooled with the earlier two, which is what makes
it a test of them.

## Predictions

- The effect is positive and under 2 SEs: between +0.03 and +0.15.
- The simulation differs from the rule in about 80% of decks, as before.

## What it can't show

It is observational. Drafters whose basics sit nearer the simulation's may differ from
the rest in ways card quality and the player's buckets miss. And the simulation
differs from the rule by one land in under half the decks where they differ, so "a
full move" is often more than a user would see.
