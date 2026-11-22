"""DIAGNOSE.md check 9: diagnose.py for lgbm-strong and lgbm-strong-noalsa on
the same drafts (the first measure run, Advisor heads 44985574439).

    python experiments/2026-11-21-learned-pick/diagnose_alsa.py RESULTS
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diagnose  # noqa: E402

if __name__ == "__main__":
    for head in ("lgbm-strong", "lgbm-strong-noalsa"):
        diagnose.main([sys.argv[1], "--head", head])
        print()
