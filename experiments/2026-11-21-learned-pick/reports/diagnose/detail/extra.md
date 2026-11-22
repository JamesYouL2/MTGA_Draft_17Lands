
# Diagnosis of `lgbm-strong-noalsa` against main (DIAGNOSE.md)

152000 drafts, 117904 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 117904 | +0.0162 (0.0052), +3.1 |
| rank of the card taken (check 1) | 117904 | -0.0085 (0.0049), -1.7 |
| rank percentile in the pack (check 1) | 117904 | +0.0026 (0.0056), +0.5 |
| missed the head's top card (audit) | 117904 | -0.0099 (0.0057), -1.8 |
| SD regret capped at 2 (audit) | 117904 | +0.0129 (0.0056), +2.3 |
| SD regret, the head's order with main's gaps (check 2a) | 117904 | -0.0013 (0.0047), -0.3 |
| SD regret, quantile map fitted on the other sets (check 2b) | 117904 | +0.0166 (0.0052), +3.2 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.737 | 0.273 | 0.444 | 0.178 |
| rank | 1.459 | 0.580 | 1.015 | 0.395 |
| missed top card | 0.535 | 0.116 | 0.457 | 0.108 |
| SD regret capped at 2 | 0.657 | 0.224 | 0.422 | 0.161 |

Both maps keep the head's top card on 99.844% of 5862000 picks. The saved scores reproduce the head's mean SD regret per draft to within 0.0000; picks whose two copies' scored cards differ: 0.

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 117897 | +0.0166 (0.0036), +4.6 |
| they disagree | 117841 | +0.0023 (0.0086), +0.3 |
| pack 1 | 117904 | -0.0100 (0.0058), -1.7 |
| pack 2 | 117601 | +0.0179 (0.0060), +3.0 |
| pack 3 | 117349 | +0.0286 (0.0081), +3.5 |

## 4. The size in plain terms

- Top card differs on 34.0% of picks: 13.1 picks per draft (median 13, middle half 10 to 16).
- Event wins per swapped pick: +0.031 (0.005), +6.5 (117904 events).
- A drafter who followed lgbm-strong-noalsa instead of main on all 13.1 disagreements of a complete event: +0.40 (0.06) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with lgbm-strong-noalsa: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 117904 | +0.031 (0.005), +6.5 |
| quick-build deck score (saved) | 117431 | -0.100 (0.005), -19.5 |
| pool GIH WR, best 23 in a pair (saved) | 117431 | +0.014 (0.006), +2.2 |
| Suggest Deck: deck rating | 117162 | -0.105 (0.006), -18.7 |
| Suggest Deck: card quality (rating points) | 117162 | -0.117 (0.006), -19.8 |
| Suggest Deck: two colors or fewer | 117162 | +0.003 (0.001), +6.4 |
| Suggest Deck: missing fixing | 117162 | -0.000 (0.000), -2.2 |
| Suggest Deck: missing spells | 117162 | -0.000 (0.000), -0.4 |
| Suggest Deck: colors | 117162 | -0.011 (0.001), -7.9 |
| Suggest Deck: removal spells | 117162 | +0.036 (0.007), +5.4 |
| Suggest Deck: creatures | 117162 | +0.080 (0.006), +13.3 |
| Suggest Deck: creatures and removal at 2 mana or less | 117162 | +0.048 (0.006), +8.5 |
| Suggest Deck: mean mana value of spells | 117162 | +0.001 (0.001), +1.9 |

### (b) The simulated draft: lgbm-strong-noalsa's own deck less main's, same packs

Screen only: it grades decks by the deck score's own beliefs.

| part | drafts | head minus main | main's mean |
|---|---|---|---|
| deck rating | 150928 | -0.124 (0.005), -25.6 | 83.886 |
| card quality (rating points) | 150928 | -0.111 (0.005), -22.6 | 5.792 |
| two colors or fewer | 150928 | -0.004 (0.000), -15.2 | 0.998 |
| missing fixing | 150928 | +0.000 (0.000), +2.0 | 0.000 |
| missing spells | 150928 | +0.000 (0.000), +0.0 | 0.000 |
| colors | 150928 | +0.005 (0.001), +6.6 | 2.004 |
| removal spells | 150928 | -0.196 (0.008), -26.0 | 6.379 |
| creatures | 150928 | +0.886 (0.010), +85.6 | 11.721 |
| creatures and removal at 2 mana or less | 150928 | +0.032 (0.008), +4.0 | 7.861 |
| mean mana value of spells | 150928 | +0.064 (0.001), +48.0 | 2.876 |

## 7. Confounding by lane and seat

### (a) With the final pool's facts as controls

Controls added: the pool's two-color share, pool GIH WR (best 23 in a pair) and on-lane playables. They are partly outcomes of the picks, so shrinkage is an upper bound on confounding.

| measure | events | usual controls | with pool controls | kept |
|---|---|---|---|---|
| event wins per swapped pick | 117431 | +0.030 (0.005), +6.3 | +0.030 (0.005), +6.1 | 98% |
| SD regret slope change | 117431 | +0.0172 (0.0052), +3.3 | +0.0247 (0.0067), +3.7 | 143% |

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 117904 | 1.5% | +0.051 (0.039), +1.3 | +0.031 (0.005), +6.4 |
| late pack 3 | 117904 | 7.0% | +0.016 (0.017), +0.9 | +0.033 (0.005), +6.5 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 5.80 | -0.0150 (0.0028), -5.4 |
| took main's top card (b) | 2.78 | -0.0327 (0.0041), -7.9 |
| took neither (c) | 4.56 | -0.0746 (0.0031), -24.4 |
| **a − b** (117904 events) | | +0.0176 (0.0049), +3.6 |
| swap measure as specified | | +0.0307 (0.0047), +6.5 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 49.9% | +0.0318 (0.0067), +4.7 |
| base on, head off | 11.4% | -0.0014 (0.0139), -0.1 |
| base off, head on | 26.3% | +0.0580 (0.0088), +6.6 |
| both off-lane | 12.4% | -0.0122 (0.0193), -0.6 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | +0.0307 (0.0047), +6.5 | +0.0309 (0.0047), +6.5 |
| unconstrained a − b | +0.0176 (0.0049), +3.6 | +0.0179 (0.0049), +3.7 |
| SD regret slope change | +0.0162 (0.0052), +3.1 | +0.0156 (0.0052), +3.0 |
| rank regret slope change | -0.0085 (0.0049), -1.7 | -0.0090 (0.0049), -1.8 |

