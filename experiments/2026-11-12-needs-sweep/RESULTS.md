# How big should Needs Fixing and Needs Creatures be: results

Run [43334565174](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43334565174)
at `201ff9e` (`exp/needs-sweep` plus a push trigger): ten sets, two samples, 60,000
drafts and 45,451 complete events, on held-out ratings only. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. The full report is
[heads.md](heads.md) and the numbers are in [heads.json](heads.json). The report's
verdict column uses the removal protocol's labels, which this sweep doesn't read.

## Verdict

**Nothing changes.** No head is better than the base by 2 SEs, so both multipliers stay.

| Needs Fixing | regret slope change (SE) | SEs | top card changes | top-1 change |
|---|---|---|---|---|
| 1.4 (base) | 0 | | | |
| 1.3 | +0.0005 (0.0004) | +1.2 | 0.94% | +0.29 |
| 1.2 | +0.0012 (0.0008) | +1.6 | 1.96% | +0.54 |
| 1.1 | +0.0022 (0.0011) | +2.1 | 2.98% | +0.72 |
| 1.0 | +0.0034 (0.0014) | +2.5 | 4.03% | +0.82 |

| Needs Creatures | regret slope change (SE) | SEs | top card changes | top-1 change |
|---|---|---|---|---|
| 1.25 (base) | 0 | | | |
| 1.18 | -0.0001 (0.0001) | -0.8 | 0.06% | +0.01 |
| 1.12 | -0.0001 (0.0001) | -0.7 | 0.11% | +0.01 |
| 1.06 | -0.0001 (0.0002) | -0.7 | 0.17% | +0.01 |
| 1.0 | -0.0001 (0.0002) | -0.6 | 0.23% | -0.01 |

Positive is worse for the head.

## Needs Fixing: smaller is steadily worse

Every step down from 1.4 reads worse, and by more: the slope rises in order through all
four heads. Removing the rule is now 2.5 SEs worse. In the composition-rules run it was
1.7, on a base that still had Curve Too Heavy and Removal Saturated. Both samples agree
in sign at every value, though `arch2` carries most of it (+0.0047 against +0.0020 at
1.0).

So the idea behind this sweep was wrong for fixing. I thought 1.4 was too big because
drafters mostly don't follow it. They don't: top-1 rises as the multiplier falls. But
the picks the rule makes go with wins.

The trend doesn't stop at 1.4, so the best value may be above it. That wasn't in the
sweep. It is the next thing to run.

The other measure still disagrees: event wins per swapped pick favor the head at every
value, +0.058 to +0.097. I can't reconcile the two. The protocol reads the slope.

## Needs Creatures: too rare to measure

The rule changes the top card on 0.23% of picks even when removed outright, and the
slope doesn't move: -0.0001 (0.0002). The samples disagree in sign. The replay can't
say what size it should be.

That also means the size hardly matters to users. By the removal protocol's standard
this rule would get "no objection" and could go as a simplification. I'm not removing
it here: this protocol said beforehand that removal needs a 2 SE gain, and the
game-results test supports creatures being worth more than their rating.

## The predictions

- **Fixing's slope is lowest at 1.2 or 1.1: failed.** It's lowest at the base.
- **One of 1.1 to 1.3 qualifies: failed.** None is better than the base at all.
- **Fixing at 1.0 doesn't qualify: held.**
- **No creatures head qualifies, and each changes under 1% of picks: held.**
- **Top-1 rises as the multiplier falls:** held for fixing, not for creatures, where it
  doesn't move.

## What it can't show

As the protocol says: slopes are associations among drafters who chose freely, and
regret says whether drafters who followed an advisor won, not what its users would win.
The two rules weren't swept together, and no value above the base was run.
