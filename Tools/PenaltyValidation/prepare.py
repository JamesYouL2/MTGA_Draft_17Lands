"""Inventory every catalog set, freeze a disjoint sample, and record exclusions."""
import argparse
import concurrent.futures
import contextlib
import csv
import gzip
import hashlib
import heapq
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Tools/AdvisorReplay'))
from sample import draft_priority, _names, _number

MANIFEST = 'https://unrealities.github.io/MTGA_Draft_17Lands/manifest.json'
SALT = 'confirm-three-rules-all-sets-v1-20261103'


def digest(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write_json(path, obj):
    tmp = path.with_suffix(path.suffix + '.partial')
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)


def catalog(manifest):
    result = {}
    for key, info in manifest['datasets'].items():
        m = re.fullmatch(r'(.+)_(PremierDraft|QuickDraft)_All', key)
        if m:
            code, fmt = m.groups()
            if code not in result or fmt == 'PremierDraft':
                result[code] = {'set': code, 'format': fmt, 'rating_key': key,
                    'rating_filename': info['filename'], 'rating_sha256': info['hash']}
    return [result[k] for k in sorted(result)]


def sample(lines, count, excluded):
    # Export prefixes are unquoted expansion,event_type,draft_id. Do not parse
    # hundreds of card-count columns for the millions of unselected picks.
    header = next(csv.reader([next(lines)]))
    col = {c: i for i, c in enumerate(header)}
    skill_field = 'user_game_win_rate_bucket' if 'user_game_win_rate_bucket' in col else 'user_match_win_rate_bucket'
    count_field = 'user_n_games_bucket' if 'user_n_games_bucket' in col else 'user_n_matches_bucket'
    if skill_field in col:col['user_game_win_rate_bucket']=col[skill_field]
    if count_field in col:col['user_n_games_bucket']=col[count_field]
    # Older exports put the two numeric user buckets first instead.
    assert col['draft_id'] == 2
    pack_cols = [(i, c[10:]) for i, c in enumerate(header) if c.startswith('pack_card_')]
    pool_cols = [(i, c[5:]) for i, c in enumerate(header) if c.startswith('pool_')]
    required = ['draft_id', 'user_game_win_rate_bucket', 'user_n_games_bucket',
                'event_match_wins', 'event_match_losses', 'pack_number', 'pick_number', 'pick']
    assert all(k in col for k in required), header[:20]
    kept, raw_drafts = [], {}
    current, keep = None, False
    total, excluded_seen = 0, 0
    for line in lines:
        prefix = line.split(',', 3)
        assert len(prefix) == 4 and '"' not in ''.join(prefix[:3])
        did = prefix[2]
        assert re.fullmatch(r'[A-Za-z0-9-]+', did), did
        if did != current:
            current = did
            total += 1
            priority = draft_priority(did, SALT)
            keep = did not in excluded and (did in raw_drafts or len(kept) < count or priority < -kept[0][0])
            if did in excluded:
                excluded_seen += 1
            if keep and did not in raw_drafts:
                if len(kept) == count:
                    raw_drafts.pop(heapq.heappop(kept)[1])
                heapq.heappush(kept, (-priority, did))
                raw_drafts[did] = []
        if keep:
            raw_drafts[did].append(line)
    drafts = {}
    for did, raw_lines in raw_drafts.items():
        for row in csv.reader(raw_lines):
            if did not in drafts:
                drafts[did] = {'id': did, 'skill': _number(row[col['user_game_win_rate_bucket']]),
                    'games': _number(row[col['user_n_games_bucket']]),
                    'wins': _number(row[col['event_match_wins']]), 'losses': _number(row[col['event_match_losses']]),
                    'time': row[col['draft_time']] if 'draft_time' in col else None, 'picks': []}
            drafts[did]['picks'].append([int(row[col['pack_number']])+1, int(row[col['pick_number']])+1,
                row[col['pick']], _names(row, pack_cols), _names(row, pool_cols)])
    assert not (set(drafts) & excluded)
    return [drafts[k] for k in sorted(drafts)], {'source_drafts': total, 'prior_drafts_excluded': excluded_seen,
        'skill_field':skill_field,'historical_count_field':count_field,
        'source_columns': [c for c in header if not c.startswith(('pack_card_','pool_'))]}


@contextlib.contextmanager
def export_csv(path):
    """Some older .csv.gz URLs contain a tar archive despite their suffix."""
    with gzip.open(path,'rb') as f:
        prefix=f.read(512)
    if prefix[257:262] == b'ustar':
        with tarfile.open(path,'r:gz') as archive:
            member=next(m for m in archive if m.isfile() and m.name.endswith('.csv'))
            with io.TextIOWrapper(archive.extractfile(member),encoding='utf-8',newline='') as f:
                yield f
    else:
        with gzip.open(path,'rt',encoding='utf-8',newline='') as f:
            yield f


def prepare(item, root, count, excluded):
    code, fmt = item['set'], item['format']
    folder = root / f'{code}_{fmt}'
    folder.mkdir(parents=True, exist_ok=True)
    receipt = folder / 'receipt.json'
    if receipt.exists():
        prior = json.loads(receipt.read_text())
        assert prior['requested_drafts'] == count and prior['salt'] == SALT
        return prior
    # 17Lands publishes this cube under underscores; use its documented alias.
    export_code = 'Cube_-_Powered' if code == 'Cube - Powered' else code
    url = f'https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.{urllib.parse.quote(export_code)}.{fmt}.csv.gz'
    rating_url = 'https://unrealities.github.io/MTGA_Draft_17Lands/' + urllib.parse.quote(item['rating_filename'])
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=45) as r:
            source_headers = dict(r.headers)
    except urllib.error.HTTPError as e:
        result = item | {'status': 'unavailable', 'dump_url': url, 'reason': f'HTTP {e.code} from public draft source'}
        write_json(folder/'unavailable.json', result)
        print(json.dumps(result), flush=True)
        return result
    start = time.time()
    for name, src in [('dump.csv.gz',url), ('dataset.json.gz',rating_url)]:
        target = folder / name
        if not target.exists():
            partial = target.with_suffix(target.suffix + '.partial')
            subprocess.run(['curl','--http1.1','-fsSL','--retry','3','--retry-all-errors','--max-time','900','-o',str(partial),src],check=True)
            partial.replace(target)
    assert digest(folder/'dataset.json.gz').lower() == item['rating_sha256'].lower(), f'Rating snapshot changed: {code}'
    with export_csv(folder/'dump.csv.gz') as f:
        drafts, coverage = sample(f, count, set(excluded.get(code, [])))
    assert len(drafts) > 0
    target = folder/'drafts.json.gz'
    with gzip.open(target.with_suffix('.gz.partial'), 'wt') as f:
        json.dump(drafts, f, separators=(',',':'), allow_nan=False)
    target.with_suffix('.gz.partial').replace(target)
    result = item | {'status': 'prepared', 'dump_url': url, 'rating_url': rating_url,
        'source_headers': source_headers, 'requested_drafts': count, 'drafts': len(drafts), 'salt': SALT,
        'sha256': {name:digest(folder/name) for name in ['dump.csv.gz','dataset.json.gz','drafts.json.gz']},
        'seconds': time.time()-start, **coverage}
    write_json(receipt,result)
    (folder/'dump.csv.gz').unlink()
    print(f"PREPARED {code} {fmt}: {len(drafts)} fresh drafts, excluded {coverage['prior_drafts_excluded']}", flush=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--exclude',type=Path,required=True)
    p.add_argument('--drafts',type=int,default=3000)
    a=p.parse_args();a.data.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(a.manifest.read_text()); excluded=json.loads(a.exclude.read_text())
    items=catalog(manifest)
    write_json(a.data/'catalog.json',{'source':MANIFEST,'manifest_sha256':digest(a.manifest),'sets':items})
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(prepare,item,a.data,a.drafts,excluded):item for item in items}
        results=[]
        for future in concurrent.futures.as_completed(futures):
            try:results.append(future.result())
            except Exception as e:
                item=futures[future];result=item|{'status':'failed','reason':str(e)}
                results.append(result);print(json.dumps(result),flush=True)
    write_json(a.data/'coverage.json',sorted(results,key=lambda r:r['set']))
    print('PREPARATION COMPLETE',len(results),flush=True)
