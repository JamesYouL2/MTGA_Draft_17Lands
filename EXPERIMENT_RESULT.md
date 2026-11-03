# Ablation: no-removal-saturation

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

10,000 drafts; 387,075 scored choices across ten sets.

| Metric | Baseline | Ablation | Difference (paired SE) |
|---|---:|---:|---:|
| Top-1 agreement, all (%) | 47.161 | 47.519 | +0.359 (0.018) |
| Top-1 agreement, strong (%) | 50.345 | 50.788 | +0.442 |
| Top-3 agreement, all (%) | 80.575 | 80.690 | +0.115 |
| Wins per SD regret | -0.2806 | -0.2810 | -0.0004 (0.0019) |
| Wins per SD fixed_regret | -0.2806 | -0.2750 | +0.0056 (0.0039) |

Changed top recommendation: 1.794% of choices.

More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.
`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.

| Set | Top-1 difference (points) |
|---|---:|
| DFT | +0.231 |
| FDN | +0.338 |
| FIN | +0.338 |
| FRA | +0.638 |
| HOB | +0.436 |
| MSH | +0.336 |
| SOS | +0.244 |
| TDM | +0.197 |
| TLA | +0.363 |
| TMT | +0.466 |

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
