# Advisor replay

Measures how often the Draft Advisor's top recommendation matches the card a
real drafter took, using 17Lands public draft dumps. Use it to check whether an
engine change helps before shipping it.

For each sampled draft, every pick is replayed with the pool and lane signals
the app would have had at that point. The advisor is scored alongside two
baselines: highest GIH WR and lowest ATA. Results are reported for all drafters
and for strong ones (60%+ game win rate over 50+ games). They are broken down by
pack and by pick within the pack.

Each cell is `top-1 % / top-3 % / mean rank` of the card actually taken. Picks
with only one distinct card left are skipped.

## Running locally

```bash
SET=FRA
curl -O https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.$SET.PremierDraft.csv.gz
curl -O https://unrealities.github.io/MTGA_Draft_17Lands/${SET}_PremierDraft_All_Data.json.gz

poetry run python Tools/AdvisorReplay/advisor_replay.py run \
    --dump draft_data_public.$SET.PremierDraft.csv.gz \
    --dataset ${SET}_PremierDraft_All_Data.json.gz \
    --drafts 50 --variant baseline --variant arch-overall-pick --out results/$SET.json

poetry run python Tools/AdvisorReplay/advisor_replay.py summarize --per-set results/*.json
```

Drafts are sampled uniformly by hashed `draft_id`, so a run is repeatable.
`--shard i --num-shards k` splits a set's sample across machines without
overlap.

Expect about 2.5 s per draft per variant, plus 1–3 minutes to scan the dump.
For bigger runs, use the **Advisor replay** workflow (Actions → Advisor replay →
Run workflow). It runs each set and shard as a separate job and posts the merged
tables to the run summary.

## Adding a variant

A variant is a context manager in `VARIANTS` that patches the engine while it
is active. For example, `arch-overall-pick` makes the archetype weight follow
the overall pick instead of the pick within the pack. Add an entry, then pass
`--variant <name>`. A variant receives the dataset, for variants that derive
something from it.

`arch-lane` replaces the "top two colors" lane with an archetype: a two- or
three-color combination that covers at least 3% of the set's games (see
`archetype_shares`). In TDM, that is the five clans plus WR. `arch-lane-soft`
also penalizes cards from the other archetypes that contain the top two colors
less (0.7) than cards that are truly off-color.

Deck-score variants. The deck score only feeds picks in pack 3, once the pool
has 23 cards, so these change few picks:

- `deck-refit` sets the aggro, two-color and evasion adjustments to 1.5, 4 and
  −1. These are their worth in wins per point relative to the power, from a
  `pools` run over all ten sets. Because they were fit on the same drafts, this
  is not a held-out test.
- `arch-shrink` scales the 0.7 archetype weight in `get_card_rating` by
  n / (n + 500), where n is the card's games in hand in that pair.
- `deck-refit-shrink` applies both.

Ideas from Draft Omen:

- `do-commit` replaces the castability penalty with soft color multipliers. A
  card on color gets 1.15. A one-pip splash gets 0.95 with a source for it and
  0.85 without. Anything else off color gets 0.75, and fixing gets 1.05. Every
  multiplier is 1 for picks 1–5 and ramps in fully by pick 16.
- `do-gate` plays a triad containing the top two colors only when three conditions hold:
  three-color decks are at least 10% of the set's games, each of the triad's
  colors is at least 20% of the pool's colored cards, and the triad's win rate
  beats the pair's. Win rates are shrunk toward the average with
  (wins + 500 · avg) / (games + 500).
- `do-tiebreak` re-sorts cards within 3 points of the top score by their GIH
  WR in the drafter's pair.
- `do-all` applies the gate, the commitment multipliers and the tiebreak.

Ablations switch off one piece of `evaluate_pack` each, by making its method
return a neutral value (see `ABLATIONS`): `no-bomb`, `no-late-signal`,
`no-synergy`, `no-lane-mult`, `no-vor`, `no-castability`, `no-composition`,
`no-deck-improvement`, `no-wheel` and `no-signal-tiebreak`. If removing a piece
leaves the win regression and match rate unchanged, that piece is a
candidate to delete.

`simplified` switches off every piece the ablations found worth nothing
(composition, VOR, late signal, wheel, signal tie-breaker and the deck
improvement bonus) and uses the `deck-refit` weights. `simplified-arch-lane`
adds `arch-lane`.

## ATA blends

`--blend <name>` (repeatable) re-ranks each variant's advice by
`(1 - w) * z(advisor score) + w * z(-ATA)`, with z-scores taken within the pack.
The weight `w` depends on the pack, the pick within the pack and the overall
pick (see `BLENDS`). Blends are reported as `<variant>+<blend>`. They only
re-sort the advice, so they add almost no time.

ATA is itself the average human pick position, so a blend matching human picks
more often partly reflects that. Strong drafters are still the more telling
group.

## Win rate

Matching picks rewards copying humans. The outcome table asks a different
question: do drafters who follow a method more closely win more?

For each draft and method, the replay records the drafter's mean **regret**. This
is how far below the method's favourite the taken card scored, in SDs of that
pack's scores (0 = always took the method's top card). The replay also records
top-1 agreement and the event result. Then, over complete events (7 wins or 3
losses), `wins` is regressed on each method's regret. The regression controls
for the drafter's win-rate bucket, games bucket and set, and uses robust SEs.
A second column also controls for ATA regret, separating "picked what this
method likes" from "picked like the crowd".

A more negative coefficient means straying from that method costs more wins,
which is evidence that its picks are better. With roughly ±2 wins of noise per
event, a set needs a few thousand drafts before differences between methods are
visible. Use the workflow with many shards for this.

Every method is fit on the same drafts, so their coefficients are correlated. The
"vs first" column therefore gives each method's difference from the first one,
with a bootstrap SE (200 resamples of drafts).

**Calibration.** The replay also scores each final pool with the advisor's own
quick best-deck estimate (`best_deck`). It also computes a simple
yardstick: the mean GIH WR of the best 23 cards in one color pair. Pools are
binned into deciles of deck score within each set, and wins and match win rate
are reported per decile. A well-calibrated score rises steadily across the
deciles. It should also beat the yardstick when both are in the same regression.

**Pieces of the deck score.** The deck score is the power from card ratings
(`75 + 12 z` of the deck's mean rating) plus fixed adjustments: curve, aggro,
two-color, tribal, domain, greedy-mana, evasion and incomplete-deck. The last
table regresses wins on each piece in score points. If the score were weighted
well, each piece would be worth as many wins per point as the power (ratio 1).
A ratio near 0 means the adjustment is noise, and a negative ratio means it
points the wrong way. With 3+ sets, the pieces are also reweighted on every set
but one and tested on the held-out set, next to the current score and the GIH
WR yardstick.

Only final pools are needed for these tables. The `pools` command skips the
per-pick replay and scores each final pool in about 15 ms, so it can use far
more drafts:

```bash
poetry run python Tools/AdvisorReplay/advisor_replay.py pools \
    --dump draft_data_public.$SET.PremierDraft.csv.gz \
    --dataset ${SET}_PremierDraft_All_Data.json.gz \
    --drafts 20000 --out results/$SET-pools.json
```

In the workflow, set **mode** to `pools`.

Caveats specific to these tables:

- The skill buckets include these drafts' own games, so they partly absorb the
  outcome. This understates every method's effect, roughly equally.
- Strong packs make every method's top card easier to take, and they also win
  more. Regret is measured relative to the pack, which limits this but does not
  remove it.

## Caveats

- The card ratings cover the whole format, including the replayed drafts, so
  use the numbers to compare methods, not as out-of-sample accuracy.
- Matching human picks is a proxy. Strong drafters still make mistakes, and the
  advisor may be right where they are not.
- The replay swaps `stack_cards` for a copy without `deepcopy`, which is about
  4× faster. The deck builders only change the top-level `count`, so the
  results are identical; `replay(..., fast=False)` runs the original.
