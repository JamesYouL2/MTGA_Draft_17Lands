# Results: removing the archetype weight on held-out ratings

Protocol: [PROTOCOL.md](PROTOCOL.md), committed before these runs. Fork runs
42530568156 and 42530571055 (no weight), 42530573875 and 42530577169 (flat 0.65):
58,800 drafts from ten sets, 44,544 complete events. Sampled drafts held 2-9% of
each set's dump.

## Verdict

**The weight earns its place in pick order.** On held-out ratings, removing it
makes the regret slope worse by +0.0063 (SE 0.0020), 3.1 SEs. The rebuilt ratings
kept the signal (+0.0086, 4.3 SEs), so the test could answer. By the protocol's
rule: don't remove it on this evidence.

The two samples differ in strength: +0.0096 (3.5 SEs) and +0.0032 (1.3 SEs).

## Regret slope, head minus base

| ratings | no weight | flat 0.65 |
|---|---|---|
| app | +0.0107 (0.0021) | +0.0030 (0.0008) |
| rebuilt | +0.0086 (0.0020) | +0.0025 (0.0008) |
| held out | +0.0063 (0.0020) | +0.0019 (0.0008) |
| held out minus rebuilt | -0.0022 (0.0004) | -0.0006 (0.0003) |

More positive is worse for the head. The leak is real and favored the weight:
holding the drafts out removes about a quarter of the gap, not all of it.

## Reported, not deciding (held-out ratings)

| | no weight | flat 0.65 |
|---|---|---|
| top-1, head minus base | -0.51 points | -0.03 points |
| top card changes | 8.4% of picks | 2.2% of picks |
| top card on-lane, base to head | 75.7% to 75.3% | 75.7% to 75.6% |
| event wins per pick swapped to head's top | -0.060 (0.013) | -0.046 (0.026) |

## The whole-deck test, rerun

`experiments/2026-11-03-rating-parts` accepted pair rates from 10 games in hand
and overall rates from 200, but the app's data has no rate under 500. Rerun with
500 in hand over the dump (fork run 42530580124), the result barely moves: no
archetype predicts better by 27.6% of card quality's worth [25.5, 29.8], against
26.9% before. Weight 0.65 predicts better by 10.8%, against 10.6%.

## How the tests fit together

They still disagree, and they ask different questions. The whole-deck test says
overall GIH WR predicts a finished deck's results better than the pair blend.
The replay says that within a pack, the blend's top card is more closely tied to
wins. Neither shows what an advisor's user would win: the slopes are associations
among drafters who chose freely.
