# Advisor replay

Measures a change to the draft advisor on real drafts. It replays picks from
17Lands' public Premier Draft data through two copies of the app (a pull
request and its base) and compares them on the same drafts.

It is separate from the app: nothing in `src/` imports it, and the app's tests
don't run it. CI runs the harness's own tests on every pull request, so a change
to the app that breaks the harness fails there.

## What it reports

- **Picks:** how often the card the drafter took was the advisor's first
  choice (top-1) or among its first three (top-3), for all drafters and for
  strong ones (60%+ game win rate over 50+ games). Picking by highest GIH WR is
  shown as a yardstick.
- **Event wins:** in finished events, how event wins relate to
  - *regret*: how far the drafter's picks fell below the advisor's top choice,
    in standard deviations of the pack's scores. If an advisor knows better
    picks, drafters who stray from it should win less, so more negative is
    better;
  - *rank regret*: how many cards the advisor ranked above the drafter's pick
    (0 when they took its top card). More negative is better;
  - *missed top*: the share of picks that weren't the advisor's top card. More
    negative is better;
  - *deck score*: the app's score for the best quick build of the final pool.
    More positive is better. Pool GIH WR is shown as a yardstick.

  Each is per +1 SD of the draft's mean and controls for set and the drafter's
  skill and games buckets.

  Read the three pick measures together. Regret in SDs reads how the advisor spaces
  its scores within a pack as well as the order it puts the cards in: two
  advisors that order every pack the same can differ on it. Rank regret and
  missed top read only the order. A learned pick model once read 4.2 SEs worse
  than main on regret but no worse on rank regret (0.5 SEs better) or missed top
  (1.9 SEs better), and giving its order main's score gaps took the whole
  regret difference away. A head that's worse on regret alone has spaced its
  scores differently; worse on all three, it orders the cards worse.
- **Head minus base** for each, with a paired bootstrap standard error. Treat a
  difference smaller than about two SEs as no difference.

Card ratings come from the whole format, including the replayed drafts, so the
numbers compare advisors with each other; they aren't out-of-sample accuracy.

Since 4.33, replay pools preserve the order cards were picked, reconstructed
from successive pool snapshots. Older reports used card-column order, which
changes recency-weighted lane detection; lane-sensitive historical results
are approximate to that extent.

The deck-score measure uses quick builds, including the curve build still
used by Sealed shells. Draft suggestions no longer offer Tempo in 4.33, so
this measure does not reproduce the live suggestion candidate set or ordering.

## On GitHub

The **Advisor replay** workflow runs on pull requests that change
`src/advisor/` or this folder, comparing the pull request with its base. It
takes about 15 minutes, and the report is on the run's summary page.

To run it by hand: Actions → Advisor replay → Run workflow. Pick the branch to
test, and set:

- `base`: the branch, tag or commit to compare with (default `main`);
- `sets`: a JSON list of set codes, for example `["FRA", "TDM"]`; empty means
  all ten;
- `drafts`: drafts per set (default 3000);
- `salt`: any text, to sample different drafts. Use a new salt to confirm a
  result on drafts it wasn't tuned on.

## Locally

```sh
SET=FRA
curl -fsSLo dump.csv.gz "https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.$SET.PremierDraft.csv.gz"
curl -fsSLo dataset.json.gz "https://unrealities.github.io/MTGA_Draft_17Lands/${SET}_PremierDraft_All_Data.json.gz"
git worktree add ../base main

poetry run python Tools/AdvisorReplay/sample.py --dump dump.csv.gz --drafts 300 --out drafts.json.gz
poetry run python Tools/AdvisorReplay/replay.py --src ../base --drafts drafts.json.gz --dataset dataset.json.gz --set $SET --label base --out results/$SET.base.json
poetry run python Tools/AdvisorReplay/replay.py --src . --drafts drafts.json.gz --dataset dataset.json.gz --set $SET --label head --out results/$SET.head.json
poetry run python Tools/AdvisorReplay/report.py results/*.json
```

Sampling reads the whole dump (about a minute); replaying 300 drafts through
one copy of the advisor takes about 20 seconds.

## Files

| file | does |
|---|---|
| `sample.py` | Picks drafts from a dump by a hash of their ID, so a sample is repeatable. Standard library only. |
| `replay.py` | Runs one copy of the app (`--src`) over the sampled drafts: the advisor at every pick, the deck score on the final pool. |
| `report.py` | Pairs the base and head results by draft and writes the Markdown report. Needs only NumPy. |
| `lanes.py` | Compares lane rules with the colors drafters played, preserving pick order and checking parity with the app. |
| `lanes_report.py` | Summarizes lane agreement by pool size, with draft-level bootstrap uncertainty. |
| `tests/` | Tests for the replay and lane scripts: `poetry run pytest Tools/AdvisorReplay/tests`. |

`replay.py` uses only the app's public entry points: `DraftAdvisor`,
`SetMetrics`, `Dataset` and the quick deck builders in `src.card_logic`. If one
of those changes, `replay.py` needs to change with it.


## Lane accuracy

Actions → **Lane accuracy** → **Run workflow** runs the separate lane study
manually; it does not run automatically on pull requests. Inputs are `sets`
(a JSON list, empty for the replay's ten sets), `drafts` (3000 per set by
default), and `salt` (changes the sampled drafts). Each set downloads draft
and game data plus the app dataset. The report appears in the run summary
and the `lanes-report` artifact.

For local use, first sample drafts as above and download the matching game
data, then run:

```sh
poetry run python Tools/AdvisorReplay/lanes.py --src . --drafts drafts.json.gz --games games.csv.gz --dataset dataset.json.gz --set FRA --out results/FRA.lanes.json
poetry run python Tools/AdvisorReplay/lanes_report.py results/*.lanes.json
```

The study compares the app with no-recency, no-switch, neither, column-order
and most-cards variants. Agreement is with the drafter's played colors,
which need not be the best colors; it does not measure a benefit from
following the lane. See the [protocol and results](../../experiments/2026-11-15-lane-accuracy/RESULTS.md)
and the [joint-removal replay](../../experiments/2026-11-15-joint-removals/RESULTS.md).
