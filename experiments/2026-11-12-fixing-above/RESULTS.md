# Should Needs Fixing be bigger than 1.4x: results

Run [43340423385](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43340423385)
at `ad08fa0` (`exp/needs-sweep` plus a push trigger): ten sets, two samples, 60,000
drafts and 45,451 complete events, on held-out ratings only. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. The full report is
[heads.md](heads.md) and the numbers are in [heads.json](heads.json). The report's
verdict column uses the removal protocol's labels, which this run doesn't read.

## Verdict

**No. Nothing changes: 1.4x stays.** No value above it is better than the base at all.

With the needs sweep's values below it, on the same drafts and base:

| Needs Fixing | regret slope change (SE) | top card changes | top-1 change |
|---|---|---|---|
| 1.0 | +0.0034 (0.0014) | 4.03% | +0.82 |
| 1.1 | +0.0022 (0.0011) | 2.98% | +0.72 |
| 1.2 | +0.0012 (0.0008) | 1.96% | +0.54 |
| 1.3 | +0.0005 (0.0004) | 0.94% | +0.29 |
| **1.4 (base)** | 0 | | |
| 1.5 | +0.0002 (0.0004) | 0.83% | -0.29 |
| 1.6 | +0.0008 (0.0008) | 1.55% | -0.55 |
| 1.8 | +0.0023 (0.0016) | 2.70% | -1.01 |
| 2.0 | +0.0051 (0.0022) | 3.54% | -1.36 |

Positive is worse than 1.4.

The slope is lowest at the base and rises on both sides, in order. Both samples agree
in sign at every value. So 1.4 is at or near the best size by this measure. The curve
is flat close to it: 1.3 and 1.5 are within about 1 SE of the base, so the data can't
tell 1.4 from its neighbors. It can tell it from 1.0 (2.5 SEs) and from 2.0 (2.3 SEs).

## The other measure, across the whole range

Event wins per swapped pick favored the smaller value everywhere: below 1.4 it was
+0.058 to +0.097 for the head, and above 1.4 it is -0.094 to -0.189 against the head.
Read on its own it says less fixing is always better, down to none. The slope says
there is a best amount, near 1.4.

They measure different things. A swapped pick is credited to whoever took that card,
and drafters who take the fixing land over a spell may be weaker on average. The slope
asks whether drafters whose picks cost them less by the advisor's scores won more. The
protocols chose the slope beforehand, and I can't show which is right from this.

## The predictions

- **1.5 and 1.6 read better than the base, by less than 2 SEs: failed.** Both read
  slightly worse.
- **The slope turns back up by 2.0: held,** and it turns at the base, not above it.
- **Top-1 falls at every value, by more as the multiplier grows: held.**

## What it can't show

As the protocol says: slopes are associations among drafters who chose freely, and
regret says whether drafters who followed an advisor won, not what its users would win.
These are the needs sweep's drafts, so the two runs share noise. The rule's boost to
basic lands is barely seen, since drafters almost never take them.
