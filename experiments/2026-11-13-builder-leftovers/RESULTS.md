# What is left of the deck builder's extras: results

Two runs of the Deck builds workflow at `505a0a0` (`exp/builder-leftovers` plus a push
trigger), on upstream main `6b6dba9`, 19 sets. The protocol is in
[PROTOCOL.md](PROTOCOL.md): its predictions were committed before any code ran, its
first amendment before the first run, and its second between the runs.

- First run, [43537685645](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43537685645):
  928,062 pools and 86,712 played decks. Reports: [deck_variants.md](deck_variants.md),
  [buttons.md](buttons.md).
- Second run, [43541069827](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43541069827),
  salt `two`: 927,915 pools and 857,818 played decks. Reports:
  [second_run_deck_variants.md](second_run_deck_variants.md),
  [second_run_buttons.md](second_run_buttons.md). The two samples overlap where a set
  has few decks, so they aren't fully independent.

## Verdicts

| feature | how often it matters | outcome, win rate points | by the rule |
|---|---|---|---|
| Tempo build | changes the first deck in 0.40% of pools | +0.07 [-0.17, +0.31] | **remove** |
| Promotion, 6-point gap | changes the first deck in 16.67% | -0.01 [-0.75, +0.73] | **no verdict** |
| Promotion, 20-point gap | changes the first two decks in 1.06% | same | **remove** |
| Auto lands' simulation | differs from the rule in 80.3% of decks | +0.10 [-0.02, +0.22] (second run) | **remove** |
| Auto optimize | changes 96.6% of decks | deck score +0.08 [+0.05, +0.11] | **keep** |

Part 1's numbers are the first run's. The second run repeats them within a hundredth
of a point on the rates, with Tempo at +0.12 [-0.10, +0.34] and promotion at
-0.09 [-0.68, +0.50].

## Tempo

A Tempo build comes first in 0.4% of pools, and removing it changes the first deck in
0.40%. Its outcome at the same card quality is +0.07, 0.6 SEs, so the rule removes it.

**This reverses the 11-08 verdict,** where the same move was +0.34 at 2.9 SEs. The
decks and builds are the same. What changed is the card quality it's held equal to: the
deck score now rates cards overall, not by the pair's blend. Against that, playing
nearer Tempo's cards does no better than its rating says. Without the control it's
still -1.27.

Removing it is visible all the same: the list changes in 71.56% of pools and the first
two decks in 30.56%. The rule counts the first deck. Whether users want a second,
lower-curve build to look at is not something the games say.

## Promotion

The 6-point gap replaces the first deck in 16.67% of pools, up from 10.30% on the old
score, from 5.24% (HOB) to 42.86% (TDM). Drafters in the safe colors did no better or
worse than those in the top's: -0.01 [-0.75, +0.73]. No verdict, so it stays.

The 20-point gap changes the first two decks in 1.06% of pools and the first never.
Under 5% with no outcome in its favor, it goes.

## Auto lands

The simulation picks different basics from the rule it starts from in 80.3% of decks,
by one land in under half of those.

- **Drafters play nearer the rule:** 1.10 lands away against 1.32, a gap of
  0.216 [0.146, 0.286]. They play exactly the rule's basics in 28.8% of decks and the
  simulation's in 19.5%.
- **The games lean to the simulation, not clearly:** +0.22 at 1.99 SEs in the first
  run, +0.10 at 1.62 SEs in the second, on ten times the decks. Under 2 SEs both
  times, so agreement decides, and the rule removes the simulation.

My reading: both runs lean the same way, so the simulation's basics may be worth
something like a tenth of a point for a full move. That's a small maybe, against
seconds of simulation, hand-set weights, and two copies of the code (the one in
`deck_builder.py` has no caller).

**Share of pips** is 1.63 lands from drafters' basics, 0.53 further than the app's
rule. No case for replacing the rule, and no follow-up run.

## Auto optimize

It changes 96.6% of played decks. The deciding score change is +0.079 [+0.048, +0.110]
win rate points, so the rule keeps it. By swap:

| swap | decks | deck score change |
|---|---|---|
| Curve Lower | 33.7% | -0.02 [-0.09, +0.04] |
| Optimize Mana | 21.3% | 0, by construction |
| Play 18 Lands | 13.7% | not judged |
| Power Up | 12.1% | +0.79 [+0.74, +0.85] |
| Fix Mana Base | 9.0% | -0.10 [-0.14, -0.06] |
| Play 16 Lands | 6.8% | not judged |
| none | 3.4% | 0 |

All of the gain is Power Up: trading the deck's worst spell for a better one from the
sideboard, which needs no simulator. The score can't judge the three swaps that only
move lands, 44% of what it does. So "keep" here means the button isn't shown to hurt,
not that its simulation is shown to help.

## The predictions

1. **Tempo never first, under 1% change, outcome still favors it: mostly failed.** It
   comes first in 0.4%, the change is 0.40% (held), and the outcome is 0.6 SEs.
2. **Promotion at 5% to 15%, within 2 SEs: failed on the rate** (16.67%), held on the
   outcome.
3. **The 20-point gap under 5% on the first two: held,** at 1.06%.
4. **The simulation differs in over 40% of decks: held** (80.3%). **Almost always by
   one land: failed** (44.4%).
5. **Drafters no nearer the simulation, outcome within 2 SEs: held,** narrowly on the
   outcome.
6. **Drafters nearer the rule than pips: held.**
7. **Auto optimize changes over 80%, mean under 0.5 points: held.** I guessed the
   commonest swaps would be land moves. The commonest is Curve Lower.

## What this changes

Three removals follow from the rule, each its own PR:

- the 20-point promotion gap (`SAFE_DECK_PROMOTE_TO_SECOND_GAP`): the clearest;
- `brute_force_mana_base`, with Auto lands using `calculate_dynamic_mana_base`, and the
  uncalled copy in `deck_builder.py`;
- `build_variant_curve`: the rule says remove, but it changes the list for most users,
  so it's the maintainer's call.

## What it can't show

As the protocol says: it's observational; agreement with drafters isn't quality; the
score can't price lands; and played decks aren't the rough drafts a user presses the
buttons on. The second run was decided after seeing the first, to settle a result at
1.99 SEs, and reads by the same rule.
