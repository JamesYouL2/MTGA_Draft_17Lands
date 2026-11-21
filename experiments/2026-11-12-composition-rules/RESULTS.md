# Do three composition rules earn their place on held-out picks: results

Run [43314302525](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43314302525)
at `29eb292` (`exp/composition-rules` plus a push trigger): ten sets, two samples, 60,000
drafts and 45,451 complete events, on held-out ratings only. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. The full report is
[heads.md](heads.md) and the numbers are in [heads.json](heads.json).

## Verdict

| head | regret slope change (SE) | SEs | top card changes | by the protocol | what to do |
|---|---|---|---|---|---|
| `no-curve-heavy` | -0.0033 (0.0011) | -2.9 | 1.96% | no objection | **remove** |
| `no-removal-saturated` | -0.0013 (0.0007) | -1.8 | 1.80% | no objection | **remove** |
| `no-fixing-hunger` | +0.0023 (0.0014) | +1.7 | 4.01% | no objection | **keep, against the label** |
| `no-fixing-block` | +0.0023 (0.0014) | +1.6 | 4.18% | no objection | not used |
| `no-three` | -0.0011 (0.0018) | -0.6 | 7.58% | no objection | a check only |

Positive is worse for the head.

- **Curve Too Heavy** goes. Without it the slope is better by 2.9 SEs, in both samples
  (-0.0033 and -0.0031). The game-results test didn't support the rule either.
- **Removal Saturated** goes. Without it the slope leans better, at 1.8 SEs, and both
  samples agree in sign. The game-results test leaned against the rule too.
- **Needs Fixing stays.** The label is "no objection", but the head is 1.7 SEs worse. The
  protocol said beforehand that a head between 1.5 and 2 SEs worse would be kept, as
  on-lane was at 1.975. Both samples agree in sign: +0.0028 (0.0018) and +0.0019 (0.0020).

## Needs Fixing: the evidence is mixed

Two readings point the other way, and neither was deciding:

- Event wins per pick swapped to the head's card are +0.084 (SE 0.019), in the head's
  favor. For on-lane that measure agreed with the slope. Here it doesn't.
- Top-1 rises 0.87 points without the rule. Where the top card changes, drafters took
  the head's card 41% of the time and the rule's 17%.

So drafters mostly don't follow this rule, and those who took the other card didn't do
worse for it. But the measure the protocol chose says the rule's picks go with wins,
short of 2 SEs. The game-results test couldn't settle it (-0.03 [-0.27, +0.20] per
card). I'm not removing a rule on that. A weaker multiplier than 1.4x is the obvious
thing to try next: the game test's interval reaches about 40% of the rule's size.

`no-fixing-block` reads the same as `no-fixing-hunger`, so letting lands and fixing
cards earn the other rules changes nothing that shows here.

## The predictions

- **All three single heads get "no objection": held** by the label. One of the three is
  kept anyway, by the protocol's own 1.5 SE note.
- **`no-fixing-hunger` changes the top card on 1% to 5% of picks: held,** at 4.01%.
- **The other two change it on under 1%: failed.** They change 1.96% and 1.80%. These
  rules do more than I thought.
- **`no-fixing-block` differs from `no-fixing-hunger` on under 0.2% of picks:** not
  measured directly. Their rates of change against the base differ by 0.17 points,
  which is a floor on it, not the number.
- **`no-three` is within 2 SEs of the sum of the three: held.** The sum is -0.0023 and
  `no-three` is -0.0011 (0.0018).

## What it can't show

As the protocol says: slopes are associations among drafters who chose freely, and
regret says whether drafters who followed an advisor won, not what its users would win.

Removing Curve Too Heavy and Removal Saturated together, without the fixing rule, wasn't
run. `no-three` is the nearest check, and it includes the fixing change. Their single
changes sum to -0.0046.
