# Where the flag's threshold belongs: results

Protocol: `PROTOCOL.md`. Reports: `heads.md`, `by_set.md`. 144,000 drafts from six sets,
108,514 complete events, held-out ratings, pools in pick order.

## The verdict

By the letter of the rule the threshold moves to 20%. I recommend leaving it at 30%:
the four sets disagree with each other far more than their SEs allow, so their average
isn't a fact about sets at that share.

| set | app's share | `softer` (SE) | SEs | first test |
|---|---|---|---|---|
| FRA | 24% | +0.0065 (0.0049) | +1.3 | -0.0030 |
| OTJ | 24% | -0.0124 (0.0040) | -3.1 | -0.0036 |
| TMT | 23% | -0.0204 (0.0045) | -4.5 | -0.0250 |
| SOS | 22% | +0.0106 (0.0049) | +2.2 | +0.0046 |
| TLA | 19% | -0.0091 (0.0041) | -2.2 | +0.0014 |
| FIN | 15% | +0.0085 (0.0043) | +2.0 | +0.0074 |

Negative is better for softening.

**The rule.** The four sets at 22% to 24%, weighted by their SEs: -0.0055 (SE 0.0023),
2.4 SEs better. The three without TMT: -0.0004 (SE 0.0026), on the better side by a
hair. Both conditions hold.

**Why I wouldn't act on it.**

- The four are not one population. Two are clearly better (OTJ, TMT) and two are worse
  (FRA at 1.3 SEs, SOS at 2.2), with a chi-squared of 30.7 on 3 degrees of freedom.
  Treating the set as the unit, the mean is -0.0039 with an SE of about 0.0074: half an
  SE.
- The share doesn't sort them. All four are within two points of each other, and the
  two sets just below split the same way (TLA better, FIN worse).
- Moving the threshold would turn softening on in FRA, the current set, and SOS, where
  it is worse. SOS was worse in both tests, and TMT better in both, so these look like
  real differences between sets, not noise.
- The "without TMT" condition was meant to guard against one set carrying the result.
  -0.0004 passes it in name only.

So what the run shows is that below about 30%, whether softening helps is a property
of the set that the three-color share doesn't capture. The flag at 30% is unaffected:
all four sets above it were at or below zero, three of them strongly.

## What might sort the sets

Unchecked. OTJ, TMT and TLA gain and FRA, SOS and FIN lose at similar shares. Something
about how easily a set's cards splash (the amount of fixing, hybrid costs) would be the
first thing to look at, and it is computable from the dataset. If it sorts these six,
it may be a better flag than the share.

## The predictions

| | predicted | found |
|---|---|---|
| the four together | better by under 2 SEs: the threshold stays | 2.4 SEs: wrong on the number |
| TMT | better by 2+ SEs again | 4.5 SEs: right |
| TLA and FIN | within 1 SE of the base | 2.2 SEs better and 2.0 worse: wrong |

## Notes

- TMT's four samples share drafts, so its SE is understated.
- Pooled numbers here weight each set by its SE, as the protocol says. `heads.md`'s
  pooled row (-0.0022, 1.2 SEs, all six sets) pools drafts instead.
- `by_set.md`'s line across six sets (2.2 SEs) is not a finding: it leans on which sets
  happen to be at which first-day share.
