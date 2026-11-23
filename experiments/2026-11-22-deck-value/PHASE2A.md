# Phase 2a: a value function from shuffled draws

Registered 2026-11-23, before any run. Phase 1 (README.md) found that E1's blind
spots (creatures, removal, the best five cards) and E3's swap edge both compare
drafters, so a better drafter's deck can look better for reasons that have
nothing to do with the cards. The library shuffle gives a randomized experiment
inside one deck: the same drafter, the same 40 cards, and a random set of them
seen in each game. This phase uses that to estimate which card properties win
games, free of drafter skill.

## Data

- 17Lands public game data, PremierDraft, for the same 20 sets as E1:
  BLB, Cube_-_Powered, DFT, DMU, DSK, EOE, FDN, FIN, FRA, HOB, LTR, MH3, MSH,
  NEO, OTJ, PIO, SOS, TDM, TLA, TMT. Card types, removal tags, mana values and
  colors come from the app's dataset through Tools/DeckScoreFit/features.App,
  as in deckfacts.py.
- A deck is (draft_id, build_index). Its 40 cards are the row's deck_ columns.
- Spells are deck cards without the Land type. Lands are never rated.

## Held-out ratings

- Drafts split into two folds by a hash of draft_id. Each game's cards are rated
  from the other fold only: GIH WR = games won / games with the card in the
  opening hand or drawn, counting a game once per card. A card needs at least
  500 such games in the other fold; otherwise it is unrated (it counts as a
  spell of average quality, and the number of unrated spells seen is a control).
- z = (GIH WR − mean) / SD, with the app's All Decks gihwr mean and SD for the
  set (as deckfacts.py), so one z unit means the same as in the deck score.
- Reliability r per set: the correlation across spells of the two folds' GIH WR.
  Noisy ratings attenuate the quality slope, which inflates every ratio to it,
  so each points figure is also reported with the slope divided by r
  ("disattenuated"). A rule's size threshold must hold under both.
- Sensitivity, no rule: the primary model with the app's own (in-sample) ratings.

## Unit, outcome, regressors

Unit: a game. Outcome: won (0/1), a linear probability model with deck fixed
effects (all variables demeaned within deck). Using the deck's own games only,
each regressor is relative to the deck's own average, and drafter, card pool,
build and opponent mix are held fixed.

Per game, over the cards seen, with z̄ = the deck's mean z over its rated spell
copies:

| | term | definition |
|---|---|---|
| (a) | Q | Σ over seen rated spells of (z − z̄). Baseline, must be strongly positive |
| (b) | C | creatures seen |
| (c) | R | removal spells seen ('removal' tag) |
| (d) | B5 | seen copies among the deck's five best spell copies by held-out z (ties split evenly) |
| (d') | T, L | Σ (z − z̄) over seen best-five copies, and over seen weakest-five copies: extra slopes |
| (d'') | Q2 | Σ (z − z̄)² over seen rated spells: a convex term |
| (e) | lands | opening hand: land-count dummies (≤1, 2, 4, ≥5; 3 is the reference). Draws version: lands seen |
| (e) | S, O | seen spells with a splash color; seen spells outside main+splash colors |
| | K | E1's "cheap": creatures or removal with mana value ≤ 2 seen |
| (f) | F | 1 if the opening hand has a creature of mana value ≤ 2. The opening hand is the only turn proxy (num_turns minus cards drawn is not a turn count), and a 2-drop in it is castable by turn 2 |
| | controls | unrated spells seen, on_play |

Models:

- **M1 (primary, clean):** games with no mulligan, opening hand only (always 7
  cards in this data, fixed before play). Q, B5, C, R, K, S, O, land dummies,
  controls.
- **M0:** M1's games with Q and the controls only (sanity).
- **M2:** M1 with T and L instead of B5 (the top-heaviness slope).
- **M3:** M1 with Q2 instead of B5 (convexity).
- **M4:** M1 plus F (curve).
- **D1 / D0:** seen = opening hand + drawn, all games, mulligan dummies (1, ≥2),
  lands seen instead of the dummies, with (D1) and without (D0) dummies for the
  number of cards seen. Game length is an outcome of play (long games draw more),
  so these are secondary.

SEs are clustered by deck. Each set is fitted alone; the 20 sets are combined
by inverse-variance (GLS on the full coefficient vector). Ratios use the delta
method. Set signs are reported.

## Converting to deck-score points

One rated card's z +1 is 12/23 deck-score points (card quality ×12, mean over
about 23 spells). A seen feature worth β_f is worth β_f / β_Q seen-z units, so

    points per card = (β_f / β_Q) × 12/23,
    points per E1 deck SD = points per card × E1's SD of the feature
                            (creatures 2.69, removal 2.40, cheap 2.41).

Every deck card is seen in the same share of games, so this ratio carries from
draws to inclusion, under the caveat below.

## Rules (read on M1 unless named)

- **Sanity:** β_Q > 0 at ≥ 10 SEs. If not, Phase 2a is inconclusive and stops.
- **Rule 1, top-heavy within a deck:** B5 > 0 at ≥ 3 SEs, and the premium
  β_B5 / β_Q ≥ 0.5 z units per best-five card (0.26 points per card, 1.3 for all
  five), raw and disattenuated → "top-heavy"; otherwise "not top-heavy".
  Compared with E1 through M2's slope ratio (β_Q + β_T) / β_Q against E1's
  top-to-middle per-card slope ratio, 7.7 (top-5 and weakest-5 fit:
  (0.0877/0.30/5 + 0.2008/23) / (0.2008/23)). Also reported: M3's Q2.
- **Rule 2, creatures and removal beyond GIH WR:** for each of C and R, ≥ 3 SEs
  and ≥ 0.5 points per E1 deck SD, raw and disattenuated → "carries value";
  otherwise "not shown". E1's joint fit had creatures +0.52 and removal +0.47
  points per SD.
- **Rule 3, skill-confound size:** for creatures, removal and cheap, the ratio
  ρ = within-deck points per card / E1 joint-fit points per card (E1: creatures
  0.193, removal 0.196, cheap 0.075), delta-method SE from both, and for the
  top-heaviness ρ = (M2 slope ratio − 1) / (7.7 − 1). With CI = ρ ± 2 SE:
  "mostly confound" if CI < 0.5; "partly confound" if 0.5 ≤ upper < 1;
  "larger within deck" if lower > 1; "consistent" if the CI covers 1 and is
  narrower than ±0.5; "unclear" otherwise. Secondary comparison: E1's flip fit
  (creatures 0.28, removal 0.22, cheap 0.06 per unit).
- **(e) and (f), reported:** lands dummies, S, O (M1), F (M4), each with SEs and
  points per card. No E1 comparison (E1's lands and colors are deck-level
  choices, not draws).
- **Draws check:** D1 and D0 against M1, per term. A sign opposite to M1's at
  ≥ 3 SEs in D1 is flagged.

## The value-function form (decided by the rules)

V = deck score + one term per property that passes its rule here, weighted by
its within-deck points per card, using the disattenuated figure (the smaller):

- creatures and removal: points per copy, if Rule 2 passes;
- top-heaviness, if Rule 1 passes: every deck has exactly five best cards, so
  the count can't enter V; the transferable form is the extra slope on the best
  five copies, (β_T / β_Q) × 12/23 points per z unit of each best-five copy's
  (z − z̄), if T is ≥ 3 SEs, else Q2's convex term if it is, else none;
- splash or off-color cards: a per-copy penalty, if ≥ 3 SEs and ≥ 0.186 points
  per copy (Rule 2's threshold per creature);
- no land term: the builder sets the land count.

## Caveat

Draw effects measure a card's value when it is drawn, relative to the deck's
average card. Inclusion value can differ: a creature count can matter through
the cards it enables when it isn't drawn, a removal spell's value depends on
the opponent's deck, and the cards seen in a long game are a product of that
game. The opening-hand model avoids the last; the first two are not identified
by draws.

## Running

experiments/2026-11-22-deck-value/p2a_fit.py, one CI job per set
(.github/workflows/deck-value-p2a.yml), then p2a_report.py combines the sets.
Job-hours are reported from the run's job timings.
