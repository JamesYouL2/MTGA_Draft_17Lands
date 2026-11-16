# Where the three-color flag's threshold belongs

Written before any result of this run was seen.

## Why

The flag (`feat/three-color-off-color`) puts every off-color multiplier at its square
root once three-color decks have 30% of a set's games. The 30% sits in a gap: the sets
tested above it are at 47% and more, and the sets below at 24% and less.

The first test (`experiments/2026-11-15-off-color-share`) hints the gap's lower edge may
be on the wrong side. In the four sets with an app share of 22% to 24%, `softer` (the
same square root, in every set) changed the regret slope by:

| set | app's share | `softer` (SE) |
|---|---|---|
| FRA | 24% | -0.0030 (0.0062) |
| OTJ | 24% | -0.0036 (0.0055) |
| TMT | 23% | -0.0250 (0.0079) |
| SOS | 22% | +0.0046 (0.0076) |

Weighted by their SEs, that is about -0.0056 (SE 0.0033), 1.7 SEs, and most of it is
TMT. In the eleven sets under 20% it was on the worse side. If the four hold up, the
threshold belongs at 20%, and the flag turns on for four more sets, one of them the
current one.

## What runs

The Advisor heads workflow with the first test's `softer` patch, unchanged, held-out
ratings, pools in pick order, base upstream main at `6b6dba9`. Six sets: the four above,
and TLA (19%) and FIN (15%) as the next two down. 6,000 drafts a set and salt, the
salts `thr1` to `thr4`, none used before.

TMT's dump is small, so its four samples share many drafts and its SE is understated.

## How it is read

Each set's change comes from `by_set.py`. Sets are pooled by weighting each by its SE.

| | verdict |
|---|---|
| the four sets at 22% to 24% together are better by 2+ SEs, and the three without TMT are on the better side | the threshold moves to 20% |
| better by 2+ SEs only with TMT | the threshold stays at 30%. TMT is its own question |
| not better by 2+ SEs | the threshold stays at 30% |

TLA and FIN are reported. If the threshold moves and those two are also better by 2+
SEs together, 20% isn't the edge either, and I will say so; nothing moves below 20% on
this run.

The first test's numbers are not pooled into the verdict. They are shown beside it.

## Predictions

- The four together are better by under 2 SEs: the threshold stays.
- TMT is better by 2+ SEs again.
- TLA and FIN are within 1 SE of the base.

## What it can't show

As in the held-out replay. A threshold moved to 20% would still sit in a gap, between
19% and 22%, chosen on the sets either side of it.
