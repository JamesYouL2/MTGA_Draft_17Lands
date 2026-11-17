# Results: sweeping four hand-set cutoffs

Run [44011837534](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44011837534)
(Advisor heads, branch `run/cutoff-sweeps`, commit `a1420e3`). Ten sets, salts
`sweep1` and `sweep2`, 60,000 drafts and 45,558 complete events per head, held-out
ratings. Raw reports: [heads.md](heads.md), [heads.json](heads.json), [by_set.md](by_set.md).

## Per head

Regret slope change: positive is worse for the head. Event wins per swapped pick:
positive is better for the head.

| head | regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs | top-card changes | on-lane, base to head |
|---|---|---|---|---|---|---|
| lane-share-10 | -0.0069 (0.0017) | -4.2 | +0.126 (0.025) | +5.0 | 2.20% | 76.0% to 76.8% |
| lane-share-20 | +0.0025 (0.0019) | +1.3 | -0.021 (0.025) | -0.8 | 2.37% | 76.0% to 75.3% |
| lane-weight-1.5 | +0.0001 (0.0004) | +0.2 | +0.015 (0.071) | +0.2 | 0.36% | 76.0% to 76.9% |
| lane-weight-3.5 | -0.0000 (0.0006) | -0.0 | -0.113 (0.056) | -2.0 | 0.57% | 76.0% to 74.5% |
| arch-start-0.4 | +0.0012 (0.0005) | +2.6 | -0.008 (0.029) | -0.3 | 1.98% | 76.0% to 75.9% |
| arch-start-0.8 | -0.0009 (0.0005) | -1.8 | -0.042 (0.028) | -1.5 | 1.98% | 76.0% to 76.0% |
| arch-ramp-0.4 | +0.0007 (0.0004) | +1.7 | -0.006 (0.037) | -0.2 | 1.22% | 76.0% to 75.9% |
| arch-ramp-1.0 | -0.0008 (0.0004) | -1.7 | -0.035 (0.032) | -1.1 | 1.24% | 76.0% to 76.0% |

The "verdict" column in heads.md is heads.py's generic one-sided check (does the regret
slope object?). The verdicts below follow this experiment's PROTOCOL.md.

## Verdict per constant

| constant | today | rule outcome | change? |
|---|---|---|---|
| lane share threshold | 0.15 | 0.10 beats today's on both measures (regret -4.2 SEs, event wins +5.0 SEs); 0.20 doesn't beat it on either | **passes: 0.15 → 0.10, pending confirmation** |
| lane weight cutoff | 2.5 | neither side beats today's; 3.5 is flagged worse on event wins (-2.0 SEs) | no change |
| ARCH_WEIGHT_START | 0.6 | neither side beats today's at 2 SEs; 0.4 is flagged worse on regret (+2.6 SEs) | no change |
| ARCH_WEIGHT_RAMP | 0.7 | neither side beats today's at 2 SEs | no change |

**Lane share 0.10** is the only pass, and a strong one: both measures agree, each well
past 2 SEs (it would survive a Bonferroni correction over 16 tests). Both salts agree
(sweep1 -0.0049 (0.0027), sweep2 -0.0090 (0.0027)), and 9 of 10 sets have a negative
regret change (SOS is +0.0026 (0.0045)). It isn't driven by TDM: the sets under 20%
three-color share give -0.0074 (0.0019), -4.0 SEs. It changes 2.2% of top picks, nearly
all between two on-lane cards (86% of changes), and the drafter took the head's pick
more often there (30.2% vs 28.6%). Per the protocol this is a retune, so it needs a
confirmation run on new salts (and ideally a 0.05 point, to see whether the gain keeps
going) before any PR.

## Does today's value look like a minimum?

A minimum means both neighbors are worse on the point estimate.

| sweep | regret slope (low, high) | event wins (low, high) | minimum at today's? |
|---|---|---|---|
| lane share | better, worse | better, worse | **no**: monotone, lower is better |
| lane weight | +0.0001, -0.0000 (flat) | better, worse | no: flat on regret, monotone on event wins (lower slightly better, not significant) |
| archetype start | worse, better | worse, worse | measures disagree: regret is monotone (more weight better), event wins is minimum-shaped |
| archetype ramp | worse, better | worse, worse | measures disagree, same pattern as start |

The two archetype sweeps tell the same story: the regret slope keeps preferring more
archetype weight (both "higher" heads at -1.7 to -1.8 SEs), while event wins leans
against raising it (-1.1 and -1.5 SEs). Neither reaches 2 SEs, so today's 0.6 + 0.7
stays; the 2026-11-08 finding that lowering the weight loses holds again on the regret
slope (arch-start-0.4 +2.6 SEs, arch-ramp-0.4 +1.7).

## Predictions

| prediction | outcome |
|---|---|
| lane share changes under 1% of top picks | wrong: 2.2% and 2.4% |
| lane weight changes 1% to 3% | wrong: 0.36% and 0.57% |
| no lane head passes | wrong: lane-share-10 passes |
| arch-start-0.4 and arch-ramp-0.4 lean worse | right on regret (+2.6, +1.7 SEs); flat on event wins |
| arch-start-0.8 and arch-ramp-1.0 within 2 SEs | right |
| no constant moves | wrong |
| archetype sweeps look like a minimum on regret | wrong: monotone on regret; minimum-shaped only on event wins |
| lane sweeps too flat to say | right for lane weight, wrong for lane share |

I misjudged where lane share acts: it changes more picks than lane weight, not fewer.
From 15 cards the threshold decides whether a third color counts as a main color, and
that turns out to matter more than the early-pick weight cutoff.

## Caveats

- Associations among drafters who chose freely, as in every held-out replay.
- One step either side can't find a better value further out; lane share may keep
  improving below 0.10.
- Ten sets, not the nineteen of the single-pip run.
- The 0.10 pass is a single run; the confirmation run on new salts comes first.
