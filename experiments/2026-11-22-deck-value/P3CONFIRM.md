# Phase 3-lite confirmation: fresh drafts, independent judge, order-only guard (registered before running)

## Why

Phase 3-lite (run 45187839933) read "mixed", and a decomposition (run
45227758150) found the gain is all card quality. Two problems surfaced after
the results:

1. **The guard was misnamed.** PHASE3LITE.md calls it "rank regret" but
   defines it as compare.change, which reads SD regret (pick field 3). SD
   regret penalizes a head that spaces its scores differently, and the blend
   changes the spacing by construction (found 2026-11-22 for the learned
   model). Read post hoc on the eval (p3_checks.py, reports/p3checks.md):
   - blend-1: SD regret +3.0 SEs, rank regret +1.2, missed top +1.2;
   - gihwr-only: rank regret +2.5.

   That reading was made after seeing the results, so it decides nothing.
2. **The judge shares the heads' ratings.** The heads pick and build with the
   same held-out ratings that grade their decks. A head that maximizes rated
   deck quality can profit from noise in those ratings, and the judge can't
   tell.

This run fixes both, on drafts the earlier runs never used.

## Design

- **Drafts:** a fresh salt `p3c1`, the first 500 per set, all 19 sets.
- **Ratings:** fold_ratings.py splits each set's games, less the 3000 sampled
  drafts', into two halves by a hash of the draft ID.
  - Half A drives every advisor: its picks, its replay on the drafter's
    pool, and Suggest Deck's builds.
  - Half B is the judge: each simulated deck is graded on B's ratings.

  Only card quality reads ratings, so the other terms stay. Half-size ratings
  are noisier than the app's, which makes this test harder on a head that
  chases noise, not easier.
- **Heads:**
  - main;
  - blend-1, λ = 1 as tuned, unchanged;
  - gihwr-only, the reference that should read worse on the guard.

  Each replays on the drafter's own pool (for regret) and drafts the packs
  itself (for the deck), all through p3_decomp.py.
- **Combining:** paired by draft; set means; an equal-weight mean over the
  19 sets with SE = √(Σ SE²)/19, as before. Regret uses compare.change's
  method (event wins per +1 SD within set, controls for set, skill bucket
  with the fixed bins, and games) with a draft-bootstrap SE.

## Outcomes

- **Primary:** blend-1 minus main, simulated deck win rate on half-B
  ratings (win-rate points).
- **Guard:** rank regret (pick field 2) change, blend-1 minus main. Positive
  is worse.
- **Also reported, no rule:**
  - the same gain on half-A ratings, and the share of it that survives on B;
  - the decomposition on B;
  - missed top;
  - SD regret, as the old guard computed it;
  - gihwr-only on every measure;
  - the deck facts.

## Decision

- **confirmed:** primary ≥ 3 SEs AND rank regret change < 3 SEs (not
  worse by 3 SEs or more).
- **not confirmed:** primary < 2 SEs. Most of the gain was rating noise,
  whatever the guard says.
- **mixed:** anything else.

If gihwr-only does not read worse than main on rank regret (+2 SEs or more),
the report says the guard had too little power to see a known-worse head here.
The decision still stands as written.

## What each outcome means for the PRs

- **confirmed:** the deck-value term earns a real-code PR stack (helper,
  module, wiring). The wiring PR still needs its own measurement with the
  real code.
- **not confirmed:** drop the deck-value scorer. The simulated measure (PR #0)
  stays useful.
- **mixed:** hold, and say which part failed.

## Rerun with copy-counted ratings (registered 2026-11-24, before running)

Run 45259059583 built both rating halves by counting a card once per game it
was in hand. 17Lands counts copies: two copies in hand count twice for GIH WR,
and GNS WR counts each copy left in the deck that was neither in hand nor
tutored. A review of the holdout tool (upstream PR 284) found this; on FDN the
copy count sits closer to the app's dataset (GNS WR off by 0.29 points RMS
instead of 0.58, GIH WR by 0.28 instead of 0.32).

The rerun changes one thing: fold_ratings.py counts copies. The drafts (salt
p3c1), the halves, the heads, the outcomes and the decision rule are the same.

- **holds:** the rule above reads "confirmed" again. The earlier verdict
  stands, and the copy-counted numbers replace it.
- **does not hold:** the rule reads anything else. The earlier "confirmed" is
  withdrawn, and the PR stack waits.

Both reports are kept: reports/p3confirm.md (once per game) and
reports/p3confirm-copies.md.
