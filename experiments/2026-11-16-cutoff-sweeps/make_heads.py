"""Write the sweep's head patches against today's src/advisor/engine.py.

    python experiments/2026-11-16-cutoff-sweeps/make_heads.py
"""

import difflib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
PATH = "src/advisor/engine.py"

SHARE = "threshold = sum(color_counts.values()) * "
HEADS = {
    "lane-share-10": (SHARE + "0.15", SHARE + "0.10"),
    "lane-share-20": (SHARE + "0.15", SHARE + "0.20"),
    "lane-weight-1.5": ("if weight >= 2.5:", "if weight >= 1.5:"),
    "lane-weight-3.5": ("if weight >= 2.5:", "if weight >= 3.5:"),
    "arch-start-0.4": ("ARCH_WEIGHT_START = 0.6\n", "ARCH_WEIGHT_START = 0.4\n"),
    "arch-start-0.8": ("ARCH_WEIGHT_START = 0.6\n", "ARCH_WEIGHT_START = 0.8\n"),
    "arch-ramp-0.4": ("ARCH_WEIGHT_RAMP = 0.7\n", "ARCH_WEIGHT_RAMP = 0.4\n"),
    "arch-ramp-1.0": ("ARCH_WEIGHT_RAMP = 0.7\n", "ARCH_WEIGHT_RAMP = 1.0\n"),
}
# The confirmation run (CONFIRM.md): 0.10 again, and one step further down.
CONFIRM = {
    "lane-share-10": HEADS["lane-share-10"],
    "lane-share-05": (SHARE + "0.15", SHARE + "0.05"),
}


def main():
    with open(os.path.join(ROOT, PATH), encoding="utf-8") as f:
        src = f.read()
    for folder, heads in (("heads", HEADS), ("confirm-heads", CONFIRM)):
        write(src, os.path.join(HERE, folder), heads)


def write(src, out, heads):
    os.makedirs(out, exist_ok=True)
    for name, (old, new) in heads.items():
        assert src.count(old) == 1, name
        patched = src.replace(old, new)
        diff = difflib.unified_diff(
            src.splitlines(True), patched.splitlines(True), f"a/{PATH}", f"b/{PATH}"
        )
        with open(os.path.join(out, f"{name}.patch"), "w", encoding="utf-8") as f:
            f.write("".join(diff))
        print(name)


if __name__ == "__main__":
    main()
