# Ablation: no-power-bonus

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

10,000 drafts; 387,075 scored choices across ten sets.

| Metric | Baseline | Ablation | Difference (paired SE) |
|---|---:|---:|---:|
| Top-1 agreement, all (%) | 47.161 | 46.351 | -0.810 (0.050) |
| Top-1 agreement, strong (%) | 50.345 | 49.168 | -1.177 |
| Top-3 agreement, all (%) | 80.575 | 79.999 | -0.575 |
| Wins per SD regret | -0.2806 | -0.2791 | +0.0015 (0.0062) |
| Wins per SD fixed_regret | -0.2806 | -0.1821 | +0.0985 (0.0236) |

Changed top recommendation: 11.656% of choices.

More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.
`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.

| Set | Top-1 difference (points) |
|---|---:|
| DFT | -1.569 |
| FDN | -0.619 |
| FIN | -0.982 |
| FRA | -0.818 |
| HOB | -0.721 |
| MSH | -0.754 |
| SOS | -0.715 |
| TDM | -1.223 |
| TLA | -0.539 |
| TMT | -0.143 |

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
