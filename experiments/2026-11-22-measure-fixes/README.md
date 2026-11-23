# Measure fixes, and earlier verdicts read again with them

2026-11-22. Follows the learned-pick diagnosis (`2026-11-21-learned-pick`,
DIAGNOSE.md), which found two flaws in how heads are read:

1. **SD regret reads spacing as well as order.** Regret is in standard
   deviations of the advisor's scores for the pack, so a head that only spaces
   its scores differently can move it. The learned model read 4.2 SEs worse on
   regret but 0.5 better on rank regret and 1.9 better on missed top. Giving its
   order main's score gaps took its whole regret harm away.
2. **The swap is constrained.** `compare.swap` fits event wins on net = a − b
   and n = a + b + c. Here a counts the event's changed picks where the drafter
   took head's top card, b those where they took base's, and c those where they
   took neither. That holds c's coefficient at the mean of a's and b's. For the
   learned model, the unconstrained figure (wins on a, b and c; β_a − β_b) was
   55% of the constrained one.

Plus a bug: `report.py` binned the drafter's win rate with float floor
division, so 0.42, 0.58 and 0.74 fell a bin low.

## What changed

| where | branch | change |
|---|---|---|
| `Tools/AdvisorReplay/report.py` | `fix/replay-skill-bins` (upstream PR) | skill bins in whole percentage points; test of every bucket |
| `Tools/AdvisorReplay/report.py`, README | `feat/replay-rank-regret` (upstream PR, stacked) | rank regret and missed top beside regret, same controls and paired bootstrap |
| `2026-11-08-heldout-replay/compare.py` | `exp/measure-fixes` | `regret_frame(data, measure)` for rank and missed; `swap_frame` keeps a, b, c; `swap_free` |
| `2026-11-08-pick-multipliers/heads.py` | `exp/measure-fixes` | new table "The order alone": rank regret, missed top and the unconstrained swap combined over salts, with an **order-only reading** (`decide`'s rule on rank regret and the unconstrained swap). `decide()` and the decision column are unchanged. The bootstrap-only table gains the same two columns. |

The order-only reading is a second line, labelled as one. It doesn't replace
the decision.

## Does the order-only reading still catch bad heads?

Yes, from the calibration heads in the simulated-draft run (combined over 8
salts; positive rank regret or negative swap is worse):

| head | decision | rank regret | unconstrained swap (share of constrained) | order-only reading |
|---|---|---|---|---|
| noise20-a | worse (swap) | +0.9 | −2.2 (59%) | worse (unconstrained swap) |
| noise40-a | worse (regret, swap) | +3.0 | −3.8 (55%) | worse (both) |
| gihwr-only | worse (regret, swap) | +5.6 | −7.2 (83%) | worse (both) |
| noise20, re-read run | worse (swap) | +1.9 | −3.5 (58%) | worse (unconstrained swap) |
| scale (spacing only, 0.16% of top cards change) | no objection; regret −1.7 (bootstrap only −2.6) | **+1.5** | −0.7 | no objection |

The constrained swap overstates known harms too: the unconstrained figure is
55% to 60% of it for the noise heads. The `scale` head changes how the scores
are spaced and almost never the order. SD regret reads it as a gain (2.6
bootstrap SEs); rank regret reads it as slightly worse. That is flaw 1 shown
directly.

## Recheck: report-only runs on the saved artifacts

Workflow `advisor-heads.yml` with `report_run` set, from `run/verdict-recheck`
at `757b4b8`. The two 2-salt wheel runs used `9f26e1c`, which adds the
bootstrap-only columns. No artifact had expired. Figures are SEs, scaled as in
the decision (8 salts, t on 7 df); the 2-salt runs are bootstrap only, as
their combined SEs (t on 1 df) say nothing. "Constrained" is the swap the verdict
used; "unconstrained" is β_a − β_b, with its share of the constrained estimate.

| verdict | run | original verdict | regret | constrained swap | rank regret | unconstrained swap (share) | order-only reading | |
|---|---|---|---|---|---|---|---|---|
| **lane 0.10 + wheel tiebreak, joint (handed over)** | 44963810815 | adopt | −1.0 | +2.2 | −1.1 | +1.9 (87%) | no objection | **no longer holds** |
| **wheel tiebreak on top of lane 0.10 (handed over, stacked)** | 44963810815 | adopt | −1.8 | +2.2 | −0.7 | +1.7 (96%) | no objection | **no longer holds** |
| lane 0.10 alone | 44963810815 | no objection | −0.8 | +1.5 | −0.8 | +1.5 (95%) | no objection | unchanged |
| wheel 0.15 alone | 44963810815 | no objection | −1.5 | +1.7 | −0.3 | +1.6 (106%) | no objection | unchanged |
| lane 0.10 alone, simulated-draft run | 44966063581 | adopt | −2.4 | +2.2 | −1.6 | +2.1 (98%) | adopt | **holds** |
| wheel 0.15 alone, simulated-draft run | 44966063581 | adopt | −2.8 | +2.0 | −0.3 | +1.6 (86%) | no objection | **no longer holds** |
| lane 0.10, 11-17 re-read (8 salts) | 44122837249 | adopt | −1.0 | +2.2 | −1.7 | +1.96 (92%) | no objection | **no longer holds** (by 0.04 SE) |
| wheel 0.15, 11-17 re-read (8 salts) | 44122837249 | adopt | −2.9 | +1.9 | −0.3 | +0.3 (17%) | no objection | **no longer holds** |
| wheel 0.15, 11-17 confirm (2 salts, bootstrap only) | 44035287900 | regret −3.3, swap +2.3 | −3.3 | +2.3 | +0.5 | +1.1 (55%) | — | **no longer holds** |
| wheel 0.30 / 0.45 / 0.60, 11-17 sweep (2 salts, bootstrap only) | 44040052598 | regret −2.3 each | −2.3 | +0.7 / +1.4 / +1.2 | +0.8 / +1.0 / +1.6 | −0.5 / +0.1 / −0.7 | — | **no longer holds** |
| no-iwd-premium, flag on (held, never handed over) | 44964368326 | adopt | −4.8 | +1.1 | +0.1 | +1.2 (111%) | no objection | **no longer holds** |

Every figure in the table is in SEs, not an effect size; each report has the
estimates. The rechecks include the skill-bin fix, so their regret and constrained
swap figures differ from the original reports by up to 0.2 SE. For example, the
simulated run's lane 0.10 swap was +2.0 and reads +2.2 here.

### What it says

- **Lane share 0.10 is a small, steady gain on the order.** The unconstrained swap keeps 92% to 98% of the constrained one in all three runs. Its estimate is +0.04, +0.06 and +0.03 event wins per swapped pick, and rank regret is better each time (−0.8, −1.6, −1.7 SEs). It passes the order-only reading in one run and misses it by 0.04 SE in another. The three runs draw different samples (salts r31, r33, ms) from the same 17Lands pools, so they overlap and can't simply be pooled. But no run points the other way.
- **The wheel tiebreak's case was SD regret, and SD regret reads spacing.** Rank regret never reads it better (−0.3, −0.3, −0.3, +0.5, and +0.8 to +1.6 for bigger weights). The unconstrained swap keeps 86% to 106% of the constrained one in the two 2026-11-21 runs, but only 17% in the 11-17 re-read and 55% in the 11-17 confirm, and nothing at bigger weights. On the order alone it passes nowhere. In the joint run, its increment over lane 0.10 keeps 96% of its estimate but its scaled SE grows from 0.051 to 0.061, because the salts spread more (tau 0.060). So it falls to 1.7.
- **The joint lane + wheel head falls just short: +1.9 instead of +2.2.** Its estimate keeps 87%. Most of what it has comes from lane 0.10.
- **no-iwd-premium's adopt rests on SD regret alone.** Rank regret +0.1, missed top −0.9, unconstrained swap +1.2. Its link was held and never handed over, so nothing changes.

## Measured: the two upstream PRs

Before and after on the replay results of an Advisor heads run, via
`measure_report.py` on compact copies (`compact.py`). Drafts are keyed by salt and id within each set, as heads.py keys them.

**Skill bins** (`fix/replay-skill-bins`), run 44963810815, 60,738 complete
events. Head minus base, before → after:

| head | regret | deck score |
|---|---|---|
| lane 0.10 + wheel | −0.0008 (0.0017) → −0.0008 (0.0017) | +0.0000 → +0.0000 |
| lane 0.10 | −0.0005 (0.0016) → −0.0005 (0.0016) | same |
| wheel 0.15 | −0.0003 (0.0002) → −0.0002 (0.0002) | same |

Every slope moves by about 0.0015 event wins per SD, under 1%. The fix is
negligible here.

**Rank regret** (`feat/replay-rank-regret`): the regret and deck rows are
unchanged to the last digit; new rows, head minus base (SE):

| head | regret | rank regret | missed top |
|---|---|---|---|
| lane 0.10 + wheel | −0.0008 (0.0017) | −0.0010 (0.0017) | −0.0022 (0.0018) |
| lane 0.10 | −0.0005 (0.0016) | −0.0007 (0.0016) | −0.0015 (0.0015) |
| wheel 0.15 | −0.0002 (0.0002) | −0.0000 (0.0006) | −0.0004 (0.0010) |

On the learned-pick run 44985574439 (19 sets, 117,365 complete events), the
three disagree as the diagnosis said they would:

| head | regret | rank regret | missed top |
|---|---|---|---|
| learned pick model (lgbm-strong-noalsa) | +0.0148 (0.0049), 3.0 SEs worse | −0.0033 (0.0044), 0.8 better | −0.0143 (0.0050), 2.9 better |
| gihwr-only | +0.0852 (0.0066) | +0.0671 (0.0053) | +0.0600 (0.0049) |

## Files

- `reports/<original run>-<name>.md`: the recheck runs' `heads.md`.
  - joint: 45105993638
  - simulated: 45105999122
  - re-read: 45106001876
  - wheel confirm: 45106805825
  - wheel sweep: 45106808742
  - no-iwd: 45105996250
- `compact.py`: downloads a heads run's artifacts one at a time and keeps the fields `report.py` reads.
- `measure_report.py`: `report.py`'s tables on those copies, with main's skill bins (`--old-bins`) or the checkout's.
