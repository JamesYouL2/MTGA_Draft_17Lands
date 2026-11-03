"""Audit immutable inputs and archive compact raw observations for reproduction."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from Tools.PenaltyValidation.prepare import digest,write_json,SALT
from Tools.PenaltyValidation.evaluate import VARIANTS
from run import read_gz
from variants import BASE_SHA,assert_baseline


def add_bytes(archive,name,content):
    info=tarfile.TarInfo(name);info.size=len(content);info.mtime=0
    archive.addfile(info,io.BytesIO(content))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['data','out','reports','manifest','exclude','original-archive','bundle']:
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();assert_baseline()
    coverage=json.loads((a.data/'coverage.json').read_text());excluded=json.loads(a.exclude.read_text())
    assert len(coverage)==27 and not any(r['status']=='failed' for r in coverage)
    prepared=[r for r in coverage if r['status']=='prepared'];assert len(prepared)==22
    original_receipts={}
    with tarfile.open(a.original_archive) as old:
        for m in old.getmembers():
            if m.name.startswith('inputs/') and m.name.endswith('/receipt.json'):
                original_receipts[m.name.split('/')[1]]=json.load(old.extractfile(m))
    inputs=[];selections={};draft_keys=[]
    for receipt in prepared:
        code,fmt=receipt['set'],receipt['format'];folder=a.data/f'{code}_{fmt}'
        for name in ['dataset.json.gz','drafts.json.gz']:
            assert digest(folder/name)==receipt['sha256'][name],(code,name)
        drafts=read_gz(folder/'drafts.json.gz');ids=[d['id'] for d in drafts]
        assert len(ids)==3000 and len(set(ids))==3000 and not (set(ids)&set(excluded.get(code,[])))
        selections[folder.name]=ids;draft_keys.extend((code,did) for did in ids)
        with gzip.open(folder/'drafts.json.gz','rb') as f:content_sha=hashlib.file_digest(f,'sha256').hexdigest()
        assert (folder/'validation-traces.json.gz').exists()
        same_source=None
        if code in original_receipts:
            same_source=receipt['sha256']['dump.csv.gz']==original_receipts[code]['sha256']['dump.csv.gz']
            assert same_source,(code,'original public dump changed')
        inputs.append({'set':code,'format':fmt,'drafts':len(ids),'sample_uncompressed_sha256':content_sha,
            'same_public_source_as_original_screen':same_source,
            'baseline_trace_sha256':digest(folder/'validation-traces.json.gz')})
    assert len(draft_keys)==66000 and len(set(draft_keys))==66000
    expected=set(draft_keys);protocol_sha=digest(ROOT/'Tools/PenaltyValidation/PROTOCOL.md')
    agreement={};agreement_rows=[]
    for v in VARIANTS:
        data=read_gz(a.out/f'{v}.json.gz')
        assert data['analysis_version']==2 and data['protocol_sha256']==protocol_sha
        assert {(r['set'],r['id']) for r in data['drafts']}==expected
        assert len(data['coverage'])==22 and all(c['parity_checks']==100 for c in data['coverage'].values())
        def pick_agreement(rows):
            n=sum(r['n'] for r in rows)
            return {'drafts':len(rows),'picks':n,
                'difference_pp':100*sum(r['head_top1']-r['base_top1'] for r in rows)/n if n else None}
        agreement[v]={s:{'all':pick_agreement([r for r in data['drafts'] if r['set']==s]),
            'strong':pick_agreement([r for r in data['drafts'] if r['set']==s and (r['skill'] or 0)>=.6 and (r['games'] or 0)>=50])}
            for s in sorted({r['set'] for r in data['drafts']})}
        all_picks=pick_agreement(data['drafts'])
        strong=pick_agreement([r for r in data['drafts'] if (r['skill'] or 0)>=.6 and (r['games'] or 0)>=50])
        agreement_rows.append(f"| {v} | {all_picks['difference_pp']:+.3f} | {strong['difference_pp']:+.3f} |")
    write_json(a.reports/'agreement-by-set.json',agreement)
    audit={'application_base_sha':BASE_SHA,'sample_salt':SALT,'drafts':66000,'catalog_sets':27,'replayed_sets':22,
        'prior_draft_ids_excluded':sum(map(len,excluded.values())),'excluded_ids_sha256':digest(a.exclude),
        'publisher_manifest_sha256':digest(a.manifest),'protocol_sha256':protocol_sha,'inputs':inputs,
        'raw_output_sha256':{f.name:digest(f) for f in sorted(a.out.glob('*.json.gz'))},
        'reproduction':'Frozen rating bytes and selected draft IDs are included. Re-download each public dump from its receipt, verify its SHA-256, and run prepare.py with the saved manifest/exclusions/salt to reconstruct the sampled packs. Check the uncompressed sample SHA-256; gzip timestamps need not match.'}
    write_json(a.reports/'input-audit.json',audit)
    manifest=json.loads((a.reports/'manifest.json').read_text());manifest['input_audit_sha256']=digest(a.reports/'input-audit.json')
    for name in ['evaluate.py','prepare.py','report.py']:
        relative='Tools/PenaltyValidation/'+name
        assert manifest['source_sha256'][relative]==digest(ROOT/relative),f'Analysis source changed: {name}'
    manifest['source_sha256']['Tools/PenaltyValidation/package.py']=digest(Path(__file__))
    manifest['packaging_source_sha256']=digest(Path(__file__))
    manifest['interval_scope']='Familywise 95% control covers the three pooled primary contrasts. Per-set and subgroup intervals are exploratory and are not simultaneous across all subgroups.'
    write_json(a.reports/'manifest.json',manifest)
    index=a.reports/'RESULTS.md'
    marker='\n<!-- agreement:start -->'
    text=index.read_text().split(marker,1)[0]
    summaries=json.loads((a.reports/'summary.json').read_text())
    if all(r['adjusted']['simultaneous_draft_ci_pp'][0]<=0<=r['adjusted']['simultaneous_draft_ci_pp'][1] for r in summaries):
        decision='## Decision\n\nNone of the three rules is established to hurt win rate: all three primary intervals include zero. If removal requires a demonstrated strength improvement, retain the rules pending stronger evidence. Removal saturation is the most promising follow-up candidate; heavy curve is centered on zero. This is not evidence of equivalence. A [prospective randomized trial](../../Tools/PenaltyValidation/PROSPECTIVE_TEST.md) is required to establish the effect of switching the full drafting policy.\n\n'
        if '## Decision\n' not in text:text=text.replace('## Primary recorded-outcome comparison\n',decision+'## Primary recorded-outcome comparison\n')
    text+=marker+'\n## Secondary pick agreement\n\nDifferences are percentage points of top-choice agreement; this measures imitation, not win-rate effects. Per-set details are in [agreement-by-set.json](agreement-by-set.json). Cube and other incomplete card states remain in this secondary partial-replay metric; the primary outcome filter is stricter.\n\n| Rule removed | All drafters | Strong drafters |\n|---|---:|---:|\n'+'\n'.join(agreement_rows)+'\n\nFamilywise 95% control covers the three pooled primary contrasts. Per-set and subgroup intervals are exploratory and are not simultaneous across all subgroups. These intervals do not bound the win-rate effect of switching the full drafting policy. All matched outcome exports in this run are PremierDraft; this study does not validate effects in QuickDraft, TradDraft or PickTwoDraft.\n'
    index.write_text(text)
    with tarfile.open(a.bundle,'w:gz',compresslevel=1) as archive:
        add_bytes(archive,'bundle-manifest.json',json.dumps(audit,indent=2).encode())
        archive.add(a.manifest,arcname='inputs/publisher-manifest.json')
        archive.add(a.exclude,arcname='inputs/original-screen-excluded-ids.json')
        for receipt in prepared:
            name=f"{receipt['set']}_{receipt['format']}";folder=a.data/name
            archive.add(folder/'dataset.json.gz',arcname=f'inputs/{name}/dataset.json.gz')
            archive.add(folder/'receipt.json',arcname=f'inputs/{name}/receipt.json')
            add_bytes(archive,f'inputs/{name}/selected-draft-ids.json.gz',gzip.compress(json.dumps(selections[name]).encode(),compresslevel=1,mtime=0))
        for f in sorted(a.out.glob('*.json.gz')):archive.add(f,arcname='raw-results/'+f.name)
    print(json.dumps({'bundle':str(a.bundle),'bytes':a.bundle.stat().st_size,'sha256':digest(a.bundle),'drafts':66000,'sets':22}),flush=True)
