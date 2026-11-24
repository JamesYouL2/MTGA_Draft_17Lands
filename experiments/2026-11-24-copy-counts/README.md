# Card-rating verdicts with copy-counted win rates: they hold

Rule in PROTOCOL.md, written before the runs. Both runs: commit f25b449, salt
`copies1`, 714,281 decks and 3,288,430 games from 20 sets.

Gain of the engine's version over each one, in millinats a game, with 98.33%
intervals. Positive means the engine's version predicts better.

| version | once per game (run 45495021748) | copies (run 45495047267) | verdict in both |
|---|---|---|---|
| `no-archetype` | -0.457 [-0.492, -0.422] | -0.421 [-0.454, -0.387] | ablation predicts better |
| `no-shrinkage` | +0.005 [+0.003, +0.006] | +0.004 [+0.003, +0.005] | engine's predicts better |
| `no-iwd` | +0.033 [+0.032, +0.035] | +0.029 [+0.028, +0.031] | engine's predicts better |
| blend weight 0.65 | -0.177 [-0.186, -0.168] | -0.164 [-0.173, -0.156] | this version better |
| blend weight 1.3 | +0.187 [+0.179, +0.196] | +0.176 [+0.168, +0.184] | engine's better |
| no power bonus | +0.295 [+0.282, +0.307] | +0.267 [+0.255, +0.279] | engine's better |
| overall GIH WR alone | -0.272 [-0.306, -0.238] | -0.272 [-0.305, -0.239] | this version better |
| the deck score's blend | +0.136 [+0.127, +0.144] | +0.114 [+0.106, +0.122] | engine's better |

**Reading: holds.** Every version has the same verdict in both runs, and no
gain moves by more than a sixth of its size.

Card quality as a whole is worth 1.62 [1.55, 1.69] millinats a game once per
game and 1.56 [1.49, 1.63] with copies. The intervals overlap and the two were
not compared as a pair, so this doesn't show either count predicts better.

The deck score's weights were never in question: `fit.py` fits on the app's
dataset, which is 17Lands' own and counts copies.

Full reports: horse-once-per-game.md, horse-copies.md.
