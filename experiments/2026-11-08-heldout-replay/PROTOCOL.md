# Does removing the archetype weight still lose on held-out ratings?

Written before any held-out result was seen.

## Why

On the app's ratings, replaying 58,800 drafts with no archetype weight loses to
the current weight: top-1 falls 0.6-0.7 points and the regret slope is worse by
+0.014 and +0.007 (SE 0.003) in two samples. But those ratings include the
replayed drafts, and pair win rates rest on fewer games than overall ones, so
the leak could favor the weight. The whole-deck test in
`experiments/2026-11-03-rating-parts`, which holds results out, favors removal.

## What runs

The Advisor replay workflow with `holdout: true`, ten sets, 3,000 drafts a set,
with the salts `""` and `arch2`, the same drafts as the runs above. Base is
5a42fb2. Two heads: no weight, and a flat weight of 0.65.

Each head and the base replay on three sets of ratings:

- **app**: the app's dataset;
- **rebuilt**: win rates rebuilt from the set's game dump, every game counted;
- **held out**: the same, leaving out the replayed drafts' games.

Rebuilt and held out differ only in those games: both rate the same cards with
the same shrinkage. A rate needs 500 games in hand in the whole dump, the
minimum in the app's own data. The dumps are smaller than the app's data (about
a third for FRA), so rebuilt is expected to differ from app in its own right.

## How it is read

The measure is the change in regret slope, no weight minus base, on the held-out
ratings, pooled over both samples with a paired bootstrap SE.

- **The rebuilt change is under 2 SEs:** rebuilding lost the signal, so this
  test can't answer the question. Inconclusive, whatever held out shows.
- **Otherwise, the held-out change is under 2 SEs, or favors no weight:** the
  replay's objection came from the leak, and it no longer stands in the way of
  removal.
- **Otherwise (held out is worse by 2 SEs or more):** the weight earns its place
  in pick order on ratings that exclude the drafts it is judged on. Don't remove
  it on this evidence.

The change between rebuilt and held out, with its paired SE, measures the leak.

Reported but not deciding: top-1 and top-3 (drafters themselves draft by pair,
so they favor the weight), how often the top card changes and stays on-lane,
wins when the two advisors disagree, and the flat weight on the same measures.

## What it can't show

Holding out removes each draft's own games, not the drafter's other drafts. The
drafters' choices are still not random, so slopes stay associations. Regret
measures whether drafters who followed an advisor won, not what an advisor's
user would win.
