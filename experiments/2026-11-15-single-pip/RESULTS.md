# Single-pip and double-pip softening: results

Protocol: `PROTOCOL.md`. Reports: `heads.md`, `by_set.md`. 228,000 drafts from 19 sets,
held-out ratings, pools in pick order.

## The verdict

**The flag stays as built.** The double-pip idea was wrong: the harm of softening in
low-share sets is in the single-pip cards, the same cards that carry the gain in
high-share sets.

| head | the four sets over 30% (SE) | the other fifteen (SE) | top card changes |
|---|---|---|---|
| `soft-single` | -0.0115 (0.0029), better at 3.9 SEs | +0.0070 (0.0015), worse at 4.7 SEs | 4.98% |
| `soft-double` | +0.0003 (0.0009) | -0.0004 (0.0004) | 0.69% |
| `soft-all` | -0.0124 (0.0030), better at 4.1 SEs | +0.0064 (0.0015), worse at 4.1 SEs | 5.44% |

Negative is better for the head.

- `soft-single` is worse by 4.7 SEs in the fifteen, which is the protocol's third row.
- `soft-double` does almost nothing anywhere. Double-pip off-color cards are too far
  down for a tenfold lift to reach the top of a pack: it changes the top card on 0.69%
  of picks.
- So the pattern found in `experiments/2026-11-15-what-sorts-sets` (softening hurting
  where a set has more double-pip cards) was chance, or stands in for something else.

## What this run adds for the flag

It is the largest test of the share so far, on drafts no earlier run used, and it
agrees with all of them.

- **Across 19 sets, softening does better as the share rises:** -0.0031 per 10 points
  of share (SE 0.0005), 6.3 SEs. Without TDM it is 6.5 SEs, and without DMU 6.0.
- **All four sets over 30% are on the better side again:** KTK -0.0271, DMU -0.0099,
  SNC -0.0090, TDM -0.0048.
- **Softening everywhere is a clear loss:** +0.0086 on all sets together, 5.9 SEs.
- **The six sets around 20% are all within 1.2 SEs of zero this time** (TMT -0.0084,
  OTJ -0.0034, FIN +0.0009, FRA +0.0020, TLA +0.0043, SOS +0.0070). The threshold test's
  large swings between them did not repeat, which supports leaving the threshold at 30%.

## The predictions

| | predicted | found |
|---|---|---|
| `soft-double` | worse by 2+ SEs in the fifteen | no effect: wrong |
| `soft-single` | within 2 SEs in the fifteen, better in the four | worse at 4.7 SEs in the fifteen, better in the four: half wrong |
| `soft-all` | better in the four, worse in the fifteen | yes |
