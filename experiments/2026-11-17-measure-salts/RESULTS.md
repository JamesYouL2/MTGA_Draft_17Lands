# How much do heads results vary from salt to salt, and why? Results

Run 2026-11-17, following [PROTOCOL.md](PROTOCOL.md) (written and committed before dispatch).

- Main study: Advisor heads run [44122837249](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44122837249), 10 sets × 8 salts (`ms1`…`ms8`) × 3,000 drafts, 80 jobs, all succeeded.
- Diagnostic: run [44122845725](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44122845725), FDN, FRA, MSH, TDM, TLA × draft salt `ms1` × ratings salts `""`, `rs1`…`rs4`, 25 jobs, all succeeded.
- Reports: run [44142013815](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44142013815) (`.github/workflows/measure-salts-report.yml`), copied to [reports/](reports/): `salts.md` (study and diagnostic), `heads.md` / `heads.json` (new combined verdicts).
- One app dataset build was used throughout (gh-pages `4fd8dbb`, 2026-11-17 01:05 UTC). The 17Lands dumps were last modified on 2026-11-14 or earlier.

## Short answer

**There is no measurable inflation.** The salts spread as much as their bootstrap SEs say, and no more: φ ≈ 1.0 on both measures, for all four heads. The replay is deterministic, and rebuilding the ratings moves the regret estimates by only 2–5% of the bootstrap variance. The "2.1–2.6×" in the need-rules runs came from 4 salts (3 df). On the same data, the per-set test (57 df) says 1.1. So it was mostly chance, and it was noticed because the readings flipped. The working rule "divide old z by ~2.3" should be withdrawn.

## 1. Inflation factors

φ = √(Q/df): how many bootstrap SEs the estimates spread. 1 means the bootstrap is right. The intervals are 95%, from χ².

| head | measure | salt level, 7 df | set level, 70 df |
|---|---|---|---|
| lane-share-0.10 | regret | 0.88 (0.59–1.80) | 1.01 (0.87–1.21) |
| lane-share-0.10 | swap | 1.05 (0.70–2.15) | 0.97 (0.83–1.16) |
| no-needs-2drops | regret | 0.68 (0.45–1.39) | 0.96 (0.83–1.16) |
| no-needs-2drops | swap | 0.85 (0.56–1.73) | 0.98 (0.84–1.17) |
| wheel-0.15 | regret | 0.90 (0.59–1.82) | 1.04 (0.89–1.25) |
| wheel-0.15 | swap | 0.87 (0.58–1.77) | 0.96 (0.82–1.15) |
| noise20 | regret | 1.02 (0.67–2.07) | 1.05 (0.90–1.26) |
| noise20 | swap | 0.92 (0.61–1.87) | 0.91 (0.78–1.09) |

Pooled over all four heads at the set level: regret 1.02 (0.94–1.11), swap 0.95 (0.88–1.04). The heads share drafts, so these pooled intervals are too narrow.

**How sure we are.**

- With 8 salts the salt-level factor alone can't rule out 2 (upper limits 1.4–2.15).
- The set level can. Its upper limits are 1.09–1.26 for every head and measure.
- The two levels agree everywhere, as they must if the excess is a job-level effect. So the set level is the headline, per the protocol: the factor is 1.0, and at most about 1.25 for any one head (95%).
- No set stands out. Per-set φ runs 0.38–1.56 over 80 cells of 7 df each, which is what χ²(7) gives.

**The earlier 2.1–2.6×.** `reports/needs-19sets.md` reruns this analysis on the two need-rules runs: 19 sets, salts `needs1`–`needs4`, 6,000 drafts each.

| head | measure | salt level, 3 df | set level, 57 df |
|---|---|---|---|
| no-needs-2drops | regret | 2.13 (1.21–7.93) | 1.14 (0.97–1.40) |
| 2drops-cap-1.25 | regret | 2.56 (1.45–9.55) | 1.11 (0.94–1.36) |
| no-needs-2drops | swap | 1.38 (0.78–5.16) | 1.15 (0.98–1.41) |
| 2drops-cap-1.25 | swap | 0.29 (0.17–1.10) | 0.96 (0.81–1.17) |

The two runs had the same code, the same patches (byte-identical) and the same dataset build, so the only difference was the salt. A job-level effect would show at the set level, and it shows at most 1.15 there. The 3-df salt-level figures are one noisy draw: the two heads share drafts, so they are one test, not two, and that test was run because the flip had been noticed.

## 2. Cause

There isn't much to explain, but each candidate was checked:

- **Replay determinism: holds.** All 25 result files of the diagnostic's `ms1` jobs are identical to the main study's `ms1` jobs, which ran in a different workflow run.
- **Rating rebuild: small.** With the drafts fixed and only the held-out ratings varied (rs1–rs4, 15 df), the variance of a set's estimate is a small fraction of its bootstrap variance b²:

  | head | regret: σ²_r / b² | swap: σ²_r / b² |
  |---|---|---|
  | lane-share-0.10 | 1.8% | 5.0% |
  | no-needs-2drops | 4.2% | 22% |
  | wheel-0.15 | 3.9% | 49% |
  | noise20 | 2.2% | 5.7% |

  On regret, the ratings would add at most φ ≈ 1.02. On swap, new ratings change which picks swap, so σ²_r there partly re-draws the same sampling noise that the event bootstrap already covers. The main study's direct excess τ² is ≤ 0 on every swap measure. With no excess, the protocol's share σ²_r / τ² isn't defined, so the report prints "n/a (no excess)" for 6 of 8 cells. The two positive cells are noise20 regret, share 0.05, and wheel regret, share 0.61 (0.07–1.18), on a τ² that is itself about 6% of b².
- **Held-out fraction: not a factor.** 3,000 drafts hold out 2.0–9.2% of a set's games (TMT the most); 6,000 drafts hold out 3.0–18.6% (TMT 18.6%, KTK 16.4%, HOB 10.4%). See `reports/heldout-frac.txt`. In the need-rules data the sets with the largest fractions have no extra spread (no-needs-2drops regret: TMT 0.32, KTK 0.69).

**Drafts per salt.** The rating rebuild contributes almost nothing, so more drafts per salt neither help nor hurt the variance. What matters is the t quantile on k − 1 df, which the corrected SE uses (step 3).

Measured job cost: 2.66 min fixed (setup plus the holdout rebuild), plus 4.62 min per 1,000 drafts with 5 labels, averaged over the 79 timed jobs. `budget.py` with φ = 1 gives the scaled SE for the same job time as 4 salts × 3,000 drafts:

| drafts per salt | salts | scaled SE vs 4 × 3,000 |
|---|---|---|
| 750 | 10.8 | 0.84 |
| 1,000 | 9.1 | 0.84 |
| 1,500 | 6.9 | 0.82 |
| 2,000 | 5.6 | 0.81 |
| 3,000 | 4.0 | 1.00 |
| 6,000 | 2.2 | 3.99 |

The curve is flat between 750 and 2,000 drafts. The advice holds within the bounds too: at φ = 1.15 with half of it from the ratings, or at φ = 1.4 all from the ratings, it is still 0.6–0.8.

**Decision: the workflow default is now 8 salts × 1,000 drafts.**

- That is 58 job-minutes a set, against 66 for 4 × 3,000.
- It has 7 df, so t/1.96 = 1.21.
- Each run gets its own salt-level φ, worth checking.

The old default of 2 salts is unreadable under the new rule: t on 1 df is 12.7.

## 3. The code change

`heads.py` now works out both measures in each salt, with each salt's bootstrap SE. It combines the salts with `compare.combine`:

- **Between-salt variance, DerSimonian–Laird.** τ² is the salts' weighted spread beyond what their bootstrap SEs allow. Each salt is then weighted by 1 / (b² + τ²).
- **SE, Hartung–Knapp–Sidik–Jonkman, floored.** The SE is rescaled by the salts' own weighted spread, so it stays honest when τ² is badly estimated from a few salts. It is floored at the plain random-effects SE, so salts that agree by chance can't make it narrower than the bootstrap alone (the "modified" HKSJ).
- **t on k − 1 df.** The "scaled SE" is the SE times t / 1.96, so "2 scaled SEs" keeps meaning about 95%. That is 1.62× with 4 salts and 1.21× with 8.

Why this method:

- The salts are the replicates. Each one is a fresh draw of everything a job shares: the drafts, and the held-out ratings rebuilt without them.
- Combining per-salt estimates puts any shared noise in the SE without modelling where it comes from.
- HKSJ with t is the standard fix for DerSimonian–Laird's overconfidence with few studies.
- Per-set-and-salt cells aren't replicates of one quantity, because sets differ in their true effects.

What it outputs:

- Per head and measure: the per-salt estimates, τ, φ with its interval, the combined estimate with its scaled SE, the two-measure decision and the smallest detectable harm.
- `--pair A:B` gives the same for head B against head A on the same drafts.
- The old bootstrap-only figures are still printed, and still written to `heads.json`, under a label.
- `compare.py` gains `combine`, `inflation`, `by_salt`, `salt_of` and `swap_frame`.
- Tests: `Tools/AdvisorReplay/tests/test_combine.py`, 10 tests. All 39 harness tests pass.

`advisor-heads.yml`: `salts` takes a count or a JSON list.

- A count makes fresh salts named after the run (`r<run number>s1`…), so a confirmation run can't reuse the drafts that picked a winner by accident.
- `salt_prefix` repeats a numbered run.
- A plan job rejects duplicate salts and salts containing `-` or `+`, which would break how `heads.py` reads salts back from artifact names.
- The default is 8 salts × 1,000 drafts.

A possible refinement, not made: φ ≈ 1 is now measured on 70 df, so τ² could be estimated within sets, on S(k − 1) df, and the t penalty dropped. That would gain the 1.21× back. It is left out to keep the rule simple and conservative.

## 4. Re-read on the 8-salt study

Combined over 8 salts. Each figure is the estimate (scaled SE), then the number of scaled SEs. Regret: positive is worse. Swap (event wins per swapped pick): negative is worse.

| head | regret slope change | event wins per swap | decision | smallest harm, regret / swap | top changes |
|---|---|---|---|---|---|
| lane-share-0.10 | −0.0012 (0.0011), −1.1 | +0.034 (0.015), **+2.3** | **adopt** | +0.0022 / −0.031 | 2.19% |
| no-needs-2drops | −0.0003 (0.0002), −1.8 | +0.090 (0.045), **+2.0** | **adopt** (at the line) | +0.0004 / −0.089 | 0.33% |
| wheel-0.15 | −0.0004 (0.0001), **−2.9** | +0.056 (0.029), +1.9 | **adopt** | +0.0003 / −0.058 | 1.04% |
| noise20 (control) | +0.0025 (0.0014), +1.8 | −0.037 (0.006), **−6.3** | worse (swap) | | 17.33% |
| wheel-0.15 against lane-share-0.10 | +0.0008 (0.0011), +0.7 | −0.014 (0.015), −0.9 | no objection | +0.0022 / −0.031 | 3.10% |

- **The control works.** noise20 is 6.3 scaled SEs worse on swap. The regret slope again misses 20% noise (+1.8, even on 240,000 drafts), as on 11-16, so swap is the measure with power.
- **lane-share-0.10: adopt.** This is its third pass on swap (sweep +5.0 and confirmation +3.4, bootstrap SEs, now readable as they stand), with regret on the better side each time.
- **wheel-0.15: adopt.** Regret −2.9. Swap is +1.9, but it has been on the better side in all three runs, and the two earlier runs pooled to +3.2.
- **no-needs-2drops: adopt by the rule, but exactly at the line** (swap +2.0). Its history is mixed: −4.8 regret / +2.7 swap in run 1, a null in run 2, and now this. A fresh-salt run with the new default should confirm it before a PR. Note too that the 11-03 game results pointed the other way.
- **Wheel against lane: no objection either way**, and the run could have seen a harm only as large as +0.0022 regret / −0.031 swap. They were tested separately, so a joint head is owed before proposing both.

## 5. Predictions against outcomes

| prediction | outcome |
|---|---|
| φ above 1 on regret: 1.8–2.6 for no-needs/wheel, 1.3–2 for lane/noise20; swap 1.0–1.6 | **Wrong.** About 1.0 throughout |
| Set and salt levels agree | Right |
| Ratings ≥ half of the excess; replay deterministic | Deterministic: right. There is no excess to share out; the ratings add 2–5% of b² on regret |
| Advice: 4+ salts of the same or fewer drafts | Right in direction, but because of t on k − 1 df, not variance. Default set to 8 × 1,000 |
| lane-0.10 under 2 corrected SEs | Wrong: +2.3 on swap, adopt |
| wheel and no-needs not adopted, not worse | Wrong: both adopt, both close to the line |
| noise20 2+ worse on swap | Right: −6.3 |

## 6. Past verdicts the inflation factor bears on

The measured factor is about 1.0. For the 19-set, 6,000-draft runs it is 1.1–1.15, with an upper limit of 1.4. So:

**Restore what the "~2.3×" rule downgraded** (memory note of 2026-11-17, "MEASURE PROBLEM"):

- lane share 0.10: sweep regret −4.2 / swap +5.0, confirmation +3.4 / −1.8. Stands as read.
- wheel 0.15: confirmation regret 3.3 / swap 2.4; swap pooled over two runs 3.2. Stands as read.
- The guidance "single-run readings under ~5 SEs are unconfirmed" no longer holds as stated. The usual 2-SE rule applies to bootstrap SEs from runs before this one, with a factor of up to 1.15–1.25 for safety.

**Could change at the upper limit (φ ≈ 1.25–1.4), so treat as borderline.** These are verdicts whose bootstrap |z| was 2–2.8, all named, none rerun:

- Needs Fixing sweep: 1.0 worse by 2.5, 2.0 worse by 2.3 (`exp/needs-sweep`).
- Bomb splashes keep: 2.6 (`exp/splash-rules`).
- On-lane 1.1× keep: 2.7 on the rerun, 1.7 after the 11-16 re-read.
- Need-rules rerun: cap-1.25 regret 2.8 worse, flat-bonus-strong 2.6 worse.
- no-needs-2drops run 1 swap +2.7 (regret −4.8 is safe).
- Wheel: s=0.15 first pass swap 2.1, confirmation swap 2.4; s=0.30 sweep regret 2.3; s=0.30 pooled swap 2.4.
- Lane 0.05 against 0.10 head to head: regret 2.0. No-threshold against 0.15: swap 2.1.
- Measure power: 40% noise detected at 2.7 / 2.0.
- no-iwd-premium: 2.3 worse in the four high three-color sets.
- #274 (pack-1, merged): 15 low sets regret 2.5 worse.
- Splash budget: leans worse at ~1.9. Not a 2-SE verdict, so unchanged.

**Safe at any plausible factor (|z| ≥ 3):**

- Arch level removed: 3.8.
- Greedy Bomb: 3.3 / 6.8.
- Splashable and premium splash: 3.7.
- Joint check: 3.9.
- Single-pip: 4.7 / 3.9.
- Lane sweep: 4.2 / 5.0.
- no-iwd-premium overall: 4.3.
- Recency and the 15-card switch: 9 SEs.

**"No objection" verdicts.** Their detectable harm was understated by at most the same 1.15–1.25. The bigger issue, noted 11-16, is unchanged: the regret slope can't see 20% noise, so "no objection" on regret alone means little. Examples are removals #273, no-needs-removal, no-curve-foundation and removal-1.15.

Not affected: deck-builds, splash-price, record-calibration and other non-heads measures, which this study didn't cover.
