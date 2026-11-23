## Phase 2a: within-deck draw effects, 20 sets

| set | games | M1 games | M1 decks | rated share (held-out) | reliability r | pass 1 s | pass 2 s |
|---|---|---|---|---|---|---|---|
| BLB | 931230 | 783378 | 163001 | 1.000 | 0.971 | 62 | 84 |
| Cube_-_Powered | 266117 | 227001 | 48362 | 0.998 | 0.916 | 58 | 74 |
| DFT | 857667 | 733461 | 151701 | 1.000 | 0.974 | 60 | 83 |
| DMU | 947395 | 904800 | 190124 | 1.000 | 0.967 | 131 | 167 |
| DSK | 1011949 | 864010 | 178390 | 1.000 | 0.971 | 116 | 149 |
| EOE | 563418 | 473717 | 104434 | 0.999 | 0.966 | 95 | 115 |
| FDN | 791159 | 670739 | 139181 | 0.999 | 0.965 | 75 | 101 |
| FIN | 769659 | 655584 | 141570 | 0.998 | 0.960 | 79 | 122 |
| FRA | 431627 | 374454 | 81700 | 0.998 | 0.958 | 52 | 66 |
| HOB | 323114 | 281232 | 58921 | 0.999 | 0.956 | 25 | 36 |
| LTR | 980485 | 830858 | 171746 | 1.000 | 0.982 | 138 | 169 |
| MH3 | 767772 | 655041 | 135511 | 0.998 | 0.959 | 102 | 153 |
| MSH | 377514 | 328721 | 69483 | 0.997 | 0.954 | 54 | 68 |
| NEO | 630450 | 542750 | 111788 | 1.000 | 0.964 | 49 | 69 |
| OTJ | 1172393 | 999796 | 207681 | 0.999 | 0.960 | 146 | 196 |
| PIO | 301821 | 256905 | 52969 | 0.988 | 0.908 | 64 | 77 |
| SOS | 582914 | 484329 | 106945 | 0.998 | 0.959 | 80 | 104 |
| TDM | 552428 | 460699 | 101703 | 0.999 | 0.969 | 64 | 80 |
| TLA | 562924 | 481425 | 103601 | 0.998 | 0.968 | 78 | 99 |
| TMT | 180204 | 154879 | 32620 | 0.996 | 0.933 | 16 | 22 |
| all | 13002240 | 11163779 | 2351431 | | 0.961 (Q-weighted) | | |

Sanity: β_Q (win probability per seen z unit) M0 +0.02747 (0.00013) +203.6 SEs; M1 +0.02497 (0.00019) +132.8 SEs -> passes.

### Terms (win probability per unit seen; points per card = β/β_Q × 12/23; disattenuated = × r̄ 0.961)

| term | model | β (SE) SEs | sets +/− | pts per card (SE) | disattenuated | pts per E1 deck SD (raw / dis.) |
|---|---|---|---|---|---|---|
| (d) best-five seen | M1 | +0.00826 (0.00030) +27.3 | 20/0 | +0.173 (0.007) | +0.166 |  |
| (b) creatures | M1 | +0.00612 (0.00022) +28.4 | 19/1 | +0.128 (0.005) | +0.123 | +0.34 / +0.33 |
| (c) removal | M1 | -0.01312 (0.00025) -53.5 | 0/20 | -0.274 (0.005) | -0.263 | -0.66 / -0.63 |
| cheap (E1 def.) | M1 | +0.01726 (0.00020) +84.9 | 20/0 | +0.361 (0.005) | +0.347 | +0.87 / +0.84 |
| (e) splash-color spells | M1 | -0.01139 (0.00050) -22.9 | 2/18 | -0.238 (0.010) | -0.229 |  |
| (e) off-color spells | M1 | -0.00528 (0.00091) -5.8 | 6/14 | -0.110 (0.019) | -0.106 |  |
| (e) ≤1 land in hand | M1 | -0.07747 (0.00400) -19.4 | 1/19 | -1.619 (0.085) | -1.556 |  |
| (e) 2 lands | M1 | -0.04532 (0.00044) -102.1 | 1/19 | -0.947 (0.012) | -0.910 |  |
| (e) 4 lands | M1 | -0.03091 (0.00048) -64.7 | 0/20 | -0.646 (0.011) | -0.621 |  |
| (e) ≥5 lands | M1 | -0.09772 (0.00273) -35.8 | 0/20 | -2.041 (0.058) | -1.962 |  |
| unrated spells | M1 | -0.02730 (0.00261) -10.4 | 2/18 | -0.570 (0.055) | -0.548 |  |
| on the play | M1 | +0.05507 (0.00033) +166.9 | 20/0 | +1.151 (0.011) | +1.106 |  |
| (d') best-five slope T | M2 | +0.00957 (0.00048) +19.8 | 20/0 | +0.190 (0.012) | +0.183 |  |
| (d') weakest-five slope L | M2 | -0.00597 (0.00049) -12.3 | 0/20 | -0.119 (0.008) | -0.114 |  |
| (d'') convex Q2 | M3 | +0.00430 (0.00011) +38.7 | 20/0 | +0.082 (0.002) | +0.078 |  |
| (f) 2-drop creature in hand | M4 | +0.03642 (0.00051) +72.1 | 20/0 | +0.760 (0.012) | +0.731 |  |

### Rule 1: top-heavy within a deck

- B5 +0.00826 (0.00030) +27.3 SEs; premium +0.33 (0.01) z units per seen best-five copy, disattenuated +0.32 (rule: ≥ 3 SEs and ≥ 0.5) -> **not top-heavy**.
- Slope per z unit relative to a middle card (M2): best five 1.36 (0.02), weakest five 0.77 (0.02). E1: best five 7.7 (0.4), weakest five 2.7.
- ρ (within-deck extra slope / E1's) 0.05 (0.01) -> mostly confound.
- Convex Q2 (M3) +0.00430 (0.00011) +38.7 SEs.

### Rules 2 and 3: creatures, removal (and cheap) against E1

| term | within pts/card (SE) | dis. | pts per E1 SD (raw / dis.) | Rule 2 | E1 joint pts/card (SE) | ρ (SE) | Rule 3 | ρ dis. | Rule 3 dis. | E1 flip pts/unit |
|---|---|---|---|---|---|---|---|---|---|---|
| (b) creatures | +0.128 (0.005) | +0.123 | +0.34 / +0.33 | not shown | +0.193 (0.035) | 0.66 (0.12) | partly confound | 0.64 (0.12) | partly confound | +0.28 |
| (c) removal | -0.274 (0.005) | -0.263 | -0.66 / -0.63 | negative value | +0.196 (0.046) | -1.40 (0.33) | mostly confound | -1.34 (0.32) | mostly confound | +0.22 |
| cheap (E1 def.) | +0.361 (0.005) | +0.347 | +0.87 / +0.84 | – | +0.076 (0.048) | 4.75 (2.99) | unclear | 4.56 (2.87) | unclear | +0.06 |

### Draws versions (D1 with seen-count dummies, D0 without) and in-sample ratings (S1), points per card

| term | M1 | S1 (app ratings) | D1 | D0 | flag |
|---|---|---|---|---|---|
| (d) best-five seen | +0.173 (0.007) | +0.148 (0.007) | +0.219 (0.007) | +0.411 (0.006) |  |
| (b) creatures | +0.128 (0.005) | +0.137 (0.005) | +0.051 (0.004) | +0.304 (0.002) |  |
| (c) removal | -0.274 (0.005) | -0.269 (0.005) | +0.097 (0.004) | +0.318 (0.003) | sign flips at ≥3 SEs |
| cheap (E1 def.) | +0.361 (0.005) | +0.354 (0.005) | -0.060 (0.004) | -0.033 (0.003) | sign flips at ≥3 SEs |
| (e) splash-color spells | -0.238 (0.010) | -0.238 (0.010) | +0.042 (0.009) | +0.084 (0.007) | sign flips at ≥3 SEs |
| (e) off-color spells | -0.110 (0.019) | -0.114 (0.019) | -0.004 (0.026) | -0.225 (0.013) |  |

β_Q: S1 +0.02559 (0.00019), D1 +0.02940 (0.00019), D0 +0.02523.

Lands seen instead of a spell (D1): -0.03174 (0.00021) -148.0 SEs = -0.563 points per card.

### Value-function form (PHASE2A.md's decision rule)

V = deck score − 0.229 × S

- (e) splash-color spells: -0.229 points per copy
