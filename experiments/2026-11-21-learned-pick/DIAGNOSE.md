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
