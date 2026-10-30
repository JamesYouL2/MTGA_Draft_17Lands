"""Run replay.py with DraftAdvisor constants overridden (throwaway).

    CONSTS=ARCH_WEIGHT=1.5,ARCH_TRUST_SAMPLES=300 python variant.py <replay.py args>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay


def main():
    argv = sys.argv[1:]
    src = argv[argv.index("--src") + 1] if "--src" in argv else "."
    sys.path.insert(0, os.path.abspath(src))
    from src.advisor.engine import DraftAdvisor

    for spec in filter(None, os.environ.get("CONSTS", "").split(",")):
        name, value = spec.split("=", 1)
        assert hasattr(DraftAdvisor, name), name
        setattr(DraftAdvisor, name, type(getattr(DraftAdvisor, name))(float(value)))
        print(f"{name} = {getattr(DraftAdvisor, name)}")
    replay.main(argv)


if __name__ == "__main__":
    main()
