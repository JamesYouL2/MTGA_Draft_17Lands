# All-set validation of three pick rules

**These are adjusted observational associations, not measured policy win-rate effects.**
The available data cannot establish whether removing a rule increases or decreases actual drafting-policy strength. That requires randomized rule-on/rule-off drafts and played games.

Catalog: 27 sets. Matching ratings plus draft/outcome exports: 22 sets, 66,000 fresh drafts. Prior-screen draft IDs are excluded.

Tested sets: BLB, Cube - Powered, DFT, DMU, DSK, EOE, FDN, FIN, FRA, HOB, LTR, MH3, MID, MSH, NEO, OTJ, SOS, STX, TDM, TLA, TMT, VOW.

## Decision

None of the three rules is established to hurt win rate: all three primary intervals include zero. If removal requires a demonstrated strength improvement, retain the rules pending stronger evidence. Removal saturation is the most promising follow-up candidate; heavy curve is centered on zero. This is not evidence of equivalence. A [prospective randomized trial](../../Tools/PenaltyValidation/PROSPECTIVE_TEST.md) is required to establish the effect of switching the full drafting policy.

## Primary recorded-outcome comparison

One first strict disagreement per draft; only completed events where the human took one of the two recommendations. Positive differences favor removal. Intervals are 98.333% per comparison (95% familywise across three rules).

| Rule removed | Compared drafts / sets | Adjusted win-rate association (points) | Draft interval | Set-cluster interval | New-set association |
|---|---:|---:|---|---|---:|
| no-fixing-hunger | 16,620 / 21 | +0.56 | [-0.39, +1.52] | [-0.22, +1.35] | +0.62 |
| no-removal-saturation | 13,419 / 21 | +0.82 | [-0.26, +1.91] | [-0.45, +2.10] | +1.10 |
| no-curve-heavy | 11,746 / 21 | -0.00 | [-1.10, +1.09] | [-1.24, +1.23] | +0.35 |

## Coverage exclusions

| Set | Rating format | Reason |
|---|---|---|
| ECL | QuickDraft | HTTP 403 from public draft source |
| MKM | QuickDraft | HTTP 403 from public draft source |
| WAR | PremierDraft | HTTP 403 from public draft source |
| WOE | QuickDraft | HTTP 403 from public draft source |
| Y26FRA | PremierDraft | HTTP 403 from public draft source |

QuickDraft ratings are not substituted into PremierDraft outcome evaluation. Cube uses the export name documented in 17Lands’ public catalog.

The primary comparison requires a fully mapped pack and pre-choice pool. Current Cube ratings and the older Cube export have different inventories. Its partial replay is not evidence validating unmapped states; per-rule comparison counts show whether any usable Cube evidence remains.

## Interpretation

- Human agreement is a secondary metric. It does not measure wins gained by following a recommendation.
- The same observed human outcome cannot be assigned to both counterfactual policies. This evaluates one observed choice with subsequent human drafting/deck-building, not a full replacement policy.
- Five-fold outcome/propensity adjustment uses only out-of-fold predictions. Unmeasured skill, later decisions, matchmaking, choice selection and completed-event selection can still confound results.
- Player IDs are absent; player clustering is unavailable. The public skill bucket and rating snapshots may include the evaluated games, so this is not a fully chronological out-of-sample test.
- Full details, per-set estimates, overlap/precision diagnostics, subgroup sensitivities and raw contrasts are in summary.json. The frozen analysis specification is PROTOCOL.md.
- No application rule is removed by this validation branch. A causal strength verdict requires a prospective randomized test.

Data: 17Lands public datasets, CC BY 4.0, https://www.17lands.com/public_datasets.

<!-- agreement:start -->
## Secondary pick agreement

Differences are percentage points of top-choice agreement; this measures imitation, not win-rate effects. Per-set details are in [agreement-by-set.json](agreement-by-set.json). Cube and other incomplete card states remain in this secondary partial-replay metric; the primary outcome filter is stricter.

| Rule removed | All drafters | Strong drafters |
|---|---:|---:|
| no-fixing-hunger | +0.623 | +0.738 |
| no-removal-saturation | +0.334 | +0.378 |
| no-curve-heavy | +0.245 | +0.282 |

Familywise 95% control covers the three pooled primary contrasts. Per-set and subgroup intervals are exploratory and are not simultaneous across all subgroups. These intervals do not bound the win-rate effect of switching the full drafting policy. All matched outcome exports in this run are PremierDraft; this study does not validate effects in QuickDraft, TradDraft or PickTwoDraft.
