# Confirmation run: lgbm-strong-noalsa

This was written and committed before the confirmation run was launched. It
was also written before any of that run's results were read.

## Why

In the first run (Advisor heads 44985574439, README.md),
`lgbm-strong-noalsa` was the one head to beat main:

- event wins per swapped pick +0.037 (scaled SE 0.005), +7.7 SEs;
- regret slope change +0.0089 (0.0053), +1.7 SEs.

Its regret was under the 2-SE bar, but the 95% upper bound (+0.019) sat far
above 0.0063. Earlier runs treated a regret change of 0.0063 as a real loss.
The head was also one of four learned heads, added after a smoke test. This
run checks it on fresh drafts with more power.

## Design

- **Models:** the fits from Learned pick models run 44982629430, reused as
  they are. Each set's model was fitted on the other 18 sets. The replay draws
  fresh drafts, and the held-out set is never in its model's fit, so a refit
  would add nothing. The artifacts expire 2027-02-20.
- **Heads:** main (the base), `lgbm-strong-noalsa`, and `gihwr-only` as the
  sanity control. The patches are in `confirm-heads/` and are byte-identical
  to `heads/`.
- **Drafts:** 19 sets (as before), with 8 fresh salts named after the new run
  (`r<run number>s1` to `s8`). None of the first run's `r35s*` salts is
  reused. Each salt has 3000 drafts, so SEs should shrink by about √3. The
  first run's regret SE of 0.0053 should become roughly 0.003.
- **Simulated draft:** `--simulate` is on. It is a screen only.
- **Extra report:** `confirm_extra.py`, which prints agreement.py's top-1 and
  top-3 tables and the skill-bucket split below.

## The decision rule

The rule applies to `lgbm-strong-noalsa` against main, with combined figures
as `heads.py` reports them in `heads.json`. "SEs" means scaled SEs. The 95%
upper bound is the combined interval's `high` (t on salts − 1 df).

- **Confirmed:**
  - event wins at least 2 SEs better than main; and
  - regret not 2 SEs worse; and
  - the regret change's 95% upper bound below 0.0063.
- **Rejected:** event wins under 2 SEs better, or regret 2 or more SEs worse.
- **Inconclusive:** anything else. It is reported as inconclusive, with no
  rescue: no new salts, subsets or re-reading.

`gihwr-only` is expected to lose on both measures, as in every run so far. If
it doesn't, something is wrong with the run, and that is reported before any
verdict.

Also reported, though not part of the rule: top-1 and top-3 agreement (all and
strong drafters), the simulated deck win rate, and per-set regret
(`by_set.md`).

## Imitation check (not part of the rule)

The swap measure controls for set, skill bucket and games bucket. Even so, a
head trained to copy strong drafters could get credit just because better
drafters within a bucket pick like it. `confirm_extra.py` therefore
re-estimates event wins per swapped pick inside each 17Lands win-rate bucket:
60%+, 56 to 60%, 52 to 56%, and under 52%. The controls are the same, and the
salts are combined in the same way.

How it will be read:

- **Gain holds:** the 60%+ bucket's estimate is positive and at least 2 SEs.
  Then imitation credit is a less likely explanation.
- **Not established:** the 60%+ bucket's estimate is positive but under
  2 SEs. The top bucket alone may lack the power to tell.
- **Fails:** the 60%+ bucket's estimate is zero or negative, while lower
  buckets are positive. Then the gain looks like credit for picking like
  stronger drafters.

Either way, the verdict above is not changed.
