
# Diagnosis of `lgbm-strong-noalsa` against main (DIAGNOSE.md)

152000 drafts, 117805 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 117805 | +0.0089 (0.0053), +1.7 |
| rank of the card taken (check 1) | 117805 | -0.0093 (0.0049), -1.9 |
| missed the head's top card (audit) | 117805 | -0.0184 (0.0058), -3.2 |
| SD regret capped at 2 (audit) | 117805 | +0.0048 (0.0054), +0.9 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.736 | 0.272 | 0.444 | 0.178 |
| rank | 1.456 | 0.579 | 1.015 | 0.395 |
| missed top card | 0.535 | 0.116 | 0.457 | 0.108 |
| SD regret capped at 2 | 0.656 | 0.223 | 0.422 | 0.161 |

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 117799 | +0.0082 (0.0037), +2.2 |
| they disagree | 117747 | -0.0059 (0.0084), -0.7 |
| pack 1 | 117805 | -0.0276 (0.0060), -4.6 |
| pack 2 | 117512 | +0.0185 (0.0059), +3.1 |
| pack 3 | 117277 | +0.0235 (0.0059), +4.0 |

## 4. The size in plain terms

- Top card differs on 33.9% of picks: 13.1 picks per draft (median 13, middle half 10 to 16).
- Event wins per swapped pick: +0.037 (0.005), +7.7 (117805 events).
- A drafter who followed lgbm-strong-noalsa instead of main on all 13.1 disagreements of a complete event: +0.48 (0.06) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with lgbm-strong-noalsa: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 117805 | +0.037 (0.005), +7.7 |
| quick-build deck score (saved) | 117365 | -0.101 (0.005), -19.2 |
| pool GIH WR, best 23 in a pair (saved) | 117365 | +0.018 (0.006), +2.9 |

## 7. Confounding by lane and seat

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 117805 | 1.5% | +0.062 (0.046), +1.4 | +0.036 (0.005), +7.5 |
| late pack 3 | 117805 | 7.0% | +0.029 (0.017), +1.7 | +0.037 (0.005), +7.3 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 5.78 | -0.0147 (0.0029), -5.1 |
| took main's top card (b) | 2.77 | -0.0414 (0.0040), -10.4 |
| took neither (c) | 4.57 | -0.0680 (0.0038), -17.9 |
| **a − b** (117805 events) | | +0.0268 (0.0049), +5.5 |
| swap measure as specified | | +0.0367 (0.0048), +7.7 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 49.8% | +0.0403 (0.0067), +6.0 |
| base on, head off | 11.4% | +0.0015 (0.0154), +0.1 |
| base off, head on | 26.4% | +0.0602 (0.0088), +6.8 |
| both off-lane | 12.4% | -0.0050 (0.0209), -0.2 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | +0.0367 (0.0048), +7.7 | +0.0370 (0.0048), +7.8 |
| unconstrained a − b | +0.0268 (0.0049), +5.5 | +0.0273 (0.0048), +5.6 |
| SD regret slope change | +0.0089 (0.0053), +1.7 | +0.0090 (0.0053), +1.7 |
| rank regret slope change | -0.0093 (0.0049), -1.9 | -0.0092 (0.0049), -1.9 |


# Diagnosis of `lgbm-strong` against main (DIAGNOSE.md)

152000 drafts, 117805 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 117805 | +0.0305 (0.0065), +4.7 |
| rank of the card taken (check 1) | 117805 | -0.0006 (0.0066), -0.1 |
| missed the head's top card (audit) | 117805 | -0.0125 (0.0069), -1.8 |
| SD regret capped at 2 (audit) | 117805 | +0.0264 (0.0065), +4.0 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.736 | 0.272 | 0.315 | 0.136 |
| rank | 1.456 | 0.579 | 0.754 | 0.293 |
| missed top card | 0.535 | 0.116 | 0.397 | 0.102 |
| SD regret capped at 2 | 0.656 | 0.223 | 0.306 | 0.128 |

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 117783 | +0.0215 (0.0057), +3.8 |
| they disagree | 117776 | +0.0154 (0.0091), +1.7 |
| pack 1 | 117805 | -0.0063 (0.0097), -0.6 |
| pack 2 | 117512 | +0.0380 (0.0067), +5.7 |
| pack 3 | 117277 | +0.0379 (0.0071), +5.3 |

## 4. The size in plain terms

- Top card differs on 40.3% of picks: 15.5 picks per draft (median 15, middle half 13 to 18).
- Event wins per swapped pick: +0.034 (0.004), +7.7 (117805 events).
- A drafter who followed lgbm-strong instead of main on all 15.6 disagreements of a complete event: +0.52 (0.07) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with lgbm-strong: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 117805 | +0.034 (0.004), +7.7 |
| quick-build deck score (saved) | 117365 | -0.141 (0.004), -31.8 |
| pool GIH WR, best 23 in a pair (saved) | 117365 | -0.008 (0.007), -1.2 |

## 7. Confounding by lane and seat

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 117805 | 1.4% | +0.095 (0.040), +2.4 | +0.033 (0.004), +7.4 |
| late pack 3 | 117805 | 6.9% | +0.029 (0.016), +1.8 | +0.034 (0.005), +7.3 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 8.16 | -0.0209 (0.0025), -8.3 |
| took main's top card (b) | 2.83 | -0.0403 (0.0039), -10.2 |
| took neither (c) | 4.62 | -0.0767 (0.0038), -20.0 |
| **a − b** (117805 events) | | +0.0192 (0.0045), +4.3 |
| swap measure as specified | | +0.0335 (0.0044), +7.7 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 52.6% | +0.0358 (0.0056), +6.4 |
| base on, head off | 12.4% | -0.0081 (0.0118), -0.7 |
| base off, head on | 21.4% | +0.0666 (0.0087), +7.6 |
| both off-lane | 13.6% | -0.0003 (0.0115), -0.0 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | +0.0335 (0.0044), +7.7 | +0.0342 (0.0044), +7.9 |
| unconstrained a − b | +0.0192 (0.0045), +4.3 | +0.0200 (0.0045), +4.5 |
| SD regret slope change | +0.0305 (0.0065), +4.7 | +0.0300 (0.0064), +4.7 |
| rank regret slope change | -0.0006 (0.0066), -0.1 | -0.0010 (0.0066), -0.2 |


# Diagnosis of `gihwr-only` against main (DIAGNOSE.md)

152000 drafts, 117805 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 117805 | +0.0973 (0.0070), +13.8 |
| rank of the card taken (check 1) | 117805 | +0.0513 (0.0065), +7.9 |
| missed the head's top card (audit) | 117805 | +0.0498 (0.0069), +7.2 |
| SD regret capped at 2 (audit) | 117805 | +0.0954 (0.0070), +13.6 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.736 | 0.272 | 0.585 | 0.273 |
| rank | 1.456 | 0.579 | 1.849 | 0.657 |
| missed top card | 0.535 | 0.116 | 0.633 | 0.116 |
| SD regret capped at 2 | 0.656 | 0.223 | 0.531 | 0.235 |

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 117799 | +0.0546 (0.0040), +13.7 |
| they disagree | 117682 | +0.1060 (0.0100), +10.6 |
| pack 1 | 117805 | +0.0322 (0.0043), +7.5 |
| pack 2 | 117512 | +0.0906 (0.0086), +10.5 |
| pack 3 | 117277 | +0.0679 (0.0082), +8.3 |

## 4. The size in plain terms

- Top card differs on 40.7% of picks: 15.7 picks per draft (median 16, middle half 13 to 18).
- Event wins per swapped pick: -0.050 (0.004), -11.9 (117805 events).
- A drafter who followed gihwr-only instead of main on all 15.7 disagreements of a complete event: -0.78 (0.07) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with gihwr-only: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 117805 | -0.050 (0.004), -11.9 |
| quick-build deck score (saved) | 117365 | -0.050 (0.005), -11.0 |
| pool GIH WR, best 23 in a pair (saved) | 117365 | -0.416 (0.007), -62.6 |

## 7. Confounding by lane and seat

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 117805 | 1.3% | +0.061 (0.049), +1.2 | -0.050 (0.004), -11.8 |
| late pack 3 | 117805 | 9.9% | -0.014 (0.014), -1.0 | -0.054 (0.005), -11.7 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 2.51 | -0.0413 (0.0041), -10.0 |
| took main's top card (b) | 6.31 | -0.0022 (0.0029), -0.8 |
| took neither (c) | 6.92 | -0.0577 (0.0025), -22.7 |
| **a − b** (117805 events) | | -0.0390 (0.0043), -9.1 |
| swap measure as specified | | -0.0496 (0.0042), -11.9 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 19.3% | -0.0010 (0.0093), -0.1 |
| base on, head off | 72.5% | -0.0712 (0.0057), -12.6 |
| base off, head on | 1.5% | +0.0897 (0.0367), +2.4 |
| both off-lane | 6.7% | -0.0077 (0.0265), -0.3 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | -0.0496 (0.0042), -11.9 | -0.0499 (0.0042), -12.0 |
| unconstrained a − b | -0.0390 (0.0043), -9.1 | -0.0395 (0.0043), -9.2 |
| SD regret slope change | +0.0973 (0.0070), +13.8 | +0.0971 (0.0070), +13.8 |
| rank regret slope change | +0.0513 (0.0065), +7.9 | +0.0517 (0.0065), +7.9 |


# Diagnosis of `lgbm-wins` against main (DIAGNOSE.md)

152000 drafts, 117805 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 117805 | +0.0327 (0.0067), +4.9 |
| rank of the card taken (check 1) | 117805 | +0.0002 (0.0083), +0.0 |
| missed the head's top card (audit) | 117805 | -0.0095 (0.0080), -1.2 |
| SD regret capped at 2 (audit) | 117805 | +0.0284 (0.0068), +4.2 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.736 | 0.272 | 0.307 | 0.133 |
| rank | 1.456 | 0.579 | 0.742 | 0.285 |
| missed top card | 0.535 | 0.116 | 0.393 | 0.100 |
| SD regret capped at 2 | 0.656 | 0.223 | 0.299 | 0.125 |

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 117781 | +0.0259 (0.0056), +4.6 |
| they disagree | 117779 | +0.0153 (0.0092), +1.7 |
| pack 1 | 117805 | -0.0047 (0.0101), -0.5 |
| pack 2 | 117512 | +0.0405 (0.0069), +5.9 |
| pack 3 | 117277 | +0.0390 (0.0065), +6.0 |

## 4. The size in plain terms

- Top card differs on 43.1% of picks: 16.6 picks per draft (median 16, middle half 14 to 19).
- Event wins per swapped pick: +0.028 (0.004), +7.0 (117805 events).
- A drafter who followed lgbm-wins instead of main on all 16.7 disagreements of a complete event: +0.47 (0.07) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with lgbm-wins: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 117805 | +0.028 (0.004), +7.0 |
| quick-build deck score (saved) | 117365 | -0.197 (0.005), -40.4 |
| pool GIH WR, best 23 in a pair (saved) | 117365 | -0.026 (0.006), -4.3 |

## 7. Confounding by lane and seat

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 117805 | 1.3% | +0.092 (0.044), +2.1 | +0.027 (0.004), +6.7 |
| late pack 3 | 117805 | 6.6% | +0.034 (0.016), +2.1 | +0.028 (0.004), +6.6 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 8.65 | -0.0237 (0.0025), -9.4 |
| took main's top card (b) | 3.18 | -0.0393 (0.0037), -10.6 |
| took neither (c) | 4.87 | -0.0773 (0.0037), -21.1 |
| **a − b** (117805 events) | | +0.0156 (0.0041), +3.8 |
| swap measure as specified | | +0.0279 (0.0040), +7.0 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 53.7% | +0.0302 (0.0053), +5.7 |
| base on, head off | 11.2% | -0.0108 (0.0120), -0.9 |
| base off, head on | 21.6% | +0.0587 (0.0081), +7.3 |
| both off-lane | 13.5% | -0.0104 (0.0109), -1.0 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | +0.0279 (0.0040), +7.0 | +0.0285 (0.0040), +7.1 |
| unconstrained a − b | +0.0156 (0.0041), +3.8 | +0.0162 (0.0041), +3.9 |
| SD regret slope change | +0.0327 (0.0067), +4.9 | +0.0318 (0.0067), +4.7 |
| rank regret slope change | +0.0002 (0.0083), +0.0 | -0.0003 (0.0082), -0.0 |


# Diagnosis of `logit-simple` against main (DIAGNOSE.md)

152000 drafts, 117805 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 117805 | +0.0145 (0.0044), +3.3 |
| rank of the card taken (check 1) | 117805 | -0.0049 (0.0047), -1.0 |
| missed the head's top card (audit) | 117805 | -0.0055 (0.0062), -0.9 |
| SD regret capped at 2 (audit) | 117805 | +0.0115 (0.0049), +2.4 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.736 | 0.272 | 0.565 | 0.226 |
| rank | 1.456 | 0.579 | 1.389 | 0.563 |
| missed top card | 0.535 | 0.116 | 0.521 | 0.119 |
| SD regret capped at 2 | 0.656 | 0.223 | 0.521 | 0.195 |

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 117799 | +0.0131 (0.0033), +4.0 |
| they disagree | 117591 | +0.0041 (0.0075), +0.5 |
| pack 1 | 117805 | -0.0140 (0.0061), -2.3 |
| pack 2 | 117512 | +0.0141 (0.0049), +2.8 |
| pack 3 | 117277 | +0.0136 (0.0075), +1.8 |

## 4. The size in plain terms

- Top card differs on 22.4% of picks: 8.7 picks per draft (median 8, middle half 6 to 11).
- Event wins per swapped pick: +0.022 (0.008), +2.6 (117805 events).
- A drafter who followed logit-simple instead of main on all 8.7 disagreements of a complete event: +0.19 (0.07) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with logit-simple: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 117805 | +0.022 (0.008), +2.6 |
| quick-build deck score (saved) | 117365 | +0.203 (0.007), +30.2 |
| pool GIH WR, best 23 in a pair (saved) | 117365 | +0.134 (0.008), +16.0 |

## 7. Confounding by lane and seat

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 117805 | 0.8% | +0.074 (0.067), +1.1 | +0.021 (0.008), +2.6 |
| late pack 3 | 117805 | 7.5% | +0.014 (0.020), +0.7 | +0.023 (0.008), +3.0 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 2.90 | -0.0098 (0.0065), -1.5 |
| took main's top card (b) | 2.38 | -0.0265 (0.0043), -6.2 |
| took neither (c) | 3.41 | -0.0625 (0.0031), -20.1 |
| **a − b** (117805 events) | | +0.0167 (0.0079), +2.1 |
| swap measure as specified | | +0.0216 (0.0082), +2.6 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 46.2% | +0.0232 (0.0096), +2.4 |
| base on, head off | 24.3% | -0.0109 (0.0160), -0.7 |
| base off, head on | 19.8% | +0.0672 (0.0131), +5.1 |
| both off-lane | 9.7% | -0.0055 (0.0302), -0.2 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | +0.0216 (0.0082), +2.6 | +0.0216 (0.0082), +2.6 |
| unconstrained a − b | +0.0167 (0.0079), +2.1 | +0.0168 (0.0079), +2.1 |
| SD regret slope change | +0.0145 (0.0044), +3.3 | +0.0147 (0.0043), +3.4 |
| rank regret slope change | -0.0049 (0.0047), -1.0 | -0.0047 (0.0046), -1.0 |


