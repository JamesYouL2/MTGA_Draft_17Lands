# The off-color penalty by three-color share: results

Protocol: `PROTOCOL.md`. Reports: `heads.md`, `by_set.md`, numbers in the two JSON
files. 204,000 drafts from 17 sets, 156,851 complete events, held-out ratings, pools in
pick order.

## The verdicts

**A flag is supported, by `softer`.** Its change falls as the share rises, by 0.0024
per 10 points of share (SE 0.0008, 3.2 SEs), and the slope keeps its sign without TDM
(-0.0031, 2.1 SEs) and without DMU (-0.0024, 2.8 SEs). Both conditions hold. I
predicted "TDM only", and that was wrong.

| head | line per 10 points of share | without TDM | without DMU | flag |
|---|---|---|---|---|
| `softer` | -0.0024 (0.0008), 3.2 SEs | -0.0031 (0.0015) | -0.0024 (0.0008) | supported |
| `harsher` | +0.0011 (0.0006), 1.7 SEs | +0.0008 (0.0011) | +0.0014 (0.0007) | not at 2 SEs; the direction agrees |
| `third-color` | -0.0011 (0.0015), 0.7 SEs | +0.0047 (0.0027) | -0.0029 (0.0017) | no |

**On all sets together, the app's penalty is about where it should be.** Both
directions lose:

| head | regret slope change (SE) | SEs | verdict |
|---|---|---|---|
| `softer` | +0.0045 (0.0016) | +2.8 | keep the app's |
| `harsher` | +0.0039 (0.0012) | +3.2 | keep the app's |
| `third-color` | +0.0251 (0.0027) | +9.4 | keep the app's |

**It is the high-share sets where softer wins:**

| | `softer` | `harsher` |
|---|---|---|
| TDM and DMU (20%+ share) | -0.0085 (0.0041), better at 2.1 SEs | +0.0083 (0.0032), worse at 2.6 SEs |
| the other 15 sets | +0.0028 (0.0014), worse at 2.0 SEs | +0.0039 (0.0011), worse at 3.5 SEs |

**`third-color` is the clearest loss of any head so far**, at 9.4 SEs, and it doesn't
help even in TDM (-0.0068, SE 0.0126). Judging castability against the lane's first two
colors stays.

## Things to know before building the flag

- **TMT doesn't fit the line.** At a 6.7% share, `softer` is better there by 0.0250
  (3.2 SEs), the largest change of any set, and `harsher` is worse by 0.0190. An earlier
  note has the app's own dataset putting TMT's three-color share at 24% against 17Lands'
  9%, unexplained. If the 24% is nearer the truth, TMT fits. This needs settling, since
  the flag would read the share from the app's dataset.
- **Where the line crosses zero.** `softer` is better from about 15% to 17% share
  (OTJ -0.0036, FRA -0.0030, TLA +0.0014). Twelve of the 17 sets are below that.
- **The gain is small.** In TDM, the set with the most to gain, `softer` is worth
  0.0134, about twice what removing the archetype weight cost on all sets.
- The two samples agree in sign for all three heads on all sets together.

## The predictions

| | predicted | found |
|---|---|---|
| `softer` | line below zero by 2+ SEs, and not without TDM: "TDM only" | below zero at 3.2 SEs, and holds without TDM: wrong on the second half |
| `third-color` | better in TDM by 2+ SEs; all sets, inconclusive | 0.5 SEs better in TDM; all sets, worse at 9.4 SEs: wrong |
| `harsher` | worse in TDM; all sets within 2 SEs | worse in TDM at 2.5 SEs; all sets worse at 3.2 SEs: half right |

## What follows

By the protocol, a second test builds the flag (the penalty's strength as a function of
the share in the app's own dataset) and replays it on new salts. First: how the app
gets the share on a set's first day, and why TMT's differs.

## What it can't show

As the protocol says. The line leans on TDM and DMU. Leaving either out keeps the sign,
but without TDM the slope is at 2.1 SEs.
