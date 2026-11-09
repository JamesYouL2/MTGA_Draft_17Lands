# Testing Enables Bomb Splash on game results: results

Run [42558929702](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/42558929702)
at `dae849d` (`6437b4e` plus a push trigger): 914,784 decks and 4.14M games from 20
sets, with 87,211 decks in the rule's region. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. The full report is
[splash_rule.md](splash_rule.md) and the numbers are in
[splash_rule.json](splash_rule.json).

## Verdict

**Not established.** A fixing card is worth +0.01 win rate points more [-0.06, +0.08]
in a deck that plays an off-lane bomb than in other decks with off-color cards. In
rating terms that's +0.02 SDs (± 0.09), against the +1.00 SD the rule's 1.3x gives.

So by this protocol the replay decides, and the replay in
`experiments/2026-11-08-pick-multipliers` (branch `exp/pick-multipliers`) has no
objection. **The rule can go.**

## The prediction

Held: not established.

## Reported, not deciding

- **The estimate is steady.** +0.03 (0.03) with counts as controls, and -0.00 (0.05)
  among strong drafters.
- **Sets split evenly.** 10 of 19 lean the rule's way, from -0.33 (FRA) to +0.68 (BLB).
- **Fixing does seem to help these decks,** +0.20 (0.08) per card. It helps about as
  much in other decks with off-color cards. The bomb is what the rule adds, and that's
  what shows nothing.

## What it can't show

As the protocol says: it sees decks, not pools, so only a bomb that was played counts.
It's observational. It values a fixing card in a finished deck, and the replay covers
the pick.
