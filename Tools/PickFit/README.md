# Pick fit

Fits the weights of the pick score in `src/advisor/engine.py` to the picks of
strong 17Lands drafters, and checks them on sets the fit didn't see.

The pick score is 50 plus a weighted sum of a few features of each card for the
cards already taken (`DraftAdvisor.pick_features`). The fit asks: with these
features, which weights make the cards strong drafters actually took most
likely? That is a conditional logit, the pick version of a logistic
regression: the chance a card is taken is proportional to `exp(score × k)`
over the cards in the pack.

Strong drafters are those with a game win rate bucket of 0.6 or more over 50 or
more games. The weights are fixed in the app, not refitted per set; rerun the
fit when a feature changes, or now and then to check the weights still hold.

## Running it

On GitHub: Actions > Pick fit > Run workflow. It samples drafts from each
set's 17Lands draft dump, computes the features with the app's own code, fits
all sets together, and writes a report to the run's summary.

By hand, for one set:

```sh
python Tools/PickFit/three_color_share.py --src . \
    --dataset FRA_PremierDraft_All_Data.json.gz --set FRA
python Tools/PickFit/drafts.py --dump draft_data_public.FRA.PremierDraft.csv.gz \
    --drafts 4000 --out drafts.json.gz
python Tools/PickFit/features.py --src . --drafts drafts.json.gz \
    --dataset FRA_PremierDraft_All_Data.json.gz --set FRA --out results/FRA.json.gz
python Tools/PickFit/fit.py results/*.json.gz > report.md
```

`three_color_share.py` adds the share of the set's games played by decks of
three or more colors to a dataset made before datasets recorded it.
`fit.py` needs NumPy. With LightGBM installed, the report adds a ranking model
that can use more facts about each card and any shape it likes, as a yardstick:
if it doesn't pick much better, the simple score isn't leaving much out.

## Reading the report

- **Fitted weights**: points per unit of each feature, ± one standard error.
  Quality is fixed at 15 points per standard deviation of GIH WR, so the other
  weights are in the same points the app shows.
- **Fitted weights by set**: whether the weights hold from set to set.
- **Held-out sets**: each set picked by a fit to the other sets. Top-1 is how
  often the model's best card is the card the drafter took.
- **For src/advisor/engine.py**: the fitted weights, ready to paste.
