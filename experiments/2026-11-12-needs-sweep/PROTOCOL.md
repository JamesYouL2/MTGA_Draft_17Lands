# How big should Needs Fixing and Needs Creatures be?

Written before any result of this run was seen. These earlier results were seen, and
they are why these two rules and these values were chosen:

- **Needs Fixing (1.4x).** Removing it read +0.0023 (SE 0.0014) on the regret slope,
  1.7 SEs worse, so it stayed (`experiments/2026-11-12-composition-rules`). But where
  the top card changed, drafters took the other card 41% of the time and the rule's
  17%, and they didn't do worse. The game-results test couldn't tell it from zero, and
  its interval reaches about 40% of the rule's size.
- **Needs Creatures (1.25x).** The game-results test supports it, at about half its
  size: +0.42 rating SDs [+0.04, +0.81] against the rule's 0.83. Creatures were worth
  as much once the deck wasn't short. Removing the rule in the exploratory ablation
  barely changed picks.

So both may be too big. Needs Removal and Needs 2-Drops fit their sizes, and aren't
swept.

## The heads

Each changes one number in `_calculate_composition_bonus()`. The patches are in
[heads/](heads/).

| rule | base | heads |
|---|---|---|
| Needs Fixing | 1.4 | 1.3, 1.2, 1.1 and 1.0 |
| Needs Creatures | 1.25 | 1.18, 1.12, 1.06 and 1.0 |

A head at 1.0 removes the rule as the app would. For creatures that deletes the check,
so a creature can earn a later rule. For fixing it is `no-fixing-hunger` again: lands
and fixing cards still earn no other rule.

## What runs

The Advisor heads workflow: ten sets, 3,000 drafts a set, the salts `""` and `arch2`,
on held-out ratings only. The base is this branch's `src/`: upstream `main` at `03f5007`
with Curve Too Heavy and Removal Saturated removed (#265, #266), since those are meant
to merge first. So `fixing-1.00` isn't quite the earlier `no-fixing-hunger`, whose base
had both rules.

## How it is read

The measure is the change in regret slope, head minus base, pooled over both samples,
with a paired bootstrap SE. Negative is better for the head.

A changed number isn't a simplification, so it has to show a gain. For each rule:

1. A head **qualifies** if it is better than the base by 2 SEs or more and both samples
   agree in sign.
2. If the 1.0 head qualifies, the rule is removed. It is the simplest outcome, and no
   other value is taken over it.
3. Otherwise, if any head qualifies, the app takes the qualifying head with the lowest
   slope.
4. Otherwise nothing changes.

Four values a rule make a false gain likelier than one would. No correction is applied,
but a pick is only acted on if its neighbors in the sweep lean the same way: a lone
qualifying value between two that read worse than the base is reported and not taken.

## Predictions

- **Fixing:** the slope is lowest at 1.2 or 1.1, and 1.0 doesn't qualify. I expect one
  of 1.1 to 1.3 to qualify, without much confidence.
- **Creatures:** no head qualifies. The top card changes on under 1% of picks for every
  head, so the replay sees little.
- For both rules, top-1 agreement rises as the multiplier falls.

Reported, not deciding: how often the top card changes, top-1, the change in each
sample, and event wins per pick swapped to the head's top card.

## What it can't show

As before: slopes are associations among drafters who chose freely, holding out a draft
doesn't remove the drafter's other drafts, and regret says whether drafters who followed
an advisor won, not what its users would win. The two rules aren't swept together.
