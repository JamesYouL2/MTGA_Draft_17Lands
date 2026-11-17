# Two new rules: a splash budget and a wheel tiebreak

Written before any result of this run was seen.

## Why

Every heads run so far has tested whether an existing rule holds up. This run tests two
rules the advisor doesn't have.

- **A splash budget.** [The splash price fit](https://github.com/JamesYouL2/MTGA_Draft_17Lands/blob/exp/splash-price/experiments/2026-11-16-splash-price/RESULTS.md)
  found that each spell needing the splash costs a finished deck -0.43 ± 0.05 points
  (9.3 SEs). A splash of four or more spells costs as much as three main colors. The
  advisor prices a splash card the same whether it is the first or the fifth in that
  color.
- **A wheel tiebreak.** The advisor already works out each card's chance to come back
  (`_wheel_chance`, from ALSA, the pick, and the card's rank in the pack). It shows that
  chance but doesn't score it. Between two near-equal cards, taking the one that won't
  come back and waiting for the one that might could get both.

## The heads

All are against today's advisor: the engine on upstream main (`src/advisor/engine.py`
at blob `8bc464d`).

| head | what changes |
|---|---|
| `splash-budget-2` | once the pool holds 2+ playables needing an off-lane color this card needs, the splash multipliers are halved |
| `splash-budget-3` | the same from 3+ |
| `wheel-tiebreak-weak` | picks 1 to 8: score × (1 − 0.05 × wheel chance) |
| `wheel-tiebreak-strong` | picks 1 to 8: score × (1 − 0.15 × wheel chance) |

**The splash budget in detail.** A playable is a pool card that isn't a land and is
rated above the format mean − 1 SD (`gihwr`, as `off_color_playables` counts it). A
pool card needs color X if X is in its off-lane cost against the top two lane colors
(`off_color_requirements`, hybrid options included). For each off-lane color the
candidate card needs, count the playables needing it; if the largest count is k or
more, the four splash multipliers (Bomb Splash and Premium Removal Splash 0.45 or 0.35,
Greedy Bomb Splash 0.30, Splashable 0.3) are multiplied by 0.5. The floor multipliers
(0.05 and 0.01) and the double-pip rule don't change. Pack 1 returns before the splash
rules, so this acts in packs 2 and 3 only.

**The wheel tiebreak in detail.** `_wheel_chance` gives 0 to 100. It is already 0 from
pick 9 on, for packs under 9 cards, and for Pick-Two or non-eight-player pods, so the
rule acts only where the app shows a wheel chance. The best card in the pack has its
chance cut to a tenth and the next two to 40%, so the rule mostly reorders cards
below the top.

**Does the replay compute wheel chance as the app does?** Yes, so no new harness code
was needed. `replay.py` calls `evaluate_pack(pack, pick_no, current_pack=pack_no)` with
the pick counted within the pack from 1 (`sample.py`), as `app_controller.py` does. The
pack passed is the real pack, so its size and each card's rank in it are the app's.
The defaults are one card a pick and eight players, which is what Premier Draft is.
`holdout.py` replaces win rates with held-out ones but keeps ALSA, which the wheel
chance reads.

`tests/test_advisor_engine.py::test_wheel_chance_does_not_change_score` fails under
the wheel heads, as it should: it pins today's behavior. The engine tests pass under
the splash heads.

## What runs

The Advisor heads workflow on the fork, branch `exp/new-rules-splash-wheel`: the ten
default sets, 3,000 drafts a set and salt, salts `newrules1` and `newrules2`, which no
earlier run used. Held-out ratings, pools in pick order. The change in regret slope is
the corrected one, with regret scaled within each set.

## How it is read

Two measures, each with its SE:

- the change in regret slope (positive is worse for the head);
- event wins per swapped pick (negative is worse for the head). [The measure-power
  run](../2026-11-16-measure-power/RESULTS.md) showed this one sees damage the regret
  slope misses.

**Adopt a head** only if all three hold:

1. It is better than today's by 2+ SEs on one measure: regret slope change ≤ −2 SEs,
   or event wins per swapped pick ≥ +2 SEs.
2. The other measure doesn't flag it worse by 2+ SEs.
3. It changes the top card on at least 0.2% of picks. Below that a rule isn't worth
   its code, whatever the measures say.

If both strengths of one rule pass, the one with the larger gain in SEs on the measure
that passed is proposed. If neither passes, the rule isn't added and I don't retest it
without a new reason. Four heads at 2 SEs give about a one-in-six chance that at least
one passes condition 1 by luck, so a pass by a single measure at just over 2 SEs is
reported as such, and would be rerun on fresh salts before anything is proposed.

**Reported as well:** top card change rates and agreement with drafters for every
head. For the splash heads, the regret slope change in high and low three-color sets
from `by_set.py` (20%+ first-day share is high). In the ten sets only TDM is high, so
that split is TDM against the other nine. The report gives no event-wins figure by set.

## Predictions

- `splash-budget-2` changes the top card on 0.2% to 0.5% of picks. `splash-budget-3`
  changes fewer, under 0.2%, and fails condition 3. Off-lane cards in packs 2 and 3
  are already scored at a third or less, so they are rarely the top card to begin
  with.
- Neither splash head passes condition 1. If either leans better, it is in the nine
  low-share sets, and TDM leans the other way.
- `wheel-tiebreak-weak` changes 1% to 2% of top cards, `wheel-tiebreak-strong` 4% to
  6%. Neither passes condition 1; strong leans worse on event wins.
- No head is adopted.

## What it can't show

**The wheel rule's benefit is mostly out of this measure's sight, and that biases it
against the rule.** Both measures score each pick on its own: did drafters who took the
head's top card, or who were further from it, win more or less? The rule's payoff is a
pair: take B now, then get A when it comes back. Three things hide that payoff.

- A drafter who takes B now makes their own choice at the wheel. If they don't take A
  when it comes back, the outcome credits the head with B alone.
- When the drafter takes A now, whether A would have come back is never seen. The
  counterfactual that justifies the rule doesn't exist in the data.
- When A does come back, the pick at which it is taken is scored separately, with no
  link to the earlier pick.

So the rule is scored for what it gives up now (a slightly lower-rated card) and only
partly for what it gains later. A wheel head that comes out flat may be a little better
than it looks, and one that comes out worse may not be. It would take a pair-level
test, checking in the replay whether the passed card was still in the pack at pick 9
and 10, to see the gain directly. A "not adopted" for the wheel heads means the
per-pick measures don't support it, not that the rule was shown to be useless. A pass,
on the other hand, would be against the bias and so is stronger evidence.

The ALSA the wheel chance reads is the same in every head and not held out, as in the
app. If ALSA was worked out from drafts that include these, it knows a little about
them; that affects base and heads alike and only through wheel chance.

The splash budget is tested only on how it changes picks. The splash price fit is about
finished decks, and the deck builder's splash choices aren't touched here.

As in the measure-power run, the regret slope's floor is high: "no objection" rules out
damage about the size of 40% noise and nothing smaller.

## Addendum: the wheel tiebreak confirmation

Written after the first run's results and before the confirmation run started.

The first run found `wheel-tiebreak-strong` (s = 0.15) better by 2.1 SEs on event wins
per swapped pick, one measure just over the line. As this protocol requires, it is
rerun before anything is proposed.

**Heads,** in [confirm/](confirm/), against today's advisor (engine blob `8bc464d`):

| head | rule |
|---|---|
| `wheel-015` | picks 1 to 8: score × (1 − 0.15 × wheel chance), the same patch as `wheel-tiebreak-strong` |
| `wheel-030` | the same with 0.30 |

**What runs:** the Advisor heads workflow on branch `run/wheel-confirm`, the same ten
sets and 3,000 drafts a set and salt, salts `wheelconfirm1` and `wheelconfirm2`, which
no earlier run used.

**Confirmed** if `wheel-015` is again 2+ SEs better than today's on at least one
measure (regret slope change ≤ −2 SEs, or event wins per swapped pick ≥ +2 SEs), and
neither measure reads it 2+ SEs worse. The first run is not pooled into this test.

**s = 0.30 replaces 0.15** only if it beats 0.15 head to head on the same drafts: both
measures computed with `wheel-015` in the base's place (the same `heads.py`, on the
per-set results with `wheel-015.json` as `base.json`), with 0.30 better by 2+ SEs on at
least one measure and neither reading it 2+ SEs worse. Otherwise 0.15 stays the
candidate. If 0.15 isn't confirmed, 0.30 can't replace it by this test: it would need
its own confirmation.

**Reported:** for each head, both measures with SEs, the top-card change rate and the
change in agreement with drafters (top-1).

**Predictions:** `wheel-015` is confirmed on event wins, at a smaller margin than the
first run (about 1.5 to 2.5 SEs), so it may well miss. `wheel-030` changes about twice
as many top cards (about 2%) and doesn't beat 0.15 head to head.

## Addendum 2: a sweep above 0.30

Written after the confirmation run's results and before the sweep run started.

0.30 passed in only one run, the one where it was first tried. Its event-wins edge over
0.15 there was 1.3 SEs, and the gain was still rising with s. This run reruns 0.30 on
fresh drafts and tries two larger weights.

**Heads,** in [sweep/](sweep/), against today's advisor (engine blob `8bc464d`). Each is
the same one-line rule, score × (1 − s × wheel chance), in picks 1 to 8:

| head | s |
|---|---|
| `wheel-030` | 0.30 |
| `wheel-045` | 0.45 |
| `wheel-060` | 0.60 |

**What runs:** the Advisor heads workflow on branch `run/wheel-sweep`: the same ten sets,
3,000 drafts a set and salt, salts `wheelsweep1` and `wheelsweep2`, which no earlier run
used.

**0.30 is confirmed** if it again beats today's by 2+ SEs on one measure (regret slope
change ≤ −2 SEs, or event wins per swapped pick ≥ +2 SEs), and neither measure reads it
2+ SEs worse. Earlier runs are not pooled in.

**A larger s replaces the current pick** only if it beats that pick head to head on the
same drafts by 2+ SEs on event wins per swapped pick, and the regret slope doesn't read
it 2+ SEs worse. Event wins decides here because the regret slope is read on each head's
own scores, and a larger s changes that scale more. The head-to-heads are run as before:
the same `heads.py` on the per-set results, with the current pick in the base's place.
They run in order:

1. `wheel-045` against `wheel-030`. If it passes, 0.45 is the current pick.
2. `wheel-060` against the current pick (0.45 if step 1 passed, otherwise 0.30).

If nothing beats 0.30, it stays. If 0.30 isn't confirmed against today's, no weight is
proposed from this run, whatever the head-to-heads say, and the rule goes back to the
coordinator.

Both head-to-heads are reported even when they don't decide anything.

**Reported:** for each head against today's, both measures with SEs, top-card changes,
change in agreement with drafters, and the regret slope change in TDM against the other
nine sets (from `by_set.py`).

**Predictions:**

- `wheel-030` is confirmed, on the regret slope at 2.5+ SEs and on event wins at
  about 2 SEs.
- Top-card changes grow roughly in line with s: about 2%, 3% and 4%.
- Neither larger head beats its comparison by 2 SEs on event wins, because event-wins
  SEs head to head are about 0.05, and the gain from 0.15 to 0.30 was +0.06. 0.30 stays.
- TDM stays flat for every head.
