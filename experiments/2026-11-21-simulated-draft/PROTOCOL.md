# Simulated draft deck score: a third measure for advisor heads

Written and committed before the run's results were read. A 40-draft local smoke
test of the tooling (HOB, not held out, base plus `scale`, `noise20-a` and
`random-a`) was run first to check that the code works. Its numbers are too small
to read and are not used.

## The question

The heads workflow grades a change to the advisor on two measures (see
`experiments/2026-11-17-measure-salts`). Both look at the picks the advisor
would have changed in drafts that real people made:

- the regret slope;
- event wins per swapped pick, the measure that has the power.

Neither looks at the deck the advice would have led to. The simulated draft deck
score does. Can it grade heads, and how many drafts does it need compared with
event wins?

## The measure

For each sampled draft, the advisor, base or head, drafts the whole draft itself.
It sees the packs the real drafter saw and takes its own first choice at every
pick. The app's deck builder then builds its final pool: the first deck Suggest
Deck offers, which is what the app shows a user first. The app's fitted deck score
scores that deck. The score is turned into an expected game win rate with
`WIN_LOG_ODDS_AT_BASE` and `WIN_LOG_ODDS_PER_POINT` (`src/advisor/deck_scorer.py`).

The measure is head minus base, paired per draft, in win rate points, positive
better. It is combined over salts as the other two are: the per-salt bootstrap SE,
then `compare.combine` (DerSimonian-Laird, modified HKSJ, scaled SE = SE × t/1.96
on salts − 1 df).

Code:

- `Tools/AdvisorReplay/simulate.py` simulates the draft.
- `replay.py --simulate` runs it alongside the replay.
- `heads.py` prints the new table.
- `sim_report.py` (this folder) prints the validation.

### Design choices

- **The packs (the wheel approximation).** In an eight-player pod, the pack at
  pick p was last seen at pick p − 8.
  - Picks 1 to 8 of a round see packs the drafter's own picks never touched, so
    they are exact.
  - From pick 9, if the advisor took A where the drafter took H, the returning
    pack would hold H and not A. So if A is in the real returning pack, A is
    swapped for H, and the swap carries to the next lap.
  - If A is not there, another drafter took it in the real draft. What they would
    have taken instead is unknown, so the pack is left as it was and the swap is
    dropped.
  - The other drafters are assumed to pick as they did.
  - The report counts how often a swap is applied and how often it is dropped.
- **Missing picks.** The TLA and TMT dumps have no P1p1 row. Those picks are
  forced: the advisor gets the drafter's card, read from the pools. A draft whose
  pools don't account for its missing picks is skipped and counted.
- **Which drafts.** These are sample.py's Premier Draft dumps, which are
  eight-player pods that take one card a pick. A pick with one distinct known card
  takes it.
- **Ratings.** The advisor, the deck builder and the deck score all read the same
  held-out ratings as the replay, so no draft is graded on ratings that include its
  own games.
- **Speed.** Suggest Deck's simulator statistics and sideboard are display-only:
  they don't choose or order the decks. replay.py stubs them out. The deck lists
  and their order were checked to be the same on 40 pools, and the stubs make
  Suggest Deck about 20 times faster.
- **Not part of the decision.** heads.py still decides on regret and swap. The new
  measure is printed beside them.

## The run

- **Base:** origin/main at `edfab59`, plus the heads tooling from
  `exp/measure-salts` and this experiment's tooling.
- **Heads:** this folder's `heads/*.patch`.
- **Run:** the heads defaults, 10 sets × 8 fresh salts × 1000 drafts, with
  `simulate` on and `extra` set to this folder's `sim_report.py`.

| head | kind | from |
|---|---|---|
| `random-a` | control: fixed random score per card | 2026-11-16-measure-power |
| `worst` | control: the advisor upside down | 2026-11-16-measure-power |
| `noise10` | control: ±10% noise per card | 2026-11-16-error-bars (`noise10-y`) |
| `noise20-a` | control: ±20% noise per card | 2026-11-16-measure-power |
| `noise40-a` | control: ±40% noise per card | 2026-11-16-measure-power |
| `scale` | control: final score → max(0, score)² / 50, which keeps the order | new |
| `lane-share-0.10` | known change | 2026-11-17-measure-salts |
| `wheel-0.15` | known change | 2026-11-17-measure-salts |
| `no-needs-2drops` | known change | 2026-11-17-measure-salts |
| `gihwr-only` | known change: win rate alone, no rules | 2026-11-16-measure-power |

## Criteria

The measure **qualifies** if all three hold:

- **(a) Power.** `noise20-a` reads at least 3 scaled SEs worse, combined over the
  first 6 of the 8 salts (by name). In a full run that is 60,000 drafts, the number
  event wins needed for 3.7 SEs on 20% noise on 11-16.
- **(b) Ignores scale.** `scale` reads within 1 scaled SE of zero over all salts.
  - The simulated draft depends only on each pick's top card, so this should hold
    by construction.
  - Where it fails, the cause is ties that the one-decimal rounding of scores
    breaks differently. The report gives `scale`'s top-card changes, and the
    regret slope's reading of it, for contrast.
- **(c) Sees large damage.** `random-a` and `worst` each read at least 10 scaled
  SEs worse over all salts, and each reads worse than `noise40-a`.

Reported, not criteria:

- **Relative power.** Each measure's scaled SEs per square root of a draft (events
  for regret and swap, the drafts each actually uses), the drafts each would need
  for 3 scaled SEs, and the ratio of simulated to swap on each control.
- **Sign agreement with event wins (swap), and with regret, on every head.** The
  known changes matter most here: event wins in 2026-11-17 read `lane-share-0.10`
  +2.3, `wheel-0.15` +1.9 and `no-needs-2drops` +2.0 better, and 2026-11-16 read
  `gihwr-only` 10.3 worse.
- **Order of the noise controls:** does the measure grade `noise10`, `noise20-a`,
  `noise40-a` and `random-a` in that order?
- **The sanity check** (below).

## The circularity caveat

The measure grades advisors by the app's own beliefs about decks, and the advisor
shares many of them:

- **The same ratings.** The deck score's card quality term reads the same GIH WR
  ratings that the advisor's base score is built from.
- **The same rules.** Its two-colour, fixing and curve terms encode the same
  ideas as the advisor's lane, splash and needs rules.

So a head that moves the advisor toward what the deck score already values will
read well whether or not real decks win more. Two examples:

- `gihwr-only` may read well on card quality while event wins say it is worse.
- A rule that adds needs, such as 2-drops, may read well on the curve term while
  event wins are indifferent.

Noise and damage controls are caught partly for the same reason: they lower card
quality by the same ratings.

Against that, the deck score's weights and its win rate link were fitted to
17Lands decks' game results, so it carries some outside truth. The sanity check
measures how much.

Whatever the criteria say, the measure is at most:

- a fast screen for heads that make pick-level changes;
- a way to see deck-level harm.

A head that changes what the deck score itself believes in is graded by event
wins, not by this measure.

## The sanity check

Does the deck score of a pool track the event's real wins? This is read on the
base replay's complete events, with both quantities centred within set. The report
gives r, its SE, and the slope.

- **Planned:** the advisor's simulated deck for drafts where the advisor agrees
  with the drafter for the whole draft. Its pool is then the drafter's own.
- **Expected problem:** top-1 agreement is about 50% a pick, so almost no draft
  will agree all the way. If fewer than 30 such events exist, the fallback is used:
  - the drafter's own final pool, built by Suggest Deck and scored the same way
    (`drafter_win`), against the event's wins. This is the closest available test
    of whether the score tracks real results;
  - the advisor's simulated deck against the event's wins, in thirds of agreement
    share. The correlation should rise with agreement if the score tracks real
    decks.

Caveat: the drafter built their own deck, which may not be Suggest Deck's.

## Predictions

- (a) passes. 20% noise lowers card quality in every draft, and the paired
  per-draft difference is far less noisy than an event's wins. Simulated reads
  `noise20-a` at least 4 scaled SEs worse on 6 salts, with a power ratio against
  swap of 3 or more.
- (b) passes, with fewer than 1% of `scale`'s decks changed.
- (c) passes by a wide margin. `worst` reads worse than `random-a`, which event
  wins could not tell apart.
- The noise controls come out in order.
- Sign agreement with event wins:
  - `lane-share-0.10`: agrees, better.
  - `gihwr-only`: worse on simulated as well, because off-colour picks lose two
    colours. Less certain than the others.
  - `wheel-0.15`: under 2 SEs either way.
  - `no-needs-2drops`: under 2 SEs, sign uncertain.
- Sanity check:
  - fewer than 30 full-agreement events, so the fallback is used;
  - `drafter_win` correlates positively with wins, r between 0.1 and 0.3;
  - the advisor deck's r rises with agreement share.
- Verdict, if (a) to (c) pass: adopt the measure as a third column for screening
  and power, not as part of the decision, because of the circularity.
