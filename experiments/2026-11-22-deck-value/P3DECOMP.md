# Phase 3-lite: where the deck-value gain comes from (registered before running)

Phase 3-lite (run 45187839933, README) found the blend-1 head's simulated decks
score higher than main's (+0.765 win-rate points, +47 SEs), but the deck score
is both the head's guide and its judge. The within-deck draw study (Phase 2a)
backs only one part of that score: card quality. Draws can't test the color
and fixing terms. This test splits the gain into the score's parts.

## Method

The app's deck score is linear (src/advisor/deck_scorer.py):

    score = 75 + 12 × card_quality + 3.1 × two_colors − 2.5 × missing_fixing − 10 × missing_spells

clamped at 0. For each draft, head minus main in each term's points
(weight × feature difference) adds up to the score difference. A residual
covers the clamp and anything Suggest Deck's rating adds.

- **Drafts:** the same as the eval: salt r36s1, held-out ratings, the first 500
  drafts per set, all 19 sets.
- **Heads:** main, blend-1 and marginal, the advisor drafting the real packs,
  as in the eval. Simulation only, with no replay on the drafter's pool.
  `simulate.deck_parts` saves the parts. The deck's spells and some facts about
  the pool are saved too, for later offline checks.
- **Combining:** paired by draft; each set's mean, then an equal-weight mean over sets. SE = sqrt(Σ SE²) / sets,
  as in p3_report.py. Drafts where either head fell back to the quick build
  (no Suggest Deck entry, so no parts) are left out. How many is reported, and
  so is the score difference on the drafts that are kept.
- **Reproduction check:** the rerun's simulated scores for main and blend-1
  should match the eval's (run 45187839933) draft for draft. The share that
  match to 4 places is reported. A mismatch above 1% is flagged.

## Reading (blend-1 primary, marginal shown beside it, 19-set combined)

Let Q be the card-quality term's share of the score difference, and C be the
share from two_colors and missing_fixing together.

- **Quality-led:** Q ≥ 75% and the quality term ≥ 3 SEs. The gain rests on the
  part of the score the within-deck draws back. The circularity worry gets
  narrower: the question becomes whether rank regret's disagreement is
  imitation (it is scored on real drafters' event wins) or real harm.
- **Colors-led:** C ≥ 50%. The gain rests on the two-color bonus and the fixing
  charge, which are fit between drafters (or to drafters' build choices) and
  untested by draws. The case for the blend is weak.
- **Mixed:** anything else.

Descriptive, not part of the rule: colors, splash spells, creatures, removal,
cheap plays, mean mana value; the pool's mean card quality; how many of the
pool's spells are in the deck's colors. These say whether the head took better
cards or cards that fit.
