# Addendum: confirm 0.05, or remove the lane share threshold

Written before the run. In the confirmation run ([CONFIRM-RESULTS.md](CONFIRM-RESULTS.md),
run 44030415583), 0.05 beat both today's 0.15 and 0.10. It has passed only in that one run,
the run where it was first tried. At 0.05 the lane already has three main colors on about
90% of picks from 15 cards, which is the cap. So the threshold may be removable
altogether, which would be a simplification.

## What runs

Two heads against today's advisor (main's engine), with patches in
[removal-heads/](removal-heads/) written by [make_heads.py](make_heads.py):

- `lane-share-05`: 0.15 → 0.05, the same patch as the confirmation run.
- `lane-share-none`: the share rule removed. A PR would make the same change. From 15
  cards (and more than 5 colored non-land cards), `_identify_main_colors` drops:
  - the threshold;
  - the count leaders (the top two colors by card count);
  - the filter loop.

  It sets `main_colors = [col for col, weight in sorted_w]`, so the lane is the three
  heaviest colors by weight. Under 15 cards nothing changes: the lane-weight rule (2.5)
  still applies.

Same ten sets as before (DFT, FDN, FIN, FRA, HOB, MSH, SOS, TDM, TLA, TMT), 3,000 drafts a
set and salt, held-out ratings, pick order, corrected regret. The salts are `removal1` and
`removal2`, which no earlier run used. The run goes through the Advisor heads workflow on
run branch `run/cutoff-removal`. [removal.py](removal.py) runs as the extra report.

## Rules

- **0.05 is confirmed** if it again beats 0.15 by 2 SEs or more on one measure, and neither
  measure reads it 2 SEs worse.
- **The removal is preferred over 0.05** if it is not 2 SEs worse than 0.05 on either
  measure, compared head to head on the same drafts with 0.05 as the base. This is the
  simplification rule.
- If 0.05 isn't confirmed, the removal is judged against 0.15 instead. It is preferred over
  today's only if it beats 0.15 by the confirmation rule (2 SEs on one measure, neither
  2 SEs worse).

The measures are the corrected regret slope change (positive is worse for the head) and
event wins per swapped pick (positive is better for the head).

## Also reported

- Top-card changes for each comparison.
- Third-color frequency by pool size, from columns replay.py records on each pick:
  - the share of picks with a three-color lane;
  - the share that gain a third color over today's;
  - the share of drafts that ever do, and at what pool size.
- Both measures for each comparison on the four sets of the ten with the highest
  first-day three-color share (TDM 81%, FRA 15%, TLA 15%, SOS 15%), against the other six.
  Only TDM is above 20%, so the high four are mostly ordinary sets.

## The oddity to watch

Without the threshold the lane is always three colors from 15 cards. `sorted_w` holds all
five colors, so the third can be a color with no playable weight, or no non-land cards
at all. replay.py now also records two more columns on each pick:
- the non-land cards of the lane's thinnest color;
- the non-land cards counted over all colors.

removal.py reports how often the lane holds a color with none, or under 5% or 10% of the
cards.

Dropping the count leaders could in principle also put a top-two color by count fourth
by weight, and so out of the lane. The same thinnest-color numbers would show it.

## Predictions

- 0.05 is confirmed, with smaller effects than in the confirmation run.
- The removal is within 2 SEs of 0.05 on both measures, so it is preferred.
- Without the threshold, about 98% of picks from 15 cards have three-color lanes. A lane
  color with no non-land cards is rare, under 1% of picks. A color under 5% of the cards is
  a few percent of picks, mostly at 15 to 19 cards.
