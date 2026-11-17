# Four hand-set cutoffs, swept

Written before any result of this run was seen.

## Why

Four of the advisor's constants have never been swept. Each was tested only for
whether its rule should exist, not for whether its value is right:

| constant | where | what it does | today |
|---|---|---|---|
| lane share | `_identify_main_colors`, from 15 cards | a color joins the lane if it holds this share of the pool's nonland colored cards (the two leading colors always do) | 0.15 |
| lane weight | `_identify_main_colors`, under 15 cards | a color joins the lane once its rating- and recency-weighted points reach this | 2.5 |
| archetype start | `ARCH_WEIGHT_START` | the weight on the card's pair win rate at the start of a pack | 0.6 |
| archetype ramp | `ARCH_WEIGHT_RAMP` | how much that weight grows by pick 15 of the pack | 0.7 |

The archetype weight is `start + ramp × min(pick, 15) / 15`: 0.65 at pick 1 and 1.3 at
pick 15 today. The lane rule itself stays (recency and the 15-card switch were tested
on 2026-11-15), as does the archetype weight (2026-11-08); only the values move here.
`ARCH_RAMP_PICKS` stays at 15.

## The heads

One value either side of today's for each constant, one change per head:

| head | change | archetype weight, pick 1 to pick 15 |
|---|---|---|
| `lane-share-10` | lane share 0.10 | |
| `lane-share-20` | lane share 0.20 | |
| `lane-weight-1.5` | lane weight 1.5 | |
| `lane-weight-3.5` | lane weight 3.5 | |
| `arch-start-0.4` | start 0.4 | 0.45 to 1.1 |
| `arch-start-0.8` | start 0.8 | 0.85 to 1.5 |
| `arch-ramp-0.4` | ramp 0.4 | 0.63 to 1.0 |
| `arch-ramp-1.0` | ramp 1.0 | 0.67 to 1.6 |

The patches are in `heads/`, written by `make_heads.py` against upstream main's
engine (`d25398c`; this branch's `src/` is identical to it).

## What runs

The Advisor heads workflow, pushed to `run/cutoff-sweeps`: ten sets, 3,000 drafts a set
and salt, the salts `sweep1` and `sweep2`, never used before. Held-out ratings, pools
in pick order. The change in regret slope is the corrected one, with regret scaled
within each set.

## How it is read

Two measures, as the [measure-power test](../2026-11-16-measure-power/RESULTS.md)
asks:

- **regret slope change**, head less base: negative is better for the head;
- **event wins per swapped pick**: positive is better for the head.

A head **beats** today's value if one measure favors it by 2 SEs or more. It is
**flagged** if either measure is against it by 2 SEs or more.

**Move a constant** only if all hold:

1. one of its two heads beats today's value;
2. that head is not flagged by the other measure;
3. the two heads don't both beat today's value. If they do, both directions look
   better than the middle, which is noise or curvature, not a direction; I report it
   and change nothing.

A constant that passes is a retune, not a simplification, so it gets its own
confirmation run on new salts before any PR, as the bomb bonus rule set out.

For each constant I also report whether its three points (low, today's, high) look
like a minimum at today's value: both heads worse than base on each measure's point
estimate, whatever the SEs. And the share of top picks each head changes.

## Predictions

- The lane cutoffs change few top picks: under 1% for lane share (it acts only from
  15 cards, where the two leading colors are already in), 1% to 3% for lane weight.
  None passes.
- `arch-start-0.4` and `arch-ramp-0.4` lean worse, since lowering the weight lost on
  2026-11-08; `arch-start-0.8` and `arch-ramp-1.0` within 2 SEs. No constant moves.
- Each archetype sweep looks like a minimum at today's value on the regret slope; the
  lane sweeps are too flat to say.

## What it can't show

As in the held-out replay: these are associations among drafters who chose freely.
One step either side of today's value can miss a better value further out, and can't
tell a flat optimum from a measure too weak to see one. The measure-power test found
the regret slope misses changes of about 17% of top picks, so "no objection" here means
only "no large harm".
