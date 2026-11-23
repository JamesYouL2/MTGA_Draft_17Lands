# Phase 3-lite: pick by value to the deck, with no learned model

Registered 2026-11-23, before any run. The headroom addendum in README.md put
a loose ceiling of about 0.14–0.19 log-odds per draft (FDN, TDM) on what any
forward value model could add over main, by the deck score's own lights. This
phase tries the simplest forward version, with no ML, before any Phase 2
labels are made.

## Heads

All heads live in [p3_heads.py](p3_heads.py): it subclasses replay.App and
replaces `advise()`. Nothing in `src/` changes. The builds are the app's own
quick builds, the ones replay.App.deck_score and the E4 labels use:
consistency, curve and greedy for each of identify_top_pairs' pairs, plus the
soup.

**V.** V is the registered Phase 2a form, in deck-score points: deck score
minus 0.229 × splash-color spells (per copy). V(pool) is the best V over the
quick builds of the pool.
- A pair build's splash-color spells are the spells with a color outside its
  pair. Only the greedy build splashes.
- The soup's are the spells with a color outside the two colors most common
  among its spells.

**Filler.** The deck score is BASE + 12 × the mean z of a deck's spells, plus
color and fixing terms. A missing-spells charge applies only below a
pool-size-scaled count (23 × pool size / 42). So any build short of about 23
spells is degenerate: a good card below the deck's current mean lowers V.
This holds well past the tiny pools (fewer than about 10 playables) that the
request named. So the pool is always padded before it is built:
- F = max(0, round(23 × (41 − cards taken so far) / 42)) filler cards: 22 at
  the first pick, about 15 at the start of pack 2, about 8 at the start of
  pack 3, and 0 at the last pick.
- A filler is a colorless 3-mana creature with GIH WR equal to the set's
  All Decks mean (z = 0). It fits every pair and adds no color weight to
  identify_top_pairs.
- So the early picks reduce to quality plus color fit (a card scores by how
  far it beats an average card in its best pair), and the padding fades out
  as the real pool fills.
- The built pool's size, as passed to the score, is cards + fillers.

**marginal.** Each distinct card in the pack scores
V(pool + card + F fillers) − V(pool + F fillers). The second term is the same
for every card of a pick, so the head ranks by the first. Ties (cards no
build would play) keep main's order.

**blend-λ.** main's score + λ × SD(main's scores in the pack) × z(marginal).
z is taken over the pack's distinct cards; it is 0 if marginal has no spread.
- main's contextual scores have no fixed scale, so the marginal z is put in
  main's own within-pack SD units.
- λ = 1 therefore means one SD of marginal moves a card as far as one SD of
  main's own score.
- λ ∈ {0.5, 1, 2}.

**References.** These are run as-is, by replay.py:
- main: the base, i.e. the app as it is.
- gihwr-only: experiments/2026-11-21-simulated-draft/heads/gihwr-only.patch.

## Tuning λ (3 sets, then frozen)

- Sets: BLB, DSK, OTJ. Salt `p3tune`, the first 500 drafts of a 500-draft
  sample, with ratings that hold those drafts out.
- Each draft is simulated by main, blend-0.5, blend-1 and blend-2 (no
  replay; simulate.py, as below).
- λ* is the λ with the highest equal-weight mean, over the three sets, of
  (blend − main) simulated deck win rate. Ties go to the smaller λ.
- λ* is written into the eval workflow in its own commit before the eval
  runs. Neither marginal nor any other head is tuned.

## Evaluation

**Drafts and ratings.**
- 19 sets: BLB, DFT, DMU, DSK, EOE, FDN, FIN, FRA, HOB, KTK, LTR, MSH, NEO,
  OTJ, SNC, SOS, TDM, TLA, TMT.
- Salt `r36s1` with a 3000-draft sample and ratings that hold all 3000 out,
  rebuilt exactly as the confirmation run 45021236056 and the E4 pilot
  (45131183513) did. The first 500 drafts are replayed. In FDN and TDM these
  are among the E4 pilot's 1000 labelled drafts.
- main, gihwr-only, marginal and blend-λ* all see the same drafts, salt and
  ratings, so every comparison is paired by draft.

**Judge.** This is the simulated-draft measure (Tools/AdvisorReplay/simulate.py,
from exp/simulated-draft, unchanged):
- each copy drafts each real draft's packs itself, with wheel swaps;
- Suggest Deck builds the pool;
- the first deck's score becomes an expected game win rate (record
  constants), in percent.

**Primary outcome.**
- Per draft: Δ = head's simulated deck win rate − main's, in win-rate points.
  Only drafts both copies simulated count.
- Per set: the mean of Δ, with SE = SD/√n (one value per draft, so clustered
  by draft).
- Combined: the equal-weight mean of the 19 set means, with
  SE = √(Σ SE²) / 19.

**Rank regret.** This is the established regret measure (compare.change): the
head's regret slope minus main's, on the drafter's own pool path, over all
complete events of the 19 sets. Its SE is report.bootstrap's draft
resampling. Positive is worse.

## Decision (on the combined figures)

- **promising:** marginal or blend-λ* beats main by ≥ 3 SEs on the primary
  outcome, AND that head's rank regret change is not worse (positive) by
  more than 3 SEs.
- **no headroom:** marginal and blend-λ* are both within ±2 SEs of main on
  the primary outcome.
- **mixed:** anything else.

## Also reported (no rule)

- gihwr-only vs main on the same figures, as a reference.
- The primary outcome on the 16 non-tuning sets, and per set.
- **Share of top cards changed** (head's top ≠ main's top on the drafter's
  pool path), overall and split:
  - by pack (P1, P2, P3);
  - by main's lane status at the pick: no lane yet, main's top on-lane, main's
    top off-lane.
- **E4 view (a second view, still circular).** On FDN and TDM, for the first
  500 drafts:
  - each head's agreement with the E4 hindsight-best card (labels from
    45131183513): the share of a draft's labelled picks where the head's top
    card has the pack's best label;
  - the summed label gap (as in the headroom addendum).

  Each is paired per draft against main, with draft-clustered SEs. The
  references are gihwr-only, noalsa (its tops from 45021236056, the same
  drafts and ratings) and the drafter.
- Seconds per draft and job-hours.

## Circularity

V is also the judge. Phase 2a found no bomb or creature skill-confound bias
in V, so it is the least-biased judge available, but a head that optimizes V
will look good on V:
- marginal ranks cards by the same deck score the simulated measure ends
  with;
- λ is tuned on that measure too.

A "promising" verdict says the deck score's own advice is not yet used by
main. It does not say decks would win more games. The E4 agreement view
shares the circularity, because its labels are also V, but it reads the
heads on the drafter's real pool path rather than their own.

## Budget

This was timed locally on 3 FDN drafts (p3_heads.py, full ratings):
- main + marginal + blend-1, replay and simulate: 16.5 s per draft. The
  heads share cached builds.
- blend-0.5/1/2, simulate only: 7.4 s per draft.

The E4 labels took 8.1 s per draft locally against 19.2 s on CI, a factor of
2.4. So on CI, marginal + blend is about 40 s per draft.

At 19 sets × 1000 drafts that is about 210 single-process hours, over the
~150 cap. So the eval is **cut to 500 drafts per set**:
- eval: 19 × 500 × 40 s ≈ 105 process-hours;
- tuning: 3 × 500 × 18 s ≈ 7 process-hours;
- total: about 112 process-hours.

Each job splits its drafts over 4 processes, one per runner core. That should
bring job-hours to roughly a third of the process-hours, about 40 h with
set-up. The report gives both.

The workflows are .github/workflows/deck-value-p3-tune.yml (one job per
tuning set) and deck-value-p3.yml (one job per eval set). The base and
gihwr-only run there by replay.py --simulate, on all 500 drafts.
