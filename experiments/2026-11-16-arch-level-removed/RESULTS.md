# The archetype weight with the pair's level taken out: results

One run of the Advisor heads workflow,
[44010224004](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44010224004):
19 sets, 228,000 drafts, 177,005 complete events, salts `archlvl1` and `archlvl2`.
The rule is in [PROTOCOL.md](PROTOCOL.md), written before the run. Reports:
[heads.md](heads.md), [within_set.md](within_set.md), [by_set.md](by_set.md), and
[swap_groups.md](swap_groups.md) (added after the run, see below).

## The answer

**Today's advisor stays.** Without the pair's level, the advisor's changed picks win
fewer events, by 3.8 SEs. The regret slope leans the other way, but by 1.1 SEs only.
By the rule, the level is earning its place in picks.

## The two measures

| | all 19 sets | DMU, TDM, SNC, KTK | the other fifteen |
|---|---|---|---|
| regret slope change, within set (positive worse) | -0.0008 (0.0007), 1.1 SEs better | +0.0003 (0.0014) | -0.0011 (0.0009) |
| event wins per swapped pick (positive better) | **-0.044 (0.012), 3.8 SEs worse** | -0.032 (0.021), 1.5 SEs worse | -0.045 (0.014), 3.2 SEs worse |

- Top card changes on 2.61% of picks; agreement with drafters' top pick -0.19 points.
- On-lane picks 76.9% to 76.3%.
- The two salts disagree on the regret slope: -0.0018 (0.0010) and +0.0002 (0.0010).
- heads.py's old pooled figure reads -0.0033 (0.0008), 4.0 SEs better. That is the
  faulty scale found on 11-16; the within-set figure decides, as the protocol says.

## Read by the rule

| result | happened? |
|---|---|
| better by 2+ SEs on either measure | no: the regret slope is 1.1 SEs better |
| worse by 2+ SEs on either measure, not better by 2+ on the other | **yes**: event wins 3.8 SEs worse |

Verdict: today's stays, and the level is earning its place.

## Where the picks change

| kind of change | share of changes | drafters took base's | drafters took head's |
|---|---|---|---|
| both on-lane | 40.3% | 27.7% | 31.5% |
| base on-lane, head off | 40.0% | 47.0% | 12.2% |
| base off-lane, head on | 15.5% | 11.7% | 49.0% |
| both off-lane | 4.2% | 39.9% | 18.8% |

As the protocol expected, level mostly moves on-lane cards against off-lane ones,
since cards without pair data get no level. Without it, the advisor leaves its lane
for an off-lane card in 40% of its changes, and drafters rarely did (12%). Among
on-lane cards the head agrees with drafters a little more (31.5% against 27.7%),
which is the "fit" part doing its job. But the lane moves cost more events than that.

## Predictions

| prediction | result |
|---|---|
| top card changes on 3% to 6% of picks | wrong, a little under: 2.61% |
| no verdict, within 2 SEs on both | wrong: event wins 3.8 SEs worse |
| leans worse, as level keeps a drafter in a strong pair | right on event wins; the regret slope leans better |

## The pair-parts result, squared

The whole-deck test found level hurts predicting decks' wins (-0.23). Here level
helps picks. The two can both hold: in picks, level works as a lane-commitment
signal (stay in a pair whose cards do well), not as a judgement on how good the
finished deck is. So the deck score should keep using overall ratings (as it does
since #264), and the advisor should keep the pair rate as it is.

## Added after the run

heads.py reports event wins per swapped pick over all sets only. `swap_groups.py`
splits it by the protocol's set groups. The all-sets figure decided the verdict
before this split was made.

## What it can't show

As in the held-out replay. And the regret slope and event wins disagree in sign
here, though only event wins clears 2 SEs. The power test found event wins the more
sensitive of the two for changes of this size.
