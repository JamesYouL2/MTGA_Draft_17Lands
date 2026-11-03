"""Freeze deterministic 17Lands samples and ratings for sequential ablations."""
import argparse
import concurrent.futures
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "AdvisorReplay"))
from sample import sample_drafts

SETS = ["DFT", "FDN", "FIN", "FRA", "HOB", "MSH", "SOS", "TDM", "TLA", "TMT"]


def prepare(code, root, count, salt):
    folder = root / code
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / "receipt.json").exists():
        receipt = json.loads((folder / "receipt.json").read_text())
        if receipt["requested_drafts"] != count or receipt["salt"] != salt:
            raise ValueError("Existing sample has a different count/salt")
        return receipt
    start = time.time()
    dump = folder / "dump.csv.gz"
    dataset = folder / "dataset.json.gz"
    urls = [
        (dump, f"https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.{code}.PremierDraft.csv.gz"),
        (dataset, f"https://unrealities.github.io/MTGA_Draft_17Lands/{code}_PremierDraft_All_Data.json.gz"),
    ]
    for path, url in urls:
        if not path.exists():
            subprocess.run(["curl", "-fsSL", "--retry", "3", "--max-time", "900", "-o", str(path), url], check=True)
    with gzip.open(dump, "rt", encoding="utf-8", newline="") as f:
        drafts = sample_drafts(f, count, salt)
    if len(drafts) != count:
        raise ValueError(f"{code}: requested {count}, got {len(drafts)}")
    target = folder / "drafts.json.gz"
    with gzip.open(target, "wt", encoding="utf-8") as f:
        json.dump(drafts, f)
    receipt = {
        "set": code, "requested_drafts": count, "drafts": len(drafts), "salt": salt,
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p, _ in urls},
        "sample_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "sources": [url for _, url in urls], "seconds": round(time.time() - start, 2),
    }
    (folder / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    dump.unlink()  # keep frozen samples/ratings; the large raw dump is reproducible
    print(json.dumps(receipt), flush=True)
    return receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--drafts", type=int, default=1000)
    p.add_argument("--salt", default="isolated-ablations-2026-11-03")
    p.add_argument("--sets", nargs="+", default=SETS)
    a = p.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda code: prepare(code, a.data, a.drafts, a.salt), a.sets))
