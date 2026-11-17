# Do the need rules and Greedy Bomb hold up in the replay? Results

Run [44012209588](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44012209588)
at `d8bc918`: 228,000 drafts from 19 sets, 176,781 complete events, held-out
ratings, salts `needs1` and `needs2`. The rule is in [PROTOCOL.md](PROTOCOL.md),
written before the run. Reports: [heads.md](heads.md), [by_set.md](by_set.md),
[ranks.md](ranks.md), and [attribute.md](attribute.md), which was written after the
results were in.

## Verdicts

Regret slope: positive is worse for the head. Swap (event wins per swapped pick):
negative is worse for the head.

| head | regret slope (SE), SEs | swap (SE), SEs | top card / top three changes | by the rule |
|---|---|---|---|---|
| `no-needs-removal` | +0.0002 (0.0002), +1.1 | +0.022 (0.023), +1.0 | 0.76% / 1.74% | removal passes, but the swap measure couldn't have seen harm: **back as a question** |
| `no-needs-2drops` | -0.0007 (0.0001), **-4.8** | +0.092 (0.034), **+2.7** | 0.35% / 0.83% | removal passes, both measures lean better: **back as a question, rerun first** |
| `no-curve-foundation` | +0.0000 (0.0002), +0.1 | +0.043 (0.023), +1.9 | 0.99% / 3.11% | removal passes, couldn't have seen harm: **back as a question** |
| `no-greedy-bomb` | +0.0008 (0.0001), **+6.8** | no reading (no top card changes) | 0.00% / 0.05% | flagged worse: **stays** |
| `removal-1.15` | +0.0002 (0.0001), +1.7 | +0.058 (0.035), +1.7 | 0.36% / 0.97% | beats today's on neither: **today's stays** |
| `2drops-cap-1.25` | -0.0002 (0.0001), **-3.3** | +0.120 (0.084), +1.4 | 0.08% / 0.21% | passes on the regret slope: **proposed, after a rerun** |
| `2drops-cap-1.75` | +0.0001 (0.0000), **+2.4** | -0.013 (0.146), -0.1 | 0.02% / 0.06% | flagged worse: **today's stays** |

"Couldn't have seen harm" is the protocol's test: twice the swap SE is above 0.035,
what 20% noise cost a swapped pick on 11-16. All three removals that pass fail it
(0.046, 0.068, 0.046), so by the protocol none goes out as a PR from this run.

## Needs 2-Drops: the replay disagrees with the game results

This is the finding. Four heads change the 2-drop bonus, and the regret slope moves
in order of the bonus's size:

| largest pack 2–3 bonus | regret slope change, SEs |
|---|---|
| 1.75x | +2.4 (worse) |
| 1.5x (today) | 0 |
| 1.25x | -3.3 (better) |
| none | -4.8 (better) |

Removing the bonus is better on the regret slope in 17 of 19 sets, and on the swap
measure by 2.7 SEs: where the head's top card differed, drafters who took it won
more. The change isn't confined to one kind of pick: changed top cards, the
drafter's card moving in rank, and only the pack's spread moving each carry about
a third of it, each about 3 SEs ([attribute.md](attribute.md)).

That runs against 11-03's strongest finding: a 2-drop is worth +0.35 [+0.15, +0.55]
win-rate points over a spell of the same rating while a deck is short, in 17 of 20
sets. The two can both hold. 11-03 says a short deck's 2-drops win more than their
rating, which is about the card. The replay says the advisor's boost, up to 1.5x on
top of an already composite score, puts 2-drops above cards drafters won more with.
11-03 put the worth at about 0.9 rating SDs, against the rule's 1.0 at two short;
the boost keeps growing to 1.5x at a bit over three short.

The pass is narrow on swap (2.7 SEs), and the coordinator's note from today's other
runs is that first-pass wins have faded on rerun. So: rerun `no-needs-2drops` and
`2drops-cap-1.25` on new salts before anything is proposed. If both hold, the cap
is the smaller step and agrees with 11-03; removal would be a second question.

## Needs Removal

Neither head moves either measure by 2 SEs. The two lean the same ways: slightly
worse on the regret slope (+1.1, +1.7) and slightly better on swap (+1.0, +1.7).
11-03 puts removal's worth at about 0.76 of the rule's size, which fits a smaller
multiplier, but this run can't separate 1.15x from 1.3x. Today's stays; removing it
isn't shown harmless, only not shown harmful.

## Curve Foundation

Changes 1% of top cards, mostly off-lane pack-1 picks (58% of changes), and moves
neither measure. Swap leans its way (+1.9 SEs). 11-03 didn't test it. A small
candidate for removal, but the run couldn't have seen a cost the size of 20% noise.

## Greedy Bomb: why a rule that changes no top card reads 3 to 7 SEs

It recurs, larger: +0.0008 (0.0001), 6.8 SEs, in both samples (+0.0008, +0.0009)
and in 15 of 19 sets, with the top card changed on 0.00% of picks (a handful, rounded away) and the
top three on 0.05%.

[attribute.md](attribute.md) puts all of it in one kind of pick: the top card
stays and the drafter's own card moves in rank. With the head's regret on only
those picks the change is +0.00080 (0.00012), 6.9 SEs; on the rest, +0.00003 and
-0.00001. Drafters whose own card dropped (drafters who took the bomb: it falls
through to Off-Color, 0.05 in pack 2 and 0.01 in pack 3, instead of 0.30, and no
other card can drop) won 3.33 events on average, against 3.25 for everyone and
3.12 for those whose card rose. So the head raises the regret of slightly
better-than-average drafters, and the regret slope weakens.

The reading is real but it is about scoring, not advice. Today's 0.30 scores a
greedy bomb closer to what drafters who took it won with than the fall-through
does; it never makes one the top card. By the rule it stays, and that is the right
call for the regret slope as a measure of scoring. As a recommendation it does
nothing users see beyond rank 2 or 3 on 0.05% of picks.

The pre-stated checks were coarser and half missed:

| check | result |
|---|---|
| 1. top card under 0.05%, top three under 0.2% | right: 0.00%, 0.05% |
| 2. over half of regret moves keep the top three and go up | half: 82% keep it, 36% go up |
| 3. drafts hit win more, regret shift per win positive | half: 3.22 against 3.26; +0.00002 |

Checks 2 and 3 counted every pick whose regret moved, and most of those are packs
where the bomb sat unpicked and only the spread changed. Those carry none of the
slope change. The attribution, done after the run, separates them.

## Predictions

| prediction | result |
|---|---|
| `no-needs-removal`: 1–2% changes, flagged worse or near, stays | 0.76%; not flagged (+1.1, +1.0 better on swap); stays as a question |
| `no-needs-2drops`: 2–4% changes, flagged worse on swap, stays | wrong: 0.35%, better on both (-4.8, +2.7) |
| `no-curve-foundation`: 1–3%, not flagged, proposed with caveat | right on size and flags (0.99%); not proposed, too little power |
| `removal-1.15`: under 1%, neither moves 2 SEs | right: 0.36%, 1.7 and 1.7 |
| both caps: under 1%, neither beats today's | half: 1.25x beats on regret (-3.3); 1.75x worse (+2.4) |
| `no-greedy-bomb`: under 0.05%, worse by 2+ SEs, explanation holds | right on rate and flag (6.8); explanation holds by the attribution, not by checks 2–3 |

## What's next

1. Rerun `no-needs-2drops` and `2drops-cap-1.25` (and perhaps a 1.1x cap) on new
   salts. A pass on both measures again would make the cap a small PR.
2. Needs Removal and Curve Foundation: no action. A larger run could tell 1.15x from
   1.3x, but neither head was near a 2 SE reading on 228,000 drafts.
3. Greedy Bomb stays. If the advice, not the scoring, is the question, the rule is
   inert and could be judged by that, but the protocol's rule keeps it.
