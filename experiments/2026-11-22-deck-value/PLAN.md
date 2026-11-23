# Value to the deck: a research plan

The question: can a pick model that scores a card by what it adds to the
final deck capture what the crowd knows? A pick model fitted to strong drafters'
picks (`lgbm-strong-noalsa`, exp/learned-pick) beat the app's advisor on event
wins per swapped pick (+10.0 SEs on the confirmation run 45021236056). A model
fitted to weak drafters (`lgbm-weak`) earned 72% of that gain. So the gain looks
like crowd-consensus picking, not expert knowledge. The decks those models lead
to rate *worse* on the app's deck score (−1.4 points per draft), yet win more.

A "value to the deck" model would train on a deck-value target, not on
imitation. The plan has four phases. Each phase can stop the work.

Experiment only: no `src/` changes and no PR candidates. Everything runs on the
fork's CI.

## Phase 1: is the deck model good enough to be the value function?

A deck-value target is only as good as the deck model that scores it. If the
crowd's edge is in things the deck score cannot see, a deck-value model trained
on the deck score will miss that edge too.

- **E3. Is the crowd's edge in the deck at all?** Join each replayed draft to
  the decks the drafter actually played (17Lands game data, by draft_id).
  Re-estimate the learned heads' unconstrained swap gain with controls for the
  played deck: its deck score, then the score's parts, then its card-quality
  shape, then plain deck counts. If the gain goes away under deck controls, the
  edge is in the deck, and the controls that remove it say which part. If it
  survives every deck control, the edge is in the player (play skill, mulligans,
  sideboarding) or in deck value no count here sees. A deck-value model could
  not learn it from decks.
- **E1. Blind spots in the deck model.** On about a million 17Lands decks,
  regress game wins on the deck score and one candidate feature at a time, then
  all together. Candidates: creature count, cheap plays, removal, main colors,
  splash, mean mana value, curve gaps and lands. Use set and player controls,
  as Tools/DeckScoreFit does, and report held-out fit by set. Also test the
  shape of card quality: mean against top-k, weakest-k, spread and maximum, and
  whether win log-odds is linear in mean quality. Then ask whether the blind
  spots flip the sign of the crowd heads' deck deficit.
- **E2 (folded into E1). The marginal value form.** From E1's shape result,
  write down what one card is worth to a deck. One candidate is (its rating −
  the 23rd card's rating) × 12/23 points, plus each blind-spot feature's change
  × its weight. A top-heavy form is the alternative.

The rules for reading Phase 1 are in [PROTOCOL.md](PROTOCOL.md).

## Phase 2: hindsight value labels

For each pick, label every card in the pack with its value to the drafter's
final pool:

    label(card) = V(build(final_pool − taken + card)) − V(build(final_pool))

Here V is the deck value: the app's deck score converted to win log-odds by
the record constants (Phase 1 may add blind-spot terms). `build` is the app's
quick deck build. The taken card's label is 0.

- **E4 pilot (in Phase 1's run):** FDN (two-color) and TDM (three-color), 1000
  drafts each. Report the cost, the share of picks where the drafter's card is
  hindsight-best, how often each head's top card is hindsight-best, the label
  distribution, and pathologies such as build flips. Feasibility only.
- **Known bias: hindsight is circular and lane-locked.** The final pool already
  reflects the drafter's lane, so labels favor cards in the colors they ended
  in. Early picks, made before the lane exists, get the most biased labels.
  Phase 4 measures this.
- **At scale:** 19 sets × 3000 drafts, on held-out ratings, sharded on CI.
  Labels go into the same per-card rows Tools/LearnedPick uses, so Phase 3
  reuses its features.

## Phase 3: forward value models

Fit models that predict the hindsight label from what is known at pick time:
the pack, the pool so far, and pack and pick. Use Tools/LearnedPick's features
without ALSA.

- **Model classes, same target and features:**
  - logistic regression (a linear score), on the label's rank within the pack;
  - logistic regression plus pairwise interactions with lane and pick stage;
  - LightGBM regression on the label itself.

  These answer the user's "is it LightGBM or logistic" with the target held
  fixed.
- **Validation:** each set's model is fitted on the other sets (as for the
  learned heads).
- **Replay** each model as an advisor head against main, `lgbm-strong-noalsa`
  and `lgbm-weak`. Score on the fixed measures:
  - rank regret alongside SD regret;
  - the unconstrained swap a − b;
  - skill bins fixed;
  - the simulated deck measure as a screen.

  The comparison that matters: does a value model reach the imitation models'
  event-win gain without their regret harm? Does it keep that gain once E3's
  deck controls are applied?

## Phase 4: rollout labels and lane-switch bias

`Tools/AdvisorReplay/simulate.py` can finish a draft from any pick. For a
sample of picks, take each candidate card, let the advisor draft the rest of
the packs, and build and score the deck. That gives a forward value label that
does not assume the drafter's final lane.

Compare rollout labels with hindsight labels pick by pick. The gap, by pack
and pick, is the hindsight label's lane-lock bias. It sets how far to discount
early-pick hindsight labels. It also sets whether Phase 3 should train on
rollout labels for pack 1.

Rollouts cost about 30 to 40 picks of advice per candidate card. So run them on
a few hundred drafts per set, and only for packs 1 and early pack 2.

## What changes the plan

- If E3 shows the edge survives every deck control, a deck-value model cannot
  learn it. Phase 3 should then aim at the regret side, not at matching
  imitation's event wins.
- If E1 finds blind spots, V in Phases 2 to 4 must include them. Otherwise
  hindsight labels will rate the crowd's picks as mistakes.
- If E4's cost projection exceeds a day of CI at 20 jobs, Phase 2 drops to
  fewer drafts or to the quick build's first pair only.
