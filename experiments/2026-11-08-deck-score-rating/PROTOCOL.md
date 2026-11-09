# Which card rating the deck score should use

Written before any result in this folder was seen, with one exception. Timing the
tool, on 35 HOB pools from part of a dump with the ratings gate lowered to 40 games,
printed how often each version changed the suggested pair: `overall` 10,
`overall+pair` 9 and `blend+pair` 4. That was seen before prediction 3 below was
written. No outcome was seen.

## Why

`suggest_deck()` ranks builds of different pairs by the deck score, whose card
quality uses `get_card_rating()`, the 0.7 / 0.3 blend of a card's pair and overall
win rates. The pair parts test (`experiments/2026-11-08-pair-parts`) found that a
pair's level doesn't cancel there. Between pairs, a point of the blend's rating goes
with about 0.95 points of win rate, and the deck score prices it at 2.9. That was
looked at after the result, on 186 pair-by-set means with only the set controlled.
Nothing has measured whether it changes the suggested deck, or whether the change
is for the better.

## What's compared

Only the deck score's rating changes. The builders keep the blend to choose cards
within a pair, so the same decks are on offer in every version.

| version | a card's rating in the deck score |
|---|---|
| `blend` | today's |
| `overall` | its overall win rate |
| `overall+pair` | overall, less the pair's average overall, plus the set's average, plus the pair's baseline |
| `blend+pair` | blend, less the pair's average blend, plus the set's average, plus the pair's baseline |

The **baseline** is the pair's game win rate less the set's, converted to rating
points at the deck score's own price (25 x 0.0387 x 12 / the set's SD win rate
points a rating point, about 2.9 at an SD of 4). So the pair's win rate is what
separates pairs, and at the price the score already uses.

Two choices need saying:

- **Adding a baseline to overall as it stands would make the excess worse.** Overall
  alone already runs +1.30 win rate points a rating point between pairs, so a pair's
  strength is partly in it. So `overall+pair` first takes out the pair's average.
  That's why it's centered.
- **`blend+pair` goes beyond the request.** It wasn't in the plan's list. It's here
  because it's the fix that doesn't simplify: it keeps fit inside the deck score and
  only corrects the level. If it wins and the others don't, the answer is a different
  one from "use overall".

The app could compute a baseline: its dataset already has `color_ratings`. Averages
are by games in hand in the pair. Only two-color keys get one. A deck of 3+ colors
uses its first two, as `deck_features()` does. A pair with no rated card gets none.

## What runs

The Deck builds workflow on 19 sets (all but the cube), up to 50,000 decks each,
salt `""`.

- **Pools:** a deck's cards plus its sideboard, without basics, and only with 35+
  cards. Builds of one draft are separate rows.
- **Ratings:** from `games.py`'s counts with the pool's own fold left out, and the
  500-game gate in every fold's total. Each pair's baseline and average leave it out
  too. So a pool's own games are in none of its numbers.
- **Deck builder:** the real `suggest_deck()`, with the shown order, the filter and
  safe-deck promotion. The simulator is off, so its mana penalties are too. It's
  random, and those penalties are already judged not worth keeping
  (`exp/mana-penalties`, not merged). The deck-variants experiment checks the
  simulator's effect on the deck shown.

A pool's suggested pair is the first two `colors` of the deck the app shows first.

## The measures

**How often it changes:** the share of pools whose suggested pair, and deck, differs
from `blend`'s. Overall and by set.

**Head to head (deciding):** among pools where a version and `blend` suggest different
pairs and the drafter's two-main-color deck is in one of them, how much better decks
in the version's pair did. A logistic regression of games won on playing it, with set
and player buckets controlled. In win rate points, 95% interval, with the larger of
model and set-clustered SEs. Needs 100+ decks on each side.

**Reported, not deciding:**

- The same comparison between the versions.
- The share of two-color decks that played the suggested pair and how they did.
- **Score gap:** the pool's best build's score less the played pair's best, per SD.
  Within each set, the slope of winning on that gap, then each version less `blend`
  over the sets. More negative means the version's gap predicts losses better.

## The decision rule

For each version against `blend`:

| head to head | verdict |
|---|---|
| favors the version by 2+ SEs | better |
| favors `blend` by 2+ SEs | worse |
| neither, and the bottom of 2 SEs is above -0.5 win rate points | not worse |
| neither, otherwise | inconclusive |

- If any version is **better**, adopt the best. Between two that are better, use the
  version comparison. If that doesn't separate them by 2 SEs, take the simpler:
  `overall`, then `overall+pair`, then `blend+pair`.
- If none is better but **`overall` is not worse**, adopt `overall`. It removes a
  lookup from the deck score and needs no baseline. The other two add a calculation,
  so being no worse doesn't justify them.
- Otherwise keep `blend`.

## The prediction

The between-pairs arithmetic says the blend prices level too highly, so:

1. `overall+pair` and `blend+pair` are both ahead of `blend` head to head, and at
   least one is by 2+ SEs.
2. `overall` is ahead by less than they are. It still prices a pair at 1.30 against
   2.9, as the plan's expected limit says.
3. Each version changes the suggested pair in 5% to 30% of pools.

This can fail. The pair's strength is real, so a blend that overrates strong pairs
still sends drafters to strong pairs, and a version that discounts them may send
drafters to worse ones.

## What it can't show

- **It's observational.** A drafter who plays the pair a version prefers isn't assigned
  to it. They chose it, for reasons in the pool and in themselves. Skill and experience
  buckets take out only part of that.
- **A pair's record includes who drafts it.** Better drafters favoring a pair raises
  both its baseline and its results here. Rates and baselines leave the pool's fold
  out, but not the habit.
- **Only played pairs count.** Pools where the drafter played neither suggestion say
  nothing, so this covers disagreements drafters themselves came close to.
- **Decks are the drafters' own,** not the build the app would show in that pair. This
  compares pairs. It doesn't test a suggested list.
- **Finished pools only.** It says nothing about the deck score's use during a draft.
