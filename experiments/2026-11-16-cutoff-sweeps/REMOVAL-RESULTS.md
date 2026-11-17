# Removal results: lane share 0.05, or no threshold

Run [44038145486](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44038145486)
(Advisor heads, branch `run/cutoff-removal`, commit `efa4bdd`). Ten sets, new salts
`removal1` and `removal2`, 60,000 drafts and 45,483 complete events per head, held-out
ratings. Rules are in [REMOVAL.md](REMOVAL.md), committed before the run. Raw reports are in
[removal-report/](removal-report/).

Regret slope change: positive is worse for the head. Event wins per swapped pick:
positive is better for the head.

## Against today's 0.15

| head | regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs | top-card changes |
|---|---|---|---|---|---|
| lane-share-05 | +0.0025 (0.0025) | +1.0 | +0.034 (0.022) | +1.6 | 3.44% |
| lane-share-none | +0.0018 (0.0026) | +0.7 | +0.042 (0.020) | +2.1 | 3.65% |

By sample, 0.05: removal1 +0.0023 (0.0031), removal2 +0.0029 (0.0036). No threshold:
removal1 +0.0010 (0.0033), removal2 +0.0028 (0.0037).

## No threshold against 0.05, head to head

| regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs | top-card changes |
|---|---|---|---|---|
| -0.0007 (0.0005) | -1.4 | +0.126 (0.062) | +2.0 | 0.31% |

## Verdict by the rules

- **0.05 isn't confirmed.** It beats 0.15 on neither measure by 2 SEs: event wins +1.6
  SEs, regret slope +1.0 SEs (the wrong way, though not flagged).
- So, by the addendum's fallback, the removal is judged against 0.15 by the confirmation
  rule. **It passes, barely.** Event wins is +2.1 SEs (2.10 before rounding), and the
  regret slope reads +0.7 SEs, the wrong way but not flagged.
- Head to head, the removal isn't worse than 0.05 on either measure. It leans better on
  both: event wins +2.0 SEs, regret -1.4 SEs. The simplification rule would have
  preferred it too.

By the written rules, then, removing the threshold is preferred over today's 0.15. It is a
borderline pass, and the regret slope disagrees in direction, so read it with the cautions
below.

## Cautions

**The effect has shrunk run by run.** For the low-threshold heads against today's:

| run | head | regret SEs | event wins SEs |
|---|---|---|---|
| sweep (sweep1, sweep2) | 0.10 | -4.2 | +5.0 |
| confirmation (confirm1, confirm2) | 0.10 | -1.8 | +3.4 |
| confirmation | 0.05 | -2.6 | +5.5 |
| removal (removal1, removal2) | 0.05 | +1.0 | +1.6 |
| removal | none | +0.7 | +2.1 |

The regret slope now points the other way. Pooling 0.05's two runs by inverse variance
gives:
- regret slope -0.0021 (0.0016), -1.3 SEs;
- event wins +0.073 (0.014), +5.1 SEs.

Event wins has stayed positive in every run, while the regret slope has not. Event wins is
also the measure that caught 20% noise in the measure-power test.

**The removal puts near-empty colors in the lane.** From 15 cards, the lane is always
three colors. On 4.1% of picks the third has no non-land cards in the pool, and on 14.5% it
has under 5% of them. At 0.05 both are 0.01% or less, and today they are 0.00%.

The reason is that `sorted_w` holds all five colors, so a color with zero weight fills the
third slot whenever only two colors carry weight. The advisor then treats that color's
cards as on-lane. A PR would want a guard, such as dropping colors with zero weight; that
guard has not been tested. The removal still matched or beat 0.05 head to head, so the
empty third color doesn't show as harm on either measure here.

## The four high three-color sets against the other six

The high four are TDM, FRA, TLA and SOS. Only TDM is above 20%; the other three are around
15%.

| base | head | sets | regret slope change (SE) | SEs | event wins (SE) | SEs |
|---|---|---|---|---|---|---|
| 0.15 | 0.05 | high four | +0.0010 (0.0033) | +0.3 | +0.029 (0.034) | +0.9 |
| 0.15 | 0.05 | other six | +0.0036 (0.0033) | +1.1 | +0.036 (0.022) | +1.6 |
| 0.15 | none | high four | +0.0000 (0.0034) | +0.0 | +0.042 (0.034) | +1.2 |
| 0.15 | none | other six | +0.0030 (0.0034) | +0.9 | +0.043 (0.022) | +1.9 |
| 0.05 | none | high four | -0.0010 (0.0006) | -1.7 | +0.231 (0.122) | +1.9 |
| 0.05 | none | other six | -0.0006 (0.0007) | -0.8 | +0.095 (0.075) | +1.3 |

No group reaches 2 SEs, and the two groups agree in direction. By set, the regret
changes against today's lean worse in MSH and DFT and better in FIN (each about 2 SEs,
with ten sets tested).

## Third-color frequency

This is the share of picks with a three-color lane, on the same picks for all three
advisors:

| cards in pool | picks | 0.15 (today) | 0.05 | no threshold |
|---|---|---|---|---|
| 0 to 14 | 827,434 | 42.1% | 42.1% | 42.1% |
| 15 to 19 | 299,600 | 44.0% | 94.2% | 100.0% |
| 20 to 24 | 299,503 | 38.8% | 87.3% | 100.0% |
| 25 to 29 | 239,512 | 39.6% | 88.9% | 100.0% |
| 30 to 34 | 299,360 | 37.8% | 92.0% | 100.0% |
| 35+ | 357,964 | 35.3% | 92.4% | 100.0% |

The share of picks that gain a third color over today's is 49% to 57% at 0.05 and 56% to 65%
with no threshold, from 15 cards. 80.7% and 82.7% of drafts gain one at some pick; the
median draft first gains one at 15 cards for both.

## Predictions (REMOVAL.md)

| prediction | outcome |
|---|---|
| 0.05 confirmed, with smaller effects | wrong: not confirmed (+1.0 and +1.6 SEs) |
| removal within 2 SEs of 0.05 on both, so preferred | right on preference; event wins is +2.0 SEs in the removal's favor |
| about 98% of picks with three-color lanes, no threshold | right in spirit: 100% |
| a lane color with no cards on under 1% of picks | wrong: 4.1% |
| a color under 5% on a few percent of picks | wrong: 14.5% |

## Caveats

- These are associations among drafters who chose freely, as in every held-out replay.
- The removal's pass is a single run at 2.1 SEs, on one measure.
- The tested removal has no guard against empty colors. A guarded version is a different
  head.
