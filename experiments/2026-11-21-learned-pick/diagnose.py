"""DIAGNOSE.md's checks: why regret and event wins disagree for a head.

    python experiments/2026-11-21-learned-pick/diagnose.py RESULTS [--head NAME] [--json out.json]

RESULTS holds one folder per set and salt with base.json and NAME.json, from
replay.py (an Advisor heads run). Checks 1, 3 and 4 read any run. Checks 2 and
5's deck parts need `replay.py --detail`, and run only where every draft has
it. Reads one folder at a time, so a full run fits in memory.

Every regret-style figure is compare.change (the head's slope of event wins on
the draft's mean of the measure, within-set z, less base's) and every
swap-style figure is compare.swap's regression with another outcome; each is
combined over salts as heads.py combines them.
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-08-pick-multipliers"))
import heads as H  # noqa: E402

C, R = H.C, H.R
PACKS = (1, 2, 3)
KNOTS = np.linspace(0.0, 1.0, 1001)
SAMPLE = 200_000  # scores kept per set and copy for the quantile map
# The deck parts of DIAGNOSE.md check 5; card quality is shown in rating points.
PARTS = [
    ("rating", "deck rating", 1.0),
    ("card_quality", "card quality (rating points)", 12.0),
    ("two_colors", "two colors or fewer", 1.0),
    ("missing_fixing", "missing fixing", 1.0),
    ("missing_spells", "missing spells", 1.0),
    ("colors", "colors", 1.0),
    ("removal", "removal spells", 1.0),
    ("creatures", "creatures", 1.0),
    ("cheap", "creatures and removal at 2 mana or less", 1.0),
    ("mana_value", "mean mana value of spells", 1.0),
]


def folders(root, head):
    for folder in sorted(glob.glob(os.path.join(root, "*"))):
        b, h = os.path.join(folder, "base.json"), os.path.join(folder, f"{head}.json")
        if os.path.exists(b) and os.path.exists(h):
            yield os.path.basename(folder).rsplit("-", 1)[-1], H.read(b), H.read(h)


def mean(xs):
    return float(np.mean(xs)) if len(xs) else np.nan


def regret_sd(scores, taken):
    sd = float(np.std(scores)) or 1.0
    return (max(scores) - scores[taken]) / sd


def percentile(scores, taken):
    """The card taken's rank among the pack's cards, as a share of the ranks."""
    n = len(scores)
    return sum(s > scores[taken] for s in scores) / (n - 1) if n > 1 else 0.0


def quantile_maps(root, head):
    """{set: (base score knots, head score knots)}, each from a sample of every
    card's score in the set's packs; None if the run has no detail."""
    rng = np.random.default_rng(0)
    samples = defaultdict(lambda: ([], []))
    for _, base, other in folders(root, head):
        for copy, data in enumerate((base, other)):
            scores = []
            for d in data["drafts"]:
                if "detail" not in d:
                    return None
                for s, _ in d["detail"]:
                    scores.extend(s)
            # Each folder (salt) gives an equal share of the set's sample.
            scores = np.array(scores)
            keep = SAMPLE // 8
            samples[data["set"]][copy].append(
                scores if len(scores) <= keep else rng.choice(scores, keep, replace=False)
            )
    return {code: (np.concatenate(b), np.concatenate(h)) for code, (b, h) in samples.items()}


def map_for(samples, code):
    """noalsa score -> main score, quantile-matched on the other sets' packs only."""
    others = [s for c, s in samples.items() if c != code]
    b = np.quantile(np.concatenate([o[0] for o in others]), KNOTS)
    h = np.quantile(np.concatenate([o[1] for o in others]), KNOTS)
    return lambda x: np.interp(x, h, b)


def summarise(root, head, samples):
    """One row per draft with picks, and pick counts for check 4."""
    rows = []
    maps = {code: map_for(samples, code) for code in samples} if samples else {}
    same_top = [0, 0]  # picks whose top card the maps keep, of picks
    detail_bad = 0
    for salt, base, other in folders(root, head):
        code = base["set"]
        theirs = {d["id"]: d for d in other["drafts"]}
        for d in base["drafts"]:
            o = theirs.get(d["id"])
            if o is None or not d["picks"] or not o["picks"]:
                continue
            head_picks = {(q[0], q[1]): q for q in o["picks"]}
            row = {
                "key": (code, f"{salt}:{d['id']}"),
                "complete": R.is_complete(d),
                "wins": d["wins"],
                "skill": d["skill"],
                "games": d["games"],
                "regret": (mean([p[3] for p in d["picks"]]), mean([q[3] for q in o["picks"]])),
                "rank": (mean([p[2] for p in d["picks"]]), mean([q[2] for q in o["picks"]])),
                "deck_score": d.get("deck_score"),
                "pool_gihwr": d.get("pool_gihwr"),
            }
            split = defaultdict(lambda: ([], []))
            net = n = matched = 0
            for p in d["picks"]:
                q = head_picks.get((p[0], p[1]))
                if q is None:
                    continue
                matched += 1
                agree = p[5] == q[5]
                for name in ("agree" if agree else "disagree", f"pack {p[0]}"):
                    split[name][0].append(p[3])
                    split[name][1].append(q[3])
                if not agree:
                    n += 1
                    net += int(q[2] == 0) - int(p[2] == 0)
            row["split"] = {k: (mean(v[0]), mean(v[1])) for k, v in split.items()}
            row["net"], row["n"], row["matched"] = net, n, matched
            if samples and "detail" in d and "detail" in o:
                pairs = list(zip(d["picks"], d["detail"]))
                theirs_detail = {(q[0], q[1]): det for q, det in zip(o["picks"], o["detail"])}
                pct, transfer, mapped, recomputed = ([], []), [], [], []
                for p, (bs, bt) in pairs:
                    det = theirs_detail.get((p[0], p[1]))
                    if det is None:
                        continue
                    hs, ht = det
                    if len(hs) != len(bs) or ht != bt:
                        detail_bad += 1
                        continue
                    hs_arr, bs_arr = np.array(hs), np.array(bs)
                    pct[0].append(percentile(bs, bt))
                    pct[1].append(percentile(hs, ht))
                    # (a) noalsa's order, main's gaps: k-th best card gets main's k-th score.
                    order = np.argsort(-hs_arr, kind="stable")
                    moved = np.empty(len(hs))
                    moved[order] = np.sort(bs_arr)[::-1]
                    transfer.append(regret_sd(moved, ht))
                    # (b) the quantile map fitted on the other sets.
                    m = maps[code](hs_arr)
                    mapped.append(regret_sd(m, ht))
                    recomputed.append(regret_sd(hs_arr, ht))
                    same_top[1] += 1
                    same_top[0] += int(np.argmax(m) == np.argmax(hs_arr) and np.argmax(moved) == np.argmax(hs_arr))
                row["percentile"] = (mean(pct[0]), mean(pct[1]))
                row["transfer"] = (row["regret"][0], mean(transfer))
                row["mapped"] = (row["regret"][0], mean(mapped))
                row["recomputed"] = mean(recomputed)
            for label, data in (("drafter_parts", d), ("sim_base", d), ("sim_head", o)):
                sim = data.get("sim") or {}
                if label == "drafter_parts" and sim.get("drafter_parts"):
                    row["drafter_parts"] = sim["drafter_parts"]
                if label != "drafter_parts" and sim.get("parts"):
                    row[label] = sim["parts"]
            rows.append(row)
        del base, other, theirs
    return rows, same_top, detail_bad


def controls(rows):
    return R.controls([{"skill": r["skill"], "games": r["games"]} for r in rows], [r["key"][0] for r in rows])


def regret_change(rows, field, sub=None):
    """compare.change on each draft's (base, head) mean of field, combined."""
    def get(r):
        return r.get(field) if sub is None else r["split"].get(sub)

    keep = [
        r for r in rows
        if r["complete"] and (v := get(r)) is not None and not (np.isnan(v[0]) or np.isnan(v[1]))
    ]
    if len(keep) < 100:
        return None, 0
    keys = [r["key"] for r in keep]
    frame = (
        np.array([r["wins"] for r in keep], dtype=float),
        controls(keep),
        np.array([get(r)[0] for r in keep]),
        np.array([get(r)[1] for r in keep]),
        keys,
    )
    salts = C.by_salt(keys, lambda i: C.change(frame, i))
    return H.combined(salts), len(keep)


def swap_y(rows, y_of):
    """compare.swap with outcome y_of(row): change in y per pick swapped from base's
    top card to the head's, combined over salts."""
    keep = [r for r in rows if r["complete"] and y_of(r) is not None]
    if len(keep) < 100:
        return None, 0
    a = np.array([[y_of(r), r["net"], r["n"]] for r in keep], dtype=float)
    frame = (a, controls(keep), [r["key"] for r in keep])
    salts = C.by_salt(frame[2], lambda i: C.swap(frame, i))
    return H.combined(salts), len(keep)


def paired(rows, a, b, part):
    """Head minus base of a deck part, per draft, combined over salts."""
    keep = [r for r in rows if r.get(a) and r.get(b) and r[a].get(part) is not None and r[b].get(part) is not None]
    if len(keep) < 100:
        return None, 0
    diff = np.array([r[b][part] - r[a][part] for r in keep], dtype=float)
    salts = C.by_salt([r["key"] for r in keep], lambda i: diff[i].mean())
    return H.combined(salts), len(keep)


def cell(m, digits, scale=1.0):
    if m is None:
        return "–"
    est, se = m["estimate"] * scale, m["scaled_se"] * abs(scale)
    return f"{est:+.{digits}f} ({se:.{digits}f}), {H.ses(m):+.1f}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("results")
    parser.add_argument("--head", default="lgbm-strong-noalsa")
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    samples = quantile_maps(args.results, args.head)
    rows, same_top, detail_bad = summarise(args.results, args.head, samples)
    out = {"drafts": len(rows), "events": sum(r["complete"] for r in rows), "detail": bool(samples)}
    print(f"# Diagnosis of `{args.head}` against main (DIAGNOSE.md)")
    print()
    print(
        f"{out['drafts']} drafts, {out['events']} complete events. Each figure: "
        "estimate (scaled SE), SEs, combined over salts. Regret-style rows: the "
        "head's event-win slope on the draft's mean of the measure less main's, "
        "positive is worse. Swap-style rows: change per pick swapped from main's "
        "top card to the head's."
    )
    print()

    print("## 1 and 2. Regret, scale-free and calibrated")
    print()
    print("| measure | events | slope change, head minus main |")
    print("|---|---|---|")
    measures = [
        ("regret", "SD regret (as in heads.py)"),
        ("rank", "rank of the card taken (check 1)"),
        ("percentile", "rank percentile in the pack (check 1)"),
        ("transfer", "SD regret, noalsa's order with main's gaps (check 2a)"),
        ("mapped", "SD regret, quantile map fitted on the other sets (check 2b)"),
    ]
    out["regret"] = {}
    for field, label in measures:
        m, n = regret_change(rows, field)
        if m is None and field not in ("regret", "rank"):
            continue
        out["regret"][field] = m
        print(f"| {label} | {n} | {cell(m, 4)} |")
    if samples:
        diffs = [abs(r["recomputed"] - r["regret"][1]) for r in rows if "recomputed" in r]
        out["same_top"] = same_top[0] / same_top[1] if same_top[1] else None
        out["recompute_max_diff"] = max(diffs) if diffs else None
        out["detail_mismatched_picks"] = detail_bad
        print()
        print(
            f"Both maps keep the head's top card on {100 * out['same_top']:.3f}% of "
            f"{same_top[1]} picks. The saved scores reproduce the head's mean SD regret "
            f"per draft to within {out['recompute_max_diff']:.4f}; picks whose two "
            f"copies' scored cards differ: {detail_bad}."
        )
    print()

    print("## 3. Where the regret gap lives")
    print()
    print("| picks | events | SD regret slope change |")
    print("|---|---|---|")
    out["split"] = {}
    for sub in ["agree", "disagree"] + [f"pack {k}" for k in PACKS]:
        m, n = regret_change(rows, None, sub)
        out["split"][sub] = m
        label = {"agree": "main and noalsa agree on the top card", "disagree": "they disagree"}.get(sub, sub)
        print(f"| {label} | {n} | {cell(m, 4)} |")
    print()

    print("## 4. The size in plain terms")
    print()
    matched = sum(r["matched"] for r in rows)
    changed = sum(r["n"] for r in rows)
    per_draft = np.array([r["n"] for r in rows], dtype=float)
    swap, n_swap = swap_y(rows, lambda r: r["wins"])
    complete_n = float(np.mean([r["n"] for r in rows if r["complete"]]))
    out["size"] = {
        "share_of_picks": changed / matched,
        "per_draft": float(per_draft.mean()),
        "per_draft_complete": complete_n,
        "swap": swap,
        "implied": {"estimate": swap["estimate"] * complete_n, "scaled_se": swap["scaled_se"] * complete_n},
    }
    print(f"- Top card differs on {100 * changed / matched:.1f}% of picks: {per_draft.mean():.1f} picks per draft "
          f"(median {np.median(per_draft):.0f}, middle half {np.percentile(per_draft, 25):.0f} to "
          f"{np.percentile(per_draft, 75):.0f}).")
    print(f"- Event wins per swapped pick: {cell(swap, 3)} ({n_swap} events).")
    print(f"- A drafter who followed noalsa instead of main on all {complete_n:.1f} disagreements "
          f"of a complete event: {swap['estimate'] * complete_n:+.2f} ({swap['scaled_se'] * complete_n:.2f}) "
          "event wins, extrapolated linearly from the per-swap estimate. Observational.")
    print()

    print("## 5. Do the final decks differ?")
    print()
    print("### (a) Drafters who sided with noalsa: their own final decks")
    print()
    print("Per pick swapped from main's top card to noalsa's, with the swap measure's controls. Observational.")
    print()
    print("| outcome | events | per swapped pick |")
    print("|---|---|---|")
    out["observed"] = {}
    outcomes = [("event wins", lambda r: r["wins"], 3), ("quick-build deck score (saved)", lambda r: r["deck_score"], 3),
                ("pool GIH WR, best 23 in a pair (saved)", lambda r: r["pool_gihwr"], 3)]
    for part, label, scale in PARTS:
        outcomes.append((
            f"Suggest Deck: {label}",
            lambda r, part=part, scale=scale: None if not r.get("drafter_parts") or r["drafter_parts"].get(part) is None
            else scale * r["drafter_parts"][part],
            3,
        ))
    for label, y_of, digits in outcomes:
        m, n = swap_y(rows, y_of)
        if m is None and label.startswith("Suggest"):
            continue
        out["observed"][label] = m
        print(f"| {label} | {n} | {cell(m, digits)} |")
    print()
    if any(r.get("sim_head") for r in rows):
        print("### (b) The simulated draft: noalsa's own deck less main's, same packs")
        print()
        print("Screen only: it grades decks by the deck score's own beliefs.")
        print()
        print("| part | drafts | head minus main | main's mean |")
        print("|---|---|---|---|")
        out["sim"] = {}
        for part, label, scale in PARTS:
            m, n = paired(rows, "sim_base", "sim_head", part)
            base_mean = np.mean([scale * r["sim_base"][part] for r in rows if r.get("sim_base") and r["sim_base"].get(part) is not None])
            out["sim"][part] = m
            print(f"| {label} | {n} | {cell(m, 3, scale)} | {base_mean:.3f} |")
        print()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
