# Do Auto optimize's land and mana swaps flag a real problem?

Written before any result of this run was seen.

## Why

[The Power Up test](../2026-11-16-optimize-power-only/RESULTS.md) found that making
the Power Up swap every time beats today's button by 0.75 win rate points of deck
score. But the deck score can't price lands. Four of the button's swaps are about
lands or mana, and that test counted them as zero:

| swap | what the button does |
|---|---|
| Play 18 Lands | the worst spell out, a basic in (one more land, whatever the count) |
| Play 16 Lands | a basic out, the best sideboard spell in (one land fewer) |
| Fix Mana Base | a colorless utility land out, a basic in |
| Optimize Mana | the basics split differently |

Before the button becomes the plain swap, this asks whether the simulation's choice of
one of these says anything true about the deck.

## The measure

Game results, not the deck score. If the button picks "one more land" for a deck
because the deck really is short of lands, then such decks should have won less than
their cards say. So: the win rate of the decks the button picked each swap for,
against the decks it picked Power Up or nothing for, with card quality, the number of
lands played, set and the player held equal, SEs clustered by set (`report.py`).

Negative means the flagged decks did worse, which is what a real fault looks like.

## What runs

The same run as `experiments/2026-11-16-auto-lands-fresh`: the Deck builds workflow,
buttons only, up to 40,000 decks a set that no earlier run used.

## The decision rule

For each of the four land and mana swaps:

| the flagged decks | verdict |
|---|---|
| did worse by 2+ SEs | the button's pick marks a real fault. The plain-swap proposal keeps that check, as a second step or a note to the user |
| otherwise | nothing shows the pick means anything. The swap goes with the simulation |

If a flagged fault is real but under 0.8 points, Power Up still comes first when both
are on offer, since that is what Power Up is worth on the deck score.

Curve Lower is reported the same way for completeness. The deck score already judged
it flat.

## Predictions

- Play 18 Lands: flagged decks did worse, but under 2 SEs.
- Play 16 Lands: no difference.
- Fix Mana Base and Optimize Mana: no difference.
- The button asks for one more land most often in 16-land decks.

## What it can't show

Whether making the swap would have fixed anything. A deck the button flags may lose
for a reason the swap doesn't touch. This shows only whether the flag carries
information. And these are decks drafters tuned themselves.
