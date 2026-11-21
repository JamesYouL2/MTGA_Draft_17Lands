# Spread between salts against the bootstrap

phi = sqrt(Q / df): how many times the bootstrap SEs the estimates spread (1 is what the bootstrap expects), with 95% intervals from chi-square. Salt level: the salts' estimates over all sets (salts - 1 df). Set level: within each set across its salts, summed over sets.

| head | measure | salt-level phi | set-level phi (df) | combined (corrected SE) | bootstrap-only SE | tau |
|---|---|---|---|---|---|---|
| lane-share-0.10 | regret | 0.88 (0.59 to 1.80) | 1.01 (0.87 to 1.21) (70) | -0.0012 (0.0009) | 0.0009 | 0.0000 |
| lane-share-0.10 | swap | 1.05 (0.70 to 2.15) | 0.97 (0.83 to 1.16) (70) | +0.034 (0.013) | 0.012 | 0.011 |
| no-needs-2drops | regret | 0.68 (0.45 to 1.39) | 0.96 (0.83 to 1.16) (70) | -0.0003 (0.0001) | 0.0001 | 0.0000 |
| no-needs-2drops | swap | 0.85 (0.56 to 1.73) | 0.98 (0.84 to 1.17) (70) | +0.090 (0.037) | 0.037 | 0.000 |
| noise20 | regret | 1.02 (0.67 to 2.07) | 1.05 (0.90 to 1.26) (70) | +0.0025 (0.0011) | 0.0011 | 0.0006 |
| noise20 | swap | 0.92 (0.61 to 1.87) | 0.91 (0.78 to 1.09) (70) | -0.037 (0.005) | 0.005 | 0.000 |
| wheel-0.15 | regret | 0.90 (0.59 to 1.82) | 1.04 (0.89 to 1.25) (70) | -0.0004 (0.0001) | 0.0001 | 0.0000 |
| wheel-0.15 | swap | 0.87 (0.58 to 1.77) | 0.96 (0.82 to 1.15) (70) | +0.056 (0.024) | 0.024 | 0.000 |

Pooled over heads (heads share drafts and ratings, so these intervals are too narrow):

- three candidates, regret: salt level 0.83 (0.64 to 1.18); set level 1.01 (0.92 to 1.11)
- three candidates, swap: salt level 0.93 (0.71 to 1.33); set level 0.97 (0.88 to 1.07)
- all four, regret: salt level 0.88 (0.70 to 1.19); set level 1.02 (0.94 to 1.11)
- all four, swap: salt level 0.93 (0.74 to 1.25); set level 0.95 (0.88 to 1.04)

## Per salt

- lane-share-0.10, regret: ms1: -0.0010 (0.0026), ms2: -0.0015 (0.0026), ms3: -0.0024 (0.0023), ms4: -0.0042 (0.0026), ms5: -0.0034 (0.0028), ms6: +0.0025 (0.0027), ms7: +0.0017 (0.0025), ms8: -0.0013 (0.0026)
- lane-share-0.10, swap: ms1: +0.051 (0.034), ms2: +0.001 (0.036), ms3: +0.001 (0.031), ms4: +0.025 (0.035), ms5: +0.098 (0.035), ms6: +0.003 (0.034), ms7: +0.028 (0.036), ms8: +0.069 (0.032)
- no-needs-2drops, regret: ms1: -0.0003 (0.0004), ms2: -0.0005 (0.0004), ms3: -0.0006 (0.0004), ms4: -0.0005 (0.0004), ms5: -0.0001 (0.0004), ms6: -0.0006 (0.0004), ms7: +0.0000 (0.0004), ms8: +0.0001 (0.0004)
- no-needs-2drops, swap: ms1: -0.012 (0.102), ms2: +0.206 (0.115), ms3: +0.061 (0.099), ms4: +0.171 (0.102), ms5: +0.037 (0.104), ms6: +0.155 (0.103), ms7: +0.152 (0.107), ms8: -0.035 (0.109)
- noise20, regret: ms1: +0.0070 (0.0031), ms2: -0.0017 (0.0030), ms3: +0.0001 (0.0033), ms4: +0.0074 (0.0033), ms5: +0.0015 (0.0031), ms6: +0.0020 (0.0031), ms7: +0.0008 (0.0032), ms8: +0.0035 (0.0032)
- noise20, swap: ms1: -0.056 (0.013), ms2: -0.030 (0.013), ms3: -0.033 (0.014), ms4: -0.037 (0.014), ms5: -0.040 (0.014), ms6: -0.034 (0.014), ms7: -0.015 (0.015), ms8: -0.051 (0.015)
- wheel-0.15, regret: ms1: +0.0001 (0.0003), ms2: -0.0008 (0.0003), ms3: -0.0004 (0.0004), ms4: -0.0002 (0.0003), ms5: -0.0003 (0.0003), ms6: -0.0008 (0.0003), ms7: -0.0004 (0.0003), ms8: -0.0005 (0.0003)
- wheel-0.15, swap: ms1: +0.045 (0.061), ms2: +0.012 (0.072), ms3: +0.040 (0.071), ms4: +0.140 (0.069), ms5: +0.019 (0.068), ms6: +0.157 (0.069), ms7: -0.011 (0.069), ms8: +0.046 (0.069)

## Set-level phi by set

| head | measure | DFT | FDN | FIN | FRA | HOB | MSH | SOS | TDM | TLA | TMT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lane-share-0.10 | regret | 1.28 | 0.68 | 1.16 | 1.26 | 0.81 | 1.06 | 0.87 | 1.12 | 0.73 | 0.92 |
| lane-share-0.10 | swap | 0.87 | 0.46 | 0.94 | 1.55 | 1.23 | 0.74 | 1.07 | 0.94 | 0.89 | 0.45 |
| no-needs-2drops | regret | 1.27 | 0.94 | 0.61 | 0.75 | 1.10 | 0.74 | 1.26 | 0.93 | 0.72 | 1.07 |
| no-needs-2drops | swap | 1.12 | 1.30 | 0.66 | 0.52 | 1.01 | 1.22 | 1.31 | 0.77 | 0.86 | 0.61 |
| noise20 | regret | 1.13 | 0.73 | 0.63 | 1.10 | 0.98 | 1.56 | 0.55 | 1.33 | 1.27 | 0.72 |
| noise20 | swap | 1.53 | 1.21 | 0.95 | 0.56 | 0.97 | 0.93 | 0.46 | 0.73 | 0.38 | 0.78 |
| wheel-0.15 | regret | 1.02 | 0.77 | 0.99 | 0.64 | 1.02 | 1.36 | 1.21 | 1.02 | 1.24 | 0.91 |
| wheel-0.15 | swap | 1.26 | 0.86 | 1.29 | 1.07 | 0.91 | 1.06 | 0.86 | 0.59 | 0.81 | 0.56 |

# Diagnostic: drafts fixed, ratings varied

Determinism: 25 result files of the diagnostic's ms1 jobs against the main study's; 0 differ.

sigma2_r: variance of a set's estimate across the ratings salts, drafts fixed (pooled over sets). tau2: the main study's variance across salts in excess of the bootstrap (b2), same sets. Share: sigma2_r / tau2, 95% interval from resampling sets.

| head | measure | sigma2_r (df) | tau2 | b2 | share of excess from ratings |
|---|---|---|---|---|---|
| lane-share-0.10 | regret | 1.13e-06 (15) | -1.78e-06 | 6.21e-05 | n/a (no excess) |
| lane-share-0.10 | swap | 0.00067 (15) | -0.00108 | 0.0134 | n/a (no excess) |
| no-needs-2drops | regret | 6.87e-08 (15) | -4.77e-07 | 1.63e-06 | n/a (no excess) |
| no-needs-2drops | swap | 0.0405 (15) | -0.0561 | 0.18 | n/a (no excess) |
| noise20 | regret | 2.05e-06 (15) | 3.91e-05 | 9.48e-05 | 0.05 (0.01 to 1.36) |
| noise20 | swap | 0.000109 (15) | -0.000712 | 0.0019 | n/a (no excess) |
| wheel-0.15 | regret | 4.21e-08 (15) | 6.86e-08 | 1.07e-06 | 0.61 (0.07 to 1.18) |
| wheel-0.15 | swap | 0.0232 (15) | -0.0113 | 0.0477 | n/a (no excess) |

## By set

- lane-share-0.10, regret: FDN: ms1 -0.0106, ms1+rs1 -0.0117, ms1+rs2 -0.0111, ms1+rs3 -0.0111, ms1+rs4 -0.0109; FRA: ms1 +0.0024, ms1+rs1 +0.0003, ms1+rs2 +0.0019, ms1+rs3 +0.0021, ms1+rs4 +0.0026; MSH: ms1 -0.0077, ms1+rs1 -0.0093, ms1+rs2 -0.0065, ms1+rs3 -0.0047, ms1+rs4 -0.0081; TDM: ms1 -0.0056, ms1+rs1 -0.0058, ms1+rs2 -0.0061, ms1+rs3 -0.0062, ms1+rs4 -0.0054; TLA: ms1 -0.0031, ms1+rs1 -0.0036, ms1+rs2 -0.0030, ms1+rs3 -0.0047, ms1+rs4 -0.0035
- lane-share-0.10, swap: FDN: ms1 +0.161, ms1+rs1 +0.180, ms1+rs2 +0.164, ms1+rs3 +0.144, ms1+rs4 +0.134; FRA: ms1 +0.050, ms1+rs1 +0.090, ms1+rs2 +0.067, ms1+rs3 +0.047, ms1+rs4 +0.052; MSH: ms1 +0.117, ms1+rs1 +0.120, ms1+rs2 +0.101, ms1+rs3 +0.070, ms1+rs4 +0.135; TDM: ms1 +0.219, ms1+rs1 +0.127, ms1+rs2 +0.218, ms1+rs3 +0.159, ms1+rs4 +0.197; TLA: ms1 -0.104, ms1+rs1 -0.091, ms1+rs2 -0.118, ms1+rs3 -0.100, ms1+rs4 -0.093
- no-needs-2drops, regret: FDN: ms1 -0.0026, ms1+rs1 -0.0026, ms1+rs2 -0.0022, ms1+rs3 -0.0026, ms1+rs4 -0.0026; FRA: ms1 -0.0014, ms1+rs1 -0.0014, ms1+rs2 -0.0013, ms1+rs3 -0.0014, ms1+rs4 -0.0014; MSH: ms1 +0.0006, ms1+rs1 +0.0007, ms1+rs2 +0.0008, ms1+rs3 +0.0010, ms1+rs4 +0.0006; TDM: ms1 -0.0027, ms1+rs1 -0.0028, ms1+rs2 -0.0019, ms1+rs3 -0.0032, ms1+rs4 -0.0024; TLA: ms1 -0.0002, ms1+rs1 -0.0003, ms1+rs2 -0.0003, ms1+rs3 -0.0002, ms1+rs4 -0.0002
- no-needs-2drops, swap: FDN: ms1 +0.750, ms1+rs1 +0.709, ms1+rs2 +0.837, ms1+rs3 +0.694, ms1+rs4 +0.625; FRA: ms1 +0.175, ms1+rs1 +0.210, ms1+rs2 -0.126, ms1+rs3 +0.789, ms1+rs4 +0.043; MSH: ms1 +0.346, ms1+rs1 +0.458, ms1+rs2 +0.489, ms1+rs3 +0.302, ms1+rs4 +0.602; TDM: ms1 +0.081, ms1+rs1 +0.160, ms1+rs2 +0.074, ms1+rs3 +0.120, ms1+rs4 +0.198; TLA: ms1 -0.366, ms1+rs1 -0.309, ms1+rs2 -0.157, ms1+rs3 -0.184, ms1+rs4 -0.451
- noise20, regret: FDN: ms1 +0.0238, ms1+rs1 +0.0220, ms1+rs2 +0.0219, ms1+rs3 +0.0214, ms1+rs4 +0.0259; FRA: ms1 -0.0227, ms1+rs1 -0.0207, ms1+rs2 -0.0210, ms1+rs3 -0.0213, ms1+rs4 -0.0218; MSH: ms1 +0.0131, ms1+rs1 +0.0134, ms1+rs2 +0.0127, ms1+rs3 +0.0160, ms1+rs4 +0.0133; TDM: ms1 +0.0013, ms1+rs1 +0.0034, ms1+rs2 +0.0041, ms1+rs3 +0.0034, ms1+rs4 +0.0021; TLA: ms1 +0.0058, ms1+rs1 +0.0066, ms1+rs2 +0.0028, ms1+rs3 +0.0062, ms1+rs4 +0.0055
- noise20, swap: FDN: ms1 -0.080, ms1+rs1 -0.093, ms1+rs2 -0.086, ms1+rs3 -0.080, ms1+rs4 -0.104; FRA: ms1 +0.019, ms1+rs1 +0.013, ms1+rs2 +0.008, ms1+rs3 -0.014, ms1+rs4 +0.005; MSH: ms1 -0.065, ms1+rs1 -0.063, ms1+rs2 -0.079, ms1+rs3 -0.059, ms1+rs4 -0.077; TDM: ms1 -0.061, ms1+rs1 -0.069, ms1+rs2 -0.042, ms1+rs3 -0.053, ms1+rs4 -0.045; TLA: ms1 +0.001, ms1+rs1 +0.004, ms1+rs2 +0.000, ms1+rs3 +0.018, ms1+rs4 +0.005
- wheel-0.15, regret: FDN: ms1 -0.0004, ms1+rs1 -0.0007, ms1+rs2 -0.0008, ms1+rs3 -0.0004, ms1+rs4 -0.0005; FRA: ms1 -0.0012, ms1+rs1 -0.0012, ms1+rs2 -0.0013, ms1+rs3 -0.0015, ms1+rs4 -0.0018; MSH: ms1 -0.0008, ms1+rs1 -0.0006, ms1+rs2 -0.0009, ms1+rs3 -0.0012, ms1+rs4 -0.0010; TDM: ms1 +0.0008, ms1+rs1 +0.0007, ms1+rs2 +0.0009, ms1+rs3 +0.0009, ms1+rs4 +0.0012; TLA: ms1 -0.0006, ms1+rs1 -0.0007, ms1+rs2 -0.0003, ms1+rs3 -0.0005, ms1+rs4 -0.0003
- wheel-0.15, swap: FDN: ms1 +0.401, ms1+rs1 +0.319, ms1+rs2 +0.331, ms1+rs3 +0.384, ms1+rs4 +0.353; FRA: ms1 +0.319, ms1+rs1 +0.302, ms1+rs2 +0.061, ms1+rs3 +0.021, ms1+rs4 -0.049; MSH: ms1 +0.202, ms1+rs1 -0.091, ms1+rs2 -0.125, ms1+rs3 -0.250, ms1+rs4 -0.016; TDM: ms1 -0.217, ms1+rs1 -0.100, ms1+rs2 -0.233, ms1+rs3 -0.188, ms1+rs4 -0.491; TLA: ms1 +0.182, ms1+rs1 -0.074, ms1+rs2 +0.397, ms1+rs3 +0.434, ms1+rs4 +0.298

