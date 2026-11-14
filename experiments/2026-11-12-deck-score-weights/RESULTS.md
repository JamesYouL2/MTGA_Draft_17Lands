# Do the deck score's small weights change what the app suggests: results

Run [43334858566](https://github.com/JamesYouL2/MTGA_Draft_17Lands/actions/runs/43334858566)
at `6b9e29d` (`exp/deck-score-weights` plus a push trigger): 928,062 pools from 19 sets,
724,659 with two-main-color decks. 11,426 pools were skipped, nearly all for a card
missing from the dataset. The protocol is in [PROTOCOL.md](PROTOCOL.md), written before
the run. The full report is [score_weights.md](score_weights.md) and the numbers are in
[score_weights.json](score_weights.json).

## Verdict

| version | suggested deck changes | suggested pair changes | head to head | what to do |
|---|---|---|---|---|
| `no-domain` | 0.93% | 0.08% | too few decks (74 against 61) | **remove the domain bonus** |
| `two-colors-3.5` | 0.54% | 0.25% | +0.86 [-2.69, +4.41], inconclusive | **keep 3.1** |
| `no-missing-fixing` | 0.02% | 0.01% | too few decks | decides nothing |
| `no-domain-or-fixing` | 0.95% | 0.09% | too few decks | decides nothing |

- **The domain bonus goes.** Too few decks differ for a head-to-head verdict, and the
  protocol said the fit decides then. The fit puts it at -0.6 ± 0.2 with the overall
  rating.
- **Two colors stays at 3.1.** 3.5 isn't "better": the two can't be told apart on 772
  decks.

## Where the domain bonus matters: DMU

The 0.93% isn't spread evenly. It's one set:

| set | suggested deck changes without the bonus |
|---|---|
| DMU | 16.26% |
| FRA | 0.95% |
| TLA | 0.15% |
| the other 16 | 0.00% |

Those are the three sets with domain payoffs. So in a domain set, removing the bonus
changes the first deck for about one pool in six, almost always to another build of the
same pair (the pair changes in 0.08% of pools overall).

DMU is where the bonus should earn its place if anywhere, and it doesn't. Fit on DMU
alone, the bonus is -0.6 with the overall rating and +0.1 with the blend. Only FRA
leans its way, at +2.0, and there it changes under 1% of pools. Those per-set fits have
no SEs in the report, so they are a reading, not a test.

## The predictions

- **`no-domain` changes the suggested deck in under 0.5% of pools: failed,** at 0.93%,
  because of DMU. I had the old app's 0.10% on ten other sets in mind.
- **Too few decks differ for its head to head: held.**
- **`no-missing-fixing` changes it in under 1%: held,** at 0.02%.
- **`two-colors-3.5` changes it in 1% to 5%: failed,** at 0.54%. The refit matters less
  than I thought.
- **Its head to head isn't "better": held.**

## The fixing penalty

`missing_fixing` changes the suggested deck in 176 of 928,062 pools. The fit can't
price it and the builds almost never set it off, since the builders rarely make a deck
short of fixing. It decides nothing here. It may still matter for a deck the user
edits by hand, which this run doesn't see.

## What it can't show

As the protocol says: it's observational, only played pairs count, and a changed
suggestion with the same pair isn't judged by the head to head. That is nearly all of
what removing the domain bonus changes, so its evidence is the fit, not this run.
