# Do the need rules and Greedy Bomb hold up in the replay?

Written before any result of this run was seen.

## Why

Of the advisor's pick rules, three of the composition rules have never been
replayed: the 1.3x **Critical: Needs Removal** (packs 2–3, fewer than three hard
removal spells), the up-to-1.5x **Critical: Needs 2-Drops** (packs 2–3, projected
early plays under seven) and its pack-1 form, the 1.1x **Curve Foundation**. The
rule-targets test (`experiments/2026-11-03-rule-targets`, 914,784 decks) supports
the first two from game results: while a deck is short, a removal spell is worth
+0.29 [+0.01, +0.58] win-rate points over a spell of the same rating (at the edge),
and a 2-drop +0.35 [+0.15, +0.55], with 17 of 20 sets its way. In rating SDs those
are +0.76 [−0.01, +1.53] for removal, against the rule's +1.00, and +0.91
[+0.38, +1.44] for 2-drops, against +1.00 at two short. Curve Foundation fires in
pack 1 and wasn't tested.

**Greedy Bomb Splash** (0.30x for a 5+ mana bomb with two off-color pips, when the
pool has four or more fixers) is the other gap. In the splash-rules run (11-15) its
removal changed 0.00% of top cards yet read +0.0011 (0.0003), 3.3 SEs worse on the
regret slope, and the 11-16 reread with regret scaled within each set kept it at
3.7 SEs, so it isn't the old scale. A rule that never changes the top card can only
move the regret slope through the drafter's own pick: regret is how far below the
top the advisor scored the card the drafter took. If drafters who took such bombs
won, dropping the bomb's score from 0.30 to the fall-through raises their regret,
and winners' regret going up weakens the slope. That is a claim about the measure,
not about picks, and this run tests it.

## Heads

Each a single change against today's advisor (this branch's `src/`, identical to
main at `d25398c`). Patches in [heads/](heads/), written by
[make_heads.py](make_heads.py).

| head | change | kind |
|---|---|---|
| `no-needs-removal` | drop Critical: Needs Removal | removal |
| `no-needs-2drops` | drop the pack 2–3 Needs 2-Drops bonus (pack 1's 1.1x stays) | removal |
| `no-curve-foundation` | drop pack 1's 1.1x (packs 2–3 stay) | removal |
| `no-greedy-bomb` | drop Greedy Bomb Splash; the card falls through to the next rule | removal |
| `removal-1.15` | Needs Removal at 1.15x | size |
| `2drops-cap-1.25` | Needs 2-Drops capped at 1.25x | size |
| `2drops-cap-1.75` | Needs 2-Drops capped at 1.75x | size |

## What runs

The Advisor heads workflow on held-out ratings, on the 19 sets of the single-pip
run: TDM, DMU, OTJ, FRA, SOS, TLA, FIN, DFT, MSH, DSK, LTR, TMT, NEO, EOE, BLB, FDN,
HOB, SNC, KTK. 6,000 drafts a set and salt, the salts `needs1` and `needs2`, which
no earlier run used. All heads share each job, so they're compared on the same
drafts and ratings.

`replay.py` now also records each pick's top three cards, so the extra report
[ranks.py](ranks.py) can say how often each head changes the top card, any of the
top three (in order), and the drafter's own card's rank and regret.

## Measures

From `heads.py`:

- **Regret slope** (`change`): head's slope less today's, regret scaled within
  each set. Positive is worse for the head; flagged worse at `change >= 2 SE`,
  better at `change <= -2 SE`.
- **Event wins per swapped pick** (`swap`): what taking the head's top card in place
  of today's is worth. Negative is worse for the head; flagged worse at
  `swap <= -2 SE`, better at `swap >= 2 SE`. A head that changes no top card has no
  reading here, and that is not a flag either way.

The 11-16 power test found the swap measure catches what the regret slope misses
(20% noise: 3.7 SEs against under 2), but its SE grows as fewer picks change
(about 0.024 at 3% of top cards changed, 0.051 at 0.6%).

## The decision rule

- **A removal** is proposed only if neither measure flags it worse at 2 SEs.
- **A size change** is proposed only if it beats today's on one measure by 2 SEs
  and the other measure doesn't flag it worse at 2 SEs. If both caps pass for
  2-drops, the one further ahead on swap is proposed.
- Otherwise today's rule stays.

The verdicts are by these two measures only; `heads.py`'s own verdict column (the
regret slope against the 0.0063 loss size) is reported but doesn't decide.

## How a disagreement with the game results is read

The game results and the replay answer different questions. 11-03 says a card the
deck is short of wins more than its rating says. The replay says whether moving
picks by this multiplier's size, against everything else the advisor does, picks
cards drafters won with.

- A removal flagged worse agrees with 11-03, and the rule stays.
- A removal that passes stands against 11-03's support. It is proposed by the rule,
  but the write-up says what the replay could have seen: if `2 × swap SE` is larger
  than 0.035, what 20% noise cost a swapped pick on 11-16, a "pass" means "couldn't
  tell",
  and 11-03 stays the stronger evidence. Nothing is handed over as a PR from this
  run in that case; it goes back as a question.
- For sizes: 11-03 puts removal's worth at about 0.76 of the rule's size, so a win
  for `removal-1.15` would agree with it; for 2-drops it puts today's size about
  right, so a win for either cap would be new.

## Greedy Bomb: what's measured and predicted

From `ranks.py`, for `no-greedy-bomb`: the top-card change rate, the top-three
change rate, the share of picks where the drafter's card's rank and regret change,
the share of regret moves with the top three unchanged, the share that go up,
the wins of drafters with any such pick against the rest, and the slope of each
draft's mean regret change on its wins.

The explanation above is supported if, for `no-greedy-bomb`:

1. the top card changes on under 0.05% of picks, the top three on under 0.2%;
2. most regret moves (over half) leave the top three unchanged and go up;
3. drafts hit win more on average than the rest, and the regret shift per win is
   positive.

If the regret slope reading doesn't recur at 2 SEs on these fresh drafts, the 11-15
reading was partly chance, and the write-up says so whatever 1–3 show.

## Predictions

- `no-needs-removal`: changes 1–2% of top cards; swap flags it worse or near; stays.
- `no-needs-2drops`: changes 2–4% of top cards; flagged worse on swap; stays.
- `no-curve-foundation`: changes 1–3%; neither measure flags it (pack 1 cards are
  mostly picked on rating); proposed, with the caveat that 11-03 didn't test it.
- `removal-1.15`: under 1% changes; neither measure moves by 2 SEs; today's stays.
- Both caps: under 1% changes; neither beats today's by 2 SEs; today's stays.
- `no-greedy-bomb`: top card under 0.05%; regret slope worse by 2+ SEs again;
  explanation 1–3 holds; swap has no reading. By the rule it is then not proposed
  for removal, because the regret slope flags it, even though the flag comes from
  the drafter's own pick and not from a changed recommendation. The write-up says
  that the rule, as written, keeps a rule that never changes a recommendation.

## What it can't show

The replay scores drafters' real picks against what the advisor would have shown;
it can't say what a drafter following the advisor would have won. The pools are
the drafters' own, so a head's effect on later picks (a pack-1 2-drop that would
have changed what the advisor wants in pack 2) never reaches the replay; Curve
Foundation is judged on its pack-1 picks alone. Fewer than 1% of top cards
changing leaves the swap measure with little to read.
