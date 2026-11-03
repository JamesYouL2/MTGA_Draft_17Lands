# Ablation: no-shrinkage

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

10,000 drafts; 387,075 scored choices across ten sets.

| Metric | Baseline | Ablation | Difference (paired SE) |
|---|---:|---:|---:|
| Top-1 agreement, all (%) | 47.161 | 47.146 | -0.015 (0.006) |
| Top-1 agreement, strong (%) | 50.345 | 50.310 | -0.036 |
| Top-3 agreement, all (%) | 80.575 | 80.545 | -0.029 |
| Wins per SD regret | -0.2806 | -0.2801 | +0.0005 (0.0010) |
| Wins per SD fixed_regret | -0.2806 | -0.2797 | +0.0008 (0.0017) |

Changed top recommendation: 0.310% of choices.

More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.
`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.

| Set | Top-1 difference (points) |
|---|---:|
| DFT | +0.010 |
| FDN | -0.028 |
| FIN | +0.013 |
| FRA | -0.003 |
| HOB | +0.000 |
| MSH | -0.056 |
| SOS | -0.026 |
| TDM | -0.021 |
| TLA | +0.008 |
| TMT | -0.050 |

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
