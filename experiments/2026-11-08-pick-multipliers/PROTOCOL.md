# Do the advisor's small multipliers earn their place?

Written before any result was seen.

## Why

`src/advisor/engine.py` multiplies a card's score by several hand-set factors.
Earlier rule tests covered the pick rules that respond to what a pool lacks. These
four haven't been tested on results. Each adds a rule to explain and maintain, so
each should show that drafts go better with it.

| head | what it removes | where |
|---|---|---|
| `no-synergy` | 1.2x for a card tagged artifact, graveyard or counters synergy once the pool has 4, 3 or 3 such cards | `_calculate_composition_bonus()` |
| `no-premium-fixing` | 1.15x for a multicolored land or fixing card in pack 1 | same |
| `no-bomb-splash` | 1.3x for a land or fixing card in the color of a pool's off-lane card rated 1.5 SDs above the mean | same |
| `no-on-lane` | 1.1x for a card the lane can cast, 1.3x when pack 3 is short of playables | `evaluate_pack()` |

The patches are in [heads/](heads/). The composition rules return at the first
match, so a card that loses one of them can still earn a later rule, as it would in
the app with the rule gone.

## What runs

The Advisor heads workflow: ten sets, 3,000 drafts a set, the salts `""` and `arch2`
(the drafts of `experiments/2026-11-08-heldout-replay`), on held-out ratings only.
The base is this branch's `src/`, the same as `5a42fb2`.

Unlike the Advisor replay workflow, all heads share each set and sample's job, with
one base replay and no app or rebuilt ratings. That compares them on one set of drafts
and ratings, with a fifth of the replays.

## How it is read

The measure is the change in regret slope, head minus base, pooled over both
samples, with a paired bootstrap SE. Positive is worse for the head. Each head gets
one verdict from the replay:

1. **Keep:** worse by 2 SEs or more.
2. **Inconclusive:** otherwise, if the change plus 2 SEs is above +0.0063, what no
   archetype weight cost in the held-out replay, already known to be a real loss. The
   replay can't rule out a loss of that size, so it doesn't clear the rule.
3. **No objection:** otherwise. The rule can go on this evidence. This isn't proof
   of equivalence.

With several heads, the 2 SE bar makes a false "keep" likelier, which only leaves a
rule in place. No correction is applied.

`no-bomb-splash` also has a test on game results, on the `exp/bomb-splash-rule`
branch, with its own protocol. It is removed only if the replay has no objection and
that test doesn't support the rule. The pack-1 gate of Premium Fixing and the lane's
position in a draft don't exist in a finished deck, so `no-premium-fixing` and
`no-on-lane` rest on the replay alone.

## Prediction

- `no-on-lane` is worse by 2 SEs or more. Staying in a lane is the main thing it
  does that the ratings don't.
- The other three get "no objection", and each changes the top card on under 1% of
  picks.

Reported, not deciding: how often the top card changes, top-1 (drafters themselves
draft by lane, so it favors `no-on-lane`'s base), the on-lane share of top cards,
the change in each sample, and event wins per pick swapped to the head's top card.

## What it can't show

As in the held-out replay: slopes are associations among drafters who chose freely,
holding out a draft doesn't remove the drafter's other drafts, and regret says
whether drafters who followed an advisor won, not what its users would win.

## Amendments

Made on 2026-11-08 after the run started and before any of its results were seen.

- **`no-synergy` can't change anything.** The rule reads the tags `synergy_artifacts`,
  `synergy_graveyard` and `synergy_counters`. `src/scryfall_tagger.py` makes none of
  them, and no card in the 19 Premier Draft datasets checked has one. So the rule never
  fires, and its head has no test on game results as first planned. It stays in the run
  as a control: if its picks aren't identical to the base's, the harness is wrong.
