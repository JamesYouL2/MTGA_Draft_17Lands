# Auto optimize with only the Power Up swap

Written before any result of this run was seen.

## Why

The Custom Deck window's Auto optimize (`optimize_deck`) builds up to about ten single
swaps of six kinds, simulates each, and keeps the best by a hand-weighted fitness.
`experiments/2026-11-13-builder-leftovers` kept it: it raised the deck score by 0.08
win rate points. All of that came from one kind, Power Up (the worst spell out, the
best castable sideboard spell in), at +0.79 in the 12.1% of decks where the simulation
picked it. Curve Lower, picked most often (33.7%), was -0.02.

If Power Up is the only swap that helps, the button could be that swap alone, with no
simulation to choose it.

## The versions

On the same decks, with a hook in `optimize_deck` that limits which swaps it tries
(`ONLY_KINDS`, `KEEP_BASE`; off by default, so the app is unchanged):

| version | what the button does |
|---|---|
| `app` | as it is |
| `power-sim` | simulates the unchanged deck and the Power Up swap, and keeps the better |
| `power-always` | makes the Power Up swap whenever there is one. No simulation decides |

## What runs

The Deck builds workflow on its 19 sets, salt `three`, with the first 20,000 sampled
40-card decks a set through the button, four times the earlier run. Source is upstream
main at `6b6dba9` with this branch's tools; `optimize_deck` is the same on today's
main.

## The measure

The change in deck score, in win rate points at the score's own price, with
set-clustered SEs: each version's mean, and its mean minus the app's on the same decks
(`report.py`). As before, the app's swaps of a spell for a land count as zero, since
the score can't price a land.

## The decision rule

| | verdict |
|---|---|
| `power-always` minus the app is above zero by 2+ SEs | the button becomes the plain swap: the simulation and the other five kinds go from it |
| not, but `power-sim` minus the app is above zero by 2+ SEs | the other five kinds go; the simulation still decides whether to swap |
| neither | the button stays |

A "go" is a recommendation to the maintainer: this is a button users press, and the
games can't say whether they like what it does.

## Predictions

- `power-always` changes over 90% of decks and raises the score by 0.5 points or more,
  far above the app's 0.08.
- `power-sim` is between the two.

## What it can't show

The deck score rates cards and can't price lands or mana. So the swaps this would
remove from the button (16 or 18 lands, Fix Mana Base, Optimize Mana) are unjudged
here, as they were on 11-13. Curve Lower is judged, and was flat. Power Up picks by the
archetype's win rate and is scored by the overall one, so the score isn't grading its
own choice. And these are decks drafters already tuned; a user presses the button on a
rougher one.
