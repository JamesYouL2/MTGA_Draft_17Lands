# Confirmation results: lane share 0.10, and 0.05

Run [44030415583](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44030415583)
(Advisor heads, branch `run/cutoff-confirm`, commit `5f2f074`). Ten sets, new salts
`confirm1` and `confirm2`, 60,000 drafts and 45,405 complete events per head, held-out
ratings. Rules are in [CONFIRM.md](CONFIRM.md), written before the run. Raw reports are in
[confirm-report/](confirm-report/).

## Against today's 0.15

Regret slope change: positive is worse for the head. Event wins per swapped pick:
positive is better for the head.

| head | regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs | top-card changes | on-lane, base to head |
|---|---|---|---|---|---|---|
| lane-share-10 | -0.0032 (0.0018) | -1.8 | +0.086 (0.025) | +3.4 | 2.17% | 76.0% to 76.8% |
| lane-share-05 | -0.0057 (0.0022) | -2.6 | +0.103 (0.019) | +5.5 | 3.40% | 76.0% to 77.5% |

Both salts agree for both heads: 0.10 gives -0.0035 (0.0026) and -0.0028 (0.0024);
0.05 gives -0.0064 (0.0034) and -0.0049 (0.0029).

## 0.05 against 0.10, head to head

Here 0.10 is the base.

| regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs | top-card changes |
|---|---|---|---|---|
| -0.0024 (0.0012) | -2.0 | +0.137 (0.033) | +4.2 | 1.37% |

The regret ratio is -2.05 before rounding. Both salts lean the same way: -0.0029 (0.0017)
and -0.0021 (0.0017).

## Verdict

- **0.10 is confirmed.** It beats today's on event wins by 3.4 SEs. The regret slope also
  favors it (-1.8 SEs) rather than flagging it. As predicted, the effect is smaller than
  in the sweep (-4.2 and +5.0 SEs there).
- **0.05 is adopted over 0.10 under the rule.** Head to head, it beats 0.10 on event wins
  by 4.2 SEs, and on the regret slope by 2.0 SEs; neither measure flags it worse. Against
  today's it is the stronger head on both measures. This contradicts my prediction that
  0.05 and 0.10 would be within 2 SEs.

The constant goes from 0.15 to 0.05.

## What the lower threshold does

This is the share of picks where the advisor's lane has three main colors, on the same
picks for all three thresholds:

| cards in pool | picks | 0.15 (today) | 0.10 | 0.05 |
|---|---|---|---|---|
| 0 to 14 | 827,370 | 42.2% | 42.2% | 42.2% |
| 15 to 19 | 299,568 | 44.0% | 71.7% | 94.4% |
| 20 to 24 | 299,483 | 38.7% | 64.9% | 87.4% |
| 25 to 29 | 239,521 | 39.4% | 68.2% | 89.0% |
| 30 to 34 | 299,367 | 37.7% | 66.7% | 92.1% |
| 35+ | 358,025 | 35.3% | 63.5% | 92.5% |

This is the share of picks where the lane has a third color that today's lacks:

| cards in pool | 0.10 | 0.05 |
|---|---|---|
| 0 to 14 | 0.0% | 0.0% |
| 15 to 19 | 27.8% | 50.4% |
| 20 to 24 | 26.2% | 48.7% |
| 25 to 29 | 28.8% | 49.6% |
| 30 to 34 | 29.0% | 54.4% |
| 35+ | 28.2% | 57.3% |

- At 0.10, 67.5% of drafts gain a third color at some pick. The median draft first gains
  one at 17 cards (quartiles 15 to 22).
- At 0.05, 80.9% of drafts do, first at 15 cards (quartiles 15 to 19), which is the first
  pick where the threshold applies.

The change is much bigger than I predicted, which was 5% to 10% of picks at 0.10. There
are two things I hadn't known:
- Before 15 cards, the lane-weight path already gives a three-color lane on 42% of picks.
- The 0.15 threshold then drops a third color from the lane at the switch to the share
  rule.

Lowering it mostly keeps that third color. At 0.05, about 90% of picks from 15 cards have
a three-color lane, the cap in `_identify_main_colors`. So 0.05 is close to "always the
three heaviest colors", and lowering it further can change little. Despite the wider lane,
86% to 87% of top-card changes are between two cards that are both on-lane. Drafters took
the head's card more often there: 30.7% against 28.6% at 0.05.

## Predictions (CONFIRM.md)

| prediction | outcome |
|---|---|
| 0.10 confirmed, with smaller effects than the sweep | right: -1.8 and +3.4 SEs, against -4.2 and +5.0 |
| 0.05 against 0.10 within 2 SEs on both measures | wrong: +4.2 SEs on event wins, -2.0 on regret |
| 0.10 gains a third color on 5% to 10% of picks from 15 cards | wrong: 26% to 29% |
| 0.05 roughly doubles that | right: 49% to 57% |

## Caveats

- These are associations among drafters who chose freely, as in every held-out replay.
- 0.10 has now passed in two independent runs. 0.05 has passed in only one, the run where
  it was first tried. Its head-to-head regret result sits right at the 2-SE line, so the
  adoption rests mainly on event wins.
- Event wins is the measure that caught 20% noise in the measure-power test, and the regret
  slope missed it. Here both measures point the same way for both heads.
- On-lane rates rise partly by construction: on-lane is judged against each advisor's own
  lane, which is wider at lower thresholds.
