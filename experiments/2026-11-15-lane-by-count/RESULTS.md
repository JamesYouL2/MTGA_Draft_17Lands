# A lane by count: results

Protocol: `PROTOCOL.md`. Report: `heads.md`, numbers in `heads.json` (60,000 drafts,
45,409 complete events, held-out ratings, pools in pick order).

## The verdict

The app's rule stays. No head got "no objection", and none did better than the app.

| head | regret slope change (SE) | SEs | verdict | top card changes |
|---|---|---|---|---|
| `count` | +0.0019 (0.0040) | +0.5 | inconclusive | 8.18% |
| `count-third` | +0.0033 (0.0039) | +0.8 | inconclusive | 7.05% |
| `count-third-from-5` | +0.0059 (0.0040) | +1.5 | inconclusive | 7.30% |
| `app-by-count` | +0.0010 (0.0034) | +0.3 | inconclusive | 4.20% |

Positive is worse for the head. All four are on the worse side, in both samples, and
none by 2 SEs. Each is "inconclusive" because its change plus 2 SEs is above +0.0063,
so the replay can't rule out a loss of the size that no archetype weight cost.

- **The better lane didn't make better picks.** `count` names the colors a drafter
  goes on to play more often than the app does, by 3.5 points, and changes the top card
  on 8.18% of picks. Drafters who followed those picks didn't win more.
- **The third color and the start don't matter much.** `count-third` is within 1 SE
  of `count`. Waiting for 5 cards is the worst of the four, at 1.5 SEs: with no lane
  early, 22.2% of its changes move the top card off the app's lane.
- **Order from 15 cards is not where anything happens.** `app-by-count` changes the
  top card on 4.20% of picks, for +0.0010.

Top-1 moved by -0.08 to +0.21 points. Event wins per swapped pick is below zero for
every head, at 0.5 to 2 SEs.

## Why it can't be settled cheaply

The SEs here are 0.0040, twice those of the earlier heads runs, because a lane change
moves many picks at once. For `count` to reach "no objection" at the change it showed,
the SE would have to be 0.0022, which is about four times the drafts. Nothing in the
result suggests that run would find a gain.

## The predictions

| | predicted | found |
|---|---|---|
| `count` | "no objection", below zero by under 2 SEs | inconclusive, above zero by 0.5 SEs: wrong |
| `count-third` | within 1 SE of `count` | 0.4 SEs apart: right |
| `count-third-from-5` | worse than `count-third`, by under 2 SEs | 0.7 SEs worse: right |
| `app-by-count` | within 1 SE of the base | 0.3 SEs: right |

## What follows

Nothing changes in the app. The lane question is closed for now: recency and the switch
earn their place on accuracy (`experiments/2026-11-15-lane-accuracy`), and the simpler
count doesn't clear the replay. The saving would have been about thirty lines.

## What it can't show

As the protocol says. One more: the accuracy test and this one measure different
things, and this result doesn't say the accuracy gain is false, only that the replay
finds no benefit from it.
