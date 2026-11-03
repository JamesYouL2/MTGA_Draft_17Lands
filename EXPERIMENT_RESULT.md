# Ablation: no-composition

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

10,000 drafts; 387,075 scored choices across ten sets.

| Metric | Baseline | Ablation | Difference (paired SE) |
|---|---:|---:|---:|
| Top-1 agreement, all (%) | 47.161 | 48.616 | +1.455 (0.044) |
| Top-1 agreement, strong (%) | 50.345 | 52.252 | +1.907 |
| Top-3 agreement, all (%) | 80.575 | 80.972 | +0.397 |
| Wins per SD regret | -0.2806 | -0.2800 | +0.0006 (0.0050) |
| Wins per SD fixed_regret | -0.2806 | -0.2358 | +0.0448 (0.0197) |

Changed top recommendation: 10.169% of choices.

More negative regret/wins association is the existing diagnostic direction; it is not a causal wins estimate.
`fixed_regret` uses the baseline pack SD for both scores, checking sensitivity to model-specific pack normalization.

| Set | Top-1 difference (points) |
|---|---:|
| DFT | +2.236 |
| FDN | +1.653 |
| FIN | +2.079 |
| FRA | +1.182 |
| HOB | +1.533 |
| MSH | +1.482 |
| SOS | +1.338 |
| TDM | +0.138 |
| TLA | +1.171 |
| TMT | +1.751 |

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
