# Lane share 0.10 and wheel tiebreak 0.15, together: results

Advisor heads run 44963810815 on the fork, at `547af95` (current `origin/main`
`edfab59` plus the heads tooling). Ten sets, 8 fresh salts (`r31s1` to `r31s8`) x 1000
drafts: 80,000 drafts, 60,823 complete events. Rule and predictions in
[PROTOCOL.md](PROTOCOL.md), written before the run. Reports in `reports/`.

## Heads

Regret slope change: positive is worse. Event wins per swapped pick: negative is worse.
Estimate (scaled SE), scaled SEs.

| head | regret slope change | event wins per swapped pick | `heads.py` | top card changes |
|---|---|---|---|---|
| `lane-share-0.10` | -0.0014 (0.0018), -0.8 | +0.042 (0.027), +1.6 | no objection | 2.19% |
| `wheel-0.15` | -0.0004 (0.0002), -1.7 | +0.086 (0.049), +1.8 | no objection | 1.03% |
| `lane-wheel` | -0.0019 (0.0019), -1.0 | +0.048 (0.023), +2.2 | adopt | 3.13% |
| `lane-wheel` against `lane-share-0.10` | -0.0005 (0.0002), -1.9 | +0.111 (0.050), +2.2 | adopt | 1.00% |
| `lane-wheel` against `wheel-0.15` | -0.0015 (0.0019), -0.8 | +0.044 (0.027), +1.6 | no objection | 2.14% |

## Verdict by the rule

1. `lane-wheel` against base: adopt (event wins +2.2, regret on the better side). Holds.
2. `lane-wheel` against each single: on the better side of both measures against both.
   Holds.

**Both changes are proposed**, as two stacked PRs: lane share first, then the wheel
tiebreak. The wheel PR's own evidence is `lane-wheel` against `lane-share-0.10`, which
passes on its own (event wins +2.2, regret -1.9).

## Predictions

| prediction | result |
|---|---|
| `lane-wheel` adopts, on the wheel's regret and the lane's event wins | adopts, on event wins only (+2.2); regret -1.0 |
| against each single within 1.5 SEs | better side on all four; two at about 2 SEs better |
| about 3% top card changes | 3.13% |

## Reading

- This run is a third the size of the 11-17 re-read (8 x 1000 against 8 x 3000 drafts
  per set), so neither single passes alone here. Both point the same way as before on
  both measures.
- Pooled with the 11-17 re-read (independent salts, inverse variance; not in the
  protocol): lane share event wins +0.036 (0.013), 2.7 SEs, regret -1.3 SEs; wheel regret
  -0.0004 (0.0001), 4.5 SEs, event wins +0.064 (0.025), 2.6 SEs.
- The two changes add up: top card changes 3.13% against 2.19% + 1.03%; the joint's
  regret change is larger than either single's, and against each single it is on the
  better side. (Event wins per swapped pick is a rate per changed pick, so the joint's
  +0.048 under the wheel's +0.086 reflects the mix of changes, not a loss.)
- By set (for reading only): the wheel tiebreak's regret is better in seven of ten sets,
  clearest in FRA (-0.0023, 0.0006), worse in SOS (+0.0012, 0.0005). Neither change
  tracks the three-color share.
- When the wheel tiebreak changes the top card, drafters took the head's card 40.6% of
  the time and the base's 10.2%: it mostly breaks near-ties toward the card that
  drafters, who could see what wheels, took.

## What this can't show

The replay can't play out the wheel: a card passed now is not added to the pool if it
comes back. The gain is from following drafters' choices and their results, not from a
simulated second chance at the passed card. The wheel chance itself comes from ALSA and
assumes eight players and one card a pick; Pick-Two and other pod sizes get no chance
and so no tiebreak.
