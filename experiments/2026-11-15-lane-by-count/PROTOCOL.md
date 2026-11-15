# A lane by count, on held-out picks

Written before any result of the run was seen. A 150-draft FRA smoke test ran first to
check the patches apply and replay; I saw its table, where every head was within 1 SE
of the base, and the top card changed on 5% to 9% of picks.

## Why

`experiments/2026-11-15-lane-accuracy` found that the two colors with the most nonland
cards name the colors a drafter goes on to play better than the app's lane does: +3.52
points net (SE 0.16), at every pool size. The count is about ten lines against the
app's forty, with no weights, no recency and no change of rule at 15 cards. Its protocol
said a win there earns a replay, since agreeing with what drafters played isn't the
same as picking well.

That test left two choices open: whether the lane ever has a third color, and whether
it starts at the first card.

## The heads

All replace or change `_identify_main_colors()` in `src/advisor/engine.py`. The
patches are in [heads/](heads/).

| head | the lane |
|---|---|
| `count` | the two colors with the most nonland cards, from the first card; ties go to the color picked first. Never a third color |
| `count-third` | the same, and from 15 cards a third color joins if it has 15% of the pool's colored cards, which is the app's bar for one |
| `count-third-from-5` | `count-third`, with no lane until the pool has 5 cards |
| `app-by-count` | the app's rule, except that from 15 cards its colors are ordered by count, not by recency-weighted rating. Not a simplification |

`count` is what the accuracy test measured. `app-by-count` is here to show where a
change comes from: from 15 cards the app's lane and `count-third`'s hold the same
colors and differ only in which two come first.

## What runs

The Advisor heads workflow, as in `experiments/2026-11-12-composition-rules`: ten sets,
3,000 drafts a set, the salts `""` and `arch2`, on held-out ratings only. The base is
upstream main at `6b6dba9`.

One thing is new. The harness now gives the advisor each pool in pick order
(`fix/replay-pool-order`); before, recency followed the dump's columns. So this base
isn't comparable with earlier runs' bases.

The accuracy test chose the count on the salt `""` drafts, by their played colors.
That isn't this run's outcome, and `arch2` wasn't in it. The change is reported by
sample.

## How it is read

As in the pick-multipliers protocol: the change in regret slope, head minus base,
pooled over both samples, with a paired bootstrap SE. Positive is worse for the head.

| verdict | means | here |
|---|---|---|
| keep | worse by 2+ SEs | the app's rule stays |
| inconclusive | the change plus 2 SEs is above +0.0063 | the app's rule stays |
| no objection | otherwise | the head can replace the app's rule |

A head doesn't have to beat the app's rule: it is the simpler code, so "no objection"
is enough.

Among heads with "no objection", the simplest is the candidate: `count`, then
`count-third`, then `count-third-from-5`. A less simple one takes its place only if its
change is lower by 2 of its own SEs. `app-by-count` decides nothing.

As before: if the deciding head lands between 1.5 and 2 SEs worse, I will say so and
recommend keeping the app's rule. No correction for four heads: a false "keep" only
leaves the rule in place.

Reported, not deciding: how often the top card changes, top-1, the on-lane share of top
cards, the change in each sample, and event wins per swapped pick.

## Predictions

- `count`: "no objection", with a change below zero by under 2 SEs.
- `count-third` is within 1 SE of `count`.
- `count-third-from-5` is worse than `count-third`, by under 2 SEs.
- `app-by-count` is within 1 SE of the base.

## What it can't show

As in the held-out replay: slopes are associations among drafters who chose freely,
and regret says whether drafters who followed an advisor won, not what its users would
win. The lane also feeds the reasons shown to the user ("Better in WU"), which the
replay doesn't see.
