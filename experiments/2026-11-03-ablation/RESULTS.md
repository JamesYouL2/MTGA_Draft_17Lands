# One-factor ablation results — November 3, 2026

Baseline application: `99dc21e1c894d03ce155cdc494063c3d5c93b358` (cache, format and hybrid fixes).
18 pick ablations on 10,000 drafts; 7 deck-score ablations on 1,000 final pools; ten sets, frozen inputs, one factor at a time.

## Pick scoring

Differences are percentage points for agreement and event wins per SD for regret. Parentheses show paired bootstrap SEs.

| Variant / result branch | Δ top-1 (SE) | Δ strong top-1 | Δ regret slope (SE) | Δ fixed-normalizer slope (SE) |
|---|---:|---:|---:|---:|
| [no-composition](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-composition-20261103) | +1.455 (0.044) | +1.907 | +0.0006 (0.0050) | +0.0448 (0.0197) |
| [no-curve-heavy](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-curve-heavy-20261103) | +0.235 (0.017) | +0.268 | -0.0022 (0.0024) | +0.0146 (0.0123) |
| [no-creature-quota](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-creature-quota-20261103) | +0.009 (0.006) | +0.027 | +0.0002 (0.0006) | +0.0008 (0.0012) |
| [no-artifact-synergy](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-artifact-synergy-20261103) | +0.000 (0.000) | +0.000 | +0.0000 (0.0000) | +0.0000 (0.0000) |
| [no-graveyard-synergy](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-graveyard-synergy-20261103) | +0.000 (0.000) | +0.000 | +0.0000 (0.0000) | +0.0000 (0.0000) |
| [no-counters-synergy](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-counters-synergy-20261103) | +0.000 (0.000) | +0.000 | +0.0000 (0.0000) | +0.0000 (0.0000) |
| [no-fixing-hunger](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-fixing-hunger-20261103) | +0.863 (0.026) | +1.093 | +0.0028 (0.0034) | +0.0370 (0.0147) |
| [no-bomb-fixing](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-bomb-fixing-20261103) | -0.003 (0.001) | -0.003 | +0.0004 (0.0002) | +0.0005 (0.0003) |
| [no-premium-fixing](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-premium-fixing-20261103) | -0.103 (0.011) | -0.134 | +0.0001 (0.0015) | -0.0020 (0.0052) |
| [no-removal-need](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-removal-need-20261103) | -0.001 (0.010) | +0.027 | -0.0011 (0.0011) | -0.0018 (0.0018) |
| [no-removal-saturation](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-removal-saturation-20261103) | +0.359 (0.018) | +0.442 | -0.0004 (0.0019) | +0.0056 (0.0039) |
| [no-early-plays](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-early-plays-20261103) | +0.079 (0.013) | +0.130 | +0.0003 (0.0015) | -0.0005 (0.0022) |
| [no-power-bonus](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-power-bonus-20261103) | -0.810 (0.050) | -1.177 | +0.0015 (0.0062) | +0.0985 (0.0236) |
| [no-iwd](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-iwd-20261103) | -0.091 (0.009) | -0.137 | -0.0002 (0.0005) | -0.0002 (0.0006) |
| [no-lane-boost](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-lane-boost-20261103) | -0.587 (0.020) | -0.581 | +0.0042 (0.0020) | +0.0021 (0.0072) |
| [no-archetype](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-archetype-20261103) | -0.591 (0.038) | -0.688 | +0.0121 (0.0044) | +0.0901 (0.0359) |
| [no-shrinkage](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-shrinkage-20261103) | -0.015 (0.006) | -0.036 | +0.0005 (0.0010) | +0.0008 (0.0017) |
| [no-castability](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-castability-20261103) | -8.630 (0.088) | -8.604 | +0.0875 (0.0215) | +0.1789 (0.0269) |

## Live deck ranking

Every baseline first displayed build was checked against live suggest_deck(). The variants reuse the same candidate builds and MC draws.

Of 1,000 sampled pools, 998 produced decks and enter the paired screen. Two produced no builds and are recorded in manifest.json.

| Variant / result branch | First build changed | Fixing-deficit builds, base → head | Δ score/wins slope (SE) |
|---|---:|---:|---:|
| [no-mc-color](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-mc-color-20261103) | 5.01% | 0.20% → 0.10% | +0.0695 (0.0528) |
| [no-mc-screw](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-mc-screw-20261103) | 0.00% | 0.20% → 0.20% | +0.0000 (0.0000) |
| [no-mc-flood](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-mc-flood-20261103) | 71.94% | 0.20% → 0.00% | +0.0206 (0.0204) |
| [no-mc-all](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-mc-all-20261103) | 76.35% | 0.20% → 0.00% | +0.0989 (0.0569) |
| [no-two-color-bonus](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-two-color-bonus-20261103) | 20.34% | 0.20% → 0.20% | +0.0107 (0.0197) |
| [no-domain-bonus](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-domain-bonus-20261103) | 0.10% | 0.20% → 0.20% | -0.0010 (0.0011) |
| [no-fixing-penalty](https://github.com/JamesYouL2/MTGA_Draft_17Lands/tree/exp/ablate-no-fixing-penalty-20261103) | 0.00% | 0.20% → 0.20% | -0.0014 (0.0014) |

## Interpretation and coverage

- No synergy_* tags occur in any frozen snapshot. The three synergy-rule ablations are therefore unexercised, not evidence against synergy as a concept.
- Own-pack and fixed-baseline-pack regret normalizations can disagree. Treat such disagreements as sensitivity, not proof of a wins gain.
- This is an exploratory paired screen using format-wide ratings, not causal evaluation or a chronological holdout. No variant is automatically approved for merging.
- Confirm promising simplifications on fresh data. A neutral small-sample result is not an equivalence test.
- Generated-deck results do not establish effects on arbitrary manual deck builds or on other event formats.

Each experiment branch contains its single application-source edit, EXPERIMENT_RESULT.md and experiment-result.json. Shared harness, all reports and provenance remain in this index branch.

Reproduce with Tools/Ablations/README.md. Raw input snapshots and output rows are archived separately; exact input/output hashes and validation counts are in manifest.json.
Public data: 17Lands, CC BY 4.0, https://www.17lands.com/public_datasets.
