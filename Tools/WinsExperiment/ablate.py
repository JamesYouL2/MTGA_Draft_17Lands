"""Replay main's advisor with one part of its score switched off.

    python Tools/WinsExperiment/ablate.py nocast --src base --drafts drafts.json.gz \
        --dataset FRA.json.gz --set FRA --label nocast --out results/FRA.nocast.json

Copies --src's src/ to a temporary folder, edits engine.py as ABLATIONS says,
and replays from the copy. A composition rule switched off keeps its place in
the rule order (later rules still don't apply to the cards it claims); only
its multiplier becomes 1.
"""

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "AdvisorReplay"))

import replay  # noqa: E402

FINAL = "(base_score + power_bonus + synergy_bonus) * cast_mult * role_mult"
CAST_START = '        mana_cost = card.get("mana_cost", "")\n'
# Each ablation: (text in main's engine.py, replacement, times it appears).
ABLATIONS = {
    # Castability and composition multipliers.
    "nocast": [(FINAL, FINAL.replace("* cast_mult", ""), 1)],
    "nocast_p1": [
        (
            CAST_START,
            '        if pack == 1:\n            return 1.0, ""\n' + CAST_START,
            1,
        )
    ],
    "nocast_late": [
        (
            CAST_START,
            '        if pack >= 2:\n            return 1.0, ""\n' + CAST_START,
            1,
        )
    ],
    "nocomp": [(FINAL, FINAL.replace("* role_mult", ""), 1)],
    "nocastcomp": [(FINAL, FINAL.replace(" * cast_mult * role_mult", ""), 1)],
    # Additions to the base score.
    "nopower": [
        (
            "power_bonus = max(0, z_score * 10 * iwd_mult) if z_score > 0.5 else 0",
            "power_bonus = 0",
            1,
        )
    ],
    "nosynergy": [(FINAL, FINAL.replace(" + synergy_bonus", ""), 1)],
    "nolane": [("base_score *= 1.3 if needs_playables else 1.1", "pass", 1)],
    "noarch": [
        (
            "arch_weight = min(0.9, 0.2 + (pick_number / self.TOTAL_PICKS) * 0.7)",
            "arch_weight = 0.0",
            1,
        )
    ],
    # Composition rules, one at a time.
    "nocurve": [('return 0.7, "Curve Too Heavy"', 'return 1.0, "Curve Too Heavy"', 1)],
    "nocreatures": [
        (
            'return 1.25, "Critical: Needs Creatures"',
            'return 1.0, "Critical: Needs Creatures"',
            1,
        )
    ],
    "notags": [("return 1.2, ", "return 1.0, ", 3)],
    "nofixing": [
        (
            'return 1.4, "Critical: Needs Fixing"',
            'return 1.0, "Critical: Needs Fixing"',
            1,
        ),
        ('return 1.3, "Enables Bomb Splash"', 'return 1.0, "Enables Bomb Splash"', 1),
        ('(1.15, "Premium Fixing")', '(1.0, "Premium Fixing")', 1),
    ],
    "noremoval": [
        (
            'return 1.3, "Critical: Needs Removal"',
            'return 1.0, "Critical: Needs Removal"',
            1,
        ),
        ('return 0.8, "Removal Saturated"', 'return 1.0, "Removal Saturated"', 1),
    ],
    "nodrops": [
        ("1.0 + min(0.5, (self.TARGET_EARLY_PLAYS - projected) * 0.15)", "1.0", 1),
        ('(1.1, "Curve Foundation")', '(1.0, "Curve Foundation")', 1),
    ],
}


def main():
    which, argv = sys.argv[1], sys.argv[2:]
    at = argv.index("--src") + 1
    work = tempfile.mkdtemp()
    shutil.copytree(os.path.join(argv[at], "src"), os.path.join(work, "src"))
    path = os.path.join(work, "src", "advisor", "engine.py")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for old, new, times in ABLATIONS[which]:
        assert text.count(old) == times, (which, old, text.count(old))
        text = text.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    argv[at] = work
    replay.main(argv)


if __name__ == "__main__":
    main()
