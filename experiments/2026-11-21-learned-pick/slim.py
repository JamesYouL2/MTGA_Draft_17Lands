"""Shrink replay results in place, so the reports fit in a runner's memory.

    python experiments/2026-11-21-learned-pick/slim.py RESULTS

The reports (heads.py, by_set.py, agreement.py, confirm_extra.py) read only a
pick's first seven fields, and field 5, the top card's name, only to test it
for equality with the other copy's; diagnose.py also reads field 7, the lane
size. This keeps those eight fields and
replaces each name with a number, using one numbering for every file, so
equal names stay equal. Everything else in each file is kept. At 3000 drafts
per salt, the full results ran the confirmation run's report job out of memory
(Advisor heads 45021236056). The reports come out identical either way
(README.md, "Confirmation run").
"""

import glob
import json
import os
import sys

KEEP = 8  # pack, pick, rank of the card taken, regret, ..., top card, on lane, lane size
NAME = 5


def slim(path, names):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for d in data.get("drafts", []):
        d["picks"] = [
            [*p[:NAME], names.setdefault(p[NAME], len(names)), *p[NAME + 1 : KEEP]]
            for p in d["picks"]
        ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))


def main(root):
    names = {}
    paths = sorted(glob.glob(os.path.join(root, "*", "*.json")))
    for path in paths:
        slim(path, names)
    print(f"Slimmed {len(paths)} files; {len(names)} distinct top cards.", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
