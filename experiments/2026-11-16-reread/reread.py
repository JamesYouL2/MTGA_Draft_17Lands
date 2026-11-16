"""Re-read stored pick replay runs with regret scaled within each set.

    python experiments/2026-11-16-reread/reread.py NAME RUN_DIR [RUN_DIR ...] --json out.json

Each RUN_DIR is one run's downloaded artifacts: heads-<set>-<salt> folders from the
Advisor heads workflow, or replay-<set> folders from Advisor replay. Prints the old
all-sets figure, the corrected one and the mean of the sets' own changes. Needs only
NumPy.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

C, R = H.C, H.R
SAMPLES = 200


def slim(draft):
    """A draft with its picks boiled down to their mean regret, to fit in memory."""
    picks = draft["picks"]
    keep = {k: v for k, v in draft.items() if k != "picks"}
    keep["picks"] = [[None, None, None, float(np.mean([p[3] for p in picks]))]] if picks else []
    return keep


def load_heads(runs):
    """{head: {(set, "run:sample:id"): {"base": draft, "head": draft}}}."""
    out = {}
    for n, run in enumerate(runs):
        for folder in sorted(glob.glob(os.path.join(run, "heads-*-*"))):
            base_path = os.path.join(folder, "base.json")
            if not os.path.exists(base_path):
                continue
            sample = os.path.basename(folder).rsplit("-", 1)[-1]
            base = H.read(base_path)
            code = base["set"]
            mine = {d["id"]: slim(d) for d in base["drafts"]}
            del base
            for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
                head = os.path.basename(path)[:-5]
                if head == "base":
                    continue
                for d in H.read(path)["drafts"]:
                    if d["id"] in mine:
                        out.setdefault(head, {})[(code, f"{n}:{sample}:{d['id']}")] = {
                            "base": mine[d["id"]], "head": slim(d)}
    return out


def load_replay(runs):
    """{arm: {(set, id): {"base": draft, "head": draft}}}, as compare.py's load."""
    out = {}
    for arm, prefix in C.ARMS.items():
        data = {}
        for run in runs:
            for path in sorted(glob.glob(os.path.join(run, "replay-*", f"{prefix}*.json"))):
                result = H.read(path)
                if "drafts" not in result or "label" not in result:
                    continue
                for d in result["drafts"]:
                    data.setdefault((result["set"], d["id"]), {})[result["label"]] = slim(d)
        data = {k: v for k, v in data.items() if len(v) == 2 and {"base", "head"} <= v.keys()}
        if data:
            out[arm] = data
    return out


def measure(data):
    data = dict(sorted(data.items()))
    frame = C.regret_frame(data)
    codes, _ = C.set_codes(frame[4])
    n = len(frame[0])
    every = np.arange(n)

    def mean_of_sets(i):
        c = codes[i]
        parts = [(np.sum(c == s), C.pooled_change(frame, i[c == s])) for s in np.unique(c)]
        return sum(k * v for k, v in parts) / sum(k for k, _ in parts)

    rng = np.random.default_rng(0)
    draws = [rng.integers(0, n, n) for _ in range(SAMPLES)]
    out = {"events": n, "sets": len(np.unique(codes))}
    for name, fn in (("pooled", C.pooled_change), ("within", C.change)):
        out[name] = (float(fn(frame, every)), float(np.std([fn(frame, d) for d in draws])))
    out["mean"] = (float(mean_of_sets(every)), float(np.std([mean_of_sets(d) for d in draws])))
    for name in ("pooled", "within"):
        out[f"{name}_verdict"] = H.verdict(*out[name])
    return out


def cell(pair):
    ses = f", {pair[0] / pair[1]:+.1f} SEs" if pair[1] else ""
    return f"{pair[0]:+.4f} ({pair[1]:.4f}){ses}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("name")
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    loaded = load_heads(args.runs) or load_replay(args.runs)
    results = {head: measure(data) for head, data in sorted(loaded.items())}
    print(f"## {args.name}\n")
    print("| head | events | sets | as first read | removal rule | corrected | removal rule "
          "| mean of sets |")
    print("|---|---|---|---|---|---|---|---|")
    for head, m in results.items():
        mark = "" if m["pooled_verdict"] == m["within_verdict"] else " **(changed)**"
        print(f"| {head} | {m['events']} | {m['sets']} | {cell(m['pooled'])} | {m['pooled_verdict']} "
              f"| {cell(m['within'])} | {m['within_verdict']}{mark} | {cell(m['mean'])} |")
    print()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
