# Diagnosis: why regret and event wins disagree for lgbm-strong-noalsa

This was written and committed before any of the diagnosis runs were
launched, and before any of their results were read. Nothing here changes the
confirmation verdict (CONFIRM.md, README.md): `lgbm-strong-noalsa` was
rejected.

## The question

In the confirmation run (Advisor heads 45021236056), the two measures split:

- **Event wins per swapped pick:** +0.027 (0.003), +10.0 SEs better than
  main.
- **Regret slope change:** +0.0168 (0.0040), +4.2 SEs worse than main.

The two measures read different things.

- **The swap measure** (`compare.swap_frame`) reads only picks where the two
  heads' top cards differ. On those picks, it counts how many more of a
  draft's picks matched noalsa's top card than main's.
- **Regret** reads every pick. It is the drafter's shortfall below the head's
  top card, in SDs of the head's scores for that pack. So it also reads
  (a) the gaps between cards, not just their order, and (b) picks where both
  heads agree on the top card.

LightGBM's lambdarank objective trains the order at the top of a pack. It
does not train calibrated gaps. So the regret harm may come from the gaps and
shape of noalsa's scores, not from worse rankings.

The user also asked whether the final decks end up better.

## Data

- **Checks 1, 3 and 4** use the confirmation run's saved results as they
  are. That is 19 sets and salts `r36s1` to `r36s8` × 3000 drafts, re-read by
  a report-only run. The saved picks hold the rank of the card taken among
  each head's scores, its SD regret and each head's top card. That is all
  these checks need.
- **Checks 2 and 5** need every card's score in each pack, and the parts of
  each deck's score. The saved results lack both, so these checks use a
  re-replay of a subset.
  - Same commit of `src/`, same fits (44982629430), same 19 sets.
  - Same salts, sampled at 3000 drafts, so the held-out ratings are exactly
    the confirmation run's.
  - Only the first 1000 drafts of each salt (by draft ID) are replayed: 8 ×
    1000 per set, 152,000 drafts in all.
  - Draft IDs are random hashes, so the first 1000 are a random subset.
  - Heads: main and `lgbm-strong-noalsa`, with `--simulate`.
  - `replay.py --detail` also saves:
    - each pick's scores for every card in the pack;
    - the parts of the score of the deck Suggest Deck builds from the
      drafter's final pool;
    - the same parts for the simulated draft's deck.
- **Reproduction check:** on the subset, each pick's saved rank and SD regret
  must match the confirmation run's for the same drafts. If they don't, that
  is reported first, and checks 2 and 5 are labelled as not on the same
  ratings.

All figures are head minus main, combined over salts as `heads.py` combines
them. Figures are given as estimate (scaled SE), SEs. "2 SEs" means 2 scaled
SEs.

## Checks, and how each outcome will be read

### 1. Scale-free regret

The regret slope is rerun with each pick's regret replaced by the rank of the
card taken among the head's scores (0 is the head's top card). The draft's
mean rank stands in for its mean SD regret. Everything else is as in
`compare.change`: within-set z, the same controls, salts combined. Positive is
worse. This runs on all 456,000 drafts. On the subset it is also run with the
rank as a percentile of the pack's distinct cards.

- **Rank regret 2+ SEs worse:** the harm is in noalsa's ordering below the
  top. Its order of the whole pack tracks wins worse than main's.
- **Rank regret not 2+ SEs worse:** the harm is in the score's gaps and
  shape, not its order.

### 2. Calibrated scores

noalsa's scores are put on main's scale with an order-preserving map, and SD
regret is recomputed. This runs on the subset, in two ways.

- **(a) Within-pack rank transfer.** noalsa's k-th best card in a pack gets
  main's k-th highest score in that pack. The order is noalsa's; the gaps are
  main's.
- **(b) A global quantile map.** For each set, noalsa's raw scores are
  quantile-matched to main's scores, fitted only on the other 18 sets'
  packs.

Neither map changes which card is on top. The swap measure therefore can't
change; the share of picks with the same top card is reported to confirm
it.

- **Calibrated regret no longer 2+ SEs worse, and its estimate under half of
  the raw one on the same subset:** the regret harm is mostly the score's
  scale. The same picks with calibrated gaps would not be penalised.
- **Calibrated regret still 2+ SEs worse:** gaps are not the explanation.
  Read it with check 1.
- **Anything between:** reported as partial.

The raw SD regret on the subset is reported next to both, because the subset
has a third of the drafts and wider SEs.

### 3. Where the regret gap lives

The regret slope change is recomputed with each draft's mean regret taken
over only some of its picks:

- picks where main and noalsa agree on the top card;
- picks where they disagree;
- pack 1, pack 2 and pack 3.

This runs on all 456,000 drafts. Each subset is normalised within set, as in
check 1.

- **2+ SEs worse on agree picks, not on disagree picks:** the harm comes from
  noalsa's gaps where it picks the same top card. That points to calibration,
  not to picking.
- **2+ SEs worse on disagree picks:** the harm comes with the picks where
  noalsa changes the top card.
- **Packs:** descriptive only.

### 4. The size in plain terms

- How often noalsa's top card differs from main's, as a share of picks and
  as a mean per draft.
- The implied event-win change for a drafter who followed noalsa on every
  disagreement instead of main. That is +0.027 × the mean number of
  disagreements per draft, with the SE scaled the same way.

This is observational: it extrapolates the per-swap estimate linearly, and
drafters chose their own picks.

### 5. Do the final decks differ?

- **(a) Observed drafts.** Each part of the drafter's final deck is
  regressed on net agreement. Net agreement is how many more of the draft's
  disagreements went noalsa's way. The deck is the first one Suggest Deck
  builds from the final pool. The controls and salt combining are the
  swap measure's, so each figure is "per pick swapped from main's card to
  noalsa's". The parts are:
  - the deck's rating;
  - card quality (in rating points: 12 × its SDs);
  - two colors or fewer;
  - missing fixing;
  - missing spells;
  - number of colors;
  - removal spells;
  - creatures;
  - creatures and removal at 2 mana or less;
  - mean mana value of the spells.

  Event wins are rerun on the subset as a check. On all 456,000 drafts, the
  saved quick-build deck score and pool GIH WR are regressed the same way.

  This shows what siding with noalsa buys, such as better colors against raw
  quality. It is observational.
  - **The deck rating 2+ SEs higher per swapped pick:** drafters who sided
    with noalsa end with decks the app's deck score rates better.
  - **Not 2+ SEs higher, or lower:** their decks are not rated better, even
    though they win more events. Then the gain lies outside what the deck
    score measures.
- **(b) The simulated draft.** For the decks noalsa and main draft
  themselves from the same packs, the same parts, head minus main. This
  shows which parts make up the −0.15 points. It is a screen only. It grades
  decks by the deck score's own beliefs.

## What will be reported

- One table for each check, and its reading above.
- A short plain answer to two questions: what the disagreement between the
  measures means, and whether the final decks end up better.

## Addendum, 2026-11-22: checks 6 to 9

Added at the user's request ("Check everything") after checks 1 to 5 were
registered and before any diagnosis run finished or was read. The first
detail re-replay (Advisor heads 45058351317) was cancelled while queued, so
that it could also save the pool facts check 7 needs. No results of any
check had been seen when this was written.

The question these add is "what is this?": does the swap measure's gain show
that noalsa picks better cards, or would any model of human picking earn it,
or does it come from the drafter's lane and seat?

### Data changes

- The detail re-replay (checks 2 and 5) also saves, for each draft, two facts
  about the drafter's final pool, both on the lane the app's advisor finds
  for that pool (its main colors):
  - **two-color share:** the share of the pool's colored non-land cards whose
    colors all lie in the lane;
  - **on-lane playables:** non-land cards whose colors all lie in the lane
    (colorless included), with GIH WR at least the set's mean minus one SD
    (the advisor's own playable line).
- The reports keep a pick's lane size (how many main colors the advisor saw,
  field 7 of a pick) as well as its first seven fields. Field 6 already
  records whether each head's top card is on that lane.

### 6. Placebo: a model of weak drafters

`lgbm-weak` is trained exactly as `lgbm-strong-noalsa` was, on weak
drafters' picks instead of strong drafters'.

- **Weak:** a 17Lands game win-rate bucket under 0.52, over a games bucket of
  50 or more. That is the strong rule's game gate with the win rate below
  0.52.
- **Sample:** a third hash sample of 2000 weak drafts per set, beside the
  existing strong and all-drafter samples (same salt). Training uses every
  weak drafter's picks in any sample, as noalsa uses every strong drafter's.
- **Same everything else:**
  - the features, with ALSA hidden;
  - the four validation sets per held-out set (the same hash);
  - the leaves grid and early stopping on NDCG@3;
  - choice by calibrated log-loss, then a refit on all 18 sets;
  - each set's model fitted without that set.
- **Replay:** the subset of checks 2 and 5. That is salts `r36s1` to
  `r36s8` sampled at 3000 drafts, the first 1000 per salt replayed (152,000
  drafts), on the same held-out ratings. Heads: main and `lgbm-weak`, without
  `--simulate`. noalsa's figures on the same drafts come from the detail
  re-replay.

Readings, on event wins per swapped pick (`lgbm-weak` against main):

- **2+ SEs better, and at least half of noalsa's estimate on the same
  drafts:** the swap measure largely rewards human-like picking. noalsa's
  +10 SEs would then say little about card value.
- **2+ SEs better, but under half of noalsa's:** partly human-likeness,
  partly what strong drafters know.
- **Not 2+ SEs better (or worse):** the gain is specific to strong drafters'
  picks, not to imitating people.

`lgbm-weak`'s top-1 agreement with strong drafters and its regret are
reported beside it.

### 7. Placebo: confounding by lane and seat

The swap measure is observational. A drafter who matches noalsa's top card
may simply be in an open or coherent lane, and win for that reason.

- **(a) Pool controls.** The swap regression (event wins on net agreement,
  number of disagreements and the usual controls) is rerun on the subset with
  three more controls: the final pool's two-color share, its GIH WR (pool
  GIH WR, best 23 in a pair, as saved) and its on-lane playables. The same
  controls are added to the regret slope change for comparison.

  These controls are partly outcomes of the picks: a better pick raises pool
  GIH WR. So any shrinkage is an upper bound on confounding.
  - **The swap estimate keeps 2/3 or more of its value and stays 2+ SEs:**
    lane and seat, as these controls measure them, explain little of the
    gain.
  - **It falls under half its value:** much of the gain goes with lane, seat
    or the pool the picks built. This check can't tell those apart.
  - **Between:** partial.

- **(b) Picks that can hardly change the deck.** Disagreements are split into
  a class and the rest. Event wins are regressed on each part's net agreement
  and disagreement count, with the usual controls. Each class figure is "per
  swapped pick of that class". Two splits, each on all 456,000 drafts and on
  the subset:
  - **off-lane in pack 3:** pack 3, the advisor sees a two-color lane, and
    neither main's nor noalsa's top card is on it;
  - **late pack 3:** pack 3, pick 10 or later.

  Readings, for each split:
  - **The class figure is 2+ SEs above zero and at least the rest's:** an
    "effect" where the pick can hardly change the deck. That means
    confounding.
  - **The class figure is within 2 SEs of zero and below the rest's:**
    consistent with the picks themselves causing the gain.
  - **Otherwise:** inconclusive, with the class's share of disagreements
    given.

### 8. Train/serve skew

For a sample of drafts from three sets (KTK, SNC and FDN; strong and other
drafters, sampled by `drafts.py`), each pick's feature rows are computed two
ways on the same dataset:

- the training pipeline's way: `features.training_rows`, as `features.py`
  runs it;
- the replay head's way: `replay.py` through a copy of `src/` with the
  noalsa patch, capturing the rows `learned_head` hands to the model.

They are compared exactly, card by card, with NaN equal to NaN.

Training stores rows as float32, but the head scores float64 rows. So each
set's noalsa model (fits run 44982629430) also scores both, and the report
gives the largest score difference and the share of picks whose top card
changes.

- **Any row mismatch:** skew. The feature and the picks it affects are
  reported.
- **Top card changes on more than 0.1% of picks from float32 alone:** a skew
  worth fixing. Otherwise it is negligible.

By design, training uses each training set's full ratings, while the replay
uses held-out ratings. That difference is known and is not tested here.

### 9. lgbm-strong (with ALSA): checks 1 and 3

These run on the first measure run (Advisor heads 44985574439, 8 × 1000
drafts, 19 sets). They come from its saved results, by a report-only run,
for `lgbm-strong` and, on the same drafts, `lgbm-strong-noalsa`. The readings
are checks 1 and 3's.

- **lgbm-strong's rank regret 2+ SEs worse while noalsa's is not:** ALSA's
  extra regret harm includes ordering.
- **Neither 2+ SEs worse:** ALSA's extra harm is in the gaps.

### The write-up

Each check says plainly what it rules in or out. The write-up ends with
"What the learned model is doing", which states only what the checks
support.
