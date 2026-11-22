"""diagnose.py for every head beside base in RESULTS, one after another
(DIAGNOSE.md check 9 and the audit addendum's gihwr-only comparison).

    python experiments/2026-11-21-learned-pick/diagnose_all.py RESULTS
"""

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diagnose  # noqa: E402

FIRST = ("lgbm-strong-noalsa", "lgbm-strong", "gihwr-only")


def heads(root):
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        names = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(folder, "*.json"))}
        if "base" in names:
            names.discard("base")
            return [h for h in FIRST if h in names] + sorted(names - set(FIRST))
    raise SystemExit(f"No results in {root}")


if __name__ == "__main__":
    for head in heads(sys.argv[1]):
        diagnose.main([sys.argv[1], "--head", head])
        print()
