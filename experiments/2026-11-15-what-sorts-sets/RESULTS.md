# What sorts the sets where a softer off-color penalty helps

Exploratory, with no protocol: seven features were tried on 19 sets after the results
were known, so some correlation is expected by chance. It is here as the reason for the
next test, not as a finding to build on.

`features.py` joins each set's change from `softer` (pooled over the four off-color
runs, 19 sets) to features of its app dataset. Output: `features.md`, `features.json`.

| feature | correlation, all 19 sets | the 15 sets under a 30% share |
|---|---|---|
| win rate of 3+-color decks minus 2-color decks | -0.70 | -0.57 |
| games played with gold cards | -0.62 | -0.37 |
| multicolor lands, by games | -0.59 | -0.19 |
| three-color share | -0.56 | -0.53 |
| fixing cards, by games | -0.52 | -0.17 |
| hybrid-cost cards, by games | -0.01 | -0.37 |
| colored cards with two pips of one color, by games | +0.48 | +0.41 |

Negative: the more of it, the more softening helps.

- **Fixing and hybrid cards don't sort the sets.** What they show comes from the four
  high-share sets.
- **The gap between three-color and two-color decks' win rates explains most.** With
  it in a weighted fit, the three-color share adds nothing (0.3 SEs). It still gets
  FRA wrong (small gap, softening hurts) and OTJ and TLA (large gaps, it helps).
- **Double-pip cards sort the six sets of the threshold test:** softening helps at
  13.6% or less (TMT, OTJ, TLA) and hurts at 14.9% or more (FRA, SOS, FIN). Found after
  the fact, with a thin margin.
- **Much is unexplained.** The best two-feature fit leaves a chi-squared of 50 on 16
  degrees of freedom.

## The lead

`softer` lifts every off-color multiplier, including "Uncastable (Double Pip)", from
0.01 to 0.1. A set with many double-pip cards gets more of them promoted. So the harm
may be in the double-pip cards and the gain in the single-pip ones. That is tested in
`experiments/2026-11-15-single-pip`.
