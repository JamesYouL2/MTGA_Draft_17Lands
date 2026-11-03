# All-set validation of three composition rules

This follow-up holds the application at
`99dc21e1c894d03ce155cdc494063c3d5c93b358` and separately disables fixing hunger,
removal saturation and the heavy-curve penalty. The analysis specification was
committed before validation outcomes were examined; see PROTOCOL.md.

The rating catalog is the publisher's `manifest.json`. Inventory every set,
then require a matching public draft/outcome export for the same event format.
PremierDraft is preferred. QuickDraft-only ratings are not silently applied to
PremierDraft players. The cube's documented export alias is `Cube_-_Powered`.
Unavailable sets remain in the coverage report with their reason.

Sample 3,000 fresh drafts per eligible set, excluding the 10,000 IDs in the
original experiment archive. `prepare.py` streams the raw CSV prefix to select
whole drafts before parsing selected card columns. Quoted card names remain
handled by the CSV parser. Source files are downloaded atomically; ratings are
checked against the frozen publisher checksum. Input/source/sample hashes and
exact export columns are retained in per-set receipts.

```sh
python Tools/PenaltyValidation/prepare.py \
  --data /tmp/penalty-validation-data --manifest /tmp/manifest.json \
  --exclude /tmp/original-draft-ids.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python Tools/PenaltyValidation/evaluate.py \
  --data /tmp/penalty-validation-data --out /tmp/penalty-validation-results --wait
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python Tools/PenaltyValidation/report.py \
  --data /tmp/penalty-validation-data --out /tmp/penalty-validation-results \
  --reports experiments/2026-11-03-all-set-validation
python -m pytest Tools/PenaltyValidation/tests
```

`--manifest` is a saved byte-for-byte copy of
https://unrealities.github.io/MTGA_Draft_17Lands/manifest.json.
`--exclude` is a JSON object mapping set code to the original sampled draft IDs;
the original public-input archive contains those drafts. Preserve this exclusion
file with validation inputs. Do not reuse caches with another input snapshot,
sample size, exclusion list, protocol, or source baseline.

Unchanged-baseline trace preparation can use four processes and overlap data
preparation. Each of the three ablation runs starts after the preceding one
finishes. No source edits are stacked. A target rule's removal can only change
cards for which it supplied the first returned composition multiplier; the fast
path then evaluates the actual edited method to preserve all later fallthrough.
Synthetic tests and 100 actual edited-engine pack comparisons per set/rule
validate this scoring path. Existing baseline trace validation also checks every
original ablation on 40 real packs per set.

Primary analysis uses the first strict disagreement in each draft, selected
without examining the human's choice or result. The outcome comparison keeps
humans who selected one of the two alternatives and completed the event.
Five-fold nuisance fits adjust recorded game wins/games for measured context;
all scoring is out of fold. Results include unadjusted rates, simultaneous
confidence intervals, set-cluster intervals, per-set results, newly added sets,
overlap diagnostics and event-average-win-fraction sensitivity.

This does **not** measure the win rate of playing a changed drafting policy.
Choice is not randomized, player IDs are unavailable, ratings/skill summaries
may include validation games, and humans make subsequent picks and builds.
These limits remain even with all available sets or a narrow confidence
interval. A rule is not deleted by this branch. See PROTOCOL.md for the exact
estimand and the prospective experiment needed to establish actual strength.

Public data: 17Lands, CC BY 4.0,
https://www.17lands.com/public_datasets.
