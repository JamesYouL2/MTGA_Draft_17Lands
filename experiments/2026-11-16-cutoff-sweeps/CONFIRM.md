# Confirmation: lane share 0.10, and 0.05

Written before the run. The sweep ([RESULTS.md](RESULTS.md), run 44011837534) found that
lowering the lane share threshold in `_identify_main_colors` from 0.15 to 0.10 beat
today's on both measures (regret slope -4.2 SEs, event wins +5.0 SEs). PROTOCOL.md calls
that a retune that needs a confirmation run on new salts before any PR. The sweep wasn't a
minimum at 0.10, since lower kept getting better, so this run also tries 0.05.

## What runs

- Heads against today's advisor (main's engine): `lane-share-10` (0.15 → 0.10, the same
  patch as the sweep) and `lane-share-05` (0.15 → 0.05). Patches are in
  [confirm-heads/](confirm-heads/), written by [make_heads.py](make_heads.py).
- The same ten sets as the sweep (DFT, FDN, FIN, FRA, HOB, MSH, SOS, TDM, TLA, TMT), 3,000
  drafts a set and salt, held-out ratings, pick order, corrected regret.
- Salts `confirm1` and `confirm2`, never used before.
- Advisor heads workflow, run branch `run/cutoff-confirm`.
- Both measures: the corrected regret slope change and event wins per swapped pick, each
  with its SE.

## Rule

- **0.10 is confirmed** if it again beats today's by 2 SEs on one measure, and the other
  measure doesn't flag it worse by 2 SEs.
- **0.05 is adopted over 0.10** only if it beats 0.10 by 2 SEs on one measure, compared head
  to head (0.10 as the base), and the other measure doesn't flag it worse by 2 SEs.
  Beating today's isn't enough.
- If 0.10 isn't confirmed, the constant stays at 0.15, whatever 0.05 does against today's.

The head-to-head comparison is computed by [confirm.py](confirm.py), which runs as the
workflow's extra report. It uses the same measures as heads.py, with lane-share-10's
replay as the base.

## What the threshold does

To show what the change does, replay.py now records two more columns on each pick: how
many main colors the advisor's lane had, and how many cards were in the pool. confirm.py
reports, for each threshold and pool size:
- the share of picks with a three-color lane;
- the share of picks where the lane has a third color that today's doesn't;
- the share of drafts that ever gain one, and the pool size at the first gain.

The threshold applies only from 15 cards, so smaller pools shouldn't change.

## Predictions

- 0.10 is confirmed, with both measures in its favor again but smaller than the sweep's
  (the sweep's -4.2 and +5.0 SEs were found in a search, so they likely overstate it).
- 0.05 against 0.10 is within 2 SEs on both measures; 0.10 stands.
- At 0.10 the lane gains a third color on about 5% to 10% of picks from 15 cards, most often
  between 15 and 24 cards; 0.05 roughly doubles that.
