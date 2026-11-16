# Are the harness's error bars the right size? Results

One run of the Advisor heads workflow,
[43814780003](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43814780003):
ten sets, 60,000 drafts, 45,409 complete events. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. Reports:
[calibrate.md](calibrate.md), [heads.md](heads.md), [within_set.md](within_set.md).

## Verdict

**The SEs are the right size. The 2 SE bar stays, and no earlier bar is widened.**
Dealt into eight folds a set, the folds scatter around their set's mean by 0.99 of
their bootstrap SE on average, from 0.89 to 1.09 over the ten heads. The protocol
calls 0.9 to 1.15 sound.

Overlap between samples is small: 1.1% to 4.5% of a set's drafts are in more than one
sample, TMT the most. Nothing reaches the 10% that would scale a set's SE.

## Two things the run found that the protocol didn't expect

**1. The all-sets figure was mis-scaled.** This is the fault described in
[the joint run's results](../2026-11-16-proposed-together/RESULTS.md): regret was
divided by a spread that includes the gaps between sets. The fold test above works
within one set at a time, so it is unaffected. The all-sets numbers below are the
corrected ones, with the first reading beside them.

| head | top card changes | as first read | corrected | top-1 change |
|---|---|---|---|---|
| `noise03-a` | 2.82% | +0.0001 (0.0004) | +0.0002 (0.0004), +0.5 SEs | -0.07 |
| `noise03-b` | 2.92% | -0.0005 (0.0004) | -0.0005 (0.0004), -1.3 SEs | -0.09 |
| `noise03-c` | 2.89% | +0.0006 (0.0004) | +0.0005 (0.0004), +1.3 SEs | -0.04 |
| `noise03-d` | 2.84% | -0.0012 (0.0004) | -0.0008 (0.0004), -2.0 SEs | -0.03 |
| `noise03-e` | 2.87% | +0.0001 (0.0005) | -0.0001 (0.0005), -0.2 SEs | -0.10 |
| `noise03-f` | 2.84% | -0.0002 (0.0004) | -0.0005 (0.0004), -1.2 SEs | -0.09 |
| `noise03-g` | 2.85% | -0.0004 (0.0005) | -0.0001 (0.0004), -0.3 SEs | -0.02 |
| `noise03-h` | 2.86% | +0.0006 (0.0004) | +0.0002 (0.0004), +0.5 SEs | -0.03 |
| `noise10-y` | 9.11% | -0.0041 (0.0013) | -0.0038 (0.0012), -3.1 SEs | -0.48 |
| `noise10-z` | 9.46% | +0.0019 (0.0012) | +0.0008 (0.0011), +0.7 SEs | -0.53 |

**2. The regret slope does not see random noise as a loss.** I expected a nudge
unrelated to card quality could only hurt. It didn't: the eight 3% heads average
-0.0001, four on each side of zero, and of the two 10% heads one is 3.1 SEs *better*
and the other flat. Scrambling 9% of top cards by up to 10% cost nothing this measure
can see. Agreement with what drafters took did fall, by half a point for the 10%
heads.

A fixed nudge by card name is a real change to the advisor, not a coin flip per draft.
So each head has its own true effect, which can be either sign, and one head at 3 SEs
doesn't say the SEs are wrong. The fold test is what speaks to that, and it passes.

What it does say:

- **"No objection" is weak evidence.** A change that reorders cards at random also
  gets "no objection". A removal passing the rule shows the rule's effect is small on
  this measure, not that the rule is useless.
- **A single head better by 2 to 3 SEs can be luck of the draw in which cards it
  favors.** Results that repeat on new drafts and across sets, as the flag's do, are
  the ones to trust.

The protocol's stop condition (two or more of the eight 3% heads better by 2+ SEs)
was not met: one is, at exactly 2.0.

## Predictions

| prediction | result |
|---|---|
| the ratio is between 1.0 and 1.15 | just under: 0.99 |
| none of the 3% heads is better by 2+ SEs; one or two are worse | wrong: one is better at 2.0, none is worse by 2 |
| both 10% heads are worse by 3+ SEs | wrong: one is 3.1 SEs better, one is flat |
| overlap is under 5% in every set but TMT | right, and TMT is under 5% too (4.5%) |

## What it can't show

Folds within a set share its ratings and format, so this checks sampling error only.
