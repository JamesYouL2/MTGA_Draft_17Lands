# The splash price in the app: results

[PROTOCOL.md](PROTOCOL.md) set up both runs before either had a result. The full
reports are next to this file: [fit-report.md](fit-report.md) and
[report.md](report.md) (with [report.json](report.json)).

## Verdict

**Propose it.** The fit kept the form: a splash costs a base plus a weight for
each splash spell. In the Deck builds run, neither head to head reads worse. The
within-pair one reads better, though the protocol predicted it wouldn't. The
change is small: the first suggested deck changes in 1.06% of pools.

## Run 1: the fit (run 44964471814)

The run used 914,655 decks from twenty sets, with salt `splash-form-2026-11-21`.
Weights are in score points, against a deck of two colors or fewer; the report
gives them to one decimal.

| term | decks it applies to | fitted | 11-16 test |
|---|---|---|---|
| `splash` | 30.9% | -1.5 ± 0.1 | -1.4 (from the bins) |
| `splash_spells` | 30.6% | -0.4 ± 0.0 | -0.43 ± 0.05 |
| `three_colors` | 11.2% | -3.3 ± 0.1 | -3.28 ± 0.31 |
| `four_colors` | 8.8% | -5.0 ± 0.1 | -4.94 ± 0.41 |
| `missing_fixing` | 2.6% | -0.2 ± 0.1 (~0) | the app keeps -2.5 |

So a splash of one to three spells costs less than three main colors
(-1.9 to -2.7, against -3.3). Four spells cost about the same as three main
colors, and more than four cost more. The record constants are refit to
`WIN_LOG_ODDS_AT_BASE = 0.1503` and `WIN_LOG_ODDS_PER_POINT = 0.05048`.

- **The form stands.** `splash_spells` is far more than 2 SEs below zero, and
  `four_colors` is below `three_colors`.
- **It agrees across sets.** Fitted per set, `splash_spells` is negative in 17
  of 20 sets.
- **Out of sample** (each set scored by models fit on the other sets): the score
  separates good decks from bad by 13.9% in game win rate, the same as the bin
  guesses (13.8%) and close to LightGBM (14.1%).

The predictions were -1.5, -0.4, -3.3 and -5; all four held.

## Run 2: Deck builds (run 44974294324)

The run covered 928,022 pools from 19 sets, with salt `splash-builds-2026-11-21`.
It skipped 11,447 pools with a card missing from the dataset, all of them in
MH3 (5,040) and TMT (6,407), and 19 that were too small. The report job failed on an artifact
path: the build artifacts downloaded to `.` and the report looked in `results/`.
The workflow is fixed, and the report was run locally on the run's 19 build
artifacts.

### How much changes

| | pair | first deck | group |
|---|---|---|---|
| `app` against `old` | 0.30% | **1.06%** | 0.94% |
| `flat-splash` against `old` | 0.32% | 1.03% | 0.91% |
| `app` against `flat-splash` | 0.09% | 0.34% | |

- **By set:** most sets change 0.2% to 2%. The outliers are MH3 (4.1%), MSH
  (2.1%) and OTJ (2.0%).
- **Moves between groups** (pools whose first deck moved, `old` → `app`):
  - three or more colors → splash: 4,218
  - three or more colors → two colors: 944
  - two colors ↔ splash: 1,727 one way, 1,821 the other
- **Share of first decks by group:**

  | group | before | after |
  |---|---|---|
  | three or more colors | 2.66% | 2.11% |
  | splash | 2.33% | 2.78% |
  | two colors | 95.0% | 95.1% |

The prediction was 2% to 6% of pools, mostly two colors becoming a splash. That
was wrong on both counts. The change is smaller, and most of it is three-color
builds (the soup) giving way to a splash: a third main color now costs 3.3 and
four or more 5.0, against 1.5 plus 0.4 a spell for a splash.

### Head to head

| | pools differing | decks in `app`'s / `old`'s | raw win rates | effect (95% interval) | verdict |
|---|---|---|---|---|---|
| **Within a pair (deciding)** | 6,280 | 1,794 / 3,228 | 54.7% vs 52.8% | **+2.28 ± 0.90** [+0.52, +4.04] | better |
| Between pairs | 920 | 332 / 506 | 54.9% vs 54.0% | +1.67 ± 1.84 [-1.95, +5.28] | inconclusive |

The within-pair row covers pools where `app` and `old` suggest the same pair in
different groups. Drafters who played the pair in the group `app` suggests won
2.3 points more of their games than those who played it in `old`'s group, with
set and player controlled. `flat-splash` reads the same (+2.83 [+0.87, +4.79]).

The prediction was "inconclusive or not worse". This is observational, so it is
not evidence that the app's builds win more. It shows that, of decks in the pair
the app picks, the ones in the color group the new score prefers did better.

### Weight per splash spell

On its own, the weight per splash spell changes the first deck in 0.34% of pools.
Both versions read the same on the head to heads. The weight is kept because the
fit supports it (it is 30.6% of decks, and negative in 17 of 20 sets), not
because of anything the builds show.

### Followed

The share of drafters who played the suggestion's pair and group went from
45.87% to 46.04%. This is reported only.

## What changes for the user

- **Power reads 3.1 lower on two-color decks.** Two colors were the only group
  with a term (+3.1), and now carry none, while every other group takes a
  negative weight. An average two-color deck shows 75 instead of 78. The record
  constants are refit, so the estimated records don't move.
- **Splash notes are new.** A splash shows "Splash (-x.x)", with the base and the
  per-spell weight summed into one note. Three-color builds show
  "Three Colors" and four or more "Four+ Colors". "Rock-Solid Mana" is gone.

## Known gaps

- **A one-color build with a light second color** (three pips or fewer) is
  labeled "Splash", but the score sees two main colors and charges nothing. In
  17Lands' data the same deck is a splash, so the fit charges it. These are rare.
- **TDM is the one set where a splash costs more than three main colors**, as in
  the 11-16 test. The weights are the same for every set.
- **The replay tool** (`Tools/AdvisorReplay/replay.py`) passes no splash colors,
  so the greedy builds it replays score as three main colors. It still works on
  older app commits.
