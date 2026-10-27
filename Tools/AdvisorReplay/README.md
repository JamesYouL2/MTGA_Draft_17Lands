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
`--variant <name>`.

## Caveats

- The card ratings cover the whole format, including the replayed drafts, so
  use the numbers to compare methods, not as out-of-sample accuracy.
- Matching human picks is a proxy. Strong drafters still make mistakes, and the
  advisor may be right where they are not.
- The replay swaps `stack_cards` for a copy without `deepcopy`, which is about
  4× faster. The deck builders only change the top-level `count`, so the
  results are identical; `replay(..., fast=False)` runs the original.
