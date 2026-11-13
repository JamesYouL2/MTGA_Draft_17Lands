# Do the deck score's small weights change what the app suggests?

Written before any result of this run was seen. These were seen first:

- The Deck score fit on 914,784 decks from twenty sets, with the overall rating (run
  [43322661144](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43322661144)):
  `domain_supported` fits at -0.6 ± 0.2 against the app's +3.2, and at +0.2 ± 0.3 with
  the old blend. `two_colors` fits at 3.1, and #264 changes it from 3.5.
- An exploratory ablation on 1,000 pools with the old app: removing the domain bonus
  changed the first build in 0.10% of pools and the fixing penalty in 0.00%.

So game results no longer support the domain bonus. This run says what removing it
does to the suggestions, on the app as it is after #263 and #264.

## What's compared

The Deck builds workflow runs the real `suggest_deck()` on pools from 19 sets, up to
50,000 decks each, with each pool's own games left out of its ratings. The simulator is
off: after #263 it doesn't change the score. Only the weights change, so the same builds
are on offer in every version.

| version | change from the app |
|---|---|
| `app` | none: this branch's `src/`, which is #264 |
| `no-domain` | `domain_supported` at 0 |
| `no-missing-fixing` | `missing_fixing` at 0 |
| `no-domain-or-fixing` | both at 0 |
| `two-colors-3.5` | `two_colors` back at 3.5 |

A supported domain deck has four or more fixing cards, so it is never short of fixing
by the score's count. Setting the weight to 0 is therefore the same as removing the
feature.

## How it is read

Head to head, as in `experiments/2026-11-08-deck-score-rating`: among pools where two
versions suggest different pairs and the drafter played one of them, how much better
decks in the version's pair did, with set and player controlled.

- **`no-domain` decides the domain bonus.** It is removed unless the head to head reads
  "worse" (2 SEs or more below the app). The fit already says the bonus isn't worth
  wins; this only checks that removing it doesn't make the suggestions worse. If too
  few decks differ for a verdict, the fit decides and the bonus is removed.
- **`two-colors-3.5` checks #264's refit.** The weight stays at 3.1 unless 3.5 reads
  "better", in which case #264 goes back to 3.5.
- **`no-missing-fixing` and `no-domain-or-fixing` decide nothing.** That weight can't be
  fit from games, because drafters rarely build such decks. They are here to see how
  often it matters.

## Predictions

- `no-domain` changes the suggested deck in under 0.5% of pools, and too few decks
  differ for a head-to-head verdict.
- `no-missing-fixing` changes it in under 1%.
- `two-colors-3.5` changes it in 1% to 5%, and its head to head isn't "better".

## What it can't show

As before: it's observational, only played pairs count, and the decks are the
drafters' own. A changed suggestion with the same pair, such as a splash build in
place of a two-color one, isn't judged by the head to head at all.
