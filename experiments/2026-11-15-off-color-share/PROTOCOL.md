# Should off-color cards cost less in sets where three-color decks are common?

Written before any result of the run was seen. A 150-draft FRA smoke test ran first to
check the patches and the report; I saw its table, where every head was within 2 SEs of
the base.

## Why

In Tarkir: Dragonstorm, 81% of first-day games were played by decks of three or more
colors; in Foundations, 3%. The advisor treats an off-color card the same in both.

An earlier test (fork branch `exp-three-color`) found that a set-level flag, the
off-color penalty times the set's three-color share, fitted on sixteen sets, predicted
TDM's picks better. That was in the logistic pick model of #232, which was closed. The
app has no such weight today. Its off-color handling is `_calculate_castability_v5()`:
hand-set multipliers (0.05 for an off-color card in pack 2, 0.01 in pack 3, 0.3 for a
splashable one, a sliding 1.0 to 0.4 in pack 1), judged against the lane's first two
colors. And that test was never checked against event wins.

So the question has to be asked again on today's app, and before building a flag: does
the right strength of the off-color penalty move with a set's three-color share at all?

The requirement from the earlier round stands: no flag that only fits TDM. It has to
hold across sets and be computable on a set's first day.

## The heads

Patches in [heads/](heads/), all to `src/advisor/engine.py`. None has a flag: each
changes every set the same way, and the reading is across sets.

| head | what changes |
|---|---|
| `softer` | every off-color multiplier becomes its square root (0.05 to 0.22, 0.01 to 0.1, 0.3 to 0.55) |
| `harsher` | every off-color multiplier is squared (0.05 to 0.0025, 0.3 to 0.09) |
| `third-color` | castability is judged against the whole lane, up to three colors, not its first two |

If the right penalty is softer where three-color decks are common, `softer` and
`third-color` should do better as the share rises, and `harsher` worse.

## What runs

The Advisor heads workflow on held-out ratings, with pools in pick order, on the 17
sets that have a draft dump with drafter buckets and an app dataset: TDM, DMU, OTJ, FRA,
SOS, TLA, FIN, DFT, MSH, DSK, LTR, TMT, NEO, EOE, BLB, FDN, HOB. 6,000 drafts a set
and salt, the salts `""` and `arch2`. The base is upstream main at `6b6dba9`.

A set's share is the first-day share of 17Lands games played by decks of three or more
colors, from `exp-three-color` ([shares.json](shares.json)).

## How it is read

`by_set.py` gives each head's change in regret slope in each set, with a bootstrap SE,
and fits a line through them against the share, weighting each set by its SE. Positive
change is worse for the head.

**A flag is supported** by a head when both hold:

1. the line's slope is 2+ SEs from zero in the flag's direction: below zero for `softer`
   and `third-color`, above for `harsher`;
2. the slope keeps its sign with TDM left out, and with DMU left out.

If 1 holds and 2 fails without TDM, the reading is "TDM only", and no flag is built.

If a flag is supported, the follow-up builds it (the penalty's strength as a function
of the share in the app's own dataset) and replays it on new salts. Nothing ships from
this run.

**Each head on all sets together** gets the usual verdict from `heads.py`.
`third-color` is no more code than the app's, so "no objection" makes it a candidate on
its own. `softer` and `harsher` are not simplifications: only a gain of 2+ SEs would
mean the multipliers want retuning, as a separate test.

Reported, not deciding: the pooled change in the sets at 20%+ share (TDM, DMU) and in
the rest, top card changes, top-1, and event wins per swapped pick.

## Predictions

- `softer`: the line slopes below zero by 2+ SEs, from TDM, and doesn't survive
  leaving TDM out. "TDM only".
- `third-color`: better in TDM by 2+ SEs; all sets together, inconclusive.
- `harsher`: worse in TDM; all sets together, within 2 SEs of the base.

## What it can't show

As in the held-out replay. Also: the heads change all multipliers by one power, so a
flag that should act on only some of them (pack 1's, or splashes) could be missed. With
17 sets and one far above the rest in share, the line leans on TDM and DMU whatever the
weights.
