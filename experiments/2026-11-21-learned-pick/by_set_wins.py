"""Event wins per swapped pick, head against base, set by set.

    python experiments/2026-11-21-learned-pick/by_set_wins.py RESULTS --append est.jsonl
    python experiments/2026-11-21-learned-pick/by_set_wins.py --combine est.jsonl

The first form adds one line per (set, salt, head) to est.jsonl: heads.py's swap
measure on that folder alone, with its bootstrap SE. Folders can be done one at
a time (a full run's results are several GB). The second form combines each
set's salts as heads.py does (compare.combine) and prints a table.
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

C, R = H.C, H.R


def estimates(root):
    for folder in sorted(glob.glob(os.path.join(root, "heads-*"))):
        salt = os.path.basename(folder).rsplit("-", 1)[-1]
        heads = [
            os.path.basename(p)[: -len(".json")]
            for p in sorted(glob.glob(os.path.join(folder, "*.json")))
            if os.path.basename(p) != "base.json"
        ]
        for head in heads:
            data = _load_one(folder, head)
            if not data:
                continue
            frame = C.swap_frame(data)
            n = len(frame[0])
            est = C.swap(frame, np.arange(n))
            se = R.bootstrap(lambda i: C.swap(frame, i), n)
            code = next(iter(data))[0]
            yield {"set": code, "salt": salt, "head": head, "estimate": float(est), "se": float(se), "events": n}


def _load_one(folder, head):
    """H.load on one folder."""
    out = {}
    base, other = H.read(os.path.join(folder, "base.json")), H.read(os.path.join(folder, f"{head}.json"))
    theirs = {d["id"]: d for d in other["drafts"]}
    salt = os.path.basename(folder).rsplit("-", 1)[-1]
    for d in base["drafts"]:
        if d["id"] in theirs:
            out[(base["set"], f"{salt}:{d['id']}")] = {"base": d, "head": theirs[d["id"]]}
    return out


def combine(path):
    rows = defaultdict(dict)
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rows[(r["set"], r["head"])][r["salt"]] = (r["estimate"], r["se"])
    sets = sorted({s for s, _ in rows})
    heads = sorted({h for _, h in rows})
    print("| set | " + " | ".join(heads) + " |")
    print("|---" * (1 + len(heads)) + "|")
    for s in sets:
        cells = []
        for h in heads:
            salts = rows.get((s, h), {})
            if len(salts) < 2:
                cells.append("")
                continue
            m = H.combined(salts)
            cells.append(f"{m['estimate']:+.3f} ({m['scaled_se']:.3f})")
        print(f"| {s} | " + " | ".join(cells) + " |")
    # How many sets each head is ahead of base in.
    print()
    print("| head | sets ahead | sets 2+ scaled SEs ahead | sets 2+ scaled SEs behind |")
    print("|---|---|---|---|")
    for h in heads:
        ms = [H.combined(rows[(s, h)]) for s in sets if len(rows.get((s, h), {})) >= 2]
        z = [m["estimate"] / m["scaled_se"] for m in ms]
        print(f"| {h} | {sum(m['estimate'] > 0 for m in ms)} of {len(ms)} | {sum(x >= 2 for x in z)} | {sum(x <= -2 for x in z)} |")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="?")
    parser.add_argument("--append")
    parser.add_argument("--combine")
    args = parser.parse_args()
    if args.combine:
        combine(args.combine)
        return
    with open(args.append, "a", encoding="utf-8") as f:
        for r in estimates(args.results):
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
