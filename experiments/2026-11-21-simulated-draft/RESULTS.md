# Simulated draft deck score: results

Run [44966063581](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/44966063581)
on the fork, at `f816b13`:

- 10 sets × 8 fresh salts (`r33s1` to `r33s8`) × 1000 drafts.
- Base plus the ten heads in `heads/`.
- `simulate` on.

The reports are in `reports/`:

- `heads.md`: the usual table plus the simulated column.
- `extra.md`: `sim_report.py`, the validation.
- `by_set.md`.

## Verdict

**The measure qualifies on all three pre-registered criteria, by wide margins.**
Adopt it as a third column, for screening and power. Don't put it in the
decision. The run shows the circularity the protocol warned about, concretely:

- The measure reads `gihwr-only` as only slightly worse: 0.05 win rate points,
  a tenth of what it reads for `noise20-a`.
- Event wins put `gihwr-only` past `noise40-a`.
- `gihwr-only` maximises the ratings the deck score's main term reads.

So its power is not a property of the measure. It depends on whether the head's
change runs along what the deck score already believes. For heads that don't
touch those beliefs (noise, lane, wheel), it sees in a few hundred drafts what
event wins need tens of thousands for.

## Criteria

| criterion | needed | read | |
|---|---|---|---|
| (a) `noise20-a`, first 6 salts (59,933 drafts) | ≤ −3 scaled SEs | −0.524 (0.013), **−39.0** | pass |
| (b) `scale`, all salts | within ±1 scaled SE of 0 | +0.000 (0.001), **+0.3** | pass |
| (c) `random-a`, all salts | ≤ −10, and worse than `noise40-a` | −12.306 (0.018), **−685** (`noise40-a` −1.420) | pass |
| (c) `worst`, all salts | ≤ −10, and worse than `noise40-a` | −21.240 (0.021), **−1013** | pass |

`scale` changed 2.0% of decks. One-decimal rounding breaks ties differently once
the scores are squared: 0.16% of top cards changed in the replay. The net effect
was 0.000 points. On the same head, the regret slope read −1.9 SEs, because it
reads the gaps between scores.

## Every head on all three measures (all 8 salts)

Each figure is the estimate (scaled SE), then the number of scaled SEs:

- Regret: positive is worse.
- Swap (event wins per swapped pick) and simulated (deck win rate points, head
  minus base): negative is worse.

| head | regret slope change | event wins per swapped pick | simulated deck win rate | SD per draft | decks changed | top cards changed |
|---|---|---|---|---|---|---|
| `random-a` | +0.2294 (0.0144), +15.9 | −0.076 (0.004), −17.8 | −12.306 (0.018), −685.2 | 3.720 | 100.0% | 80.69% |
| `worst` | +0.4593 (0.0193), +23.8 | −0.077 (0.004), −19.8 | −21.240 (0.021), −1013.1 | 4.798 | 100.0% | 96.73% |
| `noise10` | +0.0003 (0.0012), +0.3 | −0.022 (0.014), −1.6 | −0.148 (0.008), −19.2 | 1.247 | 93.7% | 9.15% |
| `noise20-a` | +0.0022 (0.0022), +1.0 | −0.038 (0.010), −3.7 | −0.522 (0.009), −56.1 | 1.551 | 99.3% | 17.30% |
| `noise40-a` | +0.0132 (0.0041), +3.3 | −0.054 (0.008), −6.7 | −1.420 (0.012), −120.9 | 1.909 | 99.9% | 29.49% |
| `scale` | −0.0040 (0.0021), −1.9 | −0.067 (0.095), −0.7 | +0.000 (0.001), +0.3 | 0.128 | 2.0% | 0.16% |
| `lane-share-0.10` | −0.0047 (0.0020), −2.3 | +0.056 (0.028), +2.0 | +0.095 (0.002), +40.3 | 0.516 | 27.8% | 2.18% |
| `wheel-0.15` | −0.0007 (0.0002), −2.9 | +0.097 (0.050), +2.0 | +0.053 (0.002), +22.4 | 0.438 | 27.3% | 1.04% |
| `no-needs-2drops` | −0.0002 (0.0003), −0.5 | −0.031 (0.096), −0.3 | −0.000 (0.000), −0.3 | 0.095 | 3.3% | 0.33% |
| `gihwr-only` | +0.1089 (0.0099), +11.0 | −0.050 (0.006), −8.9 | −0.049 (0.010), −5.0 | 2.288 | 99.9% | 40.45% |

heads.py's decisions on regret and swap are unchanged:

- `lane-share-0.10` and `wheel-0.15`: adopt, each again at swap +2.0.
- `noise20-a`: worse (swap).
- `noise40-a`, `random-a`, `worst` and `gihwr-only`: worse (both).
- The rest: no objection.

`extra.md` has the same tables on the first 6 salts.

## Relative power

The figure is each measure's scaled SEs per square root of the drafts it used
(complete events for regret and swap), with the drafts each would need to put the
head 3 scaled SEs from zero.

| head | drafts for 3 SEs: regret / swap / simulated | swap needs × as many as simulated |
|---|---|---|
| `noise10` | 6.6M / 219,000 / 1,950 | 112 |
| `noise20-a` | 546,000 / 40,000 / 228 | 175 |
| `noise40-a` | 52,000 / 12,300 / 49 | 250 |
| `random-a` | 2,150 / 1,730 / 2 | 1,129 |
| `worst` | 960 / 1,400 / 1 | 1,990 |
| `lane-share-0.10` | 103,000 / 135,000 / 443 | 306 |
| `wheel-0.15` | 65,000 / 143,000 / 1,440 | 100 |
| `gihwr-only` | 4,500 / 6,900 / 29,000 | **0.24** |
| `no-needs-2drops`, `scale` | (near zero on every measure) | |

The measure is precise because the paired per-draft difference is small and
nearly deterministic. For `noise20-a` the SD is 1.55 points, against an event's
wins, which swing by several wins. The SEs do count the spread between salts
(the held-out ratings differ per salt), as the other measures' do.

## Sign agreement

Across the eight heads that move at all, the simulated measure agrees in sign
with event wins (swap). It reads `no-needs-2drops` and `scale` as zero.

| head | regret | swap | simulated |
|---|---|---|---|
| `lane-share-0.10` | + | + | + |
| `wheel-0.15` | + | (+) | + |
| `gihwr-only` | − | − | − |
| `no-needs-2drops` | (+) | (−) | (−) |
| noise controls, `random-a`, `worst` | − or (−) | − or (−) | − |

Brackets mark readings under 2 scaled SEs.

The noise controls come out in order: −0.148, −0.522, −1.420, then −12.3 for
`random-a`. Event wins could not tell `worst` from `random-a`; the simulated
measure reads them −21.2 against −12.3.

## Magnitudes: where the circularity shows

*Not pre-registered: a rough reading added after the results.*

This puts both measures in event wins per draft:

- **Swap:** event wins per swapped pick × the share of top cards changed × 41.8
  picks a draft. This assumes the advisor drives every pick, so it is crude.
- **Simulated:** the simulated change × 0.138. That figure is the sanity check's
  slope of event wins on the drafter's own deck win rate.

| head | event wins per draft, from swap | from simulated | ratio |
|---|---|---|---|
| `worst` | −3.11 | −2.93 | 1.1 |
| `random-a` | −2.56 | −1.70 | 1.5 |
| `noise40-a` | −0.67 | −0.20 | 3.4 |
| `noise20-a` | −0.28 | −0.072 | 3.8 |
| `noise10` | −0.084 | −0.020 | 4.1 |
| `lane-share-0.10` | +0.051 | +0.013 | 3.9 |
| `wheel-0.15` | +0.042 | +0.007 | 5.8 |
| `gihwr-only` | −0.85 | −0.007 | **125** |

For most heads the two measures differ by a steady factor of about 4. That factor
is consistent with the deck score seeing only part of what decides an event, and
the swap extrapolation overstating.

`gihwr-only` is off by two orders of magnitude:

- It drafts the highest-rated card every pick and leaves its colours to the deck
  builder.
- The deck builder picks the best two colours from a pool full of strong cards.
- The deck score's card quality term reads exactly those ratings, so the deck
  scores almost as well as the base's.
- Event wins say those drafts go badly.

This is the protocol's caveat in practice. The measure can't grade a change to
what the deck score itself believes, here how much colour discipline matters
against raw card quality.

## The wheel approximation

| copy | wheel swaps applied | dropped | applied share |
|---|---|---|---|
| base | 144,817 | 854,706 | 14.5% |
| `wheel-0.15` | 137,091 | 856,790 | 13.8% |
| `gihwr-only` | 84,900 | 879,094 | 8.8% |
| `random-a` | 368,746 | 919,453 | 28.6% |
| `worst` | 458,043 | 888,049 | 34.0% |

A swap is applied when the advisor's card is still in the returning real pack. Of
the base's 1,436,800 wheel picks (picks 9 and on), about one swap in seven is
applied. The other six are dropped because another drafter took the advisor's
card, and the returning pack is left as it really was.

This has a bias. A card the advisor passed (the drafter's card H) comes back only
if the advisor's own card A also went round. So a strategy that counts on cards
wheeling gets less credit than it would in a real pod. Even so, `wheel-0.15`
read +22 SEs.

Every copy had:

- 16,031 forced picks: 16,000 TLA/TMT first picks plus 31 other gaps;
- 96 drafts skipped because their pools don't account for the gaps;
- 83 quick builds, where the pool was short of 15 spells. These are the same 83
  drafts whatever the advisor picked, which points to truncated drafts.

## Sanity check

The check uses 60,603 complete events from the base replay. Both quantities are
centred within set. The base agrees with the drafter on 35.0% of decided picks.

| deck | events | r (SE) | event wins per deck win rate point |
|---|---|---|---|
| advisor's draft, full agreement for the whole draft | 6 | too few: fallback used | |
| drafter's own pool, Suggest Deck | 60,603 | **+0.212 (0.004)** | +0.138 |
| advisor's draft, all events | 60,603 | +0.094 (0.004) | +0.092 |
| advisor's draft, agreement share 0.00–0.28 | 23,138 | +0.032 (0.007) | +0.031 |
| advisor's draft, agreement share 0.28–0.41 | 22,319 | +0.074 (0.007) | +0.073 |
| advisor's draft, agreement share 0.41–1.00 | 20,978 | +0.136 (0.007) | +0.141 |

**The deck score does track real results.** The drafter's own pool scores
correlate 0.21 with the event's wins. The slope is 0.138 event wins per predicted
win rate point. In a Premier event, a real point of game win rate is worth about
0.10 to 0.12 event wins at 50–60%, so the score's win rate scale is about right,
if anything a little cautious.

The advisor's simulated deck tracks the real event more as its pool overlaps the
drafter's.

Caveats:

- Better drafters build better pools and also play better. Some of the 0.21 is
  skill, so this is an upper bound on what the deck alone predicts.
- Suggest Deck's deck is not necessarily the one the drafter played.

## Predictions against outcomes

| prediction | outcome |
|---|---|
| (a) passes, `noise20-a` ≥ 4 SEs on 6 salts, power ratio ≥ 3 | right: 39.0 SEs, ratio 175 |
| (b) passes with < 1% of `scale`'s decks changed | passes, but 2.0% changed (ties), net 0.000 |
| (c) passes widely, `worst` worse than `random-a` | right: −21.2 against −12.3 |
| noise controls in order | right |
| `lane-share-0.10` better | right: +40 SEs |
| `gihwr-only` worse, less certain | right in sign (−5.0), but far too small: see magnitudes |
| `wheel-0.15` under 2 SEs | wrong: +22.4 |
| `no-needs-2drops` under 2 SEs | right: −0.3 |
| full agreement too rare, so the fallback is used | right: 6 events |
| `drafter_win` r between 0.1 and 0.3 | right: 0.212 |
| advisor deck's r rises with agreement | right: 0.03, 0.07, 0.14 |
| adopt as a third column for screening, outside the decision | that is the verdict |

## Runtime

- Each replay job averaged 16 minutes (longest 23) for 11 copies × 1000 drafts
  with simulation, at 4 copies at a time.
- The whole run took 2 h 41 min of wall time, most of it waiting for runners.
- The report job took 32 minutes, with `sim_report.py` redoing the per-salt
  bootstraps.

## How to use it

- Run heads with `simulate` on. It roughly doubles the replay time.
- Read the simulated column beside swap. When both agree in sign, the simulated
  SE says how sure the direction is, with far fewer drafts.
- When they disagree, or when the simulated effect is much smaller than swap's
  per-draft size (the `gihwr-only` pattern), the head is changing something the
  deck score values differently from real play. Trust event wins.
- Never adopt on the simulated measure alone. That holds for any change to
  ratings, colour discipline, or the deck score itself.
