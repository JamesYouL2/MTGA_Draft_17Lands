"""The app's three-color share as a set's dataset would give it on each early day.

The server keeps a deck color group in a dataset only from MIN_GAMES games, so early
on the small three-color groups can be missing. Game counts here are the public
dump's, which are fewer than 17Lands' own, so the filter bites harder here than live.
"""
import gzip, sys
from collections import defaultdict
from datetime import date
MIN_GAMES = 500
def run(code):
    f = gzip.open(f"{code}.PremierDraft.gz"  # 17Lands game dump, renamed, "rt", newline="")
    head = f.readline().split(",")[:20]; ix = {n: i for i, n in enumerate(head)}
    by_day = defaultdict(lambda: defaultdict(int))
    for line in f:
        a = line.split(",", 19)
        colors = "".join(c for c in "WUBRG" if c in a[ix["main_colors"]])
        by_day[a[ix.get("game_time", ix["draft_time"])][:10]][colors] += 1
    days = sorted(by_day); start = date.fromisoformat(days[0])
    cum = defaultdict(int); rows = []
    for d in days:
        for g, n in by_day[d].items(): cum[g] += n
        k = (date.fromisoformat(d) - start).days + 1
        tot = sum(cum.values()); raw = sum(n for g, n in cum.items() if len(g) >= 3) / tot
        kept = {g: n for g, n in cum.items() if n >= MIN_GAMES}
        kt = sum(kept.values())
        filt = sum(n for g, n in kept.items() if len(g) >= 3) / kt if kt else 0.0
        n3 = sum(1 for g in kept if len(g) >= 3); a3 = sum(1 for g in cum if len(g) >= 3)
        rows.append((k, tot, raw, filt, n3, a3))
    return rows
for code in sys.argv[1:]:
    rows = run(code)
    print(f"\n{code}: day | games so far | share, all groups | share, groups with {MIN_GAMES}+ games | three-color groups kept")
    for k, tot, raw, filt, n3, a3 in rows:
        if k <= 7 or k in (10, 14, 21) or k == rows[-1][0]:
            print(f"{k} | {tot} | {100*raw:.1f}% | {100*filt:.1f}% | {n3} of {a3}")
