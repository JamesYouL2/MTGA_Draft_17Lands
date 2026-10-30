"""Run replay.py with DraftAdvisor class constants overridden (throwaway sweep tool).

    python Tools/AdvisorReplay/variant.py --const ARCH_WEIGHT=1.5 -- \
        --src . --drafts drafts.json.gz --dataset dataset.json.gz --label head --out x.json
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--const", action="append", default=[], help="NAME=VALUE")
    args, rest = parser.parse_known_args()
    rest = [a for a in rest if a != "--"]
    src = rest[rest.index("--src") + 1] if "--src" in rest else "."
    sys.path.insert(0, os.path.abspath(src))
    from src.advisor.engine import DraftAdvisor

    for spec in args.const:
        name, value = spec.split("=", 1)
        assert hasattr(DraftAdvisor, name), name
        setattr(DraftAdvisor, name, type(getattr(DraftAdvisor, name))(float(value)))
        print(f"{name} = {getattr(DraftAdvisor, name)}")
    replay.main(rest)


if __name__ == "__main__":
    main()
