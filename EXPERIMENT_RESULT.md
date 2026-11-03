# Ablation: no-removal-need

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

10,000 drafts; 387,075 scored choices across ten sets.

| Metric | Baseline | Ablation | Difference (paired SE) |
|---|---:|---:|---:|
| Top-1 agreement, all (%) | 47.161 | 47.160 | -0.001 (0.010) |
| Top-1 agreement, strong (%) | 50.345 | 50.373 | +0.027 |
| Top-3 agreement, all (%) | 80.575 | 80.572 | -0.002 |
| Wins per SD regret | -0.2806 | -0.2817 | -0.0011 (0.0011) |
| Wins per SD fixed_regret | -0.2806 | -0.2824 | -0.0018 (0.0018) |

Changed top recommendation: 0.725% of choices.

More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.
`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.

| Set | Top-1 difference (points) |
|---|---:|
| DFT | -0.029 |
| FDN | +0.155 |
| FIN | +0.013 |
| FRA | -0.051 |
| HOB | +0.000 |
| MSH | -0.100 |
| SOS | +0.013 |
| TDM | -0.005 |
| TLA | -0.024 |
| TMT | +0.016 |

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
