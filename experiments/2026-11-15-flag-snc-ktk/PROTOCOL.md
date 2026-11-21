# The three-color flag on two sets it has never seen

Written before any result of this run was seen. The only things seen are the two
datasets' three-color shares and card counts.

## Why

`experiments/2026-11-15-off-color-flag` found that `flag-step` (every off-color
multiplier at its square root once three-color decks have 30% of a set's games) passes
its rule in TDM and DMU together, at 3.3 SEs. But the gain was all DMU's: -0.0177 (SE
0.0032) there, +0.0001 (SE 0.0035) in TDM. A threshold backed by one set of two isn't
worth building.

Streets of New Capenna and Khans of Tarkir are three-color sets with 17Lands dumps.
Neither was in any earlier run, and the flag's forms weren't chosen on them. The app has
no dataset for either, because the daily ETL only builds sets on Arena's calendar.

## The datasets

`Tools/AdvisorReplay/build_dataset.py` runs the server's own steps for one set (17Lands
card data for each deck color group, Scryfall, the transform) and writes what the ETL
would publish. The two files are in [datasets/](datasets/), built on 2026-11-15. The
workflow uses them where the app's site has none.

The app's share of three-color games, from those datasets: see the results. Both are
far over 30%, so `flag-step` uses the square root in both.

## The heads

The three patches of `experiments/2026-11-15-off-color-flag/heads/`, unchanged:
`flag-step`, `flag-plain` (power of one minus the share) and `flag-knee` (one minus
the share above 20%).

## What runs

The Advisor heads workflow, held-out ratings, pools in pick order, base upstream main
at `6b6dba9`: SNC and KTK, 6,000 drafts a set and salt, the salts `share1`, `share2`
and `share3`. KTK's dump is small (about a third of TDM's), so its three samples share
more drafts than usual, and its SE is somewhat understated.

## How it is read

`flag-step` decides, on its change in regret slope in each set, from `by_set.py`.

| | verdict |
|---|---|
| better by 2+ SEs in both sets, or in the two together with neither on the worse side | the flag has three sets behind it: build it |
| better by 2+ SEs in one, and on the worse side in the other | mixed: no flag |
| not better by 2+ SEs in the two together | DMU is an exception: no flag, the penalty stays |

"Build it" means a pull request with the share in `SetMetrics` and the step in the
advisor, tested, for the maintainer to judge.

`flag-plain` and `flag-knee` are reported. They take `flag-step`'s place only if
`flag-step` passes and one of them is better in both sets by 2 of its own SEs.

## Predictions

- `flag-step` is better in SNC by 2+ SEs, and within 2 SEs of the base in KTK, as in
  TDM. Mixed or one-sided: I expect "no flag".
- `flag-plain` is worse than `flag-step` in KTK.

## What it can't show

As in the held-out replay. These are older sets (2022 and 2023), and their 17Lands
drafters may not draft like today's.
