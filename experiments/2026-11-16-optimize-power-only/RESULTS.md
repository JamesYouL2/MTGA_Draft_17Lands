# Auto optimize with only the Power Up swap: results

One run of the Deck builds workflow,
[43815325916](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43815325916),
at `c4253e2`: 346,299 forty-card decks from 19 sets, salt `three`. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. Reports:
[optimize_variants.md](optimize_variants.md), [buttons.md](buttons.md).

## Verdict

**The button becomes the plain swap.** Making the Power Up swap whenever there is one
raises the deck score by 0.75 win rate points more than today's button, 33 SEs above
zero. The rule asked for 2.

| version | changes the deck | deck score change | minus the app's |
|---|---|---|---|
| `app` | 96.4% | +0.076 [+0.045, +0.108] | |
| `power-sim` | 39.4% | +0.325 [+0.295, +0.355] | +0.249 [+0.226, +0.272] |
| `power-always` | 99.7% | +0.825 [+0.780, +0.871] | +0.749 [+0.704, +0.794] |

This is a recommendation to the maintainer, as the protocol says: users press this
button, and the games can't say whether they like what it does.

## Why the simulation loses

The simulation picks Power Up in 11.9% of decks, where it is worth +0.81. In the other
88% it picks something else, and on those same decks the plain swap would have been
worth +0.76 to +0.86.

| the app's swap | decks | the app's change | the plain swap on the same decks |
|---|---|---|---|
| Curve Lower | 33.8% | -0.031 [-0.094, +0.031] | +0.830 [+0.779, +0.881] |
| Optimize Mana | 21.2% | 0 (unpriced) | +0.858 [+0.812, +0.904] |
| Play 18 Lands | 13.8% | +0.052 [-0.704, +0.807] | +0.796 [+0.750, +0.842] |
| Power Up | 11.9% | +0.808 [+0.758, +0.858] | +0.808 [+0.758, +0.858] |
| Fix Mana Base | 9.1% | -0.096 [-0.132, -0.061] | +0.822 [+0.766, +0.877] |
| Play 16 Lands | 6.8% | +0.805 [-0.193, +1.803] | +0.829 [+0.766, +0.892] |
| Base Deck | 3.6% | 0 | +0.764 [+0.724, +0.803] |

`power-sim`, which lets the simulation choose between the swap and the unchanged deck,
makes the swap in only 39.4% of decks and gets under half the gain. So the simulation
is not a good judge of this swap either.

## Predictions

| prediction | result |
|---|---|
| `power-always` changes over 90% of decks | right: 99.7% |
| it raises the score by 0.5 points or more | right: +0.825 |
| `power-sim` is between the two | right: +0.325 |

## What this doesn't show

The deck score can't price lands or mana. Four of the kinds this would drop (16 lands,
18 lands, Fix Mana Base, Optimize Mana) are counted as zero or near it, so the run
can't say they are worthless, only that the score sees nothing in them. Fix Mana Base
is the exception: it swaps spells too, and is -0.10, 5 SEs below zero.

Power Up picks by the archetype's win rate and is scored by the overall one, so the
score isn't simply grading its own choice, but both are GIH win rates and they are
close. And these are decks drafters had already tuned.

## A side result that bears on #270

The same run re-measures Auto lands on four times the decks. A full move from the
rule's basics to the simulation's is now **+0.18 [+0.04, +0.32]** win rate points, on
277,852 decks, which is 2.5 SEs above zero. On 11-13 it was +0.10 [-0.02, +0.22], and
by that run's rule the simulation was removed (#270, merged).

This run was not set up to re-decide that, and its sample overlaps the earlier one. But
by the 11-13 rule this number would have kept the simulation. It is observational:
drafters whose basics match the simulation's may differ in ways the controls miss.
