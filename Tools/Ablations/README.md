# Sequential one-factor ablations

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
This includes the cache, draft-format and hybrid fixes; no ablation is stacked
on another. `variants.py` emits a small standalone source edit for each branch.

The screen covers 18 pick variants (all composition multipliers as a group,
each of its 11 rules, relative power, IWD premium, lane boost, archetype
weighting, archetype confidence shrinkage, and castability) and 7 deck variants
(three Monte Carlo penalties separately and together, two-color bonus, domain
bonus, and fixing penalty).

```sh
python Tools/Ablations/prepare.py --data /tmp/ablation-data --drafts 1000
python -m pytest Tools/Ablations/tests
python Tools/Ablations/run.py --data /tmp/ablation-data --out /tmp/ablation-results
python Tools/Ablations/decks.py --data /tmp/ablation-data --out /tmp/ablation-results --pools 100
OPENBLAS_NUM_THREADS=1 python Tools/Ablations/report.py --out /tmp/ablation-results --reports experiments/2026-11-03-ablation
python Tools/Ablations/package.py --data /tmp/ablation-data --out /tmp/ablation-results --reports experiments/2026-11-03-ablation --payloads /tmp/ablation-branches
```

Data preparation and unchanged-baseline trace/candidate collection may run
ahead. Each ablation is then evaluated to completion before the next one.
The same sample, frozen rating bytes, MC seed/draws and baseline are reused.
Input receipts record source URLs, SHA-256 hashes and the sampling salt.
Do not reuse a cache from a different baseline, salt or requested sample size.

Pick replay instruments the unmodified baseline's intermediate arithmetic,
then changes one factor. An independently compiled, actually edited engine is
checked against this path on 40 real packs per set per variant, in addition
to synthetic fallthrough/rounding tests. Final pool scores are omitted from
pick reports because pick-score edits do not change the deck scorer.

Deck replay captures every candidate from live `suggest_deck()`, records its
score features and MC diagnostics, and reuses the actual application ranking,
deduplication, filtering and safe-core promotion code. Every baseline first
displayed deck must match the live output. Removing a penalty recomputes the
score before clamping at zero. No deck-generation policy is changed.

Reports include paired draft bootstrap SEs (200 samples), strong-drafter
agreement, per-set agreement, and two regret normalizations. The second uses
the baseline pack SD for both models. Deck reports measure changes to the
first displayed build, fixing deficits, card quality, MC diagnostics and the
score/event-wins association.

These are observational comparative screens, not causal win improvements.
Ratings include replayed drafts, and the public sample does not identify
players for player-clustered uncertainty. The deck screen uses final draft
pools, not the actual decks the players registered. Multiple hypotheses are
screened: validate promising simplifications on a fresh/chronological sample
before merging. Safety/legality guards and the principal card-quality term
are not candidates for deletion merely because a screen is neutral.

None of the ten frozen snapshots contains `synergy_*` tags. The three synergy
ablations are unexercised in this screen; their unchanged results do not
establish that those rules are unnecessary.

Public data attribution: 17Lands public datasets, CC BY 4.0,
https://www.17lands.com/public_datasets. Rating snapshots are from the
upstream MTGA_Draft_17Lands gh-pages distribution; exact URLs are in receipts.
