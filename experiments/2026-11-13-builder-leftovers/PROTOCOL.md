# What is left of the deck builder's extras, on today's app

Written before any result in this folder was seen, and before the code had run on any
deck.

## Why

Since `experiments/2026-11-08-deck-variants`, the app has changed under the things it
tested: the simulator's mana penalties are gone (#263), the deck score rates cards by
their overall win rate (#264) and the domain bonus is gone (#267). That test said
nothing was tested together. Two questions are left.

1. **Tempo builds and safe-deck promotion.** On the old score, a Tempo build never came
   first without the penalties, and promotion changed the first deck in 10.30% of pools
   with no outcome either way. Neither has been counted on the app as it is.
2. **The simulator's last two decisions.** In the suggested decks it only fills in the
   numbers shown. It still decides two things, both in the Custom Deck window:
   - **Auto lands** (`brute_force_mana_base`) simulates the basics within two of the
     app's rule (`calculate_dynamic_mana_base`) and keeps the best by a fitness with
     hand-set weights.
   - **Auto optimize** (`optimize_deck`) simulates up to about ten single swaps and
     keeps the best by a second fitness with different hand-set weights.

   `exp/mana-penalties` judged the same simulated rates not worth keeping in the deck
   score. Nothing has tested the two buttons.

## What runs

The Deck builds workflow on the same 19 sets, salt `""`, on upstream main at `6b6dba9`
plus this branch's tools.

**Part 1** uses up to 50,000 pools a set through `suggest_deck()`, as before, with
held-out ratings:

| version | what changes |
|---|---|
| `app` | nothing |
| `no-tempo` | `build_variant_curve` builds nothing |
| `no-promotion` | neither gap promotes. The safe deck is still kept and labeled |
| `neither` | both |
| `no-top-promotion` | only the 6-point gap is off |
| `no-second-promotion` | only the 20-point gap is off |

**Part 2** uses the first 5,000 sampled decks a set that are 40 cards with basics
(`Tools/DeckScoreFit/buttons.py`). Each deck keeps its spells and nonbasic lands, and
its basics are chosen again by the app's rule, by Auto lands' simulation, and in
proportion to the spells' colored pips. Then the deck and its sideboard go through
`optimize_deck()`. The simulator has a fixed seed, so it isn't random here.

## The measures

**Part 1** keeps the earlier protocol's measures: how often each version changes the
top deck, the first two and the list; which kind of build comes first; Tempo's outcome
(a full move from Consistent's cards to Tempo's at the same card quality); promotion's
outcome (drafters in the safe colors against the unpromoted top's).

**Auto lands.**
- How often the simulation's basics differ from the rule's, and by how many lands.
- **Agreement:** lands moved between each choice and what the drafter played (half the
  sum of the differences by color), and the paired difference between the simulation
  and the rule, with set-clustered SEs.
- **Outcome:** among decks where the two differ, where the played basics sit between
  them: (lands from the rule − lands from the simulation) ÷ lands between the two, so
  −1 is the rule's and +1 the simulation's. A logistic regression of games won on that
  position, controlling for card quality, set and the player's buckets, the larger of
  model and set-clustered SEs. In win rate points for a full move.

**Auto optimize.**
- How often it changes the deck, and the share of each kind of swap.
- The change in the deck score, overall and by kind, in win rate points at the score's
  own price, with set-clustered SEs.

## The decision rules

**Tempo and promotion:** the earlier rule, on the `app` rates.

| | verdict |
|---|---|
| outcome favors it by 2+ SEs | keep |
| outcome is against it by 2+ SEs | remove |
| neither, and it changes the top deck in under 5% of pools | remove |
| neither, in 5%+ of pools | no verdict |

Each gap is also read alone: the 6-point gap on the top deck, the 20-point gap on the
first two. A gap under 5% goes if promotion's outcome doesn't favor it by 2+ SEs.

**Auto lands' simulation**, against the rule it starts from:

| | verdict |
|---|---|
| outcome favors the simulation's basics by 2+ SEs | keep |
| outcome is against them by 2+ SEs | remove: the button uses the rule |
| neither, and drafters' basics are nearer the simulation's by 2+ SEs | keep |
| neither, otherwise | remove |

The simulation is the costly one (seconds, about 150 lines in two copies, its own
weights), so a tie goes to the rule.

**The pips rule** is reported, not decided. All four builders use the app's rule, so
replacing it changes every suggested deck, and that needs the builds run. If drafters'
basics are as near to pips as to the rule, that run is the follow-up.

**Auto optimize:**

| | verdict |
|---|---|
| it changes the deck in under 5% of decks | remove |
| the deck score falls by 2+ SEs on average | remove |
| the deck score rises by 2+ SEs on average | keep |
| otherwise | no verdict |

A remove here is a recommendation to the maintainer: both are buttons a user presses,
and this can't see whether users like them.

## The predictions

1. A Tempo build never comes first, and `no-tempo` changes the top deck in under 1% of
   pools. Its outcome still favors it by 2+ SEs, so it stays.
2. Promotion changes the top deck in 5% to 15% of pools, with an outcome within 2 SEs of
   zero: no verdict again.
3. The 20-point gap changes the first two decks in under 5% of pools.
4. Auto lands' simulation differs from the rule in over 40% of decks, almost always by
   one land.
5. Drafters' basics are no nearer the simulation's than the rule's, and the outcome is
   within 2 SEs of zero: remove.
6. Drafters' basics are nearer the rule's than pips'.
7. Auto optimize changes over 80% of decks. The commonest swaps move a basic or the
   land count, which the score can't see, so the mean score change is under 0.5 points
   either way. Whether it clears 2 SEs I don't predict.

## What it can't show

- **It's observational.** Drafters chose their basics and their decks. Position between
  two mana bases a land apart is a coarse measure, and most played decks will sit at one
  end or the other.
- **Agreement isn't quality.** Drafters' basics are what people do, not what's best.
  It decides only when the games don't.
- **The deck score can't price mana.** It has no land count and no basics. A swap that
  only moves lands scores zero, so Auto optimize is judged on its spell swaps and on
  how often it does anything. The simulated rates it optimizes are the ones
  `exp/mana-penalties` found didn't earn a place in the score.
- **Played decks aren't what users optimize.** A user may press the button on a rough
  draft of a deck, where it could do more good than on a finished one.
