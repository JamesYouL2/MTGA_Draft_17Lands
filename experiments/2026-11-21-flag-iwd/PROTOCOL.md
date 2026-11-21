# Removing the IWD premium, with the three-color flag on

Written before any result of this run was seen.

## Why

`no-iwd-premium` (fork `simplify/no-iwd-premium`) drops the 1.15x power bonus for a
card more than 1 SD above its pack with an IWD over 4.5. In
[removals-both-measures](https://github.com/JamesYouL2/MTGA_Draft_17Lands/blob/exp/removals-both-measures/experiments/2026-11-16-removals-both-measures/RESULTS.md)
(run 44009860514, 19 sets) it was better on the regret slope by 4.3 SEs and on the
better side of event wins (+0.028, SE 0.029), but worse by 2.3 SEs (+0.0004, SE
0.0002) in the four high three-color sets (TDM, DMU, SNC, KTK).

Those four sets are where the three-color flag (fork `feat/three-color-off-color-v2`)
softens the off-color penalty. The flag is to be proposed first, so the removal should
be judged on an advisor that has it.

## What runs

The Advisor heads workflow on this branch: base is upstream main (`edfab59`) plus the
flag commit; the one head, `no-iwd-premium`, is that branch's own diff to `src/` on top.
All 19 sets (BLB DFT DMU DSK EOE FDN FIN FRA HOB KTK LTR MSH NEO OTJ SNC SOS TDM TLA
TMT), 8 fresh salts of 1000 drafts (named after the run), held-out ratings, pools in
pick order. `heads.py` combines the salts (between-salt variance in the SE) for the
regret slope change (within-set z-scores) and event wins per swapped pick. The same
script, run on only the four high sets' results, gives the high-set reading.

## The decision rule

| reading | verdict |
|---|---|
| regret slope change worse by 2+ SEs, or event wins per swapped pick worse by 2+ SEs, over all 19 sets **or** over the four high sets | withdrawn: no link |
| none of these four readings | handed over, stacked after the flag |

"Worse" is a positive regret slope change or a negative event wins figure. A measure
whose SE is too wide to flag a 40%-noise-sized loss (event wins -0.05 a swapped pick)
is reported as "can't judge" and the verdict rests on the other measure.

## Predictions

- All 19 sets: regret slope better (about -3 SEs), event wins can't judge or no
  objection. Same as before.
- Four high sets: the flag softens off-color cards, so the premium matters less for
  pulling a bomb across colors; I expect the 2.3 SEs to shrink to under 2. Low
  confidence: the event wins SE in four sets will be wide.

## What it can't show

A removal changing about 0.5% of top cards can't be shown harmless on 152,000 drafts,
only shown not to be large harm.
