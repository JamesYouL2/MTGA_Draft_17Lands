# A flag by the win-rate gap: results

Protocol: `PROTOCOL.md`. Reports: `heads.md`, `by_set.md`. 42,000 drafts, 31,018
complete events. One of the eight jobs (FRA, salt `gap4`) was lost when its runner
died, so FRA has three samples and TMT four.

## The verdict

**No case for changing the flag.** In the two sets where the gap flag and the share
flag differ, softening did not help on these drafts.

| set | `flag-gap` (SE) | SEs |
|---|---|---|
| TMT | -0.0013 (0.0055) | -0.2 |
| FRA | +0.0077 (0.0054) | +1.4 |
| the two, weighted by SE | +0.0033 (0.0039) | +0.8 |

Negative is better. `flag-share`, the control, changed no pick, as it should.

TMT was the reason to try this. Softening there was better by 0.0250 and 0.0204 in the
first two runs, 0.0084 in the single-pip run, and 0.0013 here. Each new sample is
nearer zero. TMT's dump is small, so its samples overlap and its early SEs were
understated; the large early numbers look like one lucky set of drafts counted more
than once.

With TMT gone, nothing favors the gap over the share. The share flag stays.

## The predictions

| | predicted | found |
|---|---|---|
| TMT | better by 2+ SEs again | 0.2 SEs: wrong |
| FRA | within 2 SEs, on the worse side | 1.4 SEs worse: right |
| the two together | pass | no: wrong |
