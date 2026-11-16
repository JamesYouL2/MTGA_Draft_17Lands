# Is the softer off-color penalty's gain in single-pip cards and its harm in double-pip ones?

Written before any result of this run was seen.

## Why

Softening every off-color multiplier to its square root helps in sets with many
three-color decks and hurts slightly elsewhere. Below a 30% share the sets split with
no pattern in the share (`experiments/2026-11-15-flag-threshold`).
`experiments/2026-11-15-what-sorts-sets` found, after the fact, that the split follows
how many of a set's cards have two pips of one color.

There is a reason it might. The square root lifts "Uncastable (Double Pip)" from 0.01
to 0.1, ten times, and "Off-Color" in pack 2 from 0.05 to 0.22. A double-pip off-color
card is the one a drafter can least cast.

If the harm is the double-pip cards, softening only the others should gain in more
sets, and the advisor might not need a set flag at all.

## The heads

Patches in [heads/](heads/). In every set, with no flag:

| head | the square root applies to |
|---|---|
| `soft-single` | off-color cards with one off-color pip |
| `soft-double` | off-color cards with two or more |
| `soft-all` | both: the earlier `softer` |

## What runs

The Advisor heads workflow, held-out ratings, pools in pick order, base upstream main
at `6b6dba9`. All 19 sets with a dataset: the 17 of the first off-color test, and SNC
and KTK. 6,000 drafts a set and salt, the salts `pip1` and `pip2`, new.

## How it is read

From `heads.py` on all sets, and `by_set.py` for the four sets over a 30% share (TDM,
DMU, SNC, KTK) and the other fifteen.

| `soft-single` | verdict |
|---|---|
| better by 2+ SEs in the fifteen, and not worse than `soft-all` in the four | it replaces the flag: single-pip cards are softened in every set |
| within 2 SEs in the fifteen, and better by 2+ SEs in the four | the flag stays. It softens only single-pip cards if `soft-single` is at least as good as `soft-all` in the four, by the estimates |
| worse by 2+ SEs in the fifteen | the flag stays as built |

`soft-double` is the check on the mechanism: it should be worse in the fifteen.

Nothing ships from this run. A change to the flag or a new rule is a pull request with
this as its evidence.

## Predictions

- `soft-double` is worse by 2+ SEs in the fifteen.
- `soft-single` is within 2 SEs in the fifteen, on the better side, and better by 2+
  SEs in the four: the flag stays, on single-pip cards.
- `soft-all` repeats: better in the four, worse in the fifteen.

## What it can't show

As in the held-out replay. The idea came from the same sets it is tested on, though on
new drafts.
