# Ablation: no-fixing-hunger

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

10,000 drafts; 387,075 scored choices across ten sets.

| Metric | Baseline | Ablation | Difference (paired SE) |
|---|---:|---:|---:|
| Top-1 agreement, all (%) | 47.161 | 48.024 | +0.863 (0.026) |
| Top-1 agreement, strong (%) | 50.345 | 51.438 | +1.093 |
| Top-3 agreement, all (%) | 80.575 | 80.682 | +0.108 |
| Wins per SD regret | -0.2806 | -0.2778 | +0.0028 (0.0034) |
| Wins per SD fixed_regret | -0.2806 | -0.2436 | +0.0370 (0.0147) |

Changed top recommendation: 3.911% of choices.

More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.
`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.

| Set | Top-1 difference (points) |
|---|---:|
| DFT | +1.408 |
| FDN | +1.014 |
| FIN | +1.097 |
| FRA | +0.554 |
| HOB | +1.123 |
| MSH | +1.238 |
| SOS | +0.631 |
| TDM | +0.021 |
| TLA | +0.795 |
| TMT | +0.754 |

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
