# Value to the deck: Phase 1 and Phase 2a results

Phase 2a (within-deck draw effects) is [at the end](#phase-2a-within-deck-draw-effects).
It replaces Phase 1's advice on which terms V should add.

The question ([PLAN.md](PLAN.md)): can a pick model that values a card by what
it adds to the final deck capture what the crowd knows? Phase 1 asks whether
the deck model is good enough to be that value function. The decision rules
were written in [PROTOCOL.md](PROTOCOL.md) before any run.

Experiment only. Nothing here touches `src/` or is a PR candidate.

## Runs and commits

| what | run | commit |
|---|---|---|
| plan and protocol, before any run | – | 7dbade7 |
| E1, E3, E4 scripts and workflow | 45106784317 (E1 and 17 of 19 E3 sets; KTK, SNC and every E4 shard lost their output to a missing `out/` folder) | 4e5a55a |
| rerun: KTK and SNC joins, E4; takes the other facts from 45106784317 | 45131183513 | a963f5f |
| protocol addendum: skill-confound control, registered before it was run | – | 7e69d03 |
| skill-confound control (join saves maindeck flags per pick) | 45132114280 | 7623bdc |

Source runs: confirmation 45021236056 (base, lgbm-strong-noalsa, gihwr-only;
19 sets × 8 salts × 3000 drafts), weak 45063954691 (base, lgbm-weak; first
1000 drafts per salt), detail 45063945952 (simulated decks with parts).

Reports, as the runs printed them, are in [reports/](reports/):
- [e3.md](reports/e3.md) is from 45131183513, with 19 sets.
- [e3c.md](reports/e3c.md) and [e3-17sets.md](reports/e3-17sets.md) are from
  45132114280.
- [e1.md](reports/e1.md) and [e4.md](reports/e4.md) are from 45131183513.

**Reproduction:**
- e3.py on the modified join's 17 sets is byte-identical to 45106784317's E3.
- The 19-set E3 is byte-identical between 45131183513 and 45132114280.
- E1 is byte-identical between 45106784317 and 45131183513.

## E3: is the crowd's edge in the deck?

The data:
- Complete events: 353,760.
- Matched to game rows: 99.9%. Scored: 99.3%.
- No set is under 80%. TMT is lowest, with 87.9% scored.

The table gives the unconstrained a − b in event wins per disagreement:
estimate (scaled SE), then SEs.

| model | controls | noalsa | lgbm-weak | gihwr-only (placebo) |
|---|---|---|---|---|
| M0 | none | +0.0150 (0.0028) +5.3 | +0.0121 (0.0046) +2.6 | −0.0370 (0.0027) −13.5 |
| M1 | deck score | +0.0366 (0.0028) +13.0 | +0.0429 (0.0049) +8.8 | −0.0487 (0.0026) −18.7 |
| M2 | score parts | +0.0384 (0.0028) +13.6 | +0.0456 (0.0047) +9.6 | −0.0581 (0.0031) −19.0 |
| M3 | + quality shape | +0.0340 (0.0028) +12.1 | +0.0399 (0.0047) +8.5 | −0.0625 (0.0032) −19.4 |
| M4 | + deck counts | +0.0306 (0.0028) +10.8 (205% of M0) | +0.0361 (0.0047) +7.6 (297%) | −0.0475 (0.0032) −14.7 (129%) |
| M0g | none, game win share | +0.0014 (0.0003) +4.3 | +0.0011 (0.0005) +2.4 | −0.0032 (0.0003) −10.5 |
| M4g | M4, game win share | +0.0029 (0.0003) +9.5 | +0.0034 (0.0004) +7.5 | −0.0043 (0.0004) −12.0 |

**Reading: survives, for noalsa and lgbm-weak.** The edge is not in any deck
fact we measure. It grows under deck controls. Drafters who side with the
crowd heads end with decks the deck score rates lower, yet they win more. The
gihwr-only placebo is not explained by the deck either. M0g has M0's sign,
so the join is sound.

### Skill-confound control (addendum 7e69d03)

Disagreement picks are split into two subsets:
- **neither:** neither the head's top card nor main's top card is in any
  played build, so the pick cannot have changed the deck;
- **complement:** at least one of the two cards was maindecked.

The reading is on M4.

| head | picks in "neither" | full M4 | neither M4 | neither / full | complement M4 | verdict |
|---|---|---|---|---|---|---|
| noalsa | 42.5% of 4.62M | +0.0306 (0.0028) +10.8 | +0.0293 (0.0059) +5.0 | 96% | +0.0314 (0.0035) +8.9 | confound |
| lgbm-weak | 41.9% of 1.70M | +0.0361 (0.0047) +7.6 | +0.0344 (0.0088) +3.9 | 95% | +0.0368 (0.0061) +6.1 | confound |
| gihwr-only | 47.9% of 5.54M | −0.0475 (0.0032) −14.7 | −0.0377 (0.0052) −7.3 | 79% | −0.0522 (0.0034) −15.4 | confound |

M0 tells the same story. For noalsa, "neither" is 109% of the full estimate
and the complement is 101%.

**Reading: confound, for all three heads.** The swap edge is as large on picks
that never reached the deck as on picks that did. So it measures who the
drafter is, not what the pick did. The likeliest explanation is drafter skill
or style: drafters who pick like the crowd are better players.

The complement minus "neither" contrast is a within-draft estimate of a pick
effect. For noalsa on M4 it is about +0.002, with no sign of a pick effect.
This contrast was not registered, and its SE has not been computed.

The control has a limit. A pick that was not maindecked can still change the
rest of the draft, through the lane, signals and what gets passed. So
"neither" is not strictly zero-effect. But for a real pick effect, that
indirect route would have to be as large as the direct one, which is
implausible.

## E1: blind spots in the deck model

The data:
- 914,876 decks of 931,705 read, from 20 sets (salt dv1).
- Deck score alone: 0.0438 log-odds per point (SE 0.0021). The app's constant
  is 0.0510.

| feature | joint β per SD (SE), SEs | joint points per SD | sets with + / − sign (alone) | verdict |
|---|---|---|---|---|
| creatures | +0.0231 (0.0042) +5.6 | +0.52 | 19/1 | **blind spot** |
| removal | +0.0210 (0.0049) +4.3 | +0.47 | 13/7 | – (under 0.5 points) |
| main_colors | −0.0212 (0.0028) −7.5 | −0.48 | 0/20 | – (under 0.5 points) |
| lands | −0.0149 (0.0023) −6.4 | −0.33 | 0/20 | – |
| curve_gaps | −0.0067 (0.0018) −3.7 | −0.15 | 3/17 | – |
| splash, cheap, cheap_spells, mana_value | under 2 SEs | ≤ 0.21 | | – |

All candidates together beat the score on held-out data in 19 of 20 sets.
The gain is small, +2.0 × 10⁻⁴ nats per game.

**Quality shape: every stat is a blind spot**, at 4.7 to 14.2 SEs. In points
per deck SD:

| stat | points per deck SD |
|---|---|
| top-3 | +1.46 |
| top-5 | +1.68 |
| weakest-5 | −0.83 |
| SD | +1.03 |
| max | +1.11 |

Fitted together, top-5 is +1.93 points per SD and weakest-5 is +0.63. Mean
card quality drops from 0.55 to 0.20 log-odds per SD.

On linearity, the squared mean-quality term is +10.6 SEs but only +0.39
points at ±1 SD, so the mean-quality curve itself counts as linear. **E2
form: top-heavy.** A card's value to the deck depends mostly on whether it
enters the deck's best five. Mean quality is a weak stand-in.

**Crowd-deck flip** (noalsa minus base, simulated Suggest Deck decks, 150,928
drafts):

| measure | change per draft |
|---|---|
| rating, deck score points | −0.124 (0.005), −25.6 SEs |
| value, adding creatures +0.28, removal +0.22, colors −0.33, cheap +0.06 and mana value −0.40 points per unit | **+0.054 (0.005), +10.5 SEs** |

**Reading: flips.** In simulation, noalsa's deck deficit is entirely from
things the deck score doesn't price: more creatures, more removal and fewer
colors.

PROTOCOL.md describes the deficit as "the old −1.4 points". That figure was
the observed 13-swap number. The simulated deficit this rule applies to is
−0.124 points per draft.

## E4 pilot: hindsight labels (feasibility only, circular)

FDN and TDM, 1000 drafts each, on held-out ratings.

| | FDN | TDM |
|---|---|---|
| cost per draft | 19.2 s | 18.9 s |
| drafter's card hindsight-best (ties / strict) | 64.3% / 39.1% | 45.8% / 30.2% |
| picks with every label 0 | 23.6% | 13.2% |
| build flips | 4.2% | 9.3% |
| median label (log-odds) | about −0.010 | about −0.005 |
| top-1 hindsight-best, labels differ: main / gihwr-only / noalsa / lgbm-weak | 69.2 / 59.9 / 72.2 / 71.1% | 62.9 / 77.7 / 54.0 / 50.4% |

**Projected cost:** 19 sets × 3000 drafts at 19.1 s per draft is 302
job-hours, or 15.1 h wall-clock at 20 jobs. That is feasible against the
480 job-hour bar.

The heads' agreement order reverses between the two sets. These labels use
the app's own deck score, so nothing here ranks a head. The reversal does
warn that hindsight labels differ a lot by set.

## Answer: can a deck-value model capture what the crowd knows?

**Partly. What the crowd knows about decks, yes.** The crowd heads' decks look
worse to the deck score only because it misses three things:
- creature count;
- color count;
- a top-heavy quality shape.

Price those, and noalsa's simulated deck deficit turns into a gain at 10.5
SEs. A deck-value model whose V includes them can learn this.

**The crowd heads' event-win edge, no, and nothing should be built on it.** The
swap edge is just as large on picks that never reached the deck. So it is
mostly drafter skill, not a pick effect. That also undercuts the +10 SE
confirmation result as evidence that crowd picks help.

## What Phase 2–3 should change

1. **Stop using the observational swap edge** (unconstrained a − b, diagnose
   check 10a) to target or judge models.
   - Judge Phase 3 heads on the fixed regret-side measures, as the plan says
     when E3 survives.
   - Also judge them on simulated deck value under the blind-spot-aware V.
   - If an event-win measure is wanted, pre-register the within-draft contrast
     (complement minus "neither"), with a proper SE.
2. *(Replaced by Phase 2a below: within a deck, none of the creature, removal
   or top-5 terms passes, and E1's sizes are mostly or partly skill confound.
   The color term is not tested.)*
   **V for the Phase 2 labels must include the blind spots:**
   - deck score;
   - creatures (+0.28 points each);
   - colors (−0.33 points per color);
   - removal (+0.22 points each);
   - a top-5 quality term in place of most of the mean.

   Otherwise the labels mark the crowd's picks as mistakes. Refit the shape
   term on held-out ratings before using it. The labels use held-out ratings,
   and E1 used the full dataset.
3. **Phase 2 is affordable at full size**, at 302 job-hours, but the labels are
   small and noisy:
   - about a quarter are exactly 0;
   - the median is about −0.01 log-odds.

   Phase 3 should pool them, for example by fitting expected labels over many
   drafts. Fitting single picks won't work.

## Caveats

- **Rating leak:** E1 and E3 use full-dataset ratings that include the decks
  being scored. A deck's own games barely move a card's rating, so the leak is
  small. It is largest for rarely played cards, which are often in the top-5.
- **Skill confound in E1 too:** E1's coefficients have skill and experience
  bucket controls, but the same confound could inflate them. The flip inherits
  this.
- **The deck is a mediator:** controlling for it can absorb skill (PROTOCOL.md
  E3 caveat).
- **E4 is circular:** V is the app's own deck score. E4 shows cost only.

## Phase 2a: within-deck draw effects

The protocol is [PHASE2A.md](PHASE2A.md), committed before any run (6255944).
Unit: one game, with deck fixed effects. Outcome: won. Regressors are
properties of the cards seen, relative to the deck's own average, with
held-out ratings. Shuffling decides which cards a game sees, so these effects
are not confounded by drafter skill the way E1's are.

Scale: 20 E1 sets; 13.0M games; 11.16M games in the primary model across
2.35M decks; reliability r̄ 0.961.

| what | run | commit | job-hours |
|---|---|---|---|
| protocol | – | 6255944 | – |
| fit, report, workflow | 45163773464 (failed on the older files' layout, cancelled) | 4763e9b | 0.81 |
| parser fix (17 meta columns, counts written "0.0"), before any result | 45164368901 (**pre-fix**) | 322a6ff | 1.17 |
| fixes made after 45164368901's results were seen (below) | 45166983828 (**fixed**) | cd79730 | 1.16 |

That is 3.14 job-hours in all. The longest job was OTJ, at 8 min, and each
run took 7–8 min of wall-clock.

Reports:
- [p2a.md](reports/p2a.md) and [p2a.json](reports/p2a.json) are from the fixed
  run, and its per-set fits in [p2a_sets/](reports/p2a_sets/) reproduce them
  byte for byte.
- [p2a-prefix-45164368901.md](reports/p2a-prefix-45164368901.md) is the
  pre-fix run's report, as printed.
- [p2a-prefix-fits-fixed-combine.md](reports/p2a-prefix-fits-fixed-combine.md)
  pools the pre-fix fits with the fixed combine.
- [p2a_supp.txt](reports/p2a_supp.txt) is post hoc (see below).

### Primary reading: opening hand only (M1, no mulligan), fixed run

The opening hand is fixed before play, so this is the pre-registered clean
version. Values are deck-score points per card (β/β_Q × 12/23), with the
disattenuated figure (× r̄) in brackets.

| feature | within deck, M1 | per E1 deck SD | E1 joint fit | E1 flip | ρ = within / E1 (SE) | Rule 3 |
|---|---|---|---|---|---|---|
| (a) seen quality β_Q | +0.0250 win prob. per z, 132.8 SEs | | | | | sanity passes |
| (b) creatures | +0.128 (+0.123) | +0.34 | +0.193 | +0.28 | 0.66 (0.12) | partly confound |
| (c) removal | −0.274 (−0.263) | −0.66 | +0.196 | +0.22 | −1.40 (0.33) | mostly confound |
| cheap (E1's definition) | +0.361 (+0.347) | +0.87 | +0.076 | +0.06 | 4.75 (2.99) | unclear |
| (d) best-five seen | +0.173 (+0.166): a premium of 0.33 z per copy | | | | | |
| (d') slope of the best five vs a middle card | 1.36× (weakest five 0.77×) | | 7.7× | | 0.05 (0.01) | mostly confound |
| (d'') convex Q2 | +38.7 SEs | | | | | |
| (e) splash-color spells | −0.238 (−0.229) | | | | | |
| (e) off-color spells | −0.110 (−0.106) | | | | | |
| (e) land dummies (reference: 3 lands) | ≤1 −1.62; 2 −0.95; 4 −0.65; ≥5 −2.04 | | | | | |
| (f) 2-drop creature in hand (M4) | +0.760 (+0.731) | | | | | |

Verdicts (fixed run):
- **Sanity:** passes.
- **Rule 1, top-heavy:** **not top-heavy**. The premium is 0.33 z, or 0.32
  disattenuated, against a 0.5 bar, even though B5 is at +27.3 SEs. E1's
  top-heaviness is mostly confound (ρ 0.05).
- **Rule 2:**
  - Creatures: **not shown**, at 0.34 points per E1 SD (0.33
    disattenuated) against a 0.5 bar.
  - Removal: **not shown**. Its value in hand is negative.
- **Rule 3:**
  - creatures: partly confound;
  - removal: mostly confound;
  - cheap: unclear;
  - top-heaviness: mostly confound.
- **Draws check:** removal, cheap and splash all flip sign in D1 (whole game)
  at ≥ 3 SEs. They are flagged.
- **Registered V form:** V = deck score − 0.229 × (splash-color spells, per
  copy). Off-color is −0.106 points per copy, which misses the 0.186 bar.

What the opening hand measures: early castability. Hands with cheap plays
(+0.36 per card, and +0.76 for a 2-drop creature) win; removal (−0.27) and
splash cards (−0.24) lose. Over the whole game (D1) these flip:
- removal +0.149;
- cheap −0.053;
- splash +0.027.

So the flagged terms are mostly timing. A given copy is in the opening hand in
only about 7/40 of games, so its value in hand is not its inclusion value.

### Pre-fix vs fixed, per registered rule

| rule | pre-fix 45164368901: key estimate | verdict | fixed 45166983828: key estimate | verdict | changed |
|---|---|---|---|---|---|
| sanity | β_Q +0.01738 (100.6 SEs) | passes | +0.02497 (132.8 SEs) | passes | no |
| Rule 1 | premium 0.58 z (0.56 dis.) | top-heavy | 0.33 z (0.32 dis.) | not top-heavy | **yes** |
| Rule 2, creatures | +0.13 / +0.13 points per E1 SD | not shown | +0.34 / +0.33 | not shown | no |
| Rule 2, removal | −0.96 / −0.92 | not shown (negative) | −0.66 / −0.63 | not shown (negative) | no |
| Rule 3, creatures | ρ 0.26 (0.06) | mostly confound | 0.66 (0.12) | partly confound | **yes** |
| Rule 3, removal | ρ −2.03 (0.48) | mostly confound | −1.40 (0.33) | mostly confound | no |
| Rule 3, cheap | ρ 6.03 (3.80) | unclear | 4.75 (2.99) | unclear | no |
| Rule 3, top-heaviness | ρ 0.25 (0.02) | mostly confound | 0.05 (0.01) | mostly confound | no |
| draws flag | removal, cheap | | removal, cheap, splash | | **yes** (splash added) |
| V form | deck score + 0.848 T − 0.252 S − 2.360 O | | deck score − 0.229 S | | **yes** |

Why the M-model verdicts changed:
- **The cause is the combine, not the fits.** The per-set M0–M4, S1 and D0
  fits are identical between the two runs, to within 1e-12 SE.
- **Pooling the pre-fix fits with the fixed combine** reproduces the fixed
  run's M-model numbers exactly.
- **The bug:** in EOE, the off-color term was seen in about one game in 474k.
  Its clustered SE came from about one deck, and the set's covariance was
  numerically singular. Inverting it put a large indefinite precision into the
  pool, which distorted every pooled term.
- **Symptoms in the pre-fix report:**
  - O at −2.46 points per copy (154 SEs), although most sets are small;
  - the weakest-five slope L pooled positive, although all 20 sets are
    negative;
  - pooled creatures at 0.05, against a per-set median of about 0.13;
  - Q2 and every S1 term reported dead.
- **Where each change comes from:**
  - Rule 1's flip, creatures' Rule 3 and the T and O terms in the V form all
    come from this bug.
  - The splash flag comes from D1, which had a second bug. Its seen-count
    reference level (7, meaning no draws) is empty in 12 of 20 sets (and has
    2 games in Cube), so the design was singular and `inv()` didn't raise.
  - D1's per-set betas moved by up to 3.3 SEs. Pooled D1 splash went from
    −0.004 to +0.027.

### Deviations from PHASE2A.md

1. Parser (322a6ff, before any result): it now reads the older files' layout.
2. Combine (cd79730, after the pre-fix results were seen):
   - A term seen fewer than 100 times over a set's games is treated as dead
     in that set. In M1 this drops EOE's and OTJ's off-color term (about 1
     and 48 seen), and Cube's removal (none tagged) and ≥5-land term (16).
   - Each set's block is inverted with a pseudo-inverse with a 1e-10 cutoff.
     On the fixed run's fits it matches `inv()` to within 1e-11 SE in every
     model.
3. D1 (cd79730, after the pre-fix results were seen):
   - The reference level is now the modal seen count, not 7.
   - The fit refuses designs with a scaled condition number above 1e8. The
     largest in the fixed run is 175 (FRA's D1).
4. Implementation filters not stated in PHASE2A.md, the same in both runs:
   - a deck needs ≥ 10 rated spell copies;
   - decks with a single game drop out under the fixed effects.

The registered rules, thresholds and E1 comparators are unchanged.

### Post hoc: added after seeing results, not part of any verdict

These come from [p2a_supp.py](p2a_supp.py), on the fixed run, and are in
[reports/p2a_supp.txt](reports/p2a_supp.txt).
- **Rules 2 and 3 on the whole game (D1):**
  - creatures +0.120: 0.32 per E1 SD, ρ 0.62 (0.11);
  - removal +0.149: 0.36 per SD, ρ 0.76 (0.18);
  - cheap −0.053;
  - best-five premium 0.46 z.

  None reaches the Rule 1 or Rule 2 bar here either. So "no creature, removal
  or top-5 term" does not depend on opening-hand timing.
- **Off-color:**
  - −0.110 points per copy in M1, and −0.20 in D1 and D0.
  - Per set it is mostly small and noisy; Cube is +1.17 (0.20).
- **Splash:** −0.13 to −0.45 in 18 of 20 sets in M1, and +0.03 in D1.

### Recommended V for the Phase 2 labels

- **Primary, as registered:** V = deck score − 0.229 × splash-color spells
  (per copy).
- **Sensitivity variant: V = deck score.** Run it because the splash penalty
  is flagged: it reverses over the whole game, which points to timing in the
  opening hand.
- **Drop Phase 1's proposed add-ons:**
  - creatures +0.28;
  - removal +0.22;
  - a top-5 quality term.

  Within a deck, none passes its rule. In the primary reading, the within-deck
  sizes are 5% of E1's (top-heaviness), about 65% (creatures) and below zero
  (removal), and the same verdicts hold on the whole game. Quality is close to
  linear in z, with mild convexity: Q2 is positive, and the best-five slope is
  1.36× a middle card's.
- **Not tested:** the deck-level color count (E1: −0.33 per color). Draws can't
  vary it, and E1's estimate carries the same skill-confound risk.

**Caveat:** draw effects measure a card's value when it is drawn, relative to
the deck's average card. Inclusion value can differ:
- a creature count can matter through the cards it enables when it isn't
  drawn;
- removal's value depends on the opponent's deck;
- the cards seen in a long game are a product of that game. The opening-hand
  model avoids this one, but the first two are not identified by draws.
