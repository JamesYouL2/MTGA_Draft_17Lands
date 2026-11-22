# Auto-Optimize: the Power Up swap with and without a guard

Written before the run, before any result was seen.

## Why

`experiments/2026-11-16-optimize-power-only` (fork branch `exp/optimize-power-only`,
run 43815325916) found that making the Power Up swap whenever there is one raises the
deck score by 0.75 win rate points more than today's button. PR branch
`simplify/optimize-power-up` makes that the button. The user asked for a guard: swap
only if the incoming sideboard spell rates strictly higher than the deck spell it cuts,
by the same rating the swap uses (the pair's GIH win rate, All Decks as fallback);
otherwise leave the deck unchanged. They also asked that it be measured rather than
argued, so this re-measures all three versions on fresh decks.

## The heads

| head | what the button does |
|---|---|
| `base` | today's main button, a verbatim copy in `main_button.py`: simulates up to six kinds of one-card swap and keeps the best by a weighted fitness |
| `no-guard` | the Power Up swap whenever there is one (the 11-16 `power-always`) |
| `guard` | the Power Up swap only if the incoming spell rates strictly higher (the PR as it stands) |

`no-guard` and `guard` run the PR's own `optimize_deck`, with an experiment hook
(`_EXP_GUARD`, this branch only) that turns the guard off.

## What runs

Workflow `optimize-guard.yml` on this branch, triggered by a push to
`run/optimize-guard`. Same 19 sets and the same sample construction as run
43815325916: 100,000 decks sampled a set, the first 20,000 through the button, the same
held-out ratings, deck filters and deck score (`heads.py` follows `buttons.py`). New
salt `guard-2026-11-21`, and the sampler leaves out the decks run 43815325916 put
through the button (`three:100000:20000`), so no deck is reused.

## The measure

Each head's change in deck score, in win rate points at the score's own price, with
set-clustered SEs (`report.py`); the share of decks each head changes; and the
differences on the same decks: `no-guard` minus `base`, `guard` minus `base`, `guard`
minus `no-guard`. As on 11-16, `base`'s swaps of a spell for a land, or a land for a
spell, count as zero, since the score can't price a land.

## The decision rule

- **Keep the guard** unless `guard` minus `no-guard` is worse by 2 SEs or more.
- **The PR stands** if `guard` minus `base` is better by 2 SEs or more.

If the guard fails its rule, the PR goes back to the plain swap (`no-guard`), subject
to `no-guard` minus `base` being better by 2 SEs. If the PR doesn't stand, the button
stays as it is.

## Predictions

- The guard blocks a swap in under 5% of decks, and `guard` minus `no-guard` is within
  ±0.05 points; if anything slightly better, since a swap to a lower-rated card should
  lower the score on average.
- `guard` minus `base` is near the 11-16 figure, about +0.7, far above 2 SEs.

## What it can't show

As on 11-16: the deck score rates cards and can't price lands or mana, so `base`'s land
swaps are unjudged. Power Up picks by the pair's win rate and is scored by the overall
one, close but not the same, which is the only reason the guard could cost anything.
These are decks drafters had already tuned; a user presses the button on a rougher one.
