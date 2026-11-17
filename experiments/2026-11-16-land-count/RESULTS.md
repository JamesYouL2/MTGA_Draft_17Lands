# Does the app's land count win? Results

Run [44010108608](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44010108608):
861,167 decks of exactly 40 cards (70,498 others left out) and 3.9 million games
from 19 sets (the cube's dump gave almost no decks). Reports: [lands.md](lands.md),
the planned one, and [followup.md](followup.md), one check added after it was seen.
The rule is in [PROTOCOL.md](PROTOCOL.md), written before the run.

## The answer

By the rule, 16 lands beats the app's flat 17, and so does 15 or fewer. That holds
pooled and in every curve band. My reading is more cautious: the check by player
experience suggests most of the gap comes from who chooses 16 and when, not from the
sixteenth land itself. I would not change the flat 17 on this alone.

## As planned

Game win rate points against decks at 17, with card quality, colors, curve, set and
player buckets held equal. SEs the larger of model and set-clustered.

| lands | decks | against 17 | same sign by set | by the rule |
|---|---|---|---|---|
| 15 or fewer | 2.2% | +1.86 ± 0.20 (9.3 SEs) | 17/17 | beats 17 |
| 16 | 20.7% | +1.18 ± 0.11 (10.6 SEs) | 19/19 | beats 17 |
| 18 | 4.2% | -0.62 ± 0.31 (2.0 SEs) | 14/14 worse | no |
| 19 or more | 1.9% | -1.28 ± 0.22 (5.9 SEs) | 2/2 worse | no |

By curve band (mean mana value quintiles, edges 2.61, 2.78, 2.96, 3.17), 16 against 17:

| band | share on 16 | 16 against 17 | same sign by set |
|---|---|---|---|
| 1 (lowest) | 35.4% | +1.49 ± 0.15 | 19/19 |
| 2 | 24.1% | +1.15 ± 0.20 | 17/18 |
| 3 | 18.7% | +1.08 ± 0.24 | 15/18 |
| 4 | 16.9% | +0.88 ± 0.17 | 16/18 |
| 5 (highest) | 10.8% | +0.77 ± 0.22 | 10/14 |

Counting MDFCs as spells changes little: 16 +1.15 ± 0.10, 15 or fewer +1.35 ± 0.26,
18 -1.32 ± 0.35. Most decks the app would call 18 lands are 16 or 17 basics plus
MDFCs (70%); true 18-land decks are 1.4%.

## Why I don't take it at face value

- **It doesn't depend on the curve.** If the sixteenth land were the cause, a deck
  with a curve of 3.2 should gain much less from cutting a land than one at 2.5. The
  gain shrinks only from +1.5 to +0.8.
- **Fewer is better all the way down.** 15 or fewer beats 16, which beats 17. A deck
  at 2.9 mana value on 15 lands should stumble. A steady slope like this looks like
  a trait of the drafters who cut lands.
- **New players don't gain** (followup.md). Same model, by the player's games bucket:

| games played | decks | 16 against 17 |
|---|---|---|
| 5 | 10,295 | -0.44 ± 0.71 |
| 10 | 124,969 | +0.35 ± 0.18 |
| 50 | 177,649 | +1.25 ± 0.18 |
| 100 | 492,417 | +1.33 ± 0.12 |
| 500 | 44,277 | +1.88 ± 0.29 |

  By win rate bucket it is flat (about +0.9 to +1.5 from 44% to 70%), so it is not
  "better players play 16". It is experienced players, who choose 16 for decks
  where they know it works, by signs the model doesn't see (cheap card draw, mana
  sinks, an aggressive plan). The app's 23-spell builds have no such reason, so they
  would probably gain something nearer the new players' figure: little or nothing.

That check was not planned, so it deserves less weight than the rule. But the rule
itself depends on the protocol's caveat (drafters choose land counts knowing their
deck), and here that caveat has a visible fingerprint.

## Verdict

| question | by the rule | my reading |
|---|---|---|
| 16 beats 17 | yes, pooled and in all five bands | mostly selection; don't switch on this |
| 15 or fewer beats 17 | yes, pooled and in bands 1 to 4 | same, more so |
| 18 beats 17 | no (worse, 2.0 SEs) | 17 is not too few |
| a curve-dependent count | passes in every band, so no breakpoint to set | nothing curve-shaped to build |

What would settle it: a test where the land count isn't the drafter's choice. The
Tempo build (24 spells, 16 lands) is the app's own 16-land deck; comparing drafters
who played close to it against close to the consistent build would be nearer that,
and bears on #275.

## Predictions

| prediction | result |
|---|---|
| pooled, nothing beats 17; 16 and 18 within 0.5 points | wrong: 16 is +1.18 |
| lowest band: 16 better, doesn't pass | wrong: passes, +1.49 |
| highest band: 18 better, doesn't pass | wrong: 18 worse, -0.61 |
| 15 or fewer and 19 or more worse | half: 19+ worse, 15- better |

## What this can't show

What one land fewer does to a given deck. Only what decks at each count won, with the
listed things held equal.
