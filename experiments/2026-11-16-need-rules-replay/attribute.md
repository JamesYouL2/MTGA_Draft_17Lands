# Where each head's regret slope change comes from

From attribute.py, run after the results were in, on run 44012209588.

Regret slope change, head minus today's, with the head's regret on one class of picks only. Positive is worse for the head.

| head | whole | top changed | rank changed | regret only |
|---|---|---|---|---|
| no-greedy-bomb | +0.00082 (0.00012), +6.8 SEs | +0.00003 (0.00004), +0.8 SEs | +0.00080 (0.00012), +6.9 SEs | -0.00001 (0.00001), -1.0 SEs |
| no-needs-2drops | -0.00067 (0.00014), -4.8 SEs | -0.00022 (0.00008), -2.7 SEs | -0.00018 (0.00006), -2.8 SEs | -0.00028 (0.00009), -3.2 SEs |
| 2drops-cap-1.25 | -0.00022 (0.00007), -3.3 SEs | -0.00003 (0.00002), -1.4 SEs | -0.00003 (0.00002), -1.5 SEs | -0.00016 (0.00005), -3.1 SEs |
| 2drops-cap-1.75 | +0.00009 (0.00004), +2.4 SEs | -0.00001 (0.00001), -0.9 SEs | +0.00002 (0.00001), +2.5 SEs | +0.00008 (0.00003), +2.5 SEs |
| no-needs-removal | +0.00025 (0.00022), +1.1 SEs | +0.00016 (0.00010), +1.6 SEs | -0.00008 (0.00009), -0.9 SEs | +0.00014 (0.00015), +0.9 SEs |
| no-curve-foundation | +0.00002 (0.00020), +0.1 SEs | -0.00007 (0.00009), -0.8 SEs | +0.00017 (0.00009), +1.8 SEs | -0.00008 (0.00016), -0.5 SEs |
| removal-1.15 | +0.00020 (0.00012), +1.7 SEs | +0.00005 (0.00004), +1.1 SEs | -0.00001 (0.00003), -0.3 SEs | +0.00016 (0.00010), +1.6 SEs |

- **no-greedy-bomb**: drafters whose own card dropped in rank, top card unchanged: 4374 events, 3.33 wins; whose card rose: 2559, 3.12; every event 3.25.
- **no-needs-2drops**: drafters whose own card dropped in rank, top card unchanged: 5561 events, 3.05 wins; whose card rose: 6861, 3.05; every event 3.25.
- **2drops-cap-1.25**: drafters whose own card dropped in rank, top card unchanged: 1232 events, 3.08 wins; whose card rose: 2187, 3.04; every event 3.25.
- **2drops-cap-1.75**: drafters whose own card dropped in rank, top card unchanged: 879 events, 3.14 wins; whose card rose: 374, 2.80; every event 3.25.
- **no-needs-removal**: drafters whose own card dropped in rank, top card unchanged: 12950 events, 3.11 wins; whose card rose: 14845, 3.13; every event 3.25.
- **no-curve-foundation**: drafters whose own card dropped in rank, top card unchanged: 27477 events, 3.14 wins; whose card rose: 37280, 3.15; every event 3.25.
- **removal-1.15**: drafters whose own card dropped in rank, top card unchanged: 7878 events, 3.11 wins; whose card rose: 9879, 3.14; every event 3.25.
