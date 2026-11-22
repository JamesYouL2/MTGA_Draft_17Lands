
# Diagnosis of `lgbm-weak` against main (DIAGNOSE.md)

152000 drafts, 117904 complete events. Each figure: estimate (scaled SE), SEs, combined over salts. Regret-style rows: the head's event-win slope on the draft's mean of the measure less main's, positive is worse. Swap-style rows: change per pick swapped from main's top card to the head's.

## 1 and 2. Regret, scale-free and calibrated

| measure | events | slope change, head minus main |
|---|---|---|
| SD regret (as in heads.py) | 117904 | +0.0269 (0.0060), +4.5 |
| rank of the card taken (check 1) | 117904 | -0.0012 (0.0054), -0.2 |
| missed the head's top card (audit) | 117904 | -0.0048 (0.0062), -0.8 |
| SD regret capped at 2 (audit) | 117904 | +0.0236 (0.0067), +3.5 |

Per-draft means over complete events (spread: SD across drafts):

| measure | main mean | main spread | head mean | head spread |
|---|---|---|---|---|
| SD regret | 0.737 | 0.273 | 0.422 | 0.169 |
| rank | 1.459 | 0.580 | 1.007 | 0.384 |
| missed top card | 0.535 | 0.116 | 0.456 | 0.106 |
| SD regret capped at 2 | 0.657 | 0.224 | 0.402 | 0.153 |

## 3. Where the regret gap lives

| picks | events | SD regret slope change |
|---|---|---|
| main and the head agree on the top card | 117890 | +0.0222 (0.0039), +5.7 |
| they disagree | 117857 | +0.0204 (0.0092), +2.2 |
| pack 1 | 117904 | -0.0032 (0.0074), -0.4 |
| pack 2 | 117601 | +0.0275 (0.0064), +4.3 |
| pack 3 | 117349 | +0.0387 (0.0096), +4.0 |

## 4. The size in plain terms

- Top card differs on 37.4% of picks: 14.4 picks per draft (median 14, middle half 11 to 17).
- Event wins per swapped pick: +0.022 (0.005), +4.6 (117904 events).
- A drafter who followed lgbm-weak instead of main on all 14.5 disagreements of a complete event: +0.32 (0.07) event wins, extrapolated linearly from the per-swap estimate. Observational.

## 5. Do the final decks differ?

### (a) Drafters who sided with lgbm-weak: their own final decks

Per pick swapped from main's top card to the head's, with the swap measure's controls. Observational.

| outcome | events | per swapped pick |
|---|---|---|
| event wins | 117904 | +0.022 (0.005), +4.6 |
| quick-build deck score (saved) | 117431 | -0.177 (0.005), -37.3 |
| pool GIH WR, best 23 in a pair (saved) | 117431 | +0.010 (0.006), +1.8 |

## 7. Confounding by lane and seat

### (b) Disagreements where the pick can hardly change the deck

Per swapped pick inside the class and outside it, from one regression. Off-lane in pack 3: pack 3, the advisor sees a two-color lane, and neither top card is on it. Late pack 3: pick 10 or later.

| class | events | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 117904 | 1.3% | +0.051 (0.038), +1.3 | +0.022 (0.005), +4.7 |
| late pack 3 | 117904 | 6.5% | +0.006 (0.025), +0.2 | +0.024 (0.005), +5.0 |

## 10. Audit checks (addendum 2)

### (a) The swap regression without its constraint

Event wins on how many disagreements went each way. The swap measure regresses on net agreement and the count, which forces c = (a + b) / 2; here a, b and c are free. a − b is the unconstrained figure per pick swapped from main's top card to the head's.

| coefficient | per draft | event wins per such pick |
|---|---|---|
| took the head's top card (a) | 6.25 | -0.0170 (0.0027), -6.3 |
| took main's top card (b) | 3.20 | -0.0293 (0.0039), -7.5 |
| took neither (c) | 5.02 | -0.0715 (0.0032), -22.6 |
| **a − b** (117904 events) | | +0.0119 (0.0047), +2.5 |
| swap measure as specified | | +0.0222 (0.0048), +4.6 |

### (b) By kind of disagreement

Per swapped pick of each kind, one regression; on-lane is the advisor's lane at that pick.

| kind | share of disagreements | per swapped pick |
|---|---|---|
| both on-lane | 51.4% | +0.0271 (0.0070), +3.9 |
| base on, head off | 9.0% | -0.0305 (0.0159), -1.9 |
| base off, head on | 27.5% | +0.0451 (0.0081), +5.6 |
| both off-lane | 12.1% | -0.0241 (0.0136), -1.8 |

### (c) With report.controls' skill bins fixed

| measure | as run | skill bins fixed |
|---|---|---|
| event wins per swapped pick | +0.0222 (0.0048), +4.6 | +0.0227 (0.0049), +4.6 |
| unconstrained a − b | +0.0119 (0.0047), +2.5 | +0.0125 (0.0048), +2.6 |
| SD regret slope change | +0.0269 (0.0060), +4.5 | +0.0259 (0.0062), +4.2 |
| rank regret slope change | -0.0012 (0.0054), -0.2 | -0.0021 (0.0054), -0.4 |

