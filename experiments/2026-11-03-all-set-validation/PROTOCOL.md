# Three-rule validation protocol

Frozen before examining validation outcomes, November 3, 2026.
Application baseline: 99dc21e1c894d03ce155cdc494063c3d5c93b358.
Parent screen/harness: e8b8e91ca5729b48f32619e4c6ddff1d105c376c.

## Scope and sample

Test `no-fixing-hunger`, `no-removal-saturation`, and `no-curve-heavy`
individually. Baseline trace preparation may run alongside data downloads;
ablations run sequentially, with no stacked source changes.

Inventory every distinct set in the publisher's current rating manifest.
Prefer PremierDraft; use QuickDraft only when the catalog has no PremierDraft
snapshot and a matching public pick/outcome dump exists. Resolve unusual source
names against 17Lands' published public-data catalog. Record unavailable or
mismatched sources explicitly; do not silently substitute another format.

Hash sample 3,000 drafts per available set using a fresh fixed salt. Exclude all
10,000 draft IDs in the first screen, using the preserved original archive.
Use fewer if the source has fewer eligible drafts, reporting the actual count.
Keep source/snapshot/sample hashes, dates and exclusions. A disjoint sample is
not chronological independence: the rating snapshots include validation games.

## Outcomes and selection

Primary outcome evidence is recorded game wins and losses, not human-pick
agreement or a regret/wins correlation. At the first pick in each draft where
baseline and ablation have different, uniquely highest scored recommendations,
record the two alternatives and the pre-choice draft state. Select that pick
before inspecting the human's choice or event outcome. This gives at most one
observation per draft per rule. If the human took neither alternative, exclude
it from the two-choice outcome comparison and report that exclusion.

Primary outcome sample: completed best-of-one events (7 wins or 3 losses),
valid nonnegative integer wins/losses, and at least one game. Report missing or
incomplete outcomes. Compare the observed game-weighted win rates, then a
cross-fitted adjustment using set, skill/games buckets, draft phase, pool needs,
lane, candidate characteristics and baseline/ablation score margins. These
covariates are available at the logged choice; the published skill summary may
itself summarize games beyond that choice.

Five folds assigned by a stable draft-ID hash; nuisance models never train on
the observation whose adjustment they produce. Fixed histogram gradient
boosting classifiers/regressors: 150 iterations, depth 4, minimum leaf 30,
L2 penalty 10, seed 20261103. Predict treatment probability and, for each arm,
event wins and event games. Doubly robust pseudo-outcomes are aggregated as
expected wins / expected games. Report an event-average win-fraction sensitivity
analysis too. Clip propensity weights at 0.05 and 0.95; report clipping and arm
effective sample sizes, plus an overlap-only (0.1–0.9) sensitivity result.

Report adjusted differences in percentage points, positive favoring removal.
Use influence-function intervals, including intervals clustered by set, and
98.333% simultaneous intervals (Bonferroni for three tests). Player identifiers
are absent, preventing player-clustered inference. Report per-set estimates,
the earlier ten sets versus newly added sets, and unadjusted contrasts.
Use ±1 percentage point as a practical-reference band, not proof of causal
equivalence. Report cross-fitted outcome predictive error as a model diagnostic.

Secondary replication: aggregate and per-set human agreement, and the prior
own-pack/fixed-baseline-normalizer regret associations with recorded outcomes.
Never treat an improved correlation as a measured policy win-rate gain.

## What this can establish

This is observational validation among humans who chose one of two disagreeing
recommendations. There are no randomized policy assignments, logged behavior
propensities, counterfactual decks/games, or game-playing simulator. The same
human's observed wins cannot be relabelled as baseline wins versus ablation
wins. Adjustment cannot eliminate unobserved player skill, private information,
matchmaking, later picks or deck-building decisions. Selecting completed events
and the two candidate choices may also introduce selection bias.

Thus even a narrow interval favoring one arm is an adjusted association, not
proof that switching the full drafting policy changes win rate. Actual strength
confirmation requires randomizing rule-on/rule-off per draft and observing
played games, with draft-level assignment, predeclared stopping and sufficient
power. An inconclusive association must remain inconclusive.

## Data-quality amendment before outcome comparisons

The card-name audit found that the current Powered Cube rating snapshot and
its older public export have different card inventories. For the primary
comparison, require every card in the logged pack and pre-choice pool (and the
taken card) to resolve to the frozen rating inventory. Select the first strict
disagreement satisfying that requirement; record skipped incomplete states and
unmatched names by set. Report sets with no usable outcome comparisons rather
than implying that a partially mapped replay validates them. Include the logged
draft date among the adjustment covariates. These checks were added before any
validation outcome comparison was examined, based solely on input compatibility.
