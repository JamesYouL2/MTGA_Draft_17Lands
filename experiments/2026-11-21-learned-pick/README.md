# Learned pick models as advisor heads

Can a pick model learned from 17Lands picks replace the advisor's score? This
tests LightGBM tuned to strong drafters, LightGBM weighted by event wins, and a
three-input logit, with no rarity or play counts. The rule was fixed before the
run in [PROTOCOL.md](PROTOCOL.md).

**Verdict.** One head beats main on the pre-registered rule: LightGBM on strong
drafters with ALSA held out (`lgbm-strong-noalsa`). Even so, its regret leans
worse (+1.7 SEs). The three heads the user asked for lose to main:
`lgbm-strong`, `lgbm-wins` and `logit-simple`. Each picks a better top card
than main (event wins 2.6 to 7.7 SEs better), but its scores track wins worse
(regret 3.3 to 4.9 SEs worse), and the rule counts that as a loss. Nothing
here goes to main.

**Confirmation: rejected.** `lgbm-strong-noalsa` was rerun on fresh drafts
with three times the drafts, under the rule in [CONFIRM.md](CONFIRM.md). Its
event wins held (+10.0 SEs), but its regret came out 4.2 SEs worse than
main's. The rule rejects any head 2 or more SEs worse on regret. So no learned
head beats main. See "Confirmation run" below.

**Diagnosis.** The learned head orders packs as well as main; its regret harm
is in how it spaces cards within a pack. Drafters who followed it where it
disagreed with main won more, but a model of weak drafters earns about 72% of
that gain on the same drafts. Their final decks rate worse on the app's deck
score. See "Diagnosis" below.

## Runs

- Fits: Learned pick models, run
  [44982629430](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44982629430).
  It covers 19 sets with 2000 strong and 2000 other drafts each. Each set's
  models are fitted on the other 18 sets.
- Measure: Advisor heads, run
  [44985574439](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44985574439).
  It covers 19 sets, 8 salts × 1000 drafts (152,000 drafts, 117,805 complete
  events), on held-out ratings, with `--simulate`.
- Reports: [reports/](reports/).
  - `fits.md`: offline agreement, hyperparameters, gain, logit weights.
  - `heads.md` / `heads.json`: the measures.
  - `agreement.md`: top-1 and top-3.
  - `by_set_wins.md`: event wins set by set.
  - `by_set.md`: regret set by set.
- Confirmation: Advisor heads, run
  [45021236056](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/45021236056)
  for the replays, reported by run
  [45039932320](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/45039932320).
  The reports are in [reports/confirm/](reports/confirm/).

## Results

Head against main (the base), combined over 8 salts. Each figure is the
estimate (scaled SE), then that many SEs. Event wins: positive is better.
Regret slope: positive is worse. Top-1 is the share of strong drafters' picks
(win-rate bucket ≥ 0.6, ≥ 50 games) where the card taken is the head's top
card, on the replay's held-out ratings. The simulated column is the change in
the simulated deck win rate, in points; it is a screen only, not part of the
rule.

| head | event wins per swapped pick | regret slope change | top-1 strong (vs main) | simulated deck win rate | verdict |
|---|---|---|---|---|---|
| main | — | — | 50.2 | — | — |
| gihwr-only (control) | −0.050 (0.004), −11.9 | +0.097 (0.007), +13.8 | 40.3 (−9.9) | −0.24 (0.01) | loses |
| lgbm-strong | +0.034 (0.004), +7.7 | +0.031 (0.007), +4.7 | 62.7 (+12.5) | −0.99 (0.01) | **loses** (regret) |
| lgbm-wins | +0.028 (0.004), +7.0 | +0.033 (0.007), +4.9 | 62.5 (+12.3) | −1.50 (0.01) | **loses** (regret) |
| lgbm-strong-noalsa (diagnostic) | +0.037 (0.005), +7.7 | +0.009 (0.005), +1.7 | 57.5 (+7.3) | −0.16 (0.01) | **beats main** |
| logit-simple | +0.022 (0.008), +2.6 | +0.015 (0.004), +3.3 | 51.7 (+1.5) | +0.45 (0.01) | **loses** (regret) |

For all drafters, top-1 is 46.8% for main and 60.5 / 60.8 / 54.5 / 48.1% for
lgbm-strong, lgbm-wins, noalsa and logit (agreement.md).

### Reading it

- **Two measures that split.** The swap measure asks whether drafters who took
  the head's top card, where it differs from main's, won more events. Every
  learned head says yes. The regret measure asks whether the head's score gaps,
  over all of a draft's picks, predict wins. All four learned heads do worse
  than main on that.
  - A hypothesis, tested in "Diagnosis" below: LightGBM's lambdarank scores
    rank cards well, but their gaps are not values.
  - The logit's gaps are proportional to its inputs, but it leaves out
    everything except quality, lane fit and off-color pips.
- **ALSA buys agreement, not wins.** ALSA is crowd pick order.
  - It is the largest gain share in both full models: 35% for lgbm-strong and
    38% for lgbm-wins.
  - It adds 5 top-1 points (57.5 → 62.7).
  - It adds nothing on event wins (+0.037 without it, +0.034 with it).
  - It costs regret (+0.009 without it, +0.031 with it).

  Without ALSA, quality becomes the largest feature (38.5% of gain).
- **Wins weighting changes almost nothing.** lgbm-wins and lgbm-strong are
  within noise of each other on every measure, and their gain shares match.
- **Per set** (by_set_wins.md):
  - lgbm-strong is ahead of main on event wins in all 19 sets, 6 of them by
    2+ SEs.
  - noalsa is ahead in 18, 5 by 2+ SEs.
  - lgbm-wins is ahead in 17, 6 by 2+ SEs.
  - logit is ahead in 16, 1 by 2+ SEs.
  - None is 2 SEs behind main in any set.

  On regret (by_set.md), the learned heads do best against main on the
  three-color sets (KTK, TDM, SNC) and worst on two-color sets (FDN, NEO, DFT,
  FIN).
- **Simulated draft (screen only).** The LightGBM heads build decks that the
  app's own deck score rates 1 to 1.5 points worse, and the logit's 0.45
  better. This measure grades picks by the deck score's beliefs, so it favours
  heads that think like the app. It does not decide anything.

## Confirmation run

The rule was committed in [CONFIRM.md](CONFIRM.md) before the run started.
The run had three heads: main, `lgbm-strong-noalsa`, and `gihwr-only` as the
control. It used the fits from run 44982629430, reused as they were, and the
same 19 sets. It drew 8 fresh salts (`r36s1` to `r36s8`) of 3000 drafts each:
456,000 drafts and 353,760 complete events.

| head | event wins per swapped pick | regret slope change (95% upper bound) | top-1 strong (vs main) | top-1 all (vs main) | simulated deck win rate |
|---|---|---|---|---|---|
| main | — | — | 50.1 | 46.8 | — |
| gihwr-only (control) | −0.049 (0.002), −20.5 | +0.096 (0.005), +18.9 (0.106) | 40.3 (−9.9) | 37.0 (−9.8) | −0.24 (0.005) |
| lgbm-strong-noalsa | +0.027 (0.003), +10.0 | +0.0168 (0.0040), +4.2 (0.0247) | 57.5 (+7.3) | 54.5 (+7.7) | −0.15 (0.004) |

**Verdict: rejected.** The rule rejects a head whose event wins are under
2 SEs better, or whose regret is 2 or more SEs worse. Event wins were
10.0 SEs better, but regret was 4.2 SEs worse, so the head is rejected. It
would have failed the confirmation bound as well: the regret change's 95%
upper bound is 0.0247, against a cap of 0.0063. The control lost on both
measures, as expected, so the run itself looks sound.

- **The two runs' regret agree within noise.** Here the estimate is +0.0168.
  In the first run it was +0.0089, with an upper bound of 0.019. The two
  differ by about 1.2 SEs, so neither is a "low draw" of the other; the
  larger run simply has the power to clear 2 SEs. In 7 of the 8 salts the
  regret change is above +0.005. By set
  (reports/confirm/by_set.md), regret is 2+ SEs worse in 10 of 19 sets and
  2+ SEs better in one (KTK).
- **The swap gain is real and steady.** It was +0.037 (0.005) in the first
  run and +0.027 (0.003) here. Where the head's top card differs from main's,
  drafters who took the head's card won more events. The regret slope says
  something else: across all of a draft's picks, the head's score gaps track
  wins worse than main's. The rule needs both measures, and the head fails
  the second.
- **Imitation check (not part of the rule).** CONFIRM.md asked whether the
  swap gain comes only from picking like stronger drafters within a skill
  bucket. The gain is about the same in every bucket. That makes "drafters
  who pick like stronger drafters win more" less likely as the whole story,
  but it can't detect lane or seat confounding: a drafter in an open lane
  matches the head more often in any bucket. Checks 7 and 10 under
  "Diagnosis" test that.

  | skill bucket | events | event wins per swapped pick |
  |---|---|---|
  | 60%+ | 74,464 | +0.029 (0.006), +4.6 |
  | 56 to 60% | 72,593 | +0.032 (0.007), +4.5 |
  | 52 to 56% | 79,094 | +0.030 (0.006), +4.9 |
  | under 52% | 127,555 | +0.022 (0.004), +5.2 |
  | all with a bucket | 353,706 | +0.027 (0.003), +10.2 |

  For `gihwr-only`, the loss runs from −0.039 to −0.062 across the buckets.
- **Top-1 and the simulated draft (screen only).** The top-1 lead holds:
  +7.3 points among strong drafters, the same as in the first run. In the
  simulated draft, the head's decks are 0.15 points worse by the app's own
  deck score, again as in the first run.
- **How the report was made.** The replays (run 45021236056) all finished,
  but the report job ran out of memory. At 3000 drafts a salt, the results no
  longer fit in a runner's memory.
  - `slim.py` keeps only the pick fields the reports read. On six of the
    run's artifacts, all five reports came out byte-identical, slimmed or
    not.
  - The workflow's new `report_run` input reports an earlier run again,
    without replaying.
  - The first report-only run, 45037035011, is partial and is not used.
    `download-artifact` with a run ID fetched only 100 of the 152 artifacts.
    Run 45039932320 reads all 152 (456 files).

## Diagnosis: why regret and event wins disagree

The user asked what it means that regret is worse while event wins are
better, and whether the final decks end up better. The checks and the reading
of each outcome were committed before any result was read
([DIAGNOSE.md](DIAGNOSE.md), with two addenda). Addendum 2 adds an independent
audit's checks. The audit found no leakage and no bug that invalidates the
runs. Nothing here changes the confirmation verdict: rejected.

**Runs** (reports in [reports/diagnose/](reports/diagnose/)):

| what | run | drafts | reports |
|---|---|---|---|
| Confirmation run, reported again: noalsa and gihwr-only | [45063926047](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/45063926047) (of 45021236056) | 456,000; 353,760 events | confirm/ |
| First measure run, reported again: every head | [45063936613](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/45063936613) (of 44985574439) | 152,000; 117,805 events | first-run/ |
| Detail re-replay, noalsa with `--detail --simulate` | [45063945952](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/45063945952) | 152,000 (first 1000 per salt of the confirmation salts); 117,904 events | detail/ |
| lgbm-weak fit | [45059004381](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/45059004381) | 19 sets | fits-lgbm-weak.md |
| lgbm-weak replay, on the detail re-replay's drafts | [45063954691](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/45063954691) | 152,000; 117,904 events | lgbm-weak/ |
| Train/serve skew, local | `skew.py` | KTK, SNC, FDN; about 250 drafts each | skew/ |

All figures are head minus main, combined over salts as `heads.py` does:
estimate (scaled SE), SEs. Regret rows: positive is worse. Swap rows: event
wins per pick swapped from main's top card to the head's.

**Reproduction.** On six of the re-replay's 152 folders (KTK, SNC and TMT,
salts 1 and 2), every pick's rank, SD regret and top card equals the
confirmation run's for the same drafts. That is 12,000 draft copies and
459,160 picks, all identical. The re-replay's SD regret and swap figures sit
within noise of the full run's (+0.0162 against +0.0168; +0.031 against
+0.027).

### 1. Scale-free regret (all 19 sets, 456,000 drafts)

| measure | noalsa | gihwr-only (control) |
|---|---|---|
| SD regret (as in heads.py) | +0.0168 (0.0040), +4.2 | +0.0960 (0.0051), +18.9 |
| rank of the card taken | −0.0017 (0.0033), −0.5 | +0.0499 (0.0036), +13.7 |
| missed the head's top card | −0.0063 (0.0033), −1.9 | +0.0484 (0.0037), +13.3 |
| SD regret capped at 2 | +0.0125 (0.0037), +3.4 | +0.0955 (0.0049), +19.3 |
| rank percentile (re-replay only) | +0.0026 (0.0056), +0.5 | – |

Per-draft mean SD regret is 0.737 for main and 0.445 for noalsa. Its spread
across drafts is 0.273 for main and 0.179 for noalsa. noalsa's gaps are
compressed.

- **Rules out:** worse ordering. noalsa's order of the whole pack tracks wins
  as well as main's: rank regret −0.5 SEs, missed-top −1.9 SEs.
- **Rules in:** the harm is in the gaps. Capping SD regret at 2 doesn't remove
  it (+3.4 SEs), so it is not a few extreme gaps; it is the gap sizes in
  general.
- **The control has power:** gihwr-only is 13+ SEs worse on every variant.
- **Not met:** the addendum's "order tracks wins better" reading. Missed-top
  is −1.9 SEs, short of 2.

### 2. Calibrated scores (re-replay, 117,904 events)

| measure | slope change |
|---|---|
| SD regret, raw | +0.0162 (0.0052), +3.1 |
| (a) noalsa's order, main's gaps in each pack | −0.0013 (0.0047), −0.3 |
| (b) global quantile map, fitted on the other 18 sets | +0.0166 (0.0052), +3.2 |

Both maps keep noalsa's top card on 99.84% of 5.86 million picks. The saved
scores reproduce each draft's SD regret exactly.

- **(a) Rules in scale:** the harm is no longer 2 SEs and is under half the
  raw figure. The same order with main's per-pack gaps is not penalised.
- **(b) Rules out a global rescaling:** a single order-preserving map per set
  does not help.
- **Together:** the harm is in how noalsa spaces cards *within* each pack
  relative to the pack's spread, not in its order and not in its overall
  scale.

### 3. Where the regret gap lives (456,000 drafts)

| picks | noalsa | gihwr-only |
|---|---|---|
| main and the head agree on the top card | +0.0147 (0.0021), +7.0 | +0.0589 (0.0029), +20.5 |
| they disagree | +0.0063 (0.0064), +1.0 | +0.1005 (0.0077), +13.1 |
| pack 1 | −0.0169 (0.0038), −4.4 | +0.0371 (0.0036), +10.4 |
| pack 2 | +0.0220 (0.0037), +5.9 | +0.0842 (0.0049), +17.0 |
| pack 3 | +0.0300 (0.0040), +7.5 | +0.0693 (0.0052), +13.3 |

- **Rules in calibration, not picking:** noalsa's regret is 7 SEs worse on
  picks where it chooses the same top card as main, and not 2 SEs worse
  where it chooses differently.
- **Packs (descriptive):** noalsa's regret is *better* than main's in pack 1
  and worse in packs 2 and 3, where main's lane terms matter most.

### 4. The size in plain terms (456,000 drafts)

- noalsa's top card differs from main's on 33.9% of picks: 13.1 picks per
  draft (middle half 10 to 16).
- **As specified:** +0.027 event wins per swapped pick, so a drafter who
  followed noalsa on all 13.1 would gain +0.36 (0.04) event wins.
- **Without the swap regression's constraint** (10a, below): +0.015 per
  swap, or +0.20 (0.04) per event.
- Both are observational, linear extrapolations.

### 5. Do the final decks end up better?

**(a) Drafters who sided with noalsa: their own final decks.** Per swapped
pick, with the swap controls, on the re-replay (Suggest Deck parts) and on
all 456,000 drafts (saved figures).

| outcome | per swapped pick |
|---|---|
| event wins (456k) | +0.027 (0.003), +10.0 |
| quick-build deck score, saved (456k) | −0.097 (0.003), −31.9 |
| pool GIH WR, best 23 in a pair, saved (456k) | +0.015 (0.004), +3.4 |
| Suggest Deck: deck rating | −0.105 (0.006), −18.7 |
| card quality (rating points) | −0.117 (0.006), −19.8 |
| two colors or fewer (share) | +0.003 (0.001), +6.4 |
| colors | −0.011 (0.001), −7.9 |
| removal spells | +0.036 (0.007), +5.4 |
| creatures | +0.080 (0.006), +13.3 |
| creatures and removal at 2 mana or less | +0.048 (0.006), +8.5 |
| mean mana value | +0.001 (0.001), +1.9 |
| missing fixing; missing spells | 0.000 (−2.2); 0.000 (−0.4) |

- **Reading: not rated better.** Drafters who sided with noalsa end with
  decks the app's deck score rates *worse*, about −1.4 points over 13 swaps,
  yet they win more events. The gain lies outside what the deck score
  measures.
- **What their decks have instead:** more creatures, more cheap plays, more
  removal, slightly fewer colors, and pool GIH WR a little higher. They score
  lower on the deck score's card-quality part. That part, not GIH WR, is
  what drives the deck rating down.

**(b) The simulated draft (screen only).** The decks noalsa drafts itself
from the same packs, less main's:

| part | head minus main | main's mean |
|---|---|---|
| deck rating | −0.124 (0.005), −25.6 | 83.89 |
| card quality (rating points) | −0.111 (0.005), −22.6 | 5.79 |
| two colors or fewer (share) | −0.004 (0.000), −15.2 | 0.998 |
| colors | +0.005 (0.001), +6.6 | 2.00 |
| removal spells | −0.196 (0.008), −26.0 | 6.38 |
| creatures | +0.886 (0.010), +85.6 | 11.72 |
| creatures and removal at 2 mana or less | +0.032 (0.008), +4.0 | 7.86 |
| mean mana value | +0.064 (0.001), +48.0 | 2.88 |

Left to itself, noalsa drafts about one more creature per deck and 0.2 fewer
removal spells, at a higher curve. The deck score marks that down on card
quality.

### 6. Placebo: a model of weak drafters

`lgbm-weak` was fitted exactly as noalsa was, on drafters under a 52% game
win rate. The comparison is on the same 152,000 drafts and the same held-out
ratings.

| | noalsa | lgbm-weak |
|---|---|---|
| top-1 agreement with strong drafters, offline | 57.9% | 57.5% |
| top-1 change against main, replay | +7.77 | +7.84 |
| event wins per swapped pick | +0.031 (0.005), +6.5 | +0.022 (0.005), +4.6 |
| unconstrained a − b (10a) | +0.0176 (0.0049), +3.6 | +0.0119 (0.0047), +2.5 |
| both on-lane (10b) | +0.0318 (0.0067), +4.7 | +0.0271 (0.0070), +3.9 |
| base off, head on (10b) | +0.0580 (0.0088), +6.6 | +0.0451 (0.0081), +5.6 |
| SD regret | +0.0162 (0.0052), +3.1 | +0.0269 (0.0060), +4.5 |
| rank regret | −0.0085 (0.0049), −1.7 | −0.0012 (0.0054), −0.2 |
| deck score, saved, per swapped pick | −0.100 (0.005), −19.5 | −0.177 (0.005), −37.3 |

- **Reading: the swap measure largely rewards human-like picking.**
  lgbm-weak is 4.6 SEs better than main on event wins per swapped pick. Its
  estimate is 72% of noalsa's on the same drafts, above the half the reading
  asks for. noalsa's +10 SEs therefore says little about card value.
- **The profile is the same:**
  - SD regret worse while rank regret is not;
  - the gain largest where the head moves to an on-lane card;
  - "both on-lane" positive;
  - worse deck scores.
- **What's left for strong drafters:** noalsa leads lgbm-weak by about 0.009
  per swap, and on rank regret. A paired test of that difference on the same
  drafts was not run, so whether strong drafters add anything is open.

### 7. Confounding by lane and seat

**(a) Pool controls (re-replay):**

| measure | usual controls | with pool controls | kept |
|---|---|---|---|
| event wins per swapped pick | +0.030 (0.005), +6.3 | +0.030 (0.005), +6.1 | 98% |
| SD regret slope change | +0.0172 (0.0052), +3.3 | +0.0247 (0.0067), +3.7 | 143% |

- **Reading:** lane and seat, as the final pool's two-color share, GIH WR
  and on-lane playables measure them, explain little of the swap gain.
- **Rules out** the simple story "they matched noalsa because they were in
  a good lane". It cannot rule out confounders those three facts miss.

**(b) Picks that can hardly change the deck:**

| class | data | share of disagreements | inside | outside |
|---|---|---|---|---|
| off-lane in pack 3 | 456k | 1.5% | +0.025 (0.028), +0.9 | +0.027 (0.003), +9.9 |
| late pack 3 (pick 10+) | 456k | 7.0% | +0.005 (0.010), +0.5 | +0.030 (0.003), +10.4 |
| off-lane in pack 3 | re-replay | 1.5% | +0.051 (0.039), +1.3 | +0.031 (0.005), +6.4 |
| late pack 3 (pick 10+) | re-replay | 7.0% | +0.016 (0.017), +0.9 | +0.033 (0.005), +6.5 |

- **Late pack 3: consistent with the picks causing the gain.** It is within
  2 SEs of zero and below the rest, on both sets of drafts. Where a pick can
  hardly matter, agreeing with noalsa buys nothing. That is what a real pick
  effect predicts, not confounding.
- **Off-lane in pack 3: inconclusive.** On 456k it meets the letter of
  "consistent" (+0.025 against +0.027), but its SE is as large as the
  effect. On the re-replay it is above the rest. Too few picks (1.5%) to
  read.
- **Not pre-registered, from the first run:**
  - The ALSA heads show the confounding signature: a class figure 2+ SEs
    above zero and at least the rest's. That is lgbm-strong's off-lane
    pack 3, +0.095 (+2.4), and lgbm-wins' off-lane pack 3, +0.092 (+2.1),
    and late pack 3, +0.034 (+2.1).
  - noalsa's late pack 3 there is +0.029 (+1.7), below its rest (+0.037).
  - ALSA, the crowd's pick order, seems to carry some of "drafters like the
    crowd win" even where the pick can't matter.

### 8. Train/serve skew

| set | picks compared | cards | row mismatches | pool / scale mismatches | top card changed by float32 |
|---|---|---|---|---|---|
| KTK | 10,145 | 81,183 | 0 | 0 / 0 | 0 (largest score change 0.0) |
| SNC | 9,811 | 78,690 | 0 | 0 / 0 | 0 (0.0) |
| FDN | 9,747 | 77,650 | 0 | 0 / 0 | 0 (0.0) |

**Rules out** skew. The replay head computes exactly the rows training did.
The only gap: about 750 picks per set whose pack has fewer than two different
cards, which training's recorder saw and both pipelines then skip. The known
difference, full ratings in training against held-out ratings in the replay,
is by design and not tested.

### 9. lgbm-strong (with ALSA): checks 1 and 3 (first run, 117,805 events)

| measure | lgbm-strong | lgbm-strong-noalsa |
|---|---|---|
| SD regret | +0.0305 (0.0065), +4.7 | +0.0089 (0.0053), +1.7 |
| rank regret | −0.0006 (0.0066), −0.1 | −0.0093 (0.0049), −1.9 |
| missed top card | −0.0125 (0.0069), −1.8 | −0.0184 (0.0058), −3.2 |
| SD regret capped at 2 | +0.0264 (0.0065), +4.0 | +0.0048 (0.0054), +0.9 |
| agree picks | +0.0215 (0.0057), +3.8 | +0.0082 (0.0037), +2.2 |
| disagree picks | +0.0154 (0.0091), +1.7 | −0.0059 (0.0084), −0.7 |

- **Reading: neither is 2+ SEs worse on rank regret.** So ALSA's extra regret
  harm is in the gaps, too. With ALSA, the same pattern: order fine, gaps
  worse, harm on agree picks.
- **The other heads in that run:** lgbm-wins (rank +0.0, SD +4.9) and
  logit-simple (rank −1.0, SD +3.3) show the same pattern (first-run/).

### 10. The audit's checks (all 19 sets)

**(a) The swap regression without its constraint.** The swap measure forces
"took neither top card" (c) to sit halfway between "took the head's" (a) and
"took main's" (b).

| coefficient | noalsa | gihwr-only |
|---|---|---|
| a: took the head's top card | −0.0167 (0.0017), −10.1 | −0.0393 (0.0025), −15.5 |
| b: took main's top card | −0.0313 (0.0023), −13.4 | −0.0026 (0.0016), −1.6 |
| c: took neither | −0.0729 (0.0016), −44.9 | −0.0613 (0.0015), −40.4 |
| **a − b** | **+0.0150 (0.0028), +5.4** | **−0.0370 (0.0027), −13.8** |
| swap as specified | +0.0273 (0.0027), +10.0 | −0.0488 (0.0024), −20.5 |

Each coefficient is relative to a pick where the two heads agree.

- **Reading: the gain survives without the constraint** (+5.4 SEs). It is
  55% of the specified figure: the constraint inflates it by almost half.
- **Taking neither top card goes with far fewer wins** for every head. Much
  of what the swap measure reads is "drafters who take an advisor's top card
  win more".

**(b) By kind of disagreement** (on-lane is the advisor's lane at that
pick):

| kind | share (noalsa) | noalsa | share (gihwr-only) | gihwr-only |
|---|---|---|---|---|
| both on-lane | 49.8% | +0.0240 (0.0036), +6.6 | 19.3% | +0.0073 (0.0059), +1.2 |
| main on, head off | 11.4% | +0.0105 (0.0080), +1.3 | 72.5% | −0.0721 (0.0028), −25.5 |
| main off, head on | 26.4% | +0.0569 (0.0051), +11.2 | 1.6% | +0.0468 (0.0216), +2.2 |
| both off-lane | 12.4% | −0.0184 (0.0111), −1.7 | 6.7% | +0.0011 (0.0120), +0.1 |

- **Both on-lane, +6.6 SEs:** the cleanest evidence here of better card
  choice. It is observational, and lgbm-weak earns nearly as much there
  (+0.027, check 6).
- **The largest gain is where noalsa moves to an on-lane card** that main
  passes over.
- **gihwr-only's whole loss is the reverse:** it moves off-lane.
- **noalsa's off-lane picks are not punished** (+1.3).

**(c) Skill bins fixed** (`report.controls`' float binning; diagnose.py
only):

| measure | noalsa as run | fixed | gihwr-only as run | fixed |
|---|---|---|---|---|
| event wins per swapped pick | +0.0273 (0.0027) | +0.0274 (0.0027) | −0.0488 (0.0024) | −0.0490 (0.0025) |
| unconstrained a − b | +0.0150 (0.0028) | +0.0151 (0.0028) | −0.0370 (0.0027) | −0.0374 (0.0028) |
| SD regret | +0.0168 (0.0040) | +0.0170 (0.0039) | +0.0960 (0.0051) | +0.0964 (0.0051) |
| rank regret | −0.0017 (0.0033) | −0.0015 (0.0034) | +0.0499 (0.0036) | +0.0504 (0.0036) |

**Reading: the binning bug does not matter here.** Nothing moves by more
than a fifth of an SE on 456k drafts, or by more than a sixth on the
re-replay and lgbm-weak runs. The bug is still on main.

### Caveats

- Main's constants were tuned on these same two measures; the learned heads'
  weren't.
- Training uses the app dataset's ratings; the replay uses held-out ratings
  rebuilt per salt.
- Main's scores are rounded to 0.1 and the heads' aren't. Main has more
  ties, and a tie for the top counts as rank 0.
- Every swap figure is observational: drafters chose their own picks.
- Reproduction was checked on 6 of the re-replay's 152 folders.
- Check 6 compares two estimates on the same drafts without a paired SE.

### What the learned model is doing

Only what the checks support:

1. **It orders packs as well as main does, for predicting wins.** Rank and
   missed-top regret are not worse, on 456,000 drafts, with or without ALSA.
2. **Its regret harm is how it spaces cards within a pack.**
   - Main's gaps with its order remove the harm.
   - A global rescaling does not.
   - The harm sits on picks where it agrees with main.
   - Its gaps are compressed (per-draft SD regret spread 0.18 against 0.27).
   - This is what a ranking objective (lambdarank) leaves untrained.
3. **Where it disagrees with main, drafters who took its card won more.**
   - The figure is about +0.015 per pick once the swap measure's constraint
     is lifted, against +0.027 as specified.
   - It is not explained by the final pool's lane facts (98% kept), or by
     the skill-bin bug.
   - It is absent where a pick can hardly matter (late pack 3).
   - It is largest where the model moves to an on-lane card main passes
     over.
4. **That gain is mostly what any model of human picking earns.** A model
   fitted the same way to *weak* drafters predicts strong drafters' picks as
   well, and earns 72% of the gain on the same drafts, with the same profile.
   The checks don't show knowledge specific to strong drafters.
5. **It drafts what people draft and the deck score undervalues.** Following
   it means more creatures, more cheap plays and removal, and fewer colors.
   The app's deck score rates those decks worse. They win more events in
   the observational data.

### Plain answer

Regret worse while event wins are better means two things. First, the
learned model ranks cards fine but spaces them badly: its order of a pack
predicts wins as well as main's, and the regret penalty comes from its score
gaps, mostly on picks where it agrees with main. Second, where it disagrees
with main, the drafters who took its card won more. About half that gain
survives a fairer regression, it doesn't come from the final pool's lane
facts, and it vanishes where a pick can't matter. But a model of weak
drafters earns most of it too. So it says main's top card is often one people
avoid, typically off its own lane or light on creatures, more than it says
the learned model knows card values.

Do the final decks end up better? By event wins, yes, observationally. By the
app's own deck score, no: drafters who sided with the model end with decks
rated about 1.4 points worse over 13 swaps, with more creatures, cheaper
curves and fewer colors. Either the deck score undervalues those decks, or
drafters who pick like people win for reasons these checks don't capture.

## The top-1 lead without rarity and play counts

The 2026-10-30 fit had LightGBM 6.0 points ahead of the app's scorer for
strong drafters (58.9% against 52.9%). That fit used rarity and play counts.
Without them, on the same drafts and held-out ratings as main:

- lgbm-strong leads by **+12.5** points (62.7% against 50.2%).
- Without ALSA as well, the lead is **+7.3**.

So all of the old lead survives the removal of rarity and play counts, and
ALSA adds about 5 points more.

The setting differs from the old fit. Here GIH WR alone is 9.9 points behind
main; in the old fit it was 14.3 behind. Main also scores lower here (50.2%
against 52.9%). The replay's held-out ratings are likely part of the reason.

Offline, on each set's full ratings (fits.md), top-1 for strong drafters is:

| model | top-1 |
|---|---|
| lgbm-strong | 63.0% |
| lgbm-wins | 62.7% |
| noalsa | 57.9% |
| logit | 52.0% |
| GIH WR alone | 40.3% |

## Chosen features and settings

**Features** (`Tools/LearnedPick/features.py`; no advisor engine code):

- quality z;
- lane_fit (pair GIH WR minus GIH WR, in SDs);
- color_share;
- off-color pips;
- pack and pick;
- IWD;
- mana value;
- creature;
- ALSA;
- number of colors.

Rarity, sample counts and play counts are out.

**LightGBM.** Lambdarank with learning rate 0.05, min_data_in_leaf 200 and
feature_fraction 0.9. num_leaves comes from {15, 63}, and rounds from early
stopping on NDCG@3 (patience 50). Both are chosen by calibrated pick log-loss
on 4 of the 18 training sets, then the model is refitted on all 18.

| head | 63 leaves chosen | rounds |
|---|---|---|
| lgbm-strong | 18 of 19 fits | 228 to 564 (one 15-leaf fit: 1187) |
| lgbm-wins | 18 of 19 | 209 to 420 (KTK: 15 leaves, 704) |
| noalsa | 9 of 19 | 102 to 411 |

**Gain share** (mean over fits):

| feature | lgbm-strong | lgbm-wins | noalsa |
|---|---|---|---|
| alsa | 34.5% | 37.8% | 0% |
| lane_fit | 20.3% | 20.8% | 22.7% |
| color_share | 15.3% | 16.9% | 17.6% |
| quality | 11.2% | 5.9% | 38.5% |
| pick | 10.8% | 10.7% | 6.0% |
| everything else | under 4% each | | |

**lgbm-wins weighting.** The all-drafter sample's picks are each weighted by
their draft's event match wins (0 to 7). 0-win drafts drop out, and a 7-win
draft counts 7 times a 1-win draft.

**logit-simple.** Fitted on strong drafters' picks:

score = 50 + 15 × quality + 5.9 × lane_fit − 15.9 × (off-color pips × lane
settledness)

- quality is −2 if unrated.
- lane_fit is 0 if missing.
- Lane settledness is 0 at P1p1, rising to 1 by P1p15, then 1.

The weights are stable across folds: lane_fit 5.7 to 6.3, off-color −15.5 to
−16.6.

## Broken or approximated

- **The swap measure is observational.** It controls for set, skill bucket and
  games bucket. But within a skill bucket, drafters who pick like strong
  drafters are probably better drafters. So a head trained to imitate strong
  drafters gets some credit on this measure that it would not earn by causing
  wins. Regret is the check against this, and it went the other way for every
  learned head.
- **The noalsa head was added after the local smoke test** showed ALSA at 35%
  of gain. That was before any CI result, and it is pre-registered in
  PROTOCOL.md. It is still one of four learned heads. Its "beats" rests on
  regret staying under the 2-SE bar at +1.7 SEs. Its smallest harm, +0.011,
  is above the 0.0063 regret change known from earlier runs to be a real loss.
  So the result is strong on event wins and soft on regret.
- **The logit SEs (±0.03 points) treat picks as independent.** They ignore
  that picks from the same draft are correlated, so they are too small. The
  spread across folds is the better guide.
- **Training features use each training set's full ratings,** which include
  the training drafts' own games. The replayed set is never in its models'
  training. Its drafts are replayed on ratings without their games, as in
  every heads run. `test_heldout_set_never_reaches_the_fit` checks the fold
  separation.
- **The confirmation reused the first run's fits** (44982629430) rather
  than refitting. Each set's model still never saw that set. `noalsa` itself
  was added after a smoke test in the first run, which is why it needed a
  confirmation.
- **The confirmation's 95% bound uses t on 7 df** (8 salts). The skill
  split uses heads.py's controls and salt combining within each bucket. The
  swap measure is observational: drafters chose their picks.
- **The fit workflow is triggered by a push.** It is not on the fork's default
  branch, so it can't be dispatched. It runs when its own file changes on
  `exp/learned-pick`.

## Reproduce

- Fits: `.github/workflows/learned-pick.yml`.
- Measure: Advisor heads with:
  - `patches=experiments/2026-11-21-learned-pick/heads/*.patch`;
  - the 19 sets;
  - `simulate=true`;
  - `models_run=<fits run>`;
  - `extra=experiments/2026-11-21-learned-pick/agreement.py`.
- Confirmation: Advisor heads with:
  - `patches=experiments/2026-11-21-learned-pick/confirm-heads/*.patch`;
  - the 19 sets;
  - `salts=8`, `drafts=3000`, `simulate=true`;
  - `models_run=44982629430`;
  - `extra=experiments/2026-11-21-learned-pick/confirm_extra.py`.

  To report a finished run again, set `report_run=<run ID>` and the same
  `extra`.
- Per-set event wins: `by_set_wins.py RESULTS --append est.jsonl`, then
  `--combine est.jsonl`.
- Tests: `pytest Tools/LearnedPick/tests` (features, sampling, fold
  separation, logit recovery of known weights, LightGBM above chance).
