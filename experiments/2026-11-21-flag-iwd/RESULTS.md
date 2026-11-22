# Removing the IWD premium, with the three-color flag on: results

Protocol: `PROTOCOL.md`. Run 44964368326 at `ab7d3a8` (upstream main `edfab59` plus
the flag), 19 sets, 8 salts (`r32s1` to `r32s8`) of 1000 drafts: 152,000 drafts,
117,872 complete events. Reports in `reports/`: `heads.md` (all sets), `high.md`
(the same script on KTK, TDM, SNC and DMU only), `by_set.md`.

## The verdict

**Handed over, by the rule.** None of the four readings is 2 SEs worse.

| reading | regret slope change (scaled SE), SEs | event wins per swapped pick (scaled SE), SEs |
|---|---|---|
| all 19 sets | -0.0007 (0.0001), -4.7 (better) | +0.048 (0.042), +1.1 (better side) |
| four high sets | +0.0005 (0.0003), +1.6 (worse side) | +0.036 (0.143), can't judge |

Positive regret is worse; negative event wins is worse. Top cards changed: 0.56% of
picks (0.59% in the high sets).

In the four high sets, event wins can't judge: an SE of 0.143 is about three times the
-0.05 a 40%-noise loss costs. So the high-set verdict rests on the regret slope alone,
at +1.6 SEs.

## Against the run without the flag

| run | all sets, regret | high sets, regret | all sets, event wins |
|---|---|---|---|
| 44009860514, no flag (2 salts x 6000) | -4.3 SEs | +2.3 SEs (+0.0004, SE 0.0002) | +0.028 (0.029) |
| this run, flag on (8 salts x 1000) | -4.7 SEs | +1.6 SEs (+0.0005, SE 0.0003) | +0.048 (0.042) |

The estimate in the high sets is about the same (+0.0004 then +0.0005); the reading fell
under 2 SEs because the SE is wider (the combined SE counts the spread between salts),
not because the flag removed the effect. My prediction that the flag would shrink it
was wrong on the estimate.

## Where it costs

By set (`by_set.md`): KTK +0.0006 (0.0003), SNC +0.0011 (0.0004), TDM -0.0002 (0.0006),
DMU +0.0001 (0.0006). In the fifteen other sets it is better by -0.0010 (0.0001), 6.7
SEs, and better or level in every one of them. The change against the three-color
share is a line at +0.0002 per 10 points of share, 5.5 SEs, and survives dropping TDM
or DMU.

So the premium does something useful in the three-color sets, mostly SNC and KTK, and
harm elsewhere. A version that keeps it only in sets the flag marks would likely beat
both. That is a reading of this table, not a test.

## Predictions

| prediction | result |
|---|---|
| all sets: regret better about -3 SEs, event wins no objection | right: -4.7, +1.1 |
| high sets: the 2.3 SEs shrinks under 2 | under 2 (+1.6), but the estimate didn't shrink; the SE grew |
| high-set event wins wide | right: can't judge |
