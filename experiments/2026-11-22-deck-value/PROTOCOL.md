# Phase 1 protocol: E3, E1 (with E2) and the E4 pilot

Written and committed before any result was read. Local smoke tests may check
that the code runs, on a handful of drafts or decks. Their numbers are not read.

All runs are on the fork's CI, at the main code on this branch (deck score
`two_colors` +3.1, record constants −0.0062 and 0.05099).

## E3: is the crowd's edge in the deck?

**Drafts.** The replays already run:

- the confirmation run 45021236056 (19 sets × 8 salts × 3000 drafts, held-out
  ratings): base, `lgbm-strong-noalsa`, `gihwr-only`;
- the lgbm-weak run 45063954691 (the first 1000 drafts per salt of the same
  salts): base, `lgbm-weak`.

Only complete events count (7 wins or 3 losses), as in every swap figure.

**Join.** Each draft's draft_id is looked up in that set's 17Lands Premier
Draft game data. A played deck is one (draft_id, build_index). A draft with
several builds gets each deck fact as the mean over its builds, weighted by
games played. The match rate is the share of complete replayed events with at
least one game row. It is reported. If it is under 80% in a set, that set's
figures are flagged.

**Deck facts.** Computed by this folder's `deckfacts.py`. It uses the app's card
data (the published dataset, or the KTK/SNC copies in
`experiments/2026-11-15-flag-snc-ktk/datasets`) and the app's `deck_features`
with 17Lands' main and splash colors, as Tools/DeckScoreFit does.

The ratings are the full dataset, not held out. This is a known leak: each
deck's own games are in its cards' ratings. With 3000 drafts sampled from tens
of thousands per set, the leak is small. It is stated with the results.

**Measure.** The unconstrained swap of diagnose.py check 10a. Event wins are
regressed on:

- a, the disagreements settled with the head's top card;
- b, those settled with main's top card;
- c, those settled with neither;
- report.controls (set, skill and games buckets; the skill-bin bug is kept,
  for comparison with earlier figures).

The figure is a − b, per salt, with bootstrap SEs, combined over salts by
heads.combined. Each model runs on the same matched drafts.

| model | added controls |
|---|---|
| M0 | none (the matched sample's baseline) |
| M1 | (a) the played deck's deck score |
| M2 | (b) its parts: card_quality, two_colors, missing_fixing, missing_spells |
| M3 | M2 + (c) the deck's card quality shape: top-3, top-5 and weakest-5 mean GIH WR (in SDs), and its max |
| M4 | M3 + deck counts: creatures, cheap plays, removal, main colors, splash, mean mana value, curve gaps, lands |
| M0g, M4g | (d) M0 and M4 with the deck's game win share (17Lands games won ÷ played, weighted by games) as the outcome, not event wins |

M0g checks the join: it should carry the same sign as M0. With M4g, the
question is whether the residual edge shows up game by game.

**Readings.** Let G0 be a − b at M0 and G4 at M4. They are read for
`lgbm-strong-noalsa` (primary) and `lgbm-weak`. `gihwr-only` is a placebo with
no imitation and is reported alongside.

- **Vanishes:** G4 is under one third of G0 and within 2 SEs of zero. The edge
  is deck quality visible in the deck. If it already vanishes at M1 or M2, the
  deck score sees it. If it vanishes only at M3/M4, it is deck value the deck
  score misses, and E1 names the features.
- **Survives:** G4 is at least two thirds of G0 and at least 3 SEs from zero.
  The edge is not in any measured deck fact. It is player skill, or something
  in the deck no fact here captures. A deck-value model trained on these facts
  cannot learn it.
- **Partial:** anything else. Report the retained share G4/G0, and which
  control block took most of the drop.

Caveat stated in advance: the deck is a mediator, and skill affects both the
deck and the wins. Controlling for the deck can absorb skill too. So
"vanishes" is an upper bound on how much of the edge is in the deck.

## E1: blind spots in the deck model (and E2)

**Decks.** A fresh sample: Tools/DeckScoreFit/decks.py, 50,000 decks per set,
salt `dv1`. It covers the 20 sets of the deck-score-features workflow (about a
million decks). Each deck's facts are computed by `deckfacts.py`, as in E3.
Decks with missing_spells > 0 are left out, as fit.py does.

**Model.** A binomial logistic regression of a deck's games won. Controls: set
indicators, plus the skill and experience buckets (as fit.py). SEs are the
larger of two:

- the dispersion-widened model SE;
- the set-clustered sandwich SE.

Every candidate feature is standardized within set. Its effect in deck-score
points per SD is β_f / β_score, with β_score the deck score's coefficient in
the same fit.

**Candidates:**

| feature | definition |
|---|---|
| creatures | creature cards |
| cheap | creatures and removal of mana value 2 or less |
| cheap_spells | any spell of functional mana value 2 or less |
| removal | cards tagged removal |
| main_colors | the number of main colors |
| splash | 1 if there is a splash |
| mana_value | mean mana value of spells |
| curve_gaps | how many of mana values 2, 3 and 4 have fewer than 2 creatures |
| lands | land cards |

Each is fitted alone with the deck score, then all together.

**Blind-spot rule.** A feature is a blind spot if, in the joint fit, it is at
least 3 SEs from zero and its effect is at least 0.5 deck-score points per SD.
Two supporting figures are reported but are not part of the rule:

- the number of sets in which its alone-fit sign matches;
- the held-out log-loss gain when each set is predicted from a fit to the
  others.

**Quality shape.** Each spell's overall GIH WR, in SDs from the format mean,
counted per copy. The deck's mean of these is card_quality.

Each shape stat is added alone to a fit on card_quality plus the controls and
the other deck-score parts:

- top-3 mean;
- top-5 mean;
- weakest-5 mean;
- SD;
- max.

Then top-5 and weakest-5 are added together.

The same rule applies: ≥ 3 SEs, and ≥ 0.5 points per SD. A shape stat's
coefficient is converted to points by card_quality's coefficient ÷ 12 (log-odds
per point). That coefficient is taken from the fit *without* shape stats, since
top-k and the mean are collinear. (This clarification was added after local
smoke tests on fake outcomes, before any CI run.) Linearity is tested two
ways:

- a squared card_quality term;
- card_quality by deciles, with held-out log-loss.

It is "not linear" if the squared term passes the same rule at ±1 SD.

**E2 form.** If no shape stat passes, the marginal value of a card is linear:
12/23 points × (its z − the z of the deck's weakest spell it replaces), plus
the change in any blind-spot feature × its weight. If top-k passes with a
positive sign, the form is top-heavy. If weakest-k passes with a positive
sign, filler costs more than its mean.

**Crowd-deck flip.** The detail run 45063945952 has deck parts for the base's
and noalsa's simulated Suggest Deck decks (19 sets × 8 salts × 1000 drafts).

A second joint fit is made on the E1 decks, with only the features those parts
have: deck score, creatures, cheap, removal, colors and mana value.

Each draft's head-minus-base change in value, in points, is:

    Δ rating + Σ_k (β_k / β_score) × Δ part_k

This change is combined over salts. The deficit "flips" if the old −1.4-point
change turns positive at 2 SEs or more. It "closes" if it moves to within 2 SEs
of zero.

## E4 pilot: hindsight labels (feasibility only)

FDN and TDM. The drafts are the first 1000 of salt r36s1's 3000-draft sample,
the drafts of the detail and lgbm-weak runs. The ratings are each salt's
held-out dataset, rebuilt as the replays did.

For every pick and every distinct card in its pack:

    label = V(quick_build(final_pool − taken + card)) − V(quick_build(final_pool))

Where:

- quick_build is the app's best quick build, as replay.App.deck_score;
- V = −0.0062 + 0.05099 × (score − 75), the deck's win log-odds.

The taken card's label is 0.

**Reported, not decided:**

- seconds per draft, and the projected job-hours for 19 sets × 3000 drafts;
- the share of picks where the drafter's card is hindsight-best:
  - counting ties as best;
  - counting ties as not best;
- the share of picks with every label 0 or below;
- the share of picks where main's, gihwr-only's, noalsa's and lgbm-weak's top
  card is hindsight-best;
- the label distribution by pack;
- build flips: the share of labelled cards whose swap changes the best build's
  colors.

These labels are circular. V is the app's own deck score, so a head that
copies the deck score is favored by construction. Nothing here can promote a
head.

**Feasibility bar.** Phase 2 at full size is feasible if its projected cost
fits in one day at 20 concurrent jobs (≤ 480 job-hours). Otherwise Phase 2
shrinks as PLAN.md says.
