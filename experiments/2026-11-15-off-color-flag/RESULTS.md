# A three-color flag on the off-color penalty: results

Protocol: `PROTOCOL.md`. Reports: `high_share_*.md` (TDM and DMU, 72,000 drafts, 59,845
complete events) and `other_sets_*.md` (15 sets, 90,000 drafts, 68,518 complete
events), with the numbers in the JSON files beside them.

## The verdict

By the protocol's rule, `flag-step` passes and the other two fail. I recommend against
building it yet, because the pass rests on one set.

| head | TDM and DMU (SE) | SEs | the other 15 sets (SE) | by the rule |
|---|---|---|---|---|
| `flag-step` | -0.0087 (0.0026) | -3.3 | the app, by construction | passes |
| `flag-knee` | -0.0036 (0.0023) | -1.6 | +0.0001 (0.0001) | fails the first condition |
| `flag-plain` | -0.0031 (0.0038) | -0.8 | +0.0014 (0.0006), worse at 2.3 SEs | fails both |

Negative is better for the head.

## Why not build it

The gain is all DMU's. In TDM, the set the flag was first proposed for, it did nothing
on these drafts:

| head | power in TDM | TDM (SE) | power in DMU | DMU (SE) |
|---|---|---|---|---|
| `flag-step` | 0.5 | +0.0001 (0.0035) | 0.5 | -0.0177 (0.0032) |
| `flag-knee` | 0.41 | +0.0012 (0.0045) | 0.73 | -0.0072 (0.0014) |
| `flag-plain` | 0.21 | +0.0123 (0.0071) | 0.53 | -0.0164 (0.0029) |

- **DMU is solid.** Softening to the square root was better by 0.0064 in the first test
  and 0.0177 here. Together: -0.0148 (SE 0.0028), over 5 SEs. A milder power (0.73)
  gets less than half of it.
- **TDM didn't repeat.** The first test had `softer` better by 0.0134 (SE 0.0062); the
  same change on new drafts is +0.0001 (SE 0.0035). The two differ by 1.9 SEs.
  Together: -0.0032 (SE 0.0030), 1 SE. And softening further is worse: at a power of
  0.21, +0.0123 (1.7 SEs).
- So the protocol's guard against a TDM-only flag isn't tripped, but what it guards
  against has happened the other way round. A threshold at 30% is a rule about two
  sets, and only one of them supports it.
- **The share itself isn't what matters, on this evidence.** TDM has the highest share
  by far and no gain. In the first test TMT, at 13.5% on its first day, had the largest
  gain of any set. A flag proportional to the share (`flag-plain`) fails for that
  reason: it softens most where softening helps least.
- The six samples disagree more than their SEs suggest for `flag-step` (-0.0186 to
  +0.0021; chi-squared 10.5 on 5 degrees of freedom), which is one more reason not to
  lean on the pooled 3.3 SEs.

One thing favors the flag beyond the rule: event wins per pick swapped to the head's
top card are above zero for all three heads in TDM and DMU (+0.076, SE 0.015, for
`flag-step`). That measure has disagreed with the regret slope before, unexplained, so
it doesn't decide.

## The predictions

| | predicted | found |
|---|---|---|
| `flag-step` | passes, about -0.008 | passes, -0.0087: right, though not for the reason I expected |
| `flag-plain` | passes; better than `flag-step` in TDM; worse elsewhere by under 2 SEs | fails; worse in TDM; worse elsewhere at 2.3 SEs: wrong |
| `flag-knee` | between the app and `flag-step`; almost nothing elsewhere | -0.0036; changes 0.05% of top cards elsewhere: right |

## What follows

The flag needs a third high-share set before it is worth building. SNC and KTK are
three-color sets with 17Lands dumps and no app dataset; building those two with
`server/extract.py` and replaying `flag-step` on them is the test. If softening helps
there, the flag has three sets behind it. If it doesn't, DMU is an exception and the
penalty stays as it is.

Separately, what DMU and TMT share that TDM lacks isn't known, and I haven't looked.
If it is something about their cards, the fix may not be a set flag at all.

## Notes on the runs

- `other_sets_by_set.md` shows `nan` for `flag-knee`'s line: it changes nothing in ten
  of the fifteen sets, so those have no SE to weight by.
- The by-set tables' share column is the first-day share from `shares.json`, not the
  app's share that the heads read.

## What it can't show

As the protocol says. The forms were chosen after seeing the first test.
