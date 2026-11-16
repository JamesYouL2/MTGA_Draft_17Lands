# The bomb bonus and the IWD premium: results

One run of the Advisor heads workflow,
[43814789990](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43814789990):
ten sets, 60,000 drafts, 45,409 complete events. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. Reports: [heads.md](heads.md),
[by_set.md](by_set.md), [within_set.md](within_set.md).

The all-sets figures are the corrected ones, with regret scaled within each set. The
fault in the first reading is described in
[the joint run's results](../2026-11-16-proposed-together/RESULTS.md). It matters
here: read the old way, `no-power-bonus` was "no objection" and `double-power-bonus`
was "keep".

## Verdicts

| head | top card changes | as first read | corrected | verdict |
|---|---|---|---|---|
| `no-iwd-premium` | 0.56% | -0.0006 (0.0002) | -0.0004 (0.0002), 2.2 SEs better | **no objection: the premium can go** |
| `no-power-bonus` | 11.22% | +0.0005 (0.0027) | +0.0036 (0.0025), 1.4 SEs worse | **inconclusive: the bonus stays** |
| `half-power-bonus` | 4.30% | -0.0018 (0.0012) | -0.0004 (0.0011) | no retune |
| `double-power-bonus` | 4.99% | +0.0042 (0.0016) | +0.0018 (0.0015), 1.2 SEs worse | no retune |

Positive is worse for the head.

- **The IWD premium can go.** It changes the top card in 0.56% of picks, and the
  advisor is no worse without it. In TDM alone it leans the other way, +0.0010
  (0.0006), 1.8 SEs. That is one set and under 2 SEs, but TDM is the only three-color
  set in this run, so it is worth a look with the flag.
- **The power bonus stays.** Without it the change plus 2 SEs is +0.0086, over the
  +0.0063 line, so the run can't rule out a real loss. It leans worse in eight of the
  ten sets. It also drops agreement with drafters by 0.64 points, the most of any
  head, though drafters take bombs whatever an advisor says.
- **10 points a SD is about right.** Half is flat and double leans worse. Neither is
  better by 2 SEs, so there is nothing to retune.

## Predictions

| prediction | result |
|---|---|
| `no-power-bonus`: keep, by a wide margin | wrong: inconclusive, 1.4 SEs worse |
| `no-iwd-premium`: no objection, under 1% of picks | right: 0.56% |
| half and double are both worse or within 2 SEs | right |

## What it can't show

As in the held-out replay. The error-bars test showed this measure doesn't see random
noise as a loss, so "no objection" means the premium's effect is too small to see,
not that it was shown to be useless.
