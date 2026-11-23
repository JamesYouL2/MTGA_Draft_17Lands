"""Download a heads run's artifacts one at a time and keep a compact copy:
per draft id, skill, games, wins, losses, deck_score, pool_gihwr and picks[:5].

    python compact.py RUN OUTDIR label1,label2,...
"""
import gzip
import json
import os
import shutil
import subprocess
import sys

run, out, keep = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
names = subprocess.run(
    ["gh", "api", "--paginate",
     f"repos/JamesYouL2/MTGA_Draft_17Lands/actions/runs/{run}/artifacts?per_page=100",
     "-q", ".artifacts[].name"],
    capture_output=True, text=True, check=True).stdout.split()
names = sorted(n for n in names if n.startswith("heads-") and n != "heads-report")
print(len(names), "artifacts", flush=True)
for n in names:
    dest = os.path.join(out, n)
    if os.path.isdir(dest):
        continue
    raw = os.path.join(out + "-raw", n)
    shutil.rmtree(raw, ignore_errors=True)
    subprocess.run(["gh", "run", "download", run, "-R", "JamesYouL2/MTGA_Draft_17Lands",
                    "-n", n, "-D", raw], check=True)
    os.makedirs(dest + ".tmp", exist_ok=True)
    for f in os.listdir(raw):
        label = f[:-5]
        if keep != ["all"] and label not in keep:
            continue
        with open(os.path.join(raw, f)) as fh:
            data = json.load(fh)
        data = {"set": data["set"], "label": data["label"], "drafts": [
            {k: d.get(k) for k in ("id", "skill", "games", "wins", "losses", "deck_score", "pool_gihwr")}
            | {"picks": [p[:5] for p in d["picks"]]} for d in data["drafts"]]}
        with gzip.open(os.path.join(dest + ".tmp", f + ".gz"), "wt") as g:
            json.dump(data, g, separators=(",", ":"))
    os.rename(dest + ".tmp", dest)
    shutil.rmtree(raw)
    print(n, flush=True)
