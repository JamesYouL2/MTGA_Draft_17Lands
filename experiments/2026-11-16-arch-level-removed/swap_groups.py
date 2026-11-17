"""Event wins per swapped pick, for the four high-share sets and the other fifteen.

    python experiments/2026-11-16-arch-level-removed/swap_groups.py RESULTS

heads.py reports this measure over all sets only. Added after the run; the split is
the one PROTOCOL.md names for the regret slope.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-heldout-replay"))
import compare as C  # noqa: E402
import heads as H  # noqa: E402

HIGH = {"DMU", "TDM", "SNC", "KTK"}


def main():
    data = H.load(sys.argv[1], "arch-level-removed")
    print("| sets | drafts | event wins per swapped pick (SE) |")
    print("|---|---|---|")
    for name, high in (("DMU, TDM, SNC, KTK", True), ("the other fifteen", False)):
        sub = {k: v for k, v in data.items() if (k[0] in HIGH) == high}
        swap, se = C.disagreements(sub)
        print(f"| {name} | {len(sub)} | {swap:+.3f} ({se:.3f}), {swap / se:+.1f} SEs |")


if __name__ == "__main__":
    main()
