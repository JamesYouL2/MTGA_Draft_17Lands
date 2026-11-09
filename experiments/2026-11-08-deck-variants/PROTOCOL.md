# Whether Tempo builds and safe-deck promotion earn their place

Written before any result in this folder was seen.

## Why

Two parts of `suggest_deck()` may be doing little:

- **The Tempo build** (`build_variant_curve`) picks 24 spells, rating +4 for 2 mana or
  less and -8 for 5 or more. The deck score fit curve at about zero once card quality
  was counted, and leaves it out. So a Tempo build gives up rating for something it
  isn't scored on, and should rarely come first.
- **Safe-deck promotion** moves the best deck of up to two colors to the top if it's
  within 6 points (`SAFE_DECK_PROMOTE_TO_TOP_GAP`), or to second if within 20. The
  score already gives two colors +3.5, fit to game results.

Nothing has measured how often either changes what a user sees. Neither has been
tested against game results.

## What runs

The same run as `experiments/2026-11-08-deck-score-rating`: the Deck builds workflow on
19 sets, up to 50,000 decks each, salt `""`, with the same pools and held-out ratings.
Every version scores with the blend.

| version | what changes |
|---|---|
| `blend` | nothing: today's, apart from the simulator |
| `no-tempo` | `build_variant_curve` builds nothing |
| `no-promotion` | both gaps set so that nothing is promoted. The safe deck is still kept and labeled |
| `neither` | both |

**The simulator** is off in these, as its penalties are already judged not worth
keeping. The app has them today, though, so the first 500 pools of each set also run
all four versions with it on. Each deck is simulated once per pool, so its randomness
can't separate versions. The verdict reads the simulator-off rates, and the report
shows both.

## The measures

**How often it changes what's shown,** against `blend`: the share of pools whose top
deck, first two decks, or set of shown decks differs. Overall and by set. A deck is
its exact cards.

**Tempo's outcome.** Among two-color decks where the pair's Tempo and Consistent builds
have different spells, I place the played deck between them: the share of Tempo-only
cards it plays less the share of Consistent-only cards it plays, from -1 to +1. The
measure is a logistic regression of games won on that position, controlling for its
card quality (deciding), pair by set and the player's buckets. A full move toward
Tempo's cards, in win rate points. It's reported without quality too. Quality is the
control because Tempo gives up rating on purpose: it earns its place if it does better
than its rating says.

**Promotion's outcome.** In pools where promotion changes the top deck's identity
colors: decks whose colors are within the safe deck's, against decks whose colors
include all the unpromoted top's. Set and player controlled, in win rate points.

Both need 100+ decks, on each side for promotion, and use the larger of model and set-clustered
SEs, 95% intervals.

## The decision rule

For each of the two features, with the outcome signed so that positive favors it:

| | verdict |
|---|---|
| outcome favors it by 2+ SEs | keep |
| outcome is against it by 2+ SEs | remove |
| neither, and it changes the top deck in under 5% of pools | remove |
| neither, in 5%+ of pools | no verdict: the test doesn't settle it |

Under 5% means most users would never see a different first deck. Without an outcome
in its favor, that doesn't justify the code. No outcome to read, for lack of decks,
counts as neither. Top-deck change is the measure because it's what a user sees first.
The other two are reported.

Removing a feature is a separate PR after this, each with its own tests.

## The prediction

1. **Tempo** changes the top deck in under 5% of pools.
2. **Tempo's outcome** is within 2 SEs of zero at the same card quality, so the rule
   removes it. This can fail: the fit left curve out on average, not for this move.
3. **Promotion** changes the top deck in under 5% of pools. This is less sure: the
   deck builder keeps a soup build for every pool, and scores it within reach.
4. **Promotion's outcome** favors the safe colors. Whether by 2+ SEs, I don't predict.
   Players who play three colors are few and unusual.

## What it can't show

- **It's observational.** Drafters who play nearer Tempo's cards, or three colors,
  chose to. Buckets take out only part of who they are. A pool's cards decide both
  which deck can be built and how good it is: in promotion's case, the pools where a
  third color is tempting are unusual pools.
- **Tempo's position isn't the Tempo build.** Few drafters play exactly it. The
  estimate extrapolates from partial moves, and it can't see land count: a Tempo build
  plays 16 lands, and this counts spells only.
- **A user isn't measured.** A second deck on the list may be useful even if never
  first, and a Safe label may help a user decide. This counts only what's shown and
  what the games say.
