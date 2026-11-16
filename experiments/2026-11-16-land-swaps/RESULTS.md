# Do Auto optimize's land and mana swaps flag a real problem? Results

Run [43918276362](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43918276362):
548,462 decks from 18 sets. Reports: [land_swaps.md](land_swaps.md), the planned one,
and [followup.md](followup.md), two checks added after it was seen. The rule is in
[PROTOCOL.md](PROTOCOL.md), written before the run.

## The answer

By the rule as written, three of the four picks mark a real fault. I don't think they
do. The button makes those picks more often for three-color and splashing decks, and
such decks win less than their cards say whatever the button picks. With the deck's
colors held equal, none of the four picks says anything about how the deck did.

So the rule and my reading disagree, and the reading rests on a check that was not
planned. Both are below.

## As planned

Win rate of the decks the button picked each swap for, against the decks it picked
Power Up or nothing for, at the same card quality, land count, set and player.
Negative means the flagged decks did worse.

| the button's pick | decks | against the Power Up decks | by the rule |
|---|---|---|---|
| Play 18 Lands | 13.4% | -0.20 [-0.47, +0.07], 1.5 SEs | no fault shown |
| Play 16 Lands | 6.8% | -0.43 [-0.75, -0.11], 2.6 SEs | real fault |
| Fix Mana Base | 9.2% | -0.62 [-0.97, -0.27], 3.5 SEs | real fault |
| Optimize Mana | 21.7% | -1.02 [-1.28, -0.76], 7.7 SEs | real fault |
| Curve Lower | 33.5% | -0.26 [-0.52, -0.00], 2.0 SEs | for completeness |

## Why I checked further

Every pick reads negative, Curve Lower included. When everything is worse than the
comparison group, the comparison group is the odd one. And "the basics should be split
differently" is an obvious thing to say about a three-color deck.

## The two added checks

**Colors held equal.** The same comparison, with the number of main colors and
whether the deck splashes added to what is held equal:

| the button's pick | as planned | colors held equal |
|---|---|---|
| Play 18 Lands | -0.20, 1.5 SEs | -0.09 [-0.33, +0.15], 0.7 SEs |
| Play 16 Lands | -0.43, 2.6 SEs | -0.09 [-0.38, +0.20], 0.6 SEs |
| Fix Mana Base | -0.62, 3.5 SEs | +0.15 [-0.14, +0.45], 1.0 SEs |
| Optimize Mana | -1.02, 7.7 SEs | -0.21 [-0.45, +0.04], 1.7 SEs |
| Curve Lower | -0.26, 2.0 SEs | -0.02 [-0.28, +0.24], 0.2 SEs |

Also holding equal how far the drafter's basics sat from the rule's changes nothing.

**Who gets each pick.**

| the button's pick | three or more main colors | splashing |
|---|---|---|
| Base Deck (nothing to change) | 7.6% | 19.3% |
| Power Up | 16.9% | 32.4% |
| Play 18 Lands | 13.9% | 31.8% |
| Curve Lower | 19.7% | 35.4% |
| Play 16 Lands | 22.2% | 39.8% |
| Fix Mana Base | 22.7% | 44.9% |
| Optimize Mana | 27.7% | 52.0% |

The order of this table is the order of the planned result. The picks that looked
like faults are the ones made most for decks with stretched mana.

Against every other deck instead of the Power Up decks, only Optimize Mana stands out
(-0.76, 7.6 SEs), and the decks the button leaves alone do best (+1.05, 6.2 SEs).
Both go away with colors held equal for the same reason.

## Verdict

| question | by the rule as written | with colors held equal |
|---|---|---|
| Play 18 Lands marks a fault | no | no |
| Play 16 Lands marks a fault | yes | no |
| Fix Mana Base marks a fault | yes | no |
| Optimize Mana marks a fault | yes | no |

My recommendation is the right-hand column: the plain-swap proposal does not need to
keep these checks. What the button notices is that the deck is three colors or
splashing, which the user already knows, and re-splitting the basics does not undo
that. Optimize Mana is the one to watch: -0.21 at 1.7 SEs is the largest that is left.

The real finding is a different one: three-color and splashing decks win less than
their card quality says, by something like 0.5 to 1 point. That belongs to the deck
score, which does not price it.

## Predictions

| prediction | result |
|---|---|
| Play 18 Lands: worse, under 2 SEs | right: -0.20, 1.5 SEs |
| Play 16 Lands: no difference | wrong as planned (2.6 SEs); right with colors held equal |
| Fix Mana Base and Optimize Mana: no difference | wrong as planned (3.5 and 7.7 SEs); right with colors held equal |
| the button asks for one more land most in 16-land decks | half right: 27.4% of 16-land decks, but 32.9% of the few with 15 or fewer |

## What this can't show

Whether making the swap would have helped. And the colors check was chosen after
seeing the result, so it deserves less trust than a planned one, though the size of
the change (7.7 SEs to 1.7) is hard to get by luck.
