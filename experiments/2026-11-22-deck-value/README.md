# Value to the deck: Phase 1 results

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
2. **V for the Phase 2 labels must include the blind spots:**
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
