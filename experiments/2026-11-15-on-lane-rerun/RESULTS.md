# The on-lane bonus on the fixed harness: results

Protocol: `PROTOCOL.md`. Report: `heads.md`. 120,000 drafts from ten sets, 91,018
complete events, held-out ratings, pools in pick order.

## The verdicts

| head | regret slope change (SE) | SEs | top card changes | verdict |
|---|---|---|---|---|
| `no-on-lane` | +0.0015 (0.0006) | +2.7 | 2.27% | **keep the bonus** |
| `on-lane-flat` | -0.0000 (0.0000) | -1.5 | 0.01% | **the 1.3x can go** |

**The on-lane bonus stays, now by the rule.** Removing it is worse by 2.7 SEs. On 11-08
it was 1.975 SEs and kept against the label. All four samples agree: +0.0018 and
+0.0015 on the two old ones, +0.0016 and +0.0009 on the two new.

The size hasn't changed (+0.0017 then, +0.0015 now). The SE is smaller because there
are twice the drafts. So the truer lane didn't make the bonus worth more, as I
predicted it would; the first result was right and short of drafts.

**The 1.3x for a short pack 3 does nothing.** It applies when pack 3 starts with under
20 on-lane cards, and making it 1.1x changes the top card on 0.01% of picks. Removal is
`simplify/on-lane-flat`.

## The predictions

| | predicted | found |
|---|---|---|
| `no-on-lane` | worse by 2+ SEs | 2.7 SEs: right, though not from a larger effect |
| `on-lane-flat` | "no objection", under 1% of picks | 0.01%: right |
