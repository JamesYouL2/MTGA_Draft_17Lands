# Learned pick models as advisor heads

Written and committed before any CI result was read. Local smoke tests checked
that the code works. They used three sets (DFT, FDN, FIN), 150 strong and 300
other drafts each, and a 12-draft DFT replay on full ratings. Their numbers are
too small to read and are not used, with one exception, stated here because it
shaped the design. ALSA took 35% of LightGBM's gain and quality only 3%. Holding
ALSA out of one fit cost about 7 top-1 points on DFT. So a fourth, diagnostic
head without ALSA was added.

## The question

The 2026-10-30 pick fit (run 41052835411) found that LightGBM agreed with strong
drafters' picks more often than the app's scorer: 58.9% top-1 against 52.9%, on
held-out sets. That fit used rarity and play counts, which may copy human
habits rather than card value. The fit was never tested on what the advisor is
judged by.

This experiment asks whether a learned pick model, without those inputs, beats
the app's advisor at its job, and whether a simple logit does.

## The models

The code is in `Tools/LearnedPick`. Each pick's rows are the distinct cards in
the pack, with these features (`features.py`). None come from the advisor
engine.

| feature | what it is |
|---|---|
| quality | (GIH WR − set mean) / set SD; missing if unrated |
| lane_fit | (GIH WR in the pool's top two colors' pair − GIH WR) / SD; missing below 10 pair samples or with no second color |
| color_share | the pool's share of nonland cards in the card's thinnest color; 1 if colorless |
| off_pips | mana symbols the lane can't pay (hybrid counts only if no option is in the lane; Phyrexian and {2/C} are free) |
| pack, pick | |
| iwd | improvement when drawn, in points |
| mana_value | |
| creature | 1 if a creature |
| alsa | average last seen at (crowd pick order) |
| n_colors | the card's colors |

Rarity, sample counts and play counts are left out.

The data per set is two hash-priority samples from the 17Lands Premier Draft
dump, salt `learned` (`drafts.py`):

- 2000 drafts by strong drafters: win-rate bucket ≥ 0.6, at least 50 games;
- 2000 drafts by any drafter.

The features use the set's full ratings.

There are four heads. Each set's models are fitted on the other 18 sets only.

| head | fitted to | how |
|---|---|---|
| `lgbm-strong` | strong drafters' picks, from either sample | LightGBM lambdarank |
| `lgbm-wins` | the any-drafter sample's picks | LightGBM lambdarank, each pick weighted by its draft's event match wins (0 to 7), so 0-win drafts drop out and a 7-win draft counts 7 times a 1-win draft |
| `lgbm-strong-noalsa` (diagnostic) | as lgbm-strong | ALSA set to missing in training and scoring |
| `logit-simple` | strong drafters' picks | conditional logit on quality (unrated −2), lane_fit (missing 0) and off_pips × lane settledness (0 at P1p1, rising to 1 by P1p15, then 1). Score = 50 + 15 points per SD of quality, the other two weights in proportion to their fitted coefficients |

**LightGBM settings.** Learning rate 0.05, min_data_in_leaf 200,
feature_fraction 0.9. num_leaves comes from {15, 63}, and rounds from early
stopping on NDCG@3 (patience 50, at most 1500 rounds). Both are chosen on four
of the 18 training sets, picked by a hash, using the lowest pick log-loss after
one fitted softmax temperature. The model is then refitted on all 18 sets.

**As a head.** Each patch replaces every candidate's contextual score with the
model's score, just before `evaluate_pack` sorts. The score is 50 + 10 × raw
for LightGBM and the point scale above for the logit. The pool, the set's
GIH WR mean and SD, and the replay's held-out ratings are the advisor's own.

## The run

- Learned pick models (`.github/workflows/learned-pick.yml`) on the 19 sets
  BLB, DFT, DMU, DSK, EOE, FDN, FIN, FRA, HOB, KTK, LTR, MSH, NEO, OTJ, SNC,
  SOS, TDM, TLA and TMT.
- Then Advisor heads on the same 19 sets, with:
  - 8 fresh salts of 1000 drafts;
  - `--simulate`;
  - `models_run` set to that run;
  - heads `lgbm-strong`, `lgbm-wins`, `lgbm-strong-noalsa`, `logit-simple`
    and the control `gihwr-only`; main is the base;
  - extra report `agreement.py`.
- Each replayed set's models never saw that set's drafts or ratings. Its drafts
  are replayed on ratings rebuilt without their games, as in every heads run.

## The measures

1. **Event wins per swapped pick** against main: the primary measure.
2. **Regret slope change** against main.

Both are combined over the 8 salts with scaled SEs, as `heads.py` reports
them.

Not part of the decision:

- top-1 and top-3 agreement for all and for strong drafters (`agreement.py`);
- the simulated-draft deck win rate (a screen only: it grades picks by the deck
  score's own beliefs, and on GIH-WR-only heads it is circular);
- per-set event-win differences (`by_set.py`);
- gain importance.

## The decision rule

For each head against main:

- **Beats main**: event wins at least 2 scaled SEs better, and regret not
  2 scaled SEs worse.
- **Matches main**: within 2 scaled SEs on both.
- **Loses to main**: otherwise.

`heads.py` has its own "decision" column. Its rule is close but not the same,
and this experiment's rule is the one above. `gihwr-only` is a control: it is
expected to lose, as it has before. Four learned heads are tested, so a "beats"
at 2.0 to 2.5 SEs would be reported as such but called fragile. Whatever the
verdict, nothing goes to main: the user asked for an experiment, not a feature.

## The top-1 lead

How much of LightGBM's old 6.0-point top-1 lead over the app's scorer (58.9%
against 52.9%) survives without rarity and play counts? This is read from the
heads run: lgbm-strong's top-1 minus base's, for strong drafters, on the same
drafts and held-out ratings. `gihwr-only` minus base checks that the setting is
comparable: the old fit had GIH WR alone 14.3 points behind the scorer.
`train.py --report` gives the offline agreement on full ratings next to it.
