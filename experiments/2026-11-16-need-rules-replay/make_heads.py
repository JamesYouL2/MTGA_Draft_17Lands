"""Write one patch per head against today's src/advisor/engine.py.

    python experiments/2026-11-16-need-rules-replay/make_heads.py

Each head is one text replacement; see PROTOCOL.md for what each one tests.
"""

import difflib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PATH = "src/advisor/engine.py"

REMOVAL = '''        # 3. Removal Check
        if (
            "removal" in tags
            and pack >= 2
            and self.pool_metrics["hard_removal_count"] < self.TARGET_HARD_REMOVAL
        ):
            return 1.3, "Critical: Needs Removal"

'''
TWO_DROPS = '''                return (
                    (
                        1.0 + min(0.5, (self.TARGET_EARLY_PLAYS - projected) * 0.15),
                        "Critical: Needs 2-Drops",
                    )
                    if pack >= 2
                    else (1.1, "Curve Foundation")
                )'''
CAP = "1.0 + min(0.5, (self.TARGET_EARLY_PLAYS"
GREEDY = '''                elif (
                    off_color_pips == 2
                    and get_functional_cmc(card) >= 5
                    and z_score >= self.BOMB_Z_SCORE
                ):
                    if self.pool_metrics["fixing_count"] >= 4:
                        return 0.30, "Greedy Bomb Splash"
'''

HEADS = {
    "no-needs-removal": (REMOVAL, ""),
    "removal-1.15": ('return 1.3, "Critical: Needs Removal"',
                     'return 1.15, "Critical: Needs Removal"'),
    "no-needs-2drops": (TWO_DROPS,
                        '                return (1.0, "") if pack >= 2 else (1.1, "Curve Foundation")'),
    "2drops-cap-1.25": (CAP, CAP.replace("0.5", "0.25")),
    "2drops-cap-1.75": (CAP, CAP.replace("0.5", "0.75")),
    "no-curve-foundation": ('else (1.1, "Curve Foundation")', 'else (1.0, "")'),
    "no-greedy-bomb": (GREEDY, ""),
}


CREATURES = '''        # 1. Creature Quota Check
        if pack >= 2 and "Creature" in types:
            projected_creatures = self.pool_metrics["creature_count"] * (
                self.TOTAL_PICKS / max(1, len(self.pool))
            )
            if projected_creatures < 13:
                return 1.25, "Critical: Needs Creatures"

'''
DEF = "    def _calculate_composition_bonus(self, card: Dict, pack: int) -> Tuple[float, str]:\n"


def flat(creature, removal):
    """Needs Creatures and Needs Removal replaced by a flat multiplier on every
    creature and every removal spell in packs 2-3, on top of whatever the other
    composition rules give."""
    wrapper = f'''    def _calculate_composition_bonus(self, card: Dict, pack: int) -> Tuple[float, str]:
        mult, reason = self._composition_rule(card, pack)
        if pack >= 2:
            if "Creature" in card.get("types", []):
                mult *= {creature}
            if "removal" in card.get("tags", []):
                mult *= {removal}
        return mult, reason

    def _composition_rule(self, card: Dict, pack: int) -> Tuple[float, str]:
'''
    return [(CREATURES, ""), (REMOVAL, ""), (DEF, wrapper)]


# The rerun of 2026-11-17, in heads-rerun/: see the addendum in PROTOCOL.md.
RERUN = {
    "no-needs-2drops": HEADS["no-needs-2drops"],
    "2drops-cap-1.25": HEADS["2drops-cap-1.25"],
    "flat-bonus": flat(1.05, 1.1),
    "flat-bonus-strong": flat(1.1, 1.2),
}


def write(text, heads, folder):
    os.makedirs(os.path.join(HERE, folder), exist_ok=True)
    for head, edits in heads.items():
        changed = text
        for old, new in [edits] if isinstance(edits, tuple) else edits:
            assert changed.count(old) == 1, head
            changed = changed.replace(old, new)
        compile(changed, head, "exec")
        diff = difflib.unified_diff(
            text.splitlines(keepends=True), changed.splitlines(keepends=True),
            f"a/{PATH}", f"b/{PATH}", n=3,
        )
        with open(os.path.join(HERE, folder, f"{head}.patch"), "w", encoding="utf-8") as f:
            f.write(f"diff --git a/{PATH} b/{PATH}\n")
            f.writelines(diff)
        print(f"{folder}/{head}")


def main():
    with open(os.path.join(ROOT, PATH), encoding="utf-8") as f:
        text = f.read()
    write(text, HEADS, "heads")
    write(text, RERUN, "heads-rerun")


if __name__ == "__main__":
    main()
