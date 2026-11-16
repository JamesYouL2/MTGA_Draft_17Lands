# Does the three-color flag's share work early in a set?

A check, not a test with a protocol. The flag (`feat/three-color-off-color`) reads the
share of a set's games played by decks of three or more colors from the dataset. The
server keeps a deck color group in a dataset only from 500 games, and three-color
games are spread over many small groups, so early datasets could understate the share.

`early.py` rebuilds the share for each day from the 17Lands game dumps, counting only
groups with 500 or more games so far. Output: `early.md`. The dumps hold fewer games
than 17Lands' own data, so the filter bites harder here than it does live.

| set | first day with 10,000+ games | day 3 | day 7 | whole format |
|---|---|---|---|---|
| KTK | 93.1% | 86.6% | 85.9% | 85.4% |
| TDM | 100.0% | 83.5% | 83.2% | 79.0% |
| SNC | 86.6% (6,826 games) | 75.8% | 72.8% | 66.4% |
| DMU | 35.8% (its third day) | 35.8% | 43.4% | 45.6% |
| FRA | 0.0% | 15.4% | 16.5% | 22.5% |

- **The flag is on from the first real day in all four high-share sets,** and stays on.
- **The filter overstates, it doesn't understate, where three-color decks lead:** their
  groups reach 500 games first. On TDM's first day only three-color groups qualify, so
  the share reads 100%. That is on the right side of 30%.
- **Before a set has 500 games in any group, the share is 0 and the flag is off.**
  DMU's dump has 47 and 174 games on its first two days, and reads 0% on both. The
  advisor is then as it is today.
- **DMU is the closest call:** 35.8% on its first real day, against a 30% threshold.
  A set like it could start a few points nearer.
- A two-color set reads low early, as it should: FRA is 0% on day one and 15% by day
  three.
