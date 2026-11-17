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

# Rerun, 2026-11-17: the 2-drop heads and flat bonuses

Run [44059805912](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44059805912)
at `8dde05b`: the same 19 sets and 6,000 drafts a set and salt, new salts `needs3`
and `needs4`, 176,769 complete events. The rules are in PROTOCOL.md's addendum,
written before the run. All 38 replay jobs passed. The run's Extra report step was
cancelled after 27 minutes, probably out of memory, before anything was uploaded. So
the reports were rerun from the run's artifacts by a one-off workflow on
`run/need-rules-rerun-report`, run
[44091224510](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44091224510),
with [rerun_extra.py](rerun_extra.py) changed to read one folder at a time. They were
too big to run locally. Reports: [heads-rerun.md](heads-rerun.md),
[by_set-rerun.md](by_set-rerun.md), [extra-rerun.md](extra-rerun.md) (ranks, the
high-set split, head to head, attribution).

## Verdicts

Regret slope: positive is worse for the head. Swap: negative is worse.

| head | regret slope (SE), SEs | swap (SE), SEs | top card / top three changes | by the addendum's rule |
|---|---|---|---|---|
| `no-needs-2drops` | +0.0001 (0.0002), +0.6 | +0.000 (0.032), +0.0 | 0.36% / 0.85% | better on neither: **not confirmed** |
| `2drops-cap-1.25` | +0.0002 (0.0001), **+2.8** | +0.079 (0.078), +1.0 | 0.08% / 0.21% | 2.8 SEs *worse* on the regret slope: **not confirmed** |
| `flat-bonus` (1.05x / 1.1x) | +0.0004 (0.0003), +1.4 | +0.018 (0.011), +1.6 | 3.69% / 10.60% | better on neither by 2 SEs: **not adopted** |
| `flat-bonus-strong` (1.1x / 1.2x) | +0.0012 (0.0005), **+2.6** | -0.004 (0.008), -0.5 | 6.05% / 16.45% | 2.6 SEs worse on the regret slope: **not adopted** |

Neither 2-drop head is confirmed, so by the addendum today's Needs 2-Drops stays
and the first run's reading is taken as having faded. No head passes, so there's no
pass under 3 SEs to flag and no case to check for passing by rescaling.

## Needs 2-Drops: the first run's reading doesn't hold

The first run had removal at -4.8 SEs and the cap at -3.3, better in 17 of 19 sets.
On new salts, removal reads +0.6 and the cap +2.8, worse in 12 and 15 sets. Same
code, same patches (byte for byte), the same daily dataset build (gh-pages last
updated 01:05 UTC on the 17th, before both runs), and fixed files for KTK and SNC.
Only the drafts sampled differ.

The four salts disagree more than their SEs allow:

| head | needs1 | needs2 | needs3 | needs4 | spread SD / bootstrap SE | χ²(3) |
|---|---|---|---|---|---|---|
| `no-needs-2drops` | -0.00075 | -0.00059 | +0.00005 | +0.00013 | 0.00044 / 0.00021, 2.1x | 13.6 |
| `2drops-cap-1.25` | -0.00030 | -0.00014 | +0.00020 | +0.00017 | 0.00024 / 0.00010, 2.6x | 19.7 |

Pooled over the four salts, with the SE taken from their spread, removal reads
-0.00029 (0.00022), -1.3 SEs, and the cap -0.00002 (0.00012), -0.1. Pooled swap
(inverse variance over the two runs): removal +0.044 (0.024), the cap +0.098 (0.057).
Both measures lean toward a smaller bonus, but neither reaches 2 SEs. That is about
what 11-03's game results say: 11-03 put the worth at about 0.9 of the rule's size
at two short.

Head to head (reported though neither is confirmed): removing the bonus against the
1.25x cap reads -0.9 SEs on regret and -0.6 on swap, with the top card differing on
0.27% of picks. They can't be told apart.

## Flat bonuses

Applied in packs 2–3 only, on top of the other composition rules (see the
addendum). Neither beats today's on either measure by 2 SEs.

- `flat-bonus` changes 3.7% of top cards, ten times the 2-drop heads. Swap leans
  its way (+1.6 SEs) and the regret slope leans against it (+1.4). Its swap SE of
  0.011 is well under 0.0175, so this run could have seen a cost the size of 20%
  noise on swap, and it reads none. Dropping the thresholds for small flat bonuses
  isn't shown harmful, but isn't shown better either.
- `flat-bonus-strong` changes 6.1% of top cards and reads 2.6 SEs worse on the
  regret slope, with swap flat (-0.5 SEs, SE 0.008). By [extra-rerun.md](extra-rerun.md),
  71% of the regret change (+0.00085 of +0.00120, 2.5 SEs) comes from picks where
  neither the top card nor the drafter's rank changed: only the spread of scores
  moved. Picks where the top card changed carry +0.00008 (0.4 SEs). So this is
  Greedy Bomb's case the other way round: it scores worse but advises no worse.
  The rule still rejects it.

`2drops-cap-1.25`'s +2.8 is the same kind: 84% of it (+0.00016, 3.1 SEs) is on
"regret only" picks, and +0.00004 on changed top cards.

## The four high three-color sets against the other fifteen

Reported only (KTK, TDM, SNC, DMU against the rest):

| head | four high: regret, swap (SEs) | other 15: regret, swap (SEs) |
|---|---|---|
| `no-needs-2drops` | +0.7, -1.4 | +0.2, +0.9 |
| `2drops-cap-1.25` | +1.5, -1.2 | +2.6, +2.2 |
| `flat-bonus` | -0.0, **+2.3** | +1.5, +0.7 |
| `flat-bonus-strong` | -0.1, -0.2 | **+3.0**, -0.4 |

`flat-bonus` reads better on swap only in the four high sets (+0.057, SE 0.025). That
is one cell in sixteen over 2 SEs and decides nothing. `flat-bonus-strong`'s regret
cost is all in the other fifteen. The 2-drop heads show no high-set lean.

## Predictions

| prediction | result |
|---|---|
| `no-needs-2drops` confirmed on regret, about -4 SEs; swap better, under 2 | wrong: +0.6, swap 0.0 |
| `2drops-cap-1.25` confirmed on regret, about -3 SEs | wrong: +2.8, worse |
| head to head, removal not 2 SEs worse than the cap | right: -0.9, -0.6 |
| `flat-bonus` 1–2% top-card changes, neither measure 2 SEs | half: 3.69%; neither moves 2 SEs |
| `flat-bonus-strong` 3–5%, swap a little worse, not 2 SEs | half: 6.05%; swap -0.5 is right, but regret +2.6 worse wasn't predicted |
| 2-drop gains no larger in the four high sets | moot: no gains |

## What this means for the measure

The salt-to-salt spread is 2–2.6x the bootstrap SE for these two heads. The SE
resamples events within a salt. It doesn't resample whatever a salt shares, such as
its held-out ratings, rebuilt for each salt. Four salts is too few to pin the
factor down. Within each run the two salts agree, so it could be partly run-level
too, but nothing found differs between the runs. If the factor holds, one run's
"3 SEs" is about 1.2–1.5 true SEs. That fits the first passes that faded today:
lane share, wheel tiebreak, and these two. Greedy Bomb's 6.8 would still be about 3.

What's next, replacing the first run's list:

1. No 2-drop PR. Today's Needs 2-Drops stays; pooled, a smaller bonus leans better
   on both measures (-1.3 and +1.8 SEs), not enough to act on.
2. No flat-bonus PR. The thresholds stay.
3. For any head: judge on four or more salts across runs, with the SE from their
   spread, or work out what each salt shares and add it to the bootstrap. Until
   then, treat single-run readings under about 5 SEs as unconfirmed.
