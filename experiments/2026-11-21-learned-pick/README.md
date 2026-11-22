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
  - LightGBM's lambdarank scores rank cards well, but their gaps are not values.
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
- Per-set event wins: `by_set_wins.py RESULTS --append est.jsonl`, then
  `--combine est.jsonl`.
- Tests: `pytest Tools/LearnedPick/tests` (features, sampling, fold
  separation, logit recovery of known weights, LightGBM above chance).
