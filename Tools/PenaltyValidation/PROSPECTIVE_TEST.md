# Prospective strength confirmation

The historical validation cannot identify the win rate of switching the full
recommendation policy. A concrete confirmation experiment is a four-arm trial:

1. Frozen baseline with all three rules enabled.
2. Fixing-hunger boost disabled; all other scoring unchanged.
3. Removal-saturation penalty disabled; all other scoring unchanged.
4. Heavy-curve penalty disabled; all other scoring unchanged.

Assign an arm randomly before each draft, block by set and player where possible,
and keep that assignment stable through reconnects/resumes. Record the baseline
commit, rating-snapshot hash, assigned arm, every displayed recommendation,
actual picks, actual registered decks, and game outcomes. An experiment setting
must participate in any affected cache identity. No ablations are stacked.

Primary analysis is intention to treat by assigned draft: recorded game wins /
recorded games per arm, with draft-level and player-level uncertainty, and
prespecified set adjustment. Record recommendation adherence as a diagnostic;
do not select the primary population based on whether a player followed advice.
Use equal follow-up windows, report attrition, and retain all assignments.
Freeze three comparisons, minimum sample size and stopping before launch.
Do not repeatedly stop as soon as an uncorrected p-value becomes favorable.

A randomized advisor trial measures the effect of the advice actually used by
humans. A fully automated bot-strength claim additionally needs an appropriate
game-playing environment; this repository supplies draft recommendations rather
than a validated full Magic gameplay opponent.

## Rough sample-size reference

Assume baseline game win rate 55%, 80% power, equal allocation, and Bonferroni
familywise 5% across the three shared-control comparisons. A normal approximation
uses `n = 2 p (1-p) (z_(1-alpha/6) + z_0.8)^2 / delta^2` games per arm.
The illustration then assumes six games per draft and within-draft correlation
0.1, giving an illustrative design effect of `1 + (6-1)*0.1 = 1.5`.
These are planning assumptions, not estimates from the historical validation;
player clustering and adherence can require more data.

| Detectable change | Independent games per arm | Independent games, four arms | Games after illustrative clustering | Approximate drafts |
|---|---:|---:|---:|---:|
| 2 percentage points | 12,956 | 51,822 | 77,733 | 12,956 |
| 1 percentage points | 51,822 | 207,288 | 310,933 | 51,822 |

Removing all three rules together is a separate hypothesis. Validate individual
changes before considering combinations or interaction tests.
