
# Agreement with the card taken

Share of picks where the card taken is the head's top card (top-1) or in its top 3, on the replay's held-out ratings. Change against base in points, ± its SE, paired by draft.

| head | drafters | drafts | top-1 | top-3 | top-1 vs base | top-3 vs base |
|---|---|---|---|---|---|---|
| base | all | 456000 | 46.8 | 79.9 |  |  |
| base | strong | 81765 | 50.1 | 82.5 |  |  |
| gihwr-only | all | 456000 | 37.0 | 72.6 | -9.79 ± 0.02 | -7.28 ± 0.02 |
| gihwr-only | strong | 81765 | 40.3 | 76.3 | -9.88 ± 0.04 | -6.17 ± 0.04 |
| lgbm-strong-noalsa | all | 456000 | 54.5 | 86.9 | +7.73 ± 0.01 | +7.00 ± 0.01 |
| lgbm-strong-noalsa | strong | 81765 | 57.5 | 88.8 | +7.34 ± 0.03 | +6.35 ± 0.02 |

# Event wins per swapped pick by drafter skill bucket

Head minus base, on the complete events of drafters in each 17Lands win-rate bucket, combined over salts: estimate (scaled SE), SEs. Controls as heads.py's (set, skill bucket, games bucket).

| head | skill bucket | events | event wins per swapped pick |
|---|---|---|---|
| gihwr-only | 60%+ | 74464 | -0.044 (0.006), -7.5 |
| gihwr-only | 56 to 60% | 72593 | -0.057 (0.007), -8.2 |
| gihwr-only | 52 to 56% | 79094 | -0.062 (0.005), -11.7 |
| gihwr-only | under 52% | 127555 | -0.039 (0.004), -10.6 |
| gihwr-only | all with a bucket | 353706 | -0.049 (0.002), -20.4 |
| lgbm-strong-noalsa | 60%+ | 74464 | +0.029 (0.006), +4.6 |
| lgbm-strong-noalsa | 56 to 60% | 72593 | +0.032 (0.007), +4.5 |
| lgbm-strong-noalsa | 52 to 56% | 79094 | +0.030 (0.006), +4.9 |
| lgbm-strong-noalsa | under 52% | 127555 | +0.022 (0.004), +5.2 |
| lgbm-strong-noalsa | all with a bucket | 353706 | +0.027 (0.003), +10.2 |
