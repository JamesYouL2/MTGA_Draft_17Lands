# Ablation: no-lane-boost

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

10,000 drafts; 387,075 scored choices across ten sets.

| Metric | Baseline | Ablation | Difference (paired SE) |
|---|---:|---:|---:|
| Top-1 agreement, all (%) | 47.161 | 46.574 | -0.587 (0.020) |
| Top-1 agreement, strong (%) | 50.345 | 49.764 | -0.581 |
| Top-3 agreement, all (%) | 80.575 | 80.181 | -0.393 |
| Wins per SD regret | -0.2806 | -0.2763 | +0.0042 (0.0020) |
| Wins per SD fixed_regret | -0.2806 | -0.2785 | +0.0021 (0.0072) |

Changed top recommendation: 2.348% of choices.

More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.
`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.

| Set | Top-1 difference (points) |
|---|---:|
| DFT | -0.442 |
| FDN | -0.748 |
| FIN | -0.636 |
| FRA | -0.487 |
| HOB | -0.682 |
| MSH | -0.572 |
| SOS | -0.705 |
| TDM | -0.379 |
| TLA | -0.645 |
| TMT | -0.574 |

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
