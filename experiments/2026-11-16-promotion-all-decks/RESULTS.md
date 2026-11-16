# Safe-deck promotion, on every deck the data has: results

One run of the Deck builds workflow,
[43815325916](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43815325916),
at `c4253e2`: 1,741,631 pools from 19 sets and 7,867,175 games, salt `three`. The
protocol is in [PROTOCOL.md](PROTOCOL.md), written before the run. Report:
[deck_variants.md](deck_variants.md).

## Verdict

**No verdict, and the question is closed for this method.** The rule stays, as the
maintainer's choice of which deck a user sees first.

Promotion changes the first deck in 16.81% of pools. Where it changes the deck's
colors (291,651 pools), drafters who played the safe deck's colors did
**-0.37 [-0.83, +0.09]** win rate points against those who played the unpromoted
top's, with card quality, set and player held equal. That is 1.6 SEs against
promotion, short of the 2 the rule asks for.

| run | pools | outcome, safe over the top's |
|---|---|---|
| 11-13, first | 928,062 | -0.01 [-0.75, +0.73] |
| 11-13, second | 927,915 | -0.09 [-0.68, +0.50] |
| this one | 1,741,631 | -0.37 [-0.83, +0.09] |

The three samples overlap, so they are not three independent readings. All three are
on the side against promotion, and this one is the furthest. Uncontrolled, the safe
colors won 52.2% and the top's 54.1%.

## Predictions

| prediction | result |
|---|---|
| within 2 SEs of zero again | right: 1.6 SEs |
| an interval about 0.7 as wide as the second run's | close: 0.92 wide against 1.18, a ratio of 0.78 |

## Also in this run

Tempo again: +0.10 [-0.08, +0.28] at the same card quality, the same "remove" as on
11-13, and it comes first in 0.4% of pools.

## What this doesn't show

It's observational. Drafters who chose the safe colors differ from those who didn't in
ways the controls may miss. This sample is most of the decks the dumps have, so a
fourth run would mostly re-read the same decks.
