# How much do heads results vary from salt to salt, and why? Protocol

Written 2026-11-17, before either run below was dispatched.

## Why

On 2026-11-17 the need-rules rerun found the same two heads, on the same code and
patches and the same daily dataset build, reading -4.8 and +0.6 SEs (`no-needs-2drops`)
and -3.3 and +2.8 (`2drops-cap-1.25`) on different salts. Over four salts the
estimates spread 2.1 and 2.6 times their bootstrap SEs (χ²(3) 13.6 and 19.7).
`experiments/2026-11-16-need-rules-replay/RESULTS.md` has the numbers. Several
other first passes faded the same day (lane share 0.05, wheel 0.30's event wins).

`report.bootstrap` resamples events. Everything one job shares is fixed across
the resamples: one set, one salt, and so one sample of drafts and one set of
held-out ratings. `holdout.py` rebuilds those ratings from the whole game dump
less that salt's drafts' games, so every salt scores with slightly different
ratings. If the head's effect depends on the ratings, that difference is a
source of variance that no bootstrap over events can see.

## Base and heads

Base: `src/` as on upstream main at `4b36e08` (#273 to #279 merged, including
#274 pack 1 and #275 Tempo removal). The heads, in [heads/](heads/), all apply to
it (seven lines of offset, same context):

| head | from | change |
|---|---|---|
| `lane-share-0.10` | `exp/cutoff-sweeps`, `confirm-heads/lane-share-10.patch` | third lane color from 10% of counted cards, not 15% |
| `wheel-0.15` | `exp/new-rules-splash-wheel`, `confirm/wheel-015.patch` | score times 1 - 0.15 × wheel chance |
| `no-needs-2drops` | `exp/need-rules-replay` | no pack 2–3 Needs 2-Drops bonus |
| `noise20` | `exp/after-landing`, `measure-power/heads/noise20-a.patch` | fixed per-card ±20% nudge: the known-harm control |

Harness: this branch, from `exp/need-rules-replay`, with `replay.py` also writing
`exp/cutoff-sweeps`' four lane columns (top three moves to the last column).

## Runs

1. **Main study.** Advisor heads, all four heads in one run, the ten default sets
   (DFT, FDN, FIN, FRA, HOB, MSH, SOS, TDM, TLA, TMT), 3,000 drafts a set and salt,
   eight fresh salts `ms1` … `ms8`. 80 jobs.
2. **Diagnostic: drafts fixed, ratings varied.** Five sets (FDN, FRA, MSH, TDM,
   TLA), draft salt `ms1`, ratings salts `""`, `rs1` … `rs4`. A ratings salt holds
   another 3,000 drafts' games out of the ratings (`holdout.py --also`) without
   replaying them. So the replayed drafts are the same in all five jobs of a set
   and only the ratings move, by the same kind of difference as between two salts:
   one sample of 3,000 drafts' games in, another out. 25 jobs.
   - The `""` job is exactly the main study's `ms1` job for the set. If its output
     isn't identical, the replay isn't deterministic, a cause by itself.
   - The other way round (ratings pinned to one salt, drafts varied) would replay
     drafts whose games are in the ratings, which is the leak holding out exists
     to prevent. So it isn't run.

The reports are produced on CI from the runs' artifacts by `salts.py`, which reads
one folder at a time.

## Measures

The two measures as in heads.py and compare.py: the regret slope change (within-set
z-scored regret, head minus base; positive is worse for the head) and event wins
per swapped pick (negative is worse). Each comes with its bootstrap SE
(`report.bootstrap`, events resampled). They are computed per salt over all ten
sets, and per set and salt.

## What is computed

For each head and measure:

- **Per-salt estimates** e_j and bootstrap SEs b_j, j = 1 … 8.
- **Inflation factor at the salt level.** Q = Σ w_j (e_j − ē)² with w_j = 1/b_j² and
  ē the weighted mean. φ = √(Q / (k − 1)), the factor by which the salts' spread
  exceeds what the bootstrap SEs allow. 95% CI from χ²(k − 1), treating the b_j as
  known: [√(Q/χ²₀.₉₇₅), √(Q/χ²₀.₀₂₅)]. With k = 8 this interval is wide (about 0.6φ
  to 1.7φ). That is why the next line is there.
- **Inflation factor at the set-and-salt level.** The same Q, within each set
  across its eight salts, summed over the ten sets: 70 degrees of freedom, CI about
  0.8φ to 1.2φ. If the excess is a job-level effect (one set, one salt, one set of
  ratings), the two levels estimate the same ratio. The set level is the headline
  factor if its CI overlaps the salt level's. If not, the salt level is reported as
  the factor and the difference is reported.
- Pooled over the three candidate heads too, where their factors agree (Q tests
  for homogeneity reported).

Diagnostic, for each head and measure, from the five sets:

- σ²_r: the variance of a set's estimate across `rs1` … `rs4` (drafts fixed),
  pooled over sets, 15 df.
- τ²: the main study's between-salt variance in excess of the bootstrap, for the
  same five sets: per set, the variance across its eight salts minus its mean b²,
  then averaged.
- The share of the excess the ratings explain: σ²_r / τ², with a CI by bootstrapping
  sets. Cause found if σ²_r / τ² is 0.5 or more and its CI excludes 0. If it is
  under 0.5 with a CI under 1, the ratings are at most part of it, and the rest
  (draft sampling not caught by the event bootstrap) is reported as unexplained.
- Determinism: the `""` jobs against the main `ms1` jobs, pick for pick.

## Drafts per salt

If the ratings are the cause, more drafts per salt do not help. Holding out a
fraction p of a dump's games moves each rating by noise with variance about p
times the rating's own sampling variance. So the ratings part of a salt's variance
grows with the drafts per salt n, while the bootstrap part falls as 1/n. With k
salts of n drafts and a fixed total J = kn, the variance of the combined estimate is
about (a/n + cn) / k = (a + cn²) / J. That falls as n falls: spend jobs on salts,
not drafts. The study measures c (from σ²_r) and a (from b²). It then states the
split of a fixed job budget that minimises the combined SE, allowing for each job's
fixed cost (downloads and the holdout rebuild).

## Re-read rule (part 3)

Under the corrected SE from the code change (random-effects combination of the
eight salts; see the code and RESULTS.md):

- **Adopt** if the combined estimate is 2+ corrected SEs better on one measure and
  neither measure is 2 corrected SEs worse.
- For a **no objection**, the smallest harm it could have detected: 2 × the
  corrected SE, on each measure.
- `noise20` is the control. If it isn't 2+ corrected SEs worse on event wins
  (11-16: 3.7 SEs on 60,000 drafts), the corrected measure has lost the power to
  see 20% noise. That will be said, and it bears on every "no objection".

## Predictions

- The factor is above 1 for every head on the regret slope: 1.8–2.6 for
  `no-needs-2drops` and `wheel-0.15`, which change under about 1% of top cards and
  whose effects lean on fine score differences; 1.3–2 for `lane-share-0.10` and
  `noise20`, whose effects are larger and steadier. On event wins the factors are
  smaller, 1.0–1.6.
- Set level and salt level agree within their CIs.
- The diagnostic puts at least half of the excess on the ratings (σ²_r / τ² ≥ 0.5),
  and the replay is deterministic.
- So the advice for future runs: four or more salts of the same or fewer drafts
  each, not two salts of more.
- Re-read: `lane-share-0.10` stays the best candidate but at under 2 corrected SEs
  on the combined estimate; `wheel-0.15` and `no-needs-2drops` not adopted, neither
  2 SEs worse. `noise20` 2+ corrected SEs worse on event wins.
