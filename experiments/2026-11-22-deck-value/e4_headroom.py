"""Exploratory (not registered): headroom over main under the E4 pilot's
hindsight labels.

    python e4_headroom.py --labels e4_labels/ --replays conf/ [--json out.json]

--labels holds e4_hindsight.py's shards (run 45131183513, any depth);
--replays holds heads-SET-r36s1 folders (confirmation run 45021236056) with
base.json (main), gihwr-only.json and lgbm-strong-noalsa.json.

A label is the change in the drafter's final deck V (game-win log-odds by the
record constants) from swapping that pick's taken card for another card of the
pack. For each pick and each chooser (main's, gihwr-only's and noalsa's top
card, and the drafter's own pick, whose label is 0), the gap is
label(choice) - max label in the pack (<= 0). The oracle gap is the negative of
main's. Per-pick means are ratio estimates; every SE is clustered by draft.

Units: per draft, the summed log-odds gap is converted linearly at the draft's
own baseline: game win d = p0 (1 - p0) x gap, with p0 from the replay's deck
score of the drafter's pool; event wins = dE/dp(p0) x d, with E the expected
wins of a 7-win / 3-loss event. Circular: V is the app's deck score.
"""

import argparse
import glob
import gzip
import json
import math
import os
from collections import defaultdict

import numpy as np

HEADS = {"main": "base", "gihwr-only": "gihwr-only", "noalsa": "lgbm-strong-noalsa"}
CHOOSERS = ["main", "gihwr-only", "noalsa", "drafter"]
WIN_LOG_ODDS_AT_BASE, WIN_LOG_ODDS_PER_POINT, BASE_SCORE = -0.0062, 0.05099, 75.0


def event_wins(p, wins=7, losses=3):
    """Expected wins of an event that ends at `wins` wins or `losses` losses."""
    e, prob = 0.0, {(0, 0): 1.0}
    for _ in range(wins + losses - 1):
        nxt = defaultdict(float)
        for (w, l), q in prob.items():
            if w == wins or l == losses:
                nxt[(w, l)] += q
                continue
            nxt[(w + 1, l)] += q * p
            nxt[(w, l + 1)] += q * (1 - p)
        prob = nxt
    return sum(q * w for (w, l), q in prob.items())


def d_event_wins(p, h=1e-4):
    return (event_wins(p + h) - event_wins(p - h)) / (2 * h)


def cluster_mean(sums, counts=None):
    """Mean over drafts (counts None) or ratio Σsums/Σcounts, with a draft-clustered SE."""
    s = np.asarray(sums, float)
    g = len(s)
    if counts is None:
        return s.mean(), s.std(ddof=1) / math.sqrt(g)
    n = np.asarray(counts, float)
    r = s.sum() / n.sum()
    u = s - r * n
    return r, math.sqrt(g / (g - 1) * (u ** 2).sum()) / n.sum()


def load(labels_dir, replays_dir):
    shards = defaultdict(list)
    for path in glob.glob(os.path.join(labels_dir, "**", "*.json.gz"), recursive=True):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        shards[data["set"]] += data["drafts"]
    out = {}
    for code, drafts in sorted(shards.items()):
        folder = os.path.join(replays_dir, f"heads-{code}-r36s1")
        reps = {}
        for head, fname in HEADS.items():
            with open(os.path.join(folder, fname + ".json"), encoding="utf-8") as f:
                reps[head] = {d["id"]: d for d in json.load(f)["drafts"]}
        out[code] = (drafts, reps)
    return out


def analyse(drafts, reps):
    rows = []  # per draft: dict
    missing = defaultdict(int)
    for d in drafts:
        if not d["labels"] or d["id"] not in reps["main"]:
            missing["draft unlabelled or not replayed"] += 1
            continue
        top = {h: {(p[0], p[1]): p for p in reps[h][d["id"]]["picks"]} for h in HEADS}
        score = reps["main"][d["id"]]["deck_score"]
        lo = WIN_LOG_ODDS_AT_BASE + WIN_LOG_ODDS_PER_POINT * (score - BASE_SCORE)
        p0 = 1 / (1 + math.exp(-lo))
        picks = []
        for pack, pick, taken, labels in d["labels"]:
            vals = {c: v[0] for c, v in labels.items()}
            best = max(vals.values())
            mp = top["main"].get((pack, pick))
            choice = {h: (top[h].get((pack, pick)) or [None] * 6)[5] for h in HEADS}
            if any(c not in vals for c in choice.values()):
                missing["a head's top card not labelled"] += 1
                continue
            gap = {h: vals[c] - best for h, c in choice.items()}
            gap["drafter"] = vals[taken] - best
            lane = "no lane yet" if mp[7] == 0 else ("on-lane" if mp[6] else "off-lane")
            picks.append(dict(pack=pack, lane=lane, gap=gap))
        rows.append(dict(p0=p0, picks=picks))
    return rows, missing


def summarise(rows):
    res = {}
    k_game = np.array([r["p0"] * (1 - r["p0"]) for r in rows])
    k_event = np.array([d_event_wins(r["p0"]) for r in rows]) * k_game
    n = [len(r["picks"]) for r in rows]
    res["drafts"], res["picks"] = len(rows), int(sum(n))
    res["p0_mean"] = float(np.mean([r["p0"] for r in rows]))
    res["choosers"] = {}
    for c in CHOOSERS:
        sums = np.array([sum(p["gap"][c] for p in r["picks"]) for r in rows])
        per_pick = cluster_mean(sums, n)
        res["choosers"][c] = dict(
            per_pick=per_pick, per_draft=cluster_mean(sums),
            game_pp=cluster_mean(100 * k_game * sums), event_wins=cluster_mean(k_event * sums))
    # oracle gap (hindsight best - main) by pack and by main's lane status
    res["by"] = {}
    for key, groups in (("pack", [1, 2, 3]), ("lane", ["no lane yet", "on-lane", "off-lane"])):
        for g in groups:
            sums = np.array([-sum(p["gap"]["main"] for p in r["picks"] if p[key] == g) for r in rows])
            cnt = [sum(p[key] == g for p in r["picks"]) for r in rows]
            res["by"][f"{key} {g}"] = dict(
                picks=int(sum(cnt)), per_pick=cluster_mean(sums, cnt), per_draft=cluster_mean(sums),
                event_wins=cluster_mean(k_event * sums),
                main_best=sum(1 for r in rows for p in r["picks"] if p[key] == g and p["gap"]["main"] == 0) / max(1, sum(cnt)))
    return res


def f(ms, scale=1.0, digits=4):
    return f"{ms[0] * scale:+.{digits}f} ({ms[1] * scale:.{digits}f})"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--labels", required=True)
    ap.add_argument("--replays", required=True)
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    out = {}
    print("## E4 headroom (exploratory, not registered; circular: V is the app's deck score)\n")
    for code, (drafts, reps) in load(args.labels, args.replays).items():
        rows, missing = analyse(drafts, reps)
        r = summarise(rows)
        r["missing"] = dict(missing)
        out[code] = r
        print(f"### {code}: {r['drafts']} drafts, {r['picks']} picks (baseline game win {r['p0_mean']:.3f});"
              f" skipped {dict(missing)}\n")
        print("Gap to the hindsight-best card (≤ 0). SE clustered by draft.\n")
        print("| chooser | per pick, log-odds | per draft, log-odds | per draft, game win pp | per draft, event wins |")
        print("|---|---|---|---|---|")
        for c, v in r["choosers"].items():
            print(f"| {c} | {f(v['per_pick'], 1, 5)} | {f(v['per_draft'])} | {f(v['game_pp'], 1, 3)} | {f(v['event_wins'])} |")
        print("\nOracle gap (hindsight best − main's top card), by pack and by main's lane status. "
              "Per-draft figures add up to the total.\n")
        print("| group | picks | main's card is hindsight-best | per pick, log-odds | per draft, log-odds | per draft, event wins |")
        print("|---|---|---|---|---|---|")
        for g, v in r["by"].items():
            print(f"| {g} | {v['picks']} | {v['main_best']:.1%} | {f(v['per_pick'], 1, 5)} | {f(v['per_draft'])} | {f(v['event_wins'])} |")
        print()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
