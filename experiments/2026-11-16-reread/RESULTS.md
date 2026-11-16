# Re-reading earlier runs with regret scaled within each set: results

19 experiments from 22 stored runs, re-read on 2026-11-16 by [reread.py](reread.py).
The protocol is in [PROTOCOL.md](PROTOCOL.md), written before any was re-read. Every
number, old and corrected, is in [reread.md](reread.md).

## Nothing merged rests on a verdict that changed

- **The merged removals stand together.** The joint run compares today's advisor with
  `b74d7ca`, the commit before the first removal (#255), so it covers #255 to #267 in
  one head: -0.0011 (0.0018) corrected, against -0.0018 (0.0020) as first read.
- **Each merged removal stands alone:** Synergy, Premium Fixing, Enables Bomb Splash
  and shrinkage (#255 to #259), curve-heavy (#265) and removal-saturated (#266) are
  all "no objection" on the corrected figure, most of them on the better side.
- **The archetype weight stands:** at zero it is 3.6 SEs worse on held-out ratings and
  flat it is 2.7, both a little firmer than first read.
- **The flag's case stands.** It was read by set, which the fault doesn't touch. The
  one all-sets style figure in it, that a softer penalty is worse in the fifteen
  low-share sets, was +0.0064 (0.0015) and is +0.0053 (0.0015), 3.5 SEs.

## The verdicts that changed

Nine heads change label under the removal rule. None was acted on in the direction
that is now wrong.

| experiment | head | as first read | corrected | what it means |
|---|---|---|---|---|
| composition rules | `no-fixing-block` | +0.0023 (0.0014), no objection | +0.0032 (0.0013), **keep** | the rule was kept anyway; now firmly |
| composition rules | `no-fixing-hunger` | +0.0023 (0.0014), no objection | +0.0032 (0.0013), **keep** | the same |
| needs sweep | `fixing-1.20` | +0.0012 (0.0008), no objection | +0.0017 (0.0007), **keep** | lowering Needs Fixing is worse, as decided |
| fixing above | `fixing-2.00` | +0.0051 (0.0022), keep | +0.0029 (0.0020), **inconclusive** | raising it is no longer clearly worse; 1.4 stays, nothing is better |
| on-lane rerun | `no-on-lane` | +0.0015 (0.0006), keep | +0.0009 (0.0005), 1.7 SEs, **no objection** | see below |
| off-color share | `softer` | +0.0045 (0.0016), keep | +0.0007 (0.0015), **no objection** | softer everywhere is about neutral over all sets, not harmful |
| single pip | `soft-all` | +0.0086 (0.0015), keep | +0.0014 (0.0013), **no objection** | the same |
| single pip | `soft-single` | +0.0093 (0.0014), keep | +0.0020 (0.0013), **no objection** | the same |
| off-color flag, low sets | `flag-plain` | +0.0014 (0.0006), keep | +0.0010 (0.0006), **no objection** | not the head proposed |

**The on-lane 1.1x bonus.** The rerun's "keep" at 2.7 SEs is now 1.7, and the first
test is +0.0010 (0.0008). By the letter that is "no objection" twice. Both runs lean
worse by the same amount on different drafts, which together is about +0.0009
(0.0004), 2 SEs. I'd keep the bonus, and no pull request removed it.

**Softer everywhere.** The old figure said softening the off-color penalty in every
set was worse at 6 SEs. Corrected, it is +0.0014 (0.0013): a 4 SE gain in the four
three-color sets against a 3.5 SE loss in the other fifteen. That is the flag's
design, so the conclusion is the same, but the old "clearly worse overall" was the
scale fault.

## Changes of size without a change of verdict

- **The pack-1 penalty (#274, open):** -0.0001 (0.0015) becomes -0.0017 (0.0014) on
  the ten sets of the splash-rules run. The joint run on new drafts and 19 sets has it
  at +0.0008 (0.0007). The two together are about +0.0003 (0.0006): no sign of a loss.
- **Bomb splash and greedy bomb** are firmer keeps: 3.5 and 3.7 SEs.
- **Third-color castability** is still far worse, 7.1 SEs where it was 9.4.
- **A harsher penalty** is worse at 5.0 SEs where it was 3.2.

## Not fully re-read

The lane-by-count run downloaded 12 of its 20 results before GitHub's download limit
cut in. On those it is "inconclusive" for all four heads, as it was on the full run.

## Predictions

| prediction | result |
|---|---|
| most verdicts stand | right: 52 of 61 rows keep their label |
| one to three verdicts change | wrong: nine do |
| heads that change many picks move the most | partly: the largest moves are the off-color heads, which act unevenly across sets |
| the joint removals run stays within 2 SEs of zero | right: -0.6 SEs |
| the on-lane 1.1x bonus stays "keep" | wrong by the letter: 1.7 SEs |
