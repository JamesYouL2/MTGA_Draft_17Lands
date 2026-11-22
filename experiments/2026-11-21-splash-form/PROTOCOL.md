# The splash price in the app: fit and Deck builds

Written before any result of these runs was seen.

## Why

The [splash price test](../2026-11-16-splash-price/RESULTS.md) (fork `exp/splash-price`)
passed its rule: a splash costs less than three main colors (-2.47 against -3.28,
3.0 SEs), and a bigger splash costs more (-0.43 a splash spell, 9.3 SEs). Its next step
was this: put the split in `deck_features()`, fit that exact form, and measure how
often the first suggested deck changes before anything is proposed.

## The change

`deck_features()` takes the deck's splash colors. Against a deck of two colors or fewer
(no term), it has:

| term | when |
|---|---|
| `splash` (1) and `splash_spells` (spells needing a splash color, copies counted) | two main colors or fewer and a splash |
| `three_colors` | three main colors, no splash |
| `four_colors` | three main colors and a splash, or four or more |

They replace `two_colors` (+3.1 for two colors or fewer). The deck builder calls a
color a splash when the build wasn't made in it: the greedy build's splash color, and
any color a Consistent build's spells need beyond its pair. Sealed's greedy splash does
the same. With no splash colors given, every color counts as a main color.

Scores of two-color decks drop by 3.1 points (the reference moves from "3+ colors" to
"two colors"), so the record constants are refit with the weights.

## Run 1: the fit

The Deck score fit workflow (`features.py` then `fit.py`) on twenty sets, 50,000 decks
each, salt `splash-form-2026-11-21`, which no earlier run used. `features.py` passes
17Lands' splash colors, so the fit sees the app's own terms. The weights that go into
the app are this fit's, with its record constants. `missing_fixing` and
`missing_spells` keep the app's weights, as before.

The form stands if `splash_spells` is 2 SEs or more below zero and `four_colors` is
below `three_colors`. If `splash_spells` fails, it is dropped and the three-term split
(the 11-16 test's) goes in instead.

## Run 2: Deck builds

`builds.py` runs the real `suggest_deck()` on pools from 19 sets, 50,000 decks each,
salt `splash-builds-2026-11-21`, each pool's own games left out of its ratings, the
simulator off. Only the scoring changes between versions:

| version | the score |
|---|---|
| `old` | one weight of -3.1 for every deck of three colors or more, no splash colors: exactly today's ranking |
| `app` | this branch: the fitted split with the weight per splash spell |
| `flat-splash` | the split with the 11-16 weights and no weight per splash spell |

Groups come from the builder's label, which is what the user sees. One case
differs from the score: a build of two active colors whose second color has
three pips or fewer is labeled "Splash", but the score sees two main colors.

The fit's weights are the app's (`splash` -1.5, `splash_spells` -0.4,
`three_colors` -3.3, `four_colors` -5.0; fit run 44964471814). They were known
before this run started.

The report (`report.py`):

- How often the suggested pair, deck and color group (two, splash, three or more by the
  builder's label) change from `old`, overall and by set.
- **Head to head within a pair (deciding):** pools where `app` and `old` suggest the same
  pair in different groups, and the drafter played that pair in one of the two groups.
  How much better the decks in `app`'s group did, set and player controlled.
- Head to head between pairs, as in the earlier Deck builds tests.
- How many drafters played the suggestion's pair and group.

## The decision rule

Propose the change (a PR off main with the fitted weights) unless either head to head
reads "worse" (2 SEs or more below `old`). If too few decks differ for a verdict, the
fit decides and the change is proposed, with the change rate stated. `flat-splash`
decides nothing; it shows how much of the change is the weight per splash spell.

## Predictions

- Fit: splash base about -1.5, per spell about -0.4, three about -3.3, four or more
  about -5.
- `app` changes the suggested deck in 2% to 6% of pools, most of them from a two-color
  build to a splash build of the same pair; few pair changes.
- The within-pair head to head is "inconclusive" or "not worse", not "better":
  drafters choose when to splash, so the decks in each group differ in more than the
  splash.

## What it can't show

It's observational: only pools where the drafter played one of the two suggestions
count, and the decks are the drafters' own, not the app's builds. A drafter who
splashed may have done so because the pool called for it, which the head to head
can't separate from what splashing did.
