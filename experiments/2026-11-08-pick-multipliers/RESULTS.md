# Do the advisor's small multipliers earn their place: results

Run [42558680265](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/42558680265)
at `467b4b0` (`6120746` plus a push trigger): ten sets, two samples, 60,000 drafts and
45,451 complete events, on held-out ratings only. The protocol is in
[PROTOCOL.md](PROTOCOL.md), written before the run. The full report is
[heads.md](heads.md) and the numbers are in [heads.json](heads.json). The report's
`no-shrinkage` row belongs to `experiments/2026-11-08-shrinkage-replay`.

## Verdict

| head | regret slope change (SE) | top card changes | by the protocol | what to do |
|---|---|---|---|---|
| `no-synergy` | 0 (control) | 0.00% | can't change anything | remove: dead code |
| `no-bomb-splash` | +0.0001 (0.0001) | 0.01% | no objection | remove |
| `no-premium-fixing` | -0.0005 (0.0006) | 0.78% | no objection | remove |
| `no-on-lane` | +0.0017 (0.0009) | 2.37% | no objection, at 1.97 SEs | **keep, against the label** |

Positive is worse for the head.

- **Synergy:** the control passed. Every pick matches the base's, so the harness only
  changes what a patch changes. The report labels it "keep" because 0 >= 2 x 0.
  `heads.py` now says "no change", and the report is left as the run wrote it. The
  rule never fires in any dataset checked, so it can go without a test.
- **Enables Bomb Splash** goes by the protocol's two-part rule. The replay has no
  objection, and the game-results test on `exp/bomb-splash-rule` doesn't support it:
  +0.01 win rate points per card [-0.06, +0.08].
- **Premium Fixing:** nothing here says it helps.

## On-lane: why not to act on the label

The rule's bar is 2 SEs. `no-on-lane` is at 0.001699 / 0.000860 = 1.975. The rule says
"no objection", and that's a bootstrap's noise away from "keep". This is my judgment,
not the rule's:

- It's the one head here that changes much: the top card on 2.37% of picks, and 77%
  of those changes take an on-lane card away.
- Event wins per pick swapped to the head's card are -0.101 (SE 0.026). That wasn't
  deciding, and drafters who take off-lane cards may be weaker anyway, but it's the
  same direction, at nearly 4 SEs.
- Top-1 falls 0.56 points. The protocol warned this favors the base, so it adds little.
- Both samples agree in sign: +0.0010 (0.0012) and +0.0024 (0.0012).

The change is about a quarter of what no archetype weight cost, +0.0063. So this
doesn't show a large loss. It doesn't clear the rule either.

## The predictions

- **`no-on-lane` worse by 2+ SEs failed,** narrowly, at 1.975.
- **The other three get "no objection" and change the top card on under 1% of picks:**
  held for `no-bomb-splash` and `no-premium-fixing`. `no-synergy` can't be read as
  holding: the amendment made it a control.

## What it can't show

As the protocol says: slopes are associations among drafters who chose freely, and
regret says whether drafters who followed an advisor won, not what its users would win.
"No objection" isn't proof of equivalence.

Each head removes one rule. Removing several together hasn't been run, though each
changes so few picks that they shouldn't interact much.
