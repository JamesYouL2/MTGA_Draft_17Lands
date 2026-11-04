# Mana luck and the deck builder's penalties: results

Run [41752671721](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/41752671721)
at `067c22f` (`269f8df` plus a push trigger; that workflow ran this test
and the card-rating test together), on the same decks as the rule tests:
914,784 registered decks and 4.14M games from all 20 sets with Premier
Draft game data and Premier Draft ratings, up to 50,000 decks a set.

The protocol is in [Tools/DeckScoreFit/README.md](../../Tools/DeckScoreFit/README.md#mana-luck-and-the-deck-builders-penalties).
It was written down before the first run. The full report is
[mana.md](mana.md), and the numbers are in [mana.json](mana.json).

The first run,
[41745035079](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/41745035079),
showed a problem in the data, fixed before this run:

- **DMU.** DMU's dump records a mulligan in only 0.14% of games, against
  10–13% in every other set, so its mulligans pass as 7-card keeps. The
  mana test now leaves out any dump that records mulligans in under 2% of
  games, which here is only DMU. Its mana estimates in the first run were
  in line with the other sets.

## The deck builder's mana penalties

`suggest_deck()` charges a build so many score points per point of
`simulate_deck()`'s rate past a threshold. The value column below is what a
point of that rate actually costs, in the same score points. It comes from
three measurements:

- what the event costs in the game it happens in, measured within decks;
- how far a point of the simulator's rate moves the real chance of the
  event in kept hands;
- what card quality is worth per score point.

The data cover 798,355 decks and 3.24M 7-card keeps from 19 sets. The
intervals are 98.75%, which is 95% familywise across the four readings.

| penalty | event's cost (win rate points) | value (score points per point of rate) | penalty | decks past its threshold | keep or drop |
|---|---|---|---|---|---|
| Color Screw (`no-mc-color`) | −14.1 [−16.3, −11.9] | −0.17 [−0.20, −0.14] | −2.5 past 10% | 47,816 | **drop** |
| Mana Screw (`no-mc-screw`) | −19.2 [−22.0, −16.3] | −0.37 [−0.45, −0.30] | −1.5 past 22% | 531 | **drop** |
| Flood Risk (`no-mc-flood`) | −13.2 [−14.5, −11.9] | −0.19 [−0.22, −0.16] | −1.5 past 27% | 609,650 | **drop** |
| All three (`no-mc-all`) | | −0.38 [−0.44, −0.33] for the average deck's rates past the thresholds | −3.37 on average | 617,424 | **drop** |

The events are real and costly: a kept hand that ends up screwed by turn 3
loses about 19 points of win rate. But the penalties are 4 to 15 times what
the rates are worth.

- **Size.** Flood's penalty is 8 times its value and color screw's 15
  times. Across the decks with any penalty, the penalties take 3.4 points
  on average, while their rates past the thresholds cost about 0.4.
- **What "drop" means.** It means no penalty at all is closer to the data
  than these penalties are. It does not mean mana luck doesn't matter. The
  data support a penalty of about 0.2 points per point of color screw or
  flood and about 0.4 per point of screw.
- **Flood's threshold.** Flood's 27% threshold sits at the simulator's
  average rate (27.2%), so three quarters of all decks (76%) pay it.
- **Screw's threshold.** Screw's 22% threshold is reached by only 531
  decks, so that penalty almost never applies.
- **Deck-level check.** A deck-level fit, regressing games won on each rate
  past its threshold, agrees. It is not used for the verdict. It finds
  −0.32 [−0.52, −0.13] for color screw and −0.34 [−0.61, −0.07] for flood.
  That is about twice the within-deck values, but still a quarter of the
  penalties or less.

The value is worked out per point of rate. Rates below a threshold cost wins
too; a smaller penalty could start from zero rather than from a threshold.

### What the simulator gets wrong

| | real (in 7-card keeps) | simulator's own keeps | `simulate_deck()` |
|---|---|---|---|
| mulligans | 11.3% | | 12.8% |
| screw by turn 3 | 7.1% | 8.6% | 10.0% |
| flood by turn 5 | 21.3% | 28.3% | 27.2% |
| color screw by turn 3 | 3.6% | 4.1% | 4.2% |

- **Hand smoothing.** Arena's Bo1 hand smoothing makes 3-land keeps 57.5%
  of keeps, against 32.2% for random 7s. That alone makes real flood and
  screw rarer than the simulator says.
- **Calibration.** Across decks, a point of the simulator's color-screw rate
  is a point of real chance (slope 1.00). For screw it is 1.62 and for flood
  1.18. So the simulator overstates the level of screw and flood but
  understates how much decks differ in them.
- **Within decks,** keeps with 2 or 4 lands win about 4 points less than
  3-landers, and keeps with 5 lands about 12 points less.
- **By set,** each event costs wins in every set but the Cube, which has
  only 1,040 keeps. Screw costs from −11 (LTR) to −27 (DFT), flood from −9
  to −17, and color screw from −7 (MH3) to −19.

## What this suggests

This is a suggestion, not part of the test:

- **Mana penalties.** Cut them to about 0.2 points per point of color screw
  and flood and 0.4 per point of screw. Or drop them: at the right size,
  the average deck with any penalty would lose about 0.4 points.
