# Do three composition rules earn their place on held-out picks?

Written before any result of this run was seen. Two earlier results on these rules
were seen first, and they are why these three were chosen:

- The game-results test (`experiments/2026-11-03-rule-targets`) called all three "not
  established": each interval includes zero and excludes the rule's own size.
- An exploratory ablation on 10,000 drafts (fork branch `exp/ablation-results-20261103`),
  on ratings that included the replayed drafts' games, found removing each raised
  top-1 agreement and left the regret slope within noise.

Neither says what removing a rule does to picks on ratings the drafts aren't in. This
run does, with the method of `experiments/2026-11-08-pick-multipliers`.

## The heads

All are in `_calculate_composition_bonus()` in `src/advisor/engine.py`. The patches
are in [heads/](heads/). The rules return at the first match, so a card that loses
one can still earn a later rule, as it would in the app with the rule gone.

| head | what it removes |
|---|---|
| `no-curve-heavy` | 0.7x for a spell of mana value 5+ once the pool has four |
| `no-removal-saturated` | 0.8x for removal once the pool has more than six |
| `no-fixing-hunger` | 1.4x for a land or fixing card from pack 2 while the pool has off-lane playables and no more fixing than those. Lands and fixing cards still get no other rule. |
| `no-fixing-block` | the same, and lands and fixing cards can now earn the removal and 2-drop rules like any card |
| `no-three` | the first three together |

`no-fixing-block` is the simpler code. It is here to see whether the extra change
matters. `no-three` is here because the earlier removals were never tested together.

## What runs

The Advisor heads workflow: ten sets, 3,000 drafts a set, the salts `""` and `arch2`,
on held-out ratings only. Those are the drafts of the pick-multipliers run. The base
is this branch's `src/`, the same as upstream `main` at `03f5007`, so it already has
that run's four removals.

## How it is read

As in the pick-multipliers protocol, unchanged. The measure is the change in regret
slope, head minus base, pooled over both samples, with a paired bootstrap SE. Positive
is worse for the head.

1. **Keep:** worse by 2 SEs or more.
2. **Inconclusive:** otherwise, if the change plus 2 SEs is above +0.0063, what no
   archetype weight cost on held-out ratings.
3. **No objection:** otherwise.

A rule is removed if its head gets "no objection", since the game-results test already
doesn't support it. For fixing, `no-fixing-hunger` decides. `no-fixing-block` replaces
it in the PR only if it also gets "no objection" and its slope isn't worse than
`no-fixing-hunger`'s by 2 SEs of its own. `no-three` decides nothing: it is a check
that the three together don't add up to a loss the single heads miss. If it reads
"keep" while the single heads don't, nothing is removed until that is understood.

No correction for five heads: a false "keep" only leaves a rule in place.

One more thing is on record before the run. On-lane was kept at 1.975 SEs against its
"no objection" label. If a head here lands between 1.5 and 2 SEs worse, I will say so
and recommend keeping it, as then.

## Predictions

- All three single heads get "no objection".
- `no-fixing-hunger` changes the top card most, on 1% to 5% of picks. The other two
  change it on under 1%.
- `no-fixing-block` differs from `no-fixing-hunger` on under 0.2% of picks.
- `no-three`'s change is within 2 SEs of the sum of the three.

Reported, not deciding: how often the top card changes, top-1, the change in each
sample, and event wins per pick swapped to the head's top card.

## What it can't show

As before: slopes are associations among drafters who chose freely, holding out a
draft doesn't remove the drafter's other drafts, and regret says whether drafters who
followed an advisor won, not what its users would win. "No objection" isn't proof of
equivalence. The fixing rule also boosts basic lands, which drafters almost never
take, so the replay sees little of that part.
