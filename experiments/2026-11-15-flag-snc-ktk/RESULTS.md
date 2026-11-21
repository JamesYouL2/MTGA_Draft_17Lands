# The three-color flag on SNC and KTK: results

Protocol: `PROTOCOL.md`. Reports: `heads.md`, `by_set.md`, numbers in the JSON files.
36,000 drafts, 29,767 complete events, held-out ratings, pools in pick order.

## The verdict

**Build it.** `flag-step` is better by more than 2 SEs in each set, and by 5.9 SEs in
the two together.

| head | KTK (SE) | SNC (SE) | together (SE) | SEs |
|---|---|---|---|---|
| `flag-step` | -0.0178 (0.0055) | -0.0177 (0.0035) | -0.0170 (0.0029) | -5.9 |
| `flag-knee` | -0.0190 (0.0079) | -0.0171 (0.0034) | -0.0188 (0.0035) | -5.4 |
| `flag-plain` | -0.0090 (0.0126) | -0.0211 (0.0061) | -0.0202 (0.0055) | -3.7 |

Negative is better for the head. All three samples agree for every head (`flag-step`:
-0.0156, -0.0224, -0.0129). Neither other head beats `flag-step` in both sets by 2 of
its own SEs, so `flag-step` stays the candidate. It also changes the fewest top cards:
6.01% of picks, against 8.76% and 17.87%.

Neither set was in any earlier run, and the flag's form and threshold were fixed
before these datasets existed.

## The four high-share sets

| set | the app's three-color share | `flag-step` (SE) |
|---|---|---|
| KTK | 86% | -0.0178 (0.0055) |
| TDM | 79% | -0.0032 (0.0030), both runs together |
| SNC | 69% | -0.0177 (0.0035) |
| DMU | 47% | -0.0148 (0.0028), both runs together |

Three of four gain about the same amount. TDM is the exception, and there the flag
does no harm. Why TDM differs isn't known. One guess, unchecked: TDM's drafters and
ratings already lean three-color so far that the archetype ratings carry what the
softer penalty adds elsewhere.

The gain is large by this harness's standards: 0.017 is nearly three times what
removing the archetype weight cost.

## Limits

- KTK's three samples share drafts, since its dump is small, so its SE is somewhat
  understated. At 3.2 SEs it has room.
- Event wins per swapped pick agree here: +0.097 (SE 0.021) for `flag-step`.
- The threshold of 30% sits in a gap: no set tested has a share between 24% and 47%.
  Where in that gap it belongs is not known.
- The first test found softening slightly worse in the 15 sets under 25%, so the step
  leaves those alone.

## The predictions

| | predicted | found |
|---|---|---|
| `flag-step` | better in SNC by 2+ SEs; within 2 SEs in KTK; "no flag" | better in both: wrong about KTK and the verdict |
| `flag-plain` | worse than `flag-step` in KTK | -0.0090 against -0.0178: right, within noise |

## What follows

A pull request with the share in `SetMetrics` and the step in the advisor:
`feat/three-color-off-color`.
