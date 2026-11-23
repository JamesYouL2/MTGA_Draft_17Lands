## E3: match rate

Complete events 314089, with game rows 313730 (99.9%), scored 311624 (99.2%).

| set | complete | matched | scored |
|---|---|---|---|
| BLB | 17891 | 99.9% | 99.9% |
| DFT | 17230 | 99.9% | 99.9% |
| DMU | 21680 | 99.7% | 99.7% |
| DSK | 18300 | 99.9% | 99.9% |
| EOE | 18243 | 99.9% | 99.9% |
| FDN | 19063 | 99.9% | 99.9% |
| FIN | 18802 | 99.9% | 99.9% |
| FRA | 17938 | 99.8% | 99.8% |
| HOB | 18948 | 99.9% | 99.9% |
| LTR | 17234 | 100.0% | 100.0% |
| MSH | 18097 | 99.9% | 99.9% |
| NEO | 20492 | 99.7% | 99.7% |
| OTJ | 18184 | 99.9% | 99.9% |
| SOS | 18260 | 100.0% | 100.0% |
| TDM | 18360 | 99.9% | 99.9% |
| TLA | 17892 | 99.9% | 99.9% |
| TMT | 17475 | 99.9% | 87.9% |

## lgbm-strong-noalsa: a − b, event wins per disagreement (estimate (scaled SE) SEs)

311624 matched complete events; mean a, b, c per event: [5.632, 2.712, 4.433]

| model | controls | a − b | share of M0 |
|---|---|---|---|
| M0 | none | +0.0138 (0.0031) +4.4 | 100% |
| M1 | (a) deck score | +0.0346 (0.0031) +11.2 | 251% |
| M2 | (b) deck score parts | +0.0361 (0.0031) +11.6 | 262% |
| M3 | (c) + quality shape | +0.0319 (0.0031) +10.3 | 232% |
| M4 | + deck counts | +0.0289 (0.0031) +9.4 | 210% |
| M0g | none; outcome game win share | +0.0013 (0.0003) +4.3 | 100% |
| M4g | M4; outcome game win share | +0.0028 (0.0003) +9.5 | 220% |

## lgbm-weak: a − b, event wins per disagreement (estimate (scaled SE) SEs)

103807 matched complete events; mean a, b, c per event: [6.098, 3.138, 4.884]

| model | controls | a − b | share of M0 |
|---|---|---|---|
| M0 | none | +0.0109 (0.0048) +2.3 | 100% |
| M1 | (a) deck score | +0.0409 (0.0048) +8.6 | 376% |
| M2 | (b) deck score parts | +0.0434 (0.0048) +9.0 | 400% |
| M3 | (c) + quality shape | +0.0377 (0.0048) +7.8 | 347% |
| M4 | + deck counts | +0.0342 (0.0049) +7.0 | 315% |
| M0g | none; outcome game win share | +0.0009 (0.0005) +1.9 | 100% |
| M4g | M4; outcome game win share | +0.0031 (0.0005) +6.8 | 359% |

## gihwr-only: a − b, event wins per disagreement (estimate (scaled SE) SEs)

311624 matched complete events; mean a, b, c per event: [2.369, 6.454, 6.861]

| model | controls | a − b | share of M0 |
|---|---|---|---|
| M0 | none | -0.0433 (0.0026) -16.8 | 100% |
| M1 | (a) deck score | -0.0501 (0.0026) -19.6 | 116% |
| M2 | (b) deck score parts | -0.0589 (0.0028) -21.3 | 136% |
| M3 | (c) + quality shape | -0.0630 (0.0028) -22.8 | 146% |
| M4 | + deck counts | -0.0478 (0.0029) -16.7 | 111% |
| M0g | none; outcome game win share | -0.0038 (0.0003) -13.1 | 100% |
| M4g | M4; outcome game win share | -0.0043 (0.0003) -12.7 | 113% |
