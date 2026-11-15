# A three-color flag on the off-color penalty

Written before any result of these runs was seen. A 150-draft FRA smoke test ran first
to check the patches; I saw one head's row, within 2 SEs of the base.

## Why

`experiments/2026-11-15-off-color-share` found that softening every off-color
multiplier does better as a set's three-color share rises, at 3.4 SEs across 17 sets,
and with TDM or DMU left out. In TDM and DMU together `softer` was better by 0.0085
(2.1 SEs); in the other 15 sets it was worse by 0.0028 (2.0 SEs).

That was the same change in every set. This tests an actual flag: the app reads the
share from its own dataset and softens the penalty by it. It runs on drafts the first
test didn't use.

## The share

`SetMetrics` adds up each card's `game_count` in each deck color group, and takes the
part in groups of three or more colors. It needs nothing the dataset doesn't have, so
it works on a set's first day, when it is a little lower than later (FRA: 15% on day
one, 23% over the format). For the 17 sets it gives TDM 79%, DMU 47%, FRA 24%, OTJ
24%, TMT 23%, SOS 22%, TLA 19%, and 15% or less for the other ten.

## The heads

Each raises every off-color multiplier to a power set by the share. Power 1 is the
app; power 0.5 is the first test's `softer`. Patches in [heads/](heads/).

| head | the power | TDM | DMU | FRA | FDN |
|---|---|---|---|---|---|
| `flag-plain` | 1 minus the share | 0.21 | 0.53 | 0.76 | 0.96 |
| `flag-step` | 0.5 from a 30% share, else 1 | 0.5 | 0.5 | 1 | 1 |
| `flag-knee` | 1 minus the share above 20% | 0.41 | 0.73 | 0.96 | 1 |

`flag-plain` has no constant of its own. `flag-step` is the first test's `softer` in
TDM and DMU and the app elsewhere, so in those two sets it is a repeat of that result
on new drafts.

## What runs

The Advisor heads workflow, held-out ratings, pools in pick order, base upstream main
at `6b6dba9`, in two runs:

- **Where the flag acts:** TDM and DMU, 6,000 drafts a set and salt, the salts
  `share1` to `share6`. Twice the first test's drafts in these sets. Salts sample
  independently, so a few drafts are in more than one sample.
- **Where it shouldn't:** the other 15 sets, 3,000 drafts a set and salt, the salts
  `share1` and `share2`, with `flag-plain` and `flag-knee`. `flag-step` is the app
  there, since no share reaches 30%.

## How it is read

A flag is more code and one more thing to explain, so "no objection" isn't enough. A
head passes when both hold:

1. in TDM and DMU together, its change in regret slope is better than the base by 2+
   SEs;
2. in the other 15 sets together, it is not worse by 2+ SEs.

Among heads that pass, the order is `flag-plain`, `flag-step`, `flag-knee`, from the
least to the most to explain. A later one takes the place of an earlier one only if it
is better in TDM and DMU by 2 of its own SEs.

The requirement against a TDM-only flag: if a passing head's change in DMU alone is on
the worse side, I will say so and recommend against it, whatever the pooled number.

If none passes, no flag is built. The first test's line stays as a finding.

Reported, not deciding: each set's change, top card changes, top-1, and event wins per
swapped pick.

## Predictions

- `flag-step` passes, better in TDM and DMU by about 0.008.
- `flag-plain` passes and is better than `flag-step` in TDM, by under 2 SEs. It is
  worse in the other 15 sets by under 2 SEs.
- `flag-knee` is between the app and `flag-step` in TDM and DMU, and changes almost
  nothing elsewhere.

## What it can't show

As in the held-out replay. Two sets carry the first condition, so this can't show the
flag is right for the next three-color set, only that it holds up in these two on new
drafts. The forms were chosen after seeing the first test, on the same two sets.
