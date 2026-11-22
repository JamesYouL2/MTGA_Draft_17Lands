# Auto-Optimize with and without the guard: results

One run of the Optimize guard workflow,
[44966309428](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44966309428),
at `6cec498`. It covered 345,704 forty-card decks from 19 sets, salt `guard-2026-11-21`,
with none of run 43815325916's button decks. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. The report is in
[guard.md](guard.md) and [guard.json](guard.json).

## Verdict

**The guard stays, and the PR stands.**

- Guard minus no-guard is +0.001 [+0.001, +0.002] win rate points. That is better, not
  2 SEs worse, so the guard stays.
- Guard minus base is +0.752 [+0.706, +0.797], 32.5 SEs. That is far above the 2 SEs
  the rule asks for, so the PR stands.

| head | changes the deck | deck score change |
|---|---|---|
| `base` (today's main button) | 96.5% | +0.075 [+0.044, +0.105] |
| `no-guard` (plain Power Up swap) | 99.7% | +0.825 [+0.779, +0.871] |
| `guard` (the PR) | 98.9% | +0.826 [+0.780, +0.872] |

| difference, same decks | effect | SEs |
|---|---|---|
| no-guard minus base | +0.750 [+0.705, +0.796] | +32.4 |
| guard minus base | +0.752 [+0.706, +0.797] | +32.5 |
| guard minus no-guard | +0.001 [+0.001, +0.002] | +8.5 |

Changes are in win rate points at the deck score's own price, with set-clustered 95%
intervals. As on 11-16, `base`'s land-count swaps count as zero.

## What the guard does

The guard blocks a swap the plain version would make in 0.84% of decks. On those decks
the plain swap lowers the deck score by 0.163 [0.145, 0.181]. So the guard removes only
swaps that hurt.

The per-deck effect is small, so the gain is tiny. But it appears in all 19 sets:
- guard minus no-guard is between +0.000 and +0.004 in every set;
- MH3 gains the most, with the guard blocking 2.69% of swaps there.

Guard minus base is between +0.60 (DSK) and +0.94 (TDM) in every set.

## Against 11-16

The plain swap's gain over the button repeats on fresh decks: +0.750 now, +0.749 on
11-16 (run 43815325916). The button itself moves the score by +0.075, against +0.076
then.

## Predictions

| prediction | result |
|---|---|
| the guard blocks a swap in under 5% of decks | right: 0.84% |
| guard minus no-guard within ±0.05, if anything slightly better | right: +0.001, better |
| guard minus base about +0.7, far above 2 SEs | right: +0.752, 32.5 SEs |

## A disclosure

After the protocol was written and before the run, I ran a 231-deck smoke test on TMT
locally to check the pipeline. I saw its numbers: the guard blocked 1.7% of swaps,
guard minus no-guard was +0.004. Those decks are inside this run's TMT sample. Nothing
in the protocol or the tools changed after it.

## What this can't show

The same limits as 11-16 apply:
- The deck score can't price lands, so `base`'s land swaps are unjudged.
- The decks are ones drafters had already tuned.
- The swap picks by the pair's win rate and the score grades by the overall one. That
  mismatch is the only way the guard could have cost anything, and it didn't.
