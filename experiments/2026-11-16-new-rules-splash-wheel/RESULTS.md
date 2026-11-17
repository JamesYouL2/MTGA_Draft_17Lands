# Two new rules: a splash budget and a wheel tiebreak. Results

One run of the Advisor heads workflow,
[44012392581](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44012392581)
at `f524bce`: ten sets, 60,000 drafts, 45,673 complete events, salts `newrules1` and
`newrules2`. The protocol is in [PROTOCOL.md](PROTOCOL.md), written before the run.
Reports: [heads.md](heads.md), [by_set.md](by_set.md).

## Verdicts

| head | top card changes | regret slope change (SE) | event wins per swapped pick (SE) | verdict |
|---|---|---|---|---|
| `splash-budget-2` | 0.62% | +0.0026 (0.0014), 1.9 SEs worse | -0.100 (0.051), 2.0 SEs worse | **not adopted: leans worse on both** |
| `splash-budget-3` | 0.45% | +0.0014 (0.0013), 1.1 SEs worse | -0.107 (0.055), 2.0 SEs worse | **not adopted: leans worse on both** |
| `wheel-tiebreak-weak` | 0.38% | -0.0001 (0.0001), 1.6 SEs better | +0.132 (0.078), 1.7 SEs better | not adopted: better on both, neither at 2 SEs |
| `wheel-tiebreak-strong` | 1.07% | -0.0004 (0.0002), 1.7 SEs better | +0.102 (0.049), 2.1 SEs better | **passes the rule; rerun on fresh salts before proposing** |

For the regret slope, positive is worse for the head. For event wins, negative is worse.

- **The splash budget makes the advisor worse, not better.** Both strengths lean worse
  on both measures. Event wins per swapped pick reads -0.100 and -0.107, each 1.95 SEs.
  That is just under the protocol's 2 SE line for "flags it worse", so neither head is
  formally flagged. Neither comes near being better. The rule isn't added.
- **The wheel tiebreak at 0.15 passes all three conditions.** It is better by 2.1 SEs
  on event wins, the regret slope also leans better (1.7 SEs), and it changes 1.07% of
  top cards. But this is the case the protocol set aside: one measure, just over 2
  SEs, among four heads. So it gets a rerun on fresh salts before anything is
  proposed. At 0.05 the rule points the same way on both measures but reaches neither
  line.

## The splash heads by three-color share

Regret slope change, from [by_set.md](by_set.md). TDM is the only set in the ten at a
20%+ share.

| head | TDM | the other nine |
|---|---|---|
| `splash-budget-2` | +0.0077 (0.0044), 1.8 SEs worse | +0.0021 (0.0014), 1.5 SEs worse |
| `splash-budget-3` | +0.0067 (0.0042), 1.6 SEs worse | +0.0009 (0.0012), 0.7 SEs worse |

It leans worse in both groups, and most in TDM. `splash-budget-2` is worse in eight of
the ten sets; only DFT and FDN lean better. A set built around three colors is where
capping a splash should hurt most, and it does. The rule's premise, that each splash
spell costs a finished deck, may be true without this pick rule helping. The cost
shows up in the deck, and the deck builder can still leave a splash card out. Passing
up a splash card in the draft loses that option.

## What drafters did

When the wheel heads change the top card, drafters took the head's choice four times as
often as the base's: 41% against 10% where both choices are on-lane. That is why
agreement with drafters goes up (+0.29 points for the strong head), where the splash
heads lower it. Drafters already pass cards that tend to come back.

Under the splash heads it runs the other way. Drafters took the base's choice two to
six times as often as the head's, except where the head moves back on-lane (then about
evenly), and agreement drops 0.15 to 0.17 points.

## The protocol's bias, seen in the result

The protocol said the per-pick measures are biased against the wheel rule, because
they don't see the card that comes back. The rule came out better anyway, so the bias
makes the pass stronger evidence, not weaker. It also means a pair-level check (was the
passed card still there at pick 9?) would likely read larger than these figures.

## Predictions

| prediction | result |
|---|---|
| `splash-budget-2` changes 0.2% to 0.5% of top cards | close: 0.62% |
| `splash-budget-3` changes under 0.2% and fails condition 3 | wrong: 0.45% |
| neither splash head passes condition 1 | right; both lean worse |
| a splash head that leans better does so in the low-share sets; TDM leans the other way | neither leans better; TDM is the worst |
| wheel weak 1% to 2%, strong 4% to 6% | wrong: 0.38% and 1.07%, a third of that |
| neither wheel head passes; strong leans worse on event wins | wrong: strong passes on event wins, 2.1 SEs |
| no head is adopted | strong passes, held for a rerun |

## What's next

Rerun `wheel-tiebreak-strong` on two new salts, alone with the base, and add a stronger
head (0.30) to see whether the gain grows with the weight. Propose it only if event wins
again come out 2 SEs better and the regret slope again doesn't flag it worse. The
splash budget is closed unless a deck-level reason comes up.

## What it can't show

As in the protocol. The wheel gain is measured per pick, so it undercounts the pair. The
splash budget is judged on picks only, not on how the deck builder uses what was taken.
