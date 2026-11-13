# Can the archetype rate's shrinkage go: results

Run [42558680265](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/42558680265)
at `467b4b0`, the same run as `experiments/2026-11-08-pick-multipliers`: 60,000 drafts
and 45,451 complete events, on held-out ratings. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. The full report is
[heads.md](../2026-11-08-pick-multipliers/heads.md).

## Verdict

**No objection: shrinkage can go.**

| | |
|---|---|
| regret slope change, head minus base | -0.0010 (SE 0.0004), -2.4 SEs |
| in each sample | -0.0008 (0.0006), -0.0011 (0.0006) |
| top card changes | 0.45% of picks |
| top-1 change | -0.01 points |
| event wins per pick swapped | +0.059 (SE 0.065) |

Negative favors removing it. The protocol has no verdict for "better", and five heads
were read with no correction, so this is a clear lack of objection and not a finding
that shrinkage hurts.

## The prediction

Held: "no objection", with the top card changing on under 1% of picks.

## What it can't show

As the protocol says. The dumps are from whole formats, so this doesn't cover a new
set's first days, when pair rates are thin and shrinkage could matter more. The
500-game gate would still apply then, so the most shrinkage does is pull a rate halfway.
