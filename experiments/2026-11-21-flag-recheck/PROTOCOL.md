# The three-color flag, measured again on current main

Written before any result of this run was seen.

## Why

Every write-up behind the flag (`exp/off-color-share`, `exp/off-color-flag`,
`exp/flag-snc-ktk`, `exp/flag-threshold`, `exp/single-pip`, flag-early-days) ran
before #274 removed pack 1's off-color penalty. Back then the flag also softened
pack 1. On current main pack 1's multiplier is 1.0, which the flag leaves alone,
so the flag now acts only in packs 2 and 3. Those earlier results don't carry over
to the changed version, so it is measured again.

## What runs

The Advisor heads workflow on this branch: base is upstream main `edfab59` (`src/`
unchanged, tooling merged from `exp/measure-salts`). The one head, `flag`, is
`feat/three-color-off-color-v2`'s diff to `src/` (commit `619bfa8`). All 19 sets (BLB
DFT DMU DSK EOE FDN FIN FRA HOB KTK LTR MSH NEO OTJ SNC SOS TDM TLA TMT), 8 fresh
salts of 1000 drafts, held-out ratings, pools in pick order. `heads.py` combines the
salts for the regret slope change and event wins per swapped pick. The same script
gives:
- the pooled reading over the four high sets (KTK, TDM, SNC, DMU);
- each high set alone;
- the 15 low sets together.

## The decision rule

The flag fires only where the held-out dataset's three-color share is 30% or more,
so in the 15 low sets it should change nothing.

| reading | verdict |
|---|---|
| pooled four high sets: better by 2+ SEs on at least one measure, and not 2+ SEs worse on either | handed over |
| otherwise | not handed over (and nothing stacked on it either) |

"Better" is a negative regret slope change or a positive event wins figure.

Check, not part of the verdict: top card changes in the 15 low sets must be 0.00%.
If they aren't, the flag fires somewhere it shouldn't, and that is reported and
explained before any hand-over.

Per-set numbers are reported on both measures. They don't decide anything.

## Predictions

- Pooled high sets: regret better, about -0.010 to -0.014. That is smaller than the
  pre-#274 estimates (-0.015 to -0.018 in KTK, SNC and DMU), because pack 1 no longer
  counts. Well past 2 SEs. Event wins on the better side.
- TDM near zero again; KTK, SNC and DMU each better.
- Low sets: 0.00% top changes.
