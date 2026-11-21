# Lane share 0.10 and wheel tiebreak 0.15, together

Written 2026-11-21, before the run.

## Why

Two advisor changes passed on their own in the 8-salt re-read
(`experiments/2026-11-17-measure-salts/reports/heads.md`, run 44122837249):

- `lane-share-0.10`: the lane's share threshold in `_identify_main_colors` from 15% to
  10% of the pool's colored cards. Event wins per swapped pick +0.034 (0.015), +2.3.
- `wheel-0.15`: a card's score times `1 - 0.15 * wheel chance`. Regret slope -0.0004
  (0.0001), -2.9.

They touch different parts of the score (which colors count as the lane; how a card
ranks against others in the pack), but both change top cards, so they could overlap or
undo each other. This run tests them together before either becomes a PR.

## Heads

All on current `origin/main` (`edfab59`), the base:

| head | change |
|---|---|
| `lane-share-0.10` | threshold 0.15 to 0.10 |
| `wheel-0.15` | score times `1 - 0.15 * wheel_pct / 100` |
| `lane-wheel` | both |

Head to head on the same drafts: `lane-wheel` against `lane-share-0.10` (what the wheel
PR adds on top of the lane PR), and `lane-wheel` against `wheel-0.15`.

Advisor heads workflow, ten sets, 8 fresh salts (`r<run>s1..8`) x 1000 drafts, held-out
ratings, salts combined with the between-salt spread (`heads.py`, scaled SE).

## Rule

Both measures as `heads.py` reports them: regret slope change (positive is worse) and
event wins per swapped pick (negative is worse), each in scaled SEs.

1. `lane-wheel` against base must be "adopt": 2 or more scaled SEs better on at least
   one measure and not 2 worse on either.
2. `lane-wheel` against each single head must not be 2 scaled SEs worse on either
   measure.

If both hold, both changes are proposed, as two stacked PRs (lane share first, then the
wheel tiebreak, whose own evidence is then `lane-wheel` against `lane-share-0.10`).

If 1 holds and 2 fails against one single, only that single is proposed. If 1 fails,
neither is proposed from this run. The singles' own verdicts in this run are reported
but don't decide; they passed before.

By set (`by_set.py`) is reported for reading only. No set is dropped after the fact.

## Predictions

- `lane-wheel` against base adopts, mostly on the wheel's regret (about -3 SEs) and the
  lane's event wins (about +2).
- Against each single: within 1.5 SEs on both measures. The re-read had `wheel-0.15`
  against `lane-share-0.10` at +0.7 / -0.9, so no objection between them.
- Top card changes for `lane-wheel` about 3%, near the sum of the two (2.2% and 1.0%).
