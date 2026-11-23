## E3 skill-confound control (PROTOCOL.md addendum, 2026-11-22)

a − b, event wins per disagreement: estimate (scaled SE) SEs. Neither: neither top card maindecked. Complement: at least one was. Reading on M4.

### lgbm-strong-noalsa

351172 events; disagreement picks a, b, c: neither [580590, 306680, 1075326] (42.5%), complement [1453766, 670501, 529058]; events whose split doesn't add up to took: 0

| model | full | neither | neither / full | complement | verdict |
|---|---|---|---|---|---|
| M0 | +0.0150 (0.0028) +5.3 | +0.0163 (0.0064) +2.6 | 109% | +0.0151 (0.0035) +4.3 | (M0, not read) |
| M4 | +0.0306 (0.0028) +10.8 | +0.0293 (0.0059) +5.0 | 96% | +0.0314 (0.0035) +8.9 | confound |

### lgbm-weak

117067 events; disagreement picks a, b, c: neither [207037, 113115, 390268] (41.9%), complement [525782, 261183, 197876]; events whose split doesn't add up to took: 0

| model | full | neither | neither / full | complement | verdict |
|---|---|---|---|---|---|
| M0 | +0.0121 (0.0046) +2.6 | +0.0175 (0.0089) +2.0 | 144% | +0.0099 (0.0065) +1.5 | (M0, not read) |
| M4 | +0.0361 (0.0047) +7.6 | +0.0344 (0.0088) +3.9 | 95% | +0.0368 (0.0061) +6.1 | confound |

### gihwr-only

351172 events; disagreement picks a, b, c: neither [275869, 594791, 1778613] (47.9%), complement [609537, 1619123, 657494]; events whose split doesn't add up to took: 0

| model | full | neither | neither / full | complement | verdict |
|---|---|---|---|---|---|
| M0 | -0.0370 (0.0027) -13.5 | -0.0427 (0.0052) -8.2 | 116% | -0.0322 (0.0029) -10.9 | (M0, not read) |
| M4 | -0.0475 (0.0032) -14.7 | -0.0377 (0.0052) -7.3 | 79% | -0.0522 (0.0034) -15.4 | confound |

