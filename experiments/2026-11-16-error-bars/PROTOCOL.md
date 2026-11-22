# Are the harness's error bars the right size?

Written before any result of this run was seen.

## Why

Many calls rest on results between 2 and 3 SEs of zero. Two things suggest the SEs may
be too small. TMT's gain from a softer penalty was 4.5 SEs in one run and gone in the
next; its samples overlap, which the bootstrap doesn't know. And the threshold test's
set-by-set swings (up to 3 SEs) did not repeat on new drafts.

## What runs

The Advisor heads workflow: ten sets, 3,000 drafts a set and salt, the salts `""` and
`arch2`, held-out ratings, base upstream main at `d25398c`. Ten placebo heads, each
nudging every card's final score by a fixed amount drawn from a hash of its name, so
the nudge has nothing to do with the card's quality:

- `noise03-a` to `noise03-h`: up to 3% either way, eight different draws;
- `noise10-y`, `noise10-z`: up to 10%.

`calibrate.py` then reads the results two ways.

## The measures

1. **Do the SEs match the scatter?** For each head, each set's drafts are dealt into
   eight random folds. Each fold's change has a bootstrap SE. If the SEs are right, the
   folds sit around their set's mean by about one SE: a ratio of 1. A ratio of 1.5 means
   the true SE is half again as large.
2. **How often does noise look like a finding?** A nudge can only make an advisor
   worse or leave it alone, so the eight 3% heads should be near zero, on the worse
   side. Counted: how many reach 2 SEs either way. The 10% heads should be clearly
   worse; they show the harness can see a real loss of that kind.
3. **Overlap:** the share of each set's sampled drafts in more than one sample.

## How it is read

| the ratio, averaged over heads | reading |
|---|---|
| 0.9 to 1.15 | the SEs are sound. The 2 SE bar stays |
| above 1.15 | the SEs are too small by that factor. Every bar is multiplied by it, and results under the new bar are re-read |
| below 0.9 | the SEs are too large; noted, no change |

If two or more of the eight 3% heads are *better* by 2+ SEs, something else is wrong
with the measure, and no new verdict is issued until it is found.

Whatever the ratio, results from sets whose samples overlap by more than 10% get their
SE scaled up by the overlap, and are flagged.

## Predictions

- The ratio is between 1.0 and 1.15.
- None of the 3% heads is better by 2+ SEs; one or two are worse by 2+ SEs.
- Both 10% heads are worse by 3+ SEs.
- Overlap is under 5% in every set but TMT.

## What it can't show

Folds within a set share its ratings and its format, so this checks sampling error
only. It can't show whether a result on these ten sets carries to the next set, which
is where the threshold test went wrong.
