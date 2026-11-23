"""report.py's event-wins table on a heads run's compact results, with the
skill bins as main has them (--old-bins) or as the checkout's report.py has them.

    python measure_report.py TOOLDIR COMPACT HEAD [--old-bins] [--base base]

Drafts are keyed salt:id within each set, so a draft drawn by two salts counts
once per salt, as heads.py counts it.
"""
import argparse
import glob
import gzip
import json
import os
import sys
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("tooldir")
ap.add_argument("compact")
ap.add_argument("head")
ap.add_argument("--base", default="base")
ap.add_argument("--old-bins", action="store_true")
ap.add_argument("--table", default="wins", choices=["wins", "all"])
a = ap.parse_args()
sys.path.insert(0, a.tooldir)
import report  # noqa: E402

if a.old_bins:
    def old_controls(drafts, sets, np=report.np):
        skill = [None if d["skill"] is None
                 else int((min(max(d["skill"], 0.30), 0.74) - 0.30) // 0.04) for d in drafts]
        cols = report._dummies(sets) + report._dummies(skill) + report._dummies([d["games"] for d in drafts])
        return np.column_stack([np.ones(len(drafts)), *cols])
    report.controls = old_controls

runs = {"base": defaultdict(dict), "head": defaultdict(dict)}
for folder in sorted(glob.glob(os.path.join(a.compact, "heads-*"))):
    salt = folder.rsplit("-", 1)[1]
    for label, path in ((a.base, "base"), (a.head, "head")):
        with gzip.open(os.path.join(folder, f"{label}.json.gz"), "rt") as f:
            data = json.load(f)
        for d in data["drafts"]:
            runs[path][data["set"]][f"{salt}:{d['id']}"] = d
for code in set(runs["base"]) | set(runs["head"]):
    both = runs["base"][code].keys() & runs["head"][code].keys()
    for label in ("base", "head"):
        runs[label][code] = {i: runs[label][code][i] for i in sorted(both)}
print(report.wins_table(runs) if a.table == "wins" else report.report(runs))
