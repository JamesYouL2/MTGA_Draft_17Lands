# What the regret measure can detect: results

Run [43917895253](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43917895253):
ten sets, 60,000 drafts, salts `power1` and `power2`. Full tables in
[heads.md](heads.md) and [by_set.md](by_set.md). The rule is in
[PROTOCOL.md](PROTOCOL.md), written before the run.

## The answer

The regret slope sees an advisor that is badly broken. It does not see one that is
moderately broken: random nudges of up to 20% a card, which change 17% of top picks,
pass as "no objection" or "inconclusive". Event wins per swapped pick does see them,
at 3.7 SEs, and qualifies as a second measure.

## The damage heads

Positive regret slope change is worse for the head.

| head | top picks changed | regret slope change (SE) | SEs | agreement with drafters, points | event wins per swapped pick (SE) | SEs |
|---|---|---|---|---|---|---|
| `noise20-a` | 17.3% | +0.0022 (0.0022) | +1.0 | -1.80 | -0.034 (0.009) | -3.8 |
| `noise20-b` | 17.8% | +0.0007 (0.0021) | +0.3 | -1.92 | -0.037 (0.010) | -3.7 |
| `noise40-a` | 29.4% | +0.0106 (0.0039) | +2.7 | -4.67 | -0.049 (0.007) | -6.9 |
| `noise40-b` | 30.7% | +0.0077 (0.0039) | +2.0 | -5.24 | -0.048 (0.007) | -6.4 |
| `random-a` | 80.7% | +0.2396 (0.0142) | +16.9 | -27.61 | -0.077 (0.004) | -17.9 |
| `random-b` | 78.4% | +0.2281 (0.0141) | +16.1 | -27.37 | -0.077 (0.004) | -18.0 |
| `worst` | 96.7% | +0.4582 (0.0207) | +22.1 | -37.71 | -0.080 (0.004) | -19.8 |

## Read by the rule

| what the regret slope does | happened? |
|---|---|
| flags `random`, `worst` and both `noise40` | yes. `noise40-b` only just: 2.01 SEs |
| flags `noise20` in both draws | no, in neither: 1.0 and 0.3 SEs |
| misses `noise40` in either draw | no, by a hair |
| misses `random` or `worst` | no |

So the measure is fit to decide large questions, and its floor is 40% noise. No
verdict is reopened by the rule.

But the floor is high. The removal rule calls a change safe when its regret slope
change plus 2 SEs is under +0.0063. 20% noise moves the slope by +0.0007 to +0.0022,
and 40% noise by +0.008 to +0.011. So "no objection" rules out damage about the size
of 40% noise and nothing smaller. The removals tested so far change 0.5% to 11% of
top picks. For those, "no objection" says the removal is not a disaster. It does not
say the removal is harmless.

## The second measure

The protocol's test: order the heads as damage does, each flagged at 2+ SEs.

- **Event wins per swapped pick** passes. Every damage head is flagged, and the order
  is right: `worst` -0.080, `random` -0.077, `noise40` -0.048 and -0.049, `noise20`
  -0.034 and -0.037. It cannot tell `worst` from `random`, which are 0.003 apart with
  SEs of 0.004. It is not negative for every change: in earlier runs the three-color
  flag read +0.083 (0.018) and eight draws of 3% noise averaged about zero.
- **Agreement with drafters' picks** orders the heads correctly, but the report gives
  it no SE, so it can't be held to the 2 SE test. It also can't be a judge on its
  own: it rewards copying drafters, not winning.

Wins per swapped pick has its own limit. Its SE grows as fewer picks change: 0.009 at
17% of picks, about 0.024 at 3%, 0.051 at 0.6%. A removal that changes 3% of picks
would need to cost 0.05 wins a swapped pick, as much as 40% noise does, to be flagged.

So neither measure can show that a small removal is harmless on 60,000 drafts. What
they can show together is that it is not large harm.

## The two reference heads

| head | regret slope change (SE) | SEs | agreement with drafters | on-lane picks |
|---|---|---|---|---|
| `gihwr-only`: win rate alone, no rules | +0.0971 (0.0097) | +10.0 | -10.29 | 76.0% to 45.7% |
| `alsa-only`: the crowd's pick order | +0.0872 (0.0123) | +7.1 | -6.32 | 76.0% to 45.4% |

The rules together are worth a lot: without them the advisor is worse by 10 SEs, about
40% of the way from the app to a random advisor. Nearly all of that is staying in
lane. Both heads take an off-color card on over half of picks.

## Predictions

| prediction | result |
|---|---|
| `random` and `worst` flagged by over 10 SEs | right: 16.1, 16.9 and 22.1 |
| `noise40` flagged in both draws | right, barely: 2.7 and 2.0 |
| `noise20` flagged in one of two | wrong: neither |
| top-1 orders all the damage heads | right |
| `gihwr-only` worse than the app by 2+ SEs | right: 10.0 |
| `alsa-only` worse than `gihwr-only` | wrong: +0.087 against +0.097, not different |

## What follows

1. Removals should be read on both measures from here on, and a "no objection" on the
   regret slope alone should be reported as "not large harm".
2. The removals already merged were each small. None is reopened by the rule, but
   their evidence is weaker than the write-ups said. Re-reading them on wins per
   swapped pick is the cheap next check.
3. A draw's luck matters. `noise20-b` and `noise40-b` are both much worse in TDM
   (+0.024 and +0.051) and `-a` is not, from one fixed set of nudges. Any single-draw
   result in one set should be treated that way.

## What this can't show

Random noise is one kind of damage. A rule that is wrong in a systematic way may be
easier or harder to see than noise that changes the same number of picks.
