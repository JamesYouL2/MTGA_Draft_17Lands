# Re-reading earlier runs with regret scaled within each set

Written before any earlier run was re-read.

## Why

Until 2026-11-16 the all-sets change in regret slope divided regret by its spread over
every draft in a run. That spread includes the gaps between sets' regret levels, so a
head that moved regret in some sets more than others rescaled all of them
([the joint run](../2026-11-16-proposed-together/RESULTS.md)). On that run the figure
changed sign. `compare.change` now takes regret as z-scores within each set.

Every verdict on the pick replay since 11-08 was read from the old figure, and several
of them are merged upstream. This re-reads them.

## What is re-read

Every held-out pick replay run whose results are still on the fork, from their stored
results. No draft is replayed again.

| run | experiment |
|---|---|
| 42530568156, 42530571055 | archetype weight at zero, held out (11-08) |
| 42530573875, 42530577169 | archetype weight flat, held out (11-08) |
| 42519700054, 42519701965, 42519704241, 42519706514 | the same two, first runs (11-08) |
| 42558680265 | pick multipliers (11-08) |
| 43314302525 | composition rules (11-12) |
| 43334565174 | needs sweep (11-12) |
| 43340423385 | fixing above (11-13) |
| 43753208238 | joint removals: main against `b74d7ca` (11-15) |
| 43755194643 | lane by count |
| 43760604570 | off-color share |
| 43767043694, 43767055674 | off-color flag |
| 43774700762 | flag on SNC and KTK |
| 43786013342 | on-lane rerun |
| 43786049533 | flag threshold |
| 43793517541 | single pip |
| 43798598403 | splash rules |
| 43798734869 | gap flag (one job of it was lost) |

Not re-read: the October runs. They used ratings that included the replayed drafts and
were superseded by the held-out harness. The deck builder runs don't use this measure.

## How

`reread.py` loads each run and prints, for every head, the old figure
(`pooled_change`), the corrected one (`change`) and the plain average of the sets' own
changes, each with a bootstrap SE (200 draws). Runs that were read together are read
together.

## How it is read

Each head keeps its experiment's own rule, applied to the corrected figure. For the
removal rule that is: "keep" at 2+ SEs worse, "inconclusive" if the change plus 2 SEs
is over +0.0063, otherwise "no objection".

| | what happens |
|---|---|
| the verdict is the same | nothing; the corrected number is recorded |
| it changes and nothing was merged on it | the experiment's results get a correction |
| it changes for something merged upstream | named first in the results, with what to do: a revert where "can go" became "keep", a fresh run where it became "inconclusive" |

Verdicts that were read by set (the flag's four sets, the line against share, the
threshold) are unaffected and are not re-decided here.

## Predictions

- Most verdicts stand. The fault is largest when a head moves regret unevenly across
  sets, and most heads act in every set.
- Heads that change many picks (over 3%) move the most. One to three verdicts change.
- The joint removals run (main against `b74d7ca`) stays within 2 SEs of zero.
- The on-lane 1.1x bonus stays "keep".

## What it can't show

The same as the replay itself. And the error-bars test showed "no objection" is weak
evidence, which a re-read doesn't change.
