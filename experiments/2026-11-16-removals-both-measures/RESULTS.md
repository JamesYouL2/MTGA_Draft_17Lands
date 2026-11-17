# The three open removals, on both measures: results

One run of the Advisor heads workflow,
[44009860514](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44009860514):
19 sets, 228,000 drafts, 176,818 complete events, salts `both1` and `both2`, new.
The rule is in [PROTOCOL.md](PROTOCOL.md), written before the run. Reports:
[heads.md](heads.md), [by_set.md](by_set.md).

## The answer

By the rule, all three removals stay proposed, and so does the three together. No
head is worse by 2 SEs on either measure.

But `pack1` (#274) is on the worse side of both measures for the second run running,
and in the fifteen low-share sets it is now worse by 2.5 SEs. The rule reads only the
all-sets figures, so it passes; my recommendation is to hold #274 rather than merge
it. Details below.

## Both measures

Regret slope change: positive is worse for the head. Event wins per swapped pick:
negative is worse.

| head | top cards changed | regret slope change (SE) | SEs | event wins per swapped pick (SE) | SEs | verdict |
|---|---|---|---|---|---|---|
| `on-lane-flat` (#273) | 0.01% | -0.0000 (0.0000) | -1.3 | -0.173 (0.330) | can't judge | stays, on the regret slope alone |
| `pack1` (#274) | 3.09% | +0.0007 (0.0007) | +1.1 | -0.020 (0.011) | -1.8 | stays by the rule |
| `no-iwd-premium` | 0.54% | -0.0004 (0.0001) | -4.3 (better) | +0.028 (0.029) | +1.0 | stays |
| `all-three` | 3.45% | +0.0002 (0.0007) | +0.3 | -0.012 (0.011) | -1.1 | stays |

"Can't judge": an SE of 0.330 is over six times the -0.05 a swapped pick that 40%
noise costs, so the protocol sets event wins aside for `on-lane-flat`. It changes one
top card in 10,000.

`no-iwd-premium`'s SE of 0.029 can just see a 40%-noise-sized loss (-0.05 is 1.7 SEs),
so it is read on both, as planned, though the second measure is weak there.

## `pack1`, against the earlier run

| run | event wins per swapped pick | regret slope, fifteen low-share sets | four high-share sets |
|---|---|---|---|
| 43814769088 (`joint1`, `joint2`) | -0.039 (0.011), -3.5 SEs | +0.0012 (0.0007), +1.7 SEs | -0.0005 (0.0017) |
| this run (`both1`, `both2`) | -0.020 (0.011), -1.8 SEs | +0.0016 (0.0007), +2.5 SEs | -0.0022 (0.0016) |

The protocol said this run's verdict stands on its own drafts, and it does. But the
same direction came up twice on different drafts, on two measures. Taken together
(not a planned test) event wins would be about -0.030 (0.008), near 4 SEs. And the
by-set split shows where: removing pack 1's penalty helps a little in the three-color
sets and costs in the two-color ones (HOB +0.0060, FDN +0.0063, NEO +0.0051, OTJ
+0.0057, each about 2 SEs).

So: #274 passes the rule as written, and I recommend holding it. If it is wanted
anyway, a version that keeps the penalty below a 30% three-color share, in the same
way as the three-color flag, is the obvious test.

## The other two

- **`on-lane-flat` (#273)**: changes 0.01% of top cards. No objection on the regret
  slope (-1.3 SEs, the better side), as in every earlier run. Merge on simplicity.
- **`no-iwd-premium`**: better on the regret slope by 4.3 SEs, as in the bomb-bonus run
  (-3.2), and on the better side of event wins. In the four high-share sets it is worse
  by 2.3 SEs (+0.0004, SE 0.0002), better by 5.4 in the other fifteen. The rule reads
  all sets: stays.
- **`all-three`**: within 1.1 SEs on both. Most of its change is `pack1`'s.

## Predictions

| prediction | result |
|---|---|
| `on-lane-flat`: event wins can't judge; regret slope no objection | right |
| `pack1` flagged on event wins, about -0.03, 2 to 3 SEs; withdrawn | wrong: -0.020, 1.8 SEs, not flagged |
| `no-iwd-premium`: event wins can't judge; regret slope no objection | half right: no objection; event wins could just judge (SE 0.029) |
| `all-three` looks like `pack1` | right |

## What it can't show

As the protocol says: neither measure can show a removal under 1% of picks is
harmless on 228,000 drafts, only that it is not large harm.
