# Ablation: no-castability

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

10,000 drafts; 387,075 scored choices across ten sets.

| Metric | Baseline | Ablation | Difference (paired SE) |
|---|---:|---:|---:|
| Top-1 agreement, all (%) | 47.161 | 38.531 | -8.630 (0.088) |
| Top-1 agreement, strong (%) | 50.345 | 41.741 | -8.604 |
| Top-3 agreement, all (%) | 80.575 | 74.400 | -6.175 |
| Wins per SD regret | -0.2806 | -0.1931 | +0.0875 (0.0215) |
| Wins per SD fixed_regret | -0.2806 | -0.1017 | +0.1789 (0.0269) |

Changed top recommendation: 33.737% of choices.

More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.
`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.

| Set | Top-1 difference (points) |
|---|---:|
| DFT | -8.951 |
| FDN | -11.344 |
| FIN | -9.579 |
| FRA | -7.356 |
| HOB | -10.544 |
| MSH | -6.813 |
| SOS | -10.487 |
| TDM | -1.274 |
| TLA | -8.882 |
| TMT | -11.175 |

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
