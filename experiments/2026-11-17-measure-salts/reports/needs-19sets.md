# Spread between salts against the bootstrap

phi = sqrt(Q / df): how many times the bootstrap SEs the estimates spread (1 is what the bootstrap expects), with 95% intervals from chi-square. Salt level: the salts' estimates over all sets (salts - 1 df). Set level: within each set across its salts, summed over sets.

| head | measure | salt-level phi | set-level phi (df) | combined (corrected SE) | bootstrap-only SE | tau |
|---|---|---|---|---|---|---|
| 2drops-cap-1.25 | regret | 2.56 (1.45 to 9.55) | 1.11 (0.94 to 1.36) (57) | -0.0000 (0.0001) | 0.0000 | 0.0002 |
| 2drops-cap-1.25 | swap | 0.29 (0.17 to 1.10) | 0.96 (0.81 to 1.17) (57) | +0.097 (0.054) | 0.054 | 0.000 |
| no-needs-2drops | regret | 2.13 (1.21 to 7.93) | 1.14 (0.97 to 1.40) (57) | -0.0003 (0.0002) | 0.0001 | 0.0004 |
| no-needs-2drops | swap | 1.38 (0.78 to 5.16) | 1.15 (0.98 to 1.41) (57) | +0.043 (0.036) | 0.025 | 0.049 |

Pooled over heads (heads share drafts and ratings, so these intervals are too narrow):

- three candidates, regret: salt level 2.35 (1.52 to 5.18); set level 1.13 (1.00 to 1.30)
- three candidates, swap: salt level 1.00 (0.64 to 2.20); set level 1.06 (0.94 to 1.22)
- all four, regret: salt level 2.35 (1.52 to 5.18); set level 1.13 (1.00 to 1.30)
- all four, swap: salt level 1.00 (0.64 to 2.20); set level 1.06 (0.94 to 1.22)

## Per salt

- 2drops-cap-1.25, regret: needs1: -0.0003 (0.0001), needs2: -0.0001 (0.0001), needs3: +0.0002 (0.0001), needs4: +0.0002 (0.0001)
- 2drops-cap-1.25, swap: needs1: +0.127 (0.107), needs2: +0.112 (0.112), needs3: +0.100 (0.118), needs4: +0.056 (0.100)
- no-needs-2drops, regret: needs1: -0.0007 (0.0002), needs2: -0.0006 (0.0002), needs3: +0.0001 (0.0002), needs4: +0.0001 (0.0002)
- no-needs-2drops, swap: needs1: +0.059 (0.049), needs2: +0.124 (0.057), needs3: +0.051 (0.049), needs4: -0.050 (0.049)

## Set-level phi by set

| head | measure | BLB | DFT | DMU | DSK | EOE | FDN | FIN | FRA | HOB | KTK | LTR | MSH | NEO | OTJ | SNC | SOS | TDM | TLA | TMT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2drops-cap-1.25 | regret | 1.16 | 0.83 | 1.44 | 0.71 | 1.18 | 1.67 | 0.82 | 1.72 | 1.52 | 0.89 | 0.81 | 1.60 | 1.27 | 0.56 | 0.79 | 0.51 | 0.91 | 0.62 | 0.90 |
| 2drops-cap-1.25 | swap | 1.13 | 0.96 | 0.27 | 0.55 | 0.41 | 0.55 | 0.87 | 1.12 | 0.85 | 0.74 | 0.63 | 0.98 | 1.47 | 1.26 | 1.71 | 0.64 | 0.58 | 0.75 | 1.32 |
| no-needs-2drops | regret | 1.41 | 0.97 | 0.86 | 1.10 | 1.50 | 1.38 | 0.89 | 1.29 | 1.84 | 0.69 | 0.93 | 1.58 | 1.64 | 0.31 | 1.05 | 0.51 | 1.34 | 0.32 | 0.32 |
| no-needs-2drops | swap | 2.36 | 0.70 | 1.21 | 0.49 | 0.73 | 0.80 | 0.73 | 1.18 | 1.34 | 0.68 | 1.26 | 0.54 | 0.90 | 0.75 | 1.62 | 0.80 | 1.26 | 0.97 | 1.77 |

