# The pending advisor changes, together: results

One run of the Advisor heads workflow,
[43814769088](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43814769088):
19 sets, 228,000 drafts, 177,072 complete events, salts `joint1` and `joint2`. The
protocol is in [PROTOCOL.md](PROTOCOL.md), written before the run. Reports:
[heads.md](heads.md), [by_set.md](by_set.md), [within_set.md](within_set.md).

## The all-sets figure was wrong, and is fixed

By the protocol's letter `proposed` fails: `heads.py` put it at +0.0041 (0.0011) on
all sets, 3.7 SEs worse. But the same report put `flag` at +0.0022, 2.8 SEs worse,
when `flag` changes nothing in fifteen sets and is better in each of the other four.
A head can't be worse overall and not worse anywhere.

The cause is in how the slope was scaled. `wins_slope` divides regret by its spread
over every draft in the run. Sets differ in their average regret, so that spread
includes the gaps between sets. A head that moves regret in some sets more than others
changes the scale for all of them, and the slope moves without any pick being better
or worse.

`compare.py`'s `change` now takes regret as z-scores within each set. Within one set
nothing changes, so every by-set number stands. The old figure is kept as
`pooled_change`, and [within_set.py](within_set.py) prints both, with the plain
average of the sets' own changes as a check. The two corrected readings agree.

| head | all sets, as first read | all sets, corrected | the four over 30% | the other fifteen |
|---|---|---|---|---|
| `flag` | +0.0022 (0.0008) | **-0.0047 (0.0006)**, 7.4 SEs better | -0.0203 (0.0030) | 0 |
| `pack1` | +0.0029 (0.0007) | **+0.0008 (0.0007)**, 1.2 SEs worse | -0.0006 (0.0017) | +0.0012 (0.0007) |
| `on-lane-flat` | -0.0000 (0.0000) | -0.0001 (0.0000) | -0.0001 (0.0001) | -0.0000 (0.0000) |
| `proposed` | +0.0041 (0.0011) | **-0.0036 (0.0009)**, 3.9 SEs better | -0.0199 (0.0035) | +0.0012 (0.0007) |
| `proposed-more` | +0.0021 (0.0012) | **+0.0005 (0.0011)** | -0.0044 (0.0029) | +0.0020 (0.0012) |

Positive is worse for the head. The correction was made after seeing the result, so it
is a repair to the measure and not part of the pre-written rule. The check that
motivated it (`flag` is identical to the base in fifteen sets) doesn't depend on
which way any verdict falls.

## Verdict, on the corrected figures

**The three hold together.** `proposed` is not worse by 2 SEs on all sets (it is 3.9
SEs better) or in the fifteen (+0.0012, 1.7 SEs), and is better by 5.7 SEs in the four.

- **The flag keeps its gain alongside `pack1`:** -0.0199 in the four against -0.0203
  alone. In each of the four, set by set: KTK -0.0164, TDM -0.0070, SNC -0.0265,
  DMU -0.0245.
- **`pack1` is the weak one.** It passes its rule, but everything `proposed` loses in
  the fifteen sets is `pack1`: +0.0012 (0.0007), 1.7 SEs worse, in sets where the
  other two change nothing. Its first test was -0.0001 (0.0015) on ten sets, read the
  old way.
- **`on-lane-flat` changes 0.01% of picks** and does nothing measurable.

## Splashable and the premium-removal splash stay

`proposed-more` is worse than `proposed` by 0.0041 on all sets, 3.7 of its own SEs,
over the 2 the rule sets. Nearly all of it is in the four high-share sets, where
dropping the two rules takes the gain from -0.0199 to -0.0044. In a three-color set
those two rules are doing much of what makes the softer penalty work.

## The error bars

[The error-bars test](../2026-11-16-error-bars/RESULTS.md) found the SEs the right
size (0.99), so no bar here is widened.

## Predictions

| prediction | result |
|---|---|
| `proposed` holds: within 2 SEs on all sets, better by 2+ in the four | right on the corrected figure; wrong on the figure as first read |
| in the four, `proposed` is a little less good than `flag` alone | right: -0.0199 against -0.0203 |
| `proposed-more` is within 2 SEs of `proposed` | wrong: 3.7 SEs worse |

## What it can't show

As in the held-out replay. And the error-bars test showed the regret slope does not
see random noise as a loss, so "not worse" here is weaker evidence than "better".
