
# Diagnosis of `lgbm-strong-noalsa` against main (DIAGNOSE.md)

456000 drafts, 353760 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 353760 | +0.0168 (0.0040), +4.2 |
| rank of the card taken (check 1) | 353760 | -0.0017 (0.0033), -0.5 |
| missed the head's top card (audit) | 353760 | -0.0063 (0.0033), -1.9 |
| SD regret capped at 2 (audit) | 353760 | +0.0125 (0.0037), +3.4 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.737 | 0.273 | 0.445 | 0.179 |
| rank | 1.459 | 0.582 | 1.016 | 0.399 |
| missed top card | 0.535 | 0.116 | 0.457 | 0.108 |
| SD regret capped at 2 | 0.657 | 0.224 | 0.423 | 0.161 |

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 353733 | +0.0147 (0.0021), +7.0 |
| they disagree | 353560 | +0.0063 (0.0064), +1.0 |
| pack 1 | 353760 | -0.0169 (0.0038), -4.4 |
| pack 2 | 352818 | +0.0220 (0.0037), +5.9 |
| pack 3 | 352072 | +0.0300 (0.0040), +7.5 |

## 4. The size in plain terms

- Top card differs on 33.9% of picks: 13.1 picks per draft (median 13, middle half 10 to 16).
- Event wins per swapped pick: +0.027 (0.003), +10.0 (353760 events).
- A drafter who followed lgbm-strong-noalsa instead of main on all 13.1 disagreements of a complete event: +0.36 (0.04) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with lgbm-strong-noalsa: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 353760 | +0.027 (0.003), +10.0 |
| quick-build deck score (saved) | 352334 | -0.097 (0.003), -31.9 |
| pool GIH WR, best 23 in a pair (saved) | 352334 | +0.015 (0.004), +3.4 |

## 7. Confounding by lane and seat

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 353760 | 1.5% | +0.025 (0.028), +0.9 | +0.027 (0.003), +9.9 |
| late pack 3 | 353760 | 7.0% | +0.005 (0.010), +0.5 | +0.030 (0.003), +10.4 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 5.79 | -0.0167 (0.0017), -10.1 |
| took main's top card (b) | 2.78 | -0.0313 (0.0023), -13.4 |
| took neither (c) | 4.56 | -0.0729 (0.0016), -44.9 |
| **a − b** (353760 events) | | +0.0150 (0.0028), +5.4 |
| swap measure as specified | | +0.0273 (0.0027), +10.0 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 49.8% | +0.0240 (0.0036), +6.6 |
| base on, head off | 11.4% | +0.0105 (0.0080), +1.3 |
| base off, head on | 26.4% | +0.0569 (0.0051), +11.2 |
| both off-lane | 12.4% | -0.0184 (0.0111), -1.7 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | +0.0273 (0.0027), +10.0 | +0.0274 (0.0027), +10.1 |
| unconstrained a − b | +0.0150 (0.0028), +5.4 | +0.0151 (0.0028), +5.5 |
| SD regret slope change | +0.0168 (0.0040), +4.2 | +0.0170 (0.0039), +4.3 |
| rank regret slope change | -0.0017 (0.0033), -0.5 | -0.0015 (0.0034), -0.4 |


# Diagnosis of `gihwr-only` against main (DIAGNOSE.md)

456000 drafts, 353760 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 353760 | +0.0960 (0.0051), +18.9 |
| rank of the card taken (check 1) | 353760 | +0.0499 (0.0036), +13.7 |
| missed the head's top card (audit) | 353760 | +0.0484 (0.0037), +13.3 |
| SD regret capped at 2 (audit) | 353760 | +0.0955 (0.0049), +19.3 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.737 | 0.273 | 0.585 | 0.274 |
| rank | 1.459 | 0.582 | 1.851 | 0.661 |
| missed top card | 0.535 | 0.116 | 0.633 | 0.117 |
| SD regret capped at 2 | 0.657 | 0.224 | 0.531 | 0.236 |

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 353751 | +0.0589 (0.0029), +20.5 |
| they disagree | 353307 | +0.1005 (0.0077), +13.1 |
| pack 1 | 353760 | +0.0371 (0.0036), +10.4 |
| pack 2 | 352818 | +0.0842 (0.0049), +17.0 |
| pack 3 | 352072 | +0.0693 (0.0052), +13.3 |

## 4. The size in plain terms

- Top card differs on 40.7% of picks: 15.7 picks per draft (median 16, middle half 13 to 18).
- Event wins per swapped pick: -0.049 (0.002), -20.5 (353760 events).
- A drafter who followed gihwr-only instead of main on all 15.7 disagreements of a complete event: -0.77 (0.04) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with gihwr-only: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 353760 | -0.049 (0.002), -20.5 |
| quick-build deck score (saved) | 352334 | -0.043 (0.003), -16.7 |
| pool GIH WR, best 23 in a pair (saved) | 352334 | -0.412 (0.004), -104.8 |

## 7. Confounding by lane and seat

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 353760 | 1.4% | +0.013 (0.030), +0.4 | -0.049 (0.002), -21.0 |
| late pack 3 | 353760 | 9.9% | -0.011 (0.008), -1.3 | -0.053 (0.003), -20.9 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 2.52 | -0.0393 (0.0025), -15.5 |
| took main's top card (b) | 6.30 | -0.0026 (0.0016), -1.6 |
| took neither (c) | 6.92 | -0.0613 (0.0015), -40.4 |
| **a − b** (353760 events) | | -0.0370 (0.0027), -13.8 |
| swap measure as specified | | -0.0488 (0.0024), -20.5 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 19.3% | +0.0073 (0.0059), +1.2 |
| base on, head off | 72.5% | -0.0721 (0.0028), -25.5 |
| base off, head on | 1.6% | +0.0468 (0.0216), +2.2 |
| both off-lane | 6.7% | +0.0011 (0.0120), +0.1 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | -0.0488 (0.0024), -20.5 | -0.0490 (0.0025), -19.7 |
| unconstrained a − b | -0.0370 (0.0027), -13.8 | -0.0374 (0.0028), -13.4 |
| SD regret slope change | +0.0960 (0.0051), +18.9 | +0.0964 (0.0051), +18.8 |
| rank regret slope change | +0.0499 (0.0036), +13.7 | +0.0504 (0.0036), +13.9 |


