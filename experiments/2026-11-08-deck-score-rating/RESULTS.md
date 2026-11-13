# Which card rating the deck score should use: results

Run [42560809049](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/42560809049)
at `8acc28c` (`f2fb86d` plus a push trigger): 928,062 pools from 19 sets, 724,659 with
two-main-color decks, and 4.2M games. 11,426 pools were skipped, nearly all for a card
missing from the dataset. The protocol is in [PROTOCOL.md](PROTOCOL.md), written before
the run. The full report is [score_rating.md](score_rating.md) and the numbers are in
[score_rating.json](score_rating.json).

## Verdict

**Use the overall rating in the deck score.** It's the simplification, and it won.

| version, against `blend` | suggested pair changes | decks in its pair / the blend's | head to head, win rate points | verdict |
|---|---|---|---|---|
| `overall` | 15.6% | 91,322 / 9,276 | **+1.66 [+0.98, +2.33]** | better |
| `overall+pair` | 16.6% | 88,048 / 16,961 | **+1.36 [+0.83, +1.89]** | better |
| `blend+pair` | 13.0% | 74,036 / 10,314 | -0.71 [-1.72, +0.30] | inconclusive |

Two are better. Against each other, `overall` and `overall+pair` tie, +0.01 [-0.58,
+0.60], so the protocol's order takes the simpler, `overall`. The pair's level doesn't
need a baseline here.

## The predictions

1. **`overall+pair` and `blend+pair` both ahead of `blend`, one by 2+ SEs: failed.**
   `overall+pair` is, but `blend+pair` isn't ahead. It's the version I added.
2. **`overall` ahead by less than they are: failed.** It's ahead by the most. I
   expected it to fall short because it still prices a pair at 1.30 against 2.9. That
   didn't show.
3. **Each changes the suggested pair in 5% to 30% of pools: held,** at 13.0% to 16.6%.
   By set, the one miss is SOS's `blend+pair` at 4.7%.

## Reported, not deciding

- **The score gap agrees.** Per SD of the gap between the pool's best build and the
  played pair's, `overall` predicts losses better, -0.66 against -0.51 win rate points,
  a change of -0.15 (0.06). `blend+pair` predicts them worse, +0.34 (0.09).
- **Fit doesn't help once level is handled.** `overall+pair` beats `blend+pair` by
  +2.91 [+2.32, +3.51], and they differ only in fit. I can't say why from this. One
  idea to test: taking the best of ten pairs rewards noise, and pair rates are noisier.
- **Drafters mostly play what `overall` suggests,** 93.6% of two-color decks, against
  82.2% for the blend's suggestion.

## The lopsided comparison

Most decks in the head to head are on the version's side: about 10 to 1 for `overall`.
That's what the score would look like if the few who went against the majority were
simply unusual drafters, which the buckets only partly remove. Against that, `blend+pair`
is lopsided too, 7 to 1, and leans the other way, so being in the majority doesn't
always win. The bias can't be ruled out, and +1.66 shouldn't be read as what a user
would gain.

## What this changes

- **It answers the pair parts test's follow-up.** Level was the problem in the deck
  score too, and overall handles it about as well as an explicit baseline does.
- **The blend stays for choosing cards within a pair.** This test didn't change the
  builders.
- **The change needs its own checks.** The score's weights were fit with the blend, so
  they need checking under overall. And the pair parts test found the blend predicts
  better *among decks of one pair*, while `overall` also ranks builds within a pair.
  The suggested deck changes in 18.2% of pools and its pair in 15.6%, so about 2.6% are
  within-pair changes this test doesn't judge.

## What it can't show

As the protocol says: it's observational, only played pairs count, the decks are the
drafters' own, and it covers finished pools only. The simulator is off, so this compares
the app as it would be without the mana penalties. Today, with them on, the top deck's
pair differs in about 10% of pools (see `experiments/2026-11-08-deck-variants`).
