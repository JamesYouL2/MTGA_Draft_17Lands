# Whether Tempo builds and safe-deck promotion earn their place: results

Run [42560809049](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/42560809049)
at `8acc28c`, the same run as `experiments/2026-11-08-deck-score-rating`: 928,062 pools
from 19 sets, 9,397 of them also with the simulator on. The protocol is in
[PROTOCOL.md](PROTOCOL.md). Its predictions were committed before a dry run on part of
HOB, and its amendment before this run. The full report is
[deck_variants.md](deck_variants.md) and the numbers are in
[deck_variants.json](deck_variants.json).

## Verdict

| feature | top deck changes, simulator off | outcome, win rate points | by the rule |
|---|---|---|---|
| Tempo build | 0.12% | +0.34 [+0.11, +0.57] | **keep** |
| Safe-deck promotion | 10.30% | -0.28 [-1.00, +0.44] | **no verdict** |

Neither is removed.

## The bigger finding: the flood penalty decides what comes first

| | simulator off | simulator on, today's app |
|---|---|---|
| Tempo build comes first | under 0.2% of pools | **60.6%** |
| Consistent build comes first | 90.0% | 28.3% |
| removing Tempo changes the top deck | 0.12% | **65.56%** |
| removing promotion changes the top deck | 10.30% | 5.88% |

The penalties change the top deck in 71.5% of pools and its pair in 10.2%. On the
amendment's reading, in a dry run's builds, it's the flood penalty that does this,
because Tempo's 16 lands stay under its threshold. `exp/mana-penalties` already judged
that penalty not worth keeping.

## Tempo

At the same card quality, a full move to Tempo's cards is worth **+0.34 [+0.11, +0.57]**,
2.9 SEs. So the rule says keep: it does better than its rating says.

Without controlling for quality, the same move is **-1.27 [-1.49, -1.05]**. So Tempo's
curve is worth something, and less than the card quality it gives up. Drafters' decks
average -0.27 on the scale from Consistent (-1) to Tempo (+1), so a full move is an
extrapolation.

The amendment said that if the outcome favored Tempo, dropping the flood penalty would
need a second look, as it takes Tempo out of first place. This is that look, and it's
my reading, not the rule's: **keep Tempo as an alternative on the list, and don't put
it first.** Today's app puts first, in most pools, a build that does about 1.3 points
worse on a full move. Without the penalties it's shown second instead: removing it
changes the first two decks in 34.55% of pools and the list in 71.43%.

## Promotion

Promotion changes the top deck in 10.30% of pools, from 2.48% (HOB) to 28.96% (DMU), and
its colors in 93,993. Drafters in the safe colors did 52.2% and in the top's 54.4%, but
with set and player controlled the gap is **-0.28 [-1.00, +0.44]**. That doesn't separate
them, on 7,767 and 51,796 decks.

Past 5% with no clear outcome, the rule gives no verdict, so it stays by default. The
interval rules out a benefit above about 0.44 win rate points for these drafters, so
this is a judgment call about what users want from a Safe label, not one the games make.

## The predictions

1. **Tempo changes the top deck in under 5% of pools: held,** at 0.12%, simulator off.
   With it on it's 65.56%, as the amendment expected. The simulator-off rate decides,
   and it means the app without the penalties.
2. **Tempo's outcome is within 2 SEs of zero: failed.** It's above zero by 2.9 SEs, and
   that's why it stays.
3. **Promotion changes the top deck in under 5% of pools: failed,** at 10.30%. With the
   simulator on it's 5.88%.
4. **Promotion's outcome favors the safe colors: failed.** It leans the other way, within
   its interval.

## What this changes

- **Dropping the mana penalties is the biggest change on the table.** It changes the
  first deck for most users, mostly from a Tempo build to a Consistent one of the same
  pair, so it deserves its own PR and notes for users.
- **The order matters.** `experiments/2026-11-08-deck-score-rating` also ran with the
  simulator off, so it reads as the next step after that one.
- **Nothing was tested together.** How `overall` in the deck score changes these rates
  hasn't been run.

## What it can't show

As the protocol says: it's observational, and drafters who play nearer Tempo's cards, or
three colors, chose to. Few play a Tempo build exactly, and the measure counts spells,
not its 16 lands, so the lands' own effect isn't in it. The -1.27 wasn't deciding and
comes with the same limits. It says nothing about whether a user likes seeing a Tempo
deck or a Safe label.
