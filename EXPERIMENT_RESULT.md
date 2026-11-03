# Ablation: no-mc-color

Frozen application baseline: `99dc21e1c894d03ce155cdc494063c3d5c93b358`.
One factor removed; all other source and inputs are held fixed.

998 real final pools. Every baseline ranking was checked against live `suggest_deck()` output.

Changed first displayed build: 5.01%.

| Metric | Baseline | Ablation |
|---|---:|---:|
| unsupported_fixing_percent | 0.2004 | 0.1002 |
| mean_quality | 0.2590 | 0.2664 |
| mean_colors | 2.0962 | 2.0972 |
| color_screw_t3 | 3.1033 | 3.5467 |
| screw_t3 | 11.1023 | 11.0849 |
| flood_t5 | 24.2446 | 24.2856 |

Wins per SD displayed score: +0.2102 → +0.2797; difference +0.0695 (paired SE 0.0528).
This describes observational score association and selection behavior, not wins gained by following a build.

## Reproduction and limits

Use Tools/Ablations with the input receipts beside this report. Public 17Lands data: CC BY 4.0, https://www.17lands.com/public_datasets.
Ratings include replayed drafts: this is a paired comparative screen, not a chronological out-of-sample test.
Uncertainty uses 200 paired draft bootstrap resamples. Multiple ablations were screened; confirm candidates on a fresh sample before shipping.
Prepared traces and cached MC draws accelerate evaluation; each ablation is evaluated separately, not stacked.
