"""Fast three-rule replay with exact edited-engine parity and one choice/draft."""
import argparse
import concurrent.futures
import datetime
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Tools/Ablations'),str(ROOT)]
from run import App, build_traces, read_gz, write_gz, score_map
import run as trace_module
from variants import BASE_SHA, ENGINE, advisor_class, variant_source, assert_baseline
from src import constants
from src.card_utils import get_functional_cmc

VARIANTS=['no-fixing-hunger','no-removal-saturation','no-curve-heavy']
TARGETS={'no-fixing-hunger':(1.4,'Critical: Needs Fixing'),
         'no-removal-saturation':(0.8,'Removal Saturated'),
         'no-curve-heavy':(0.7,'Curve Too Heavy')}
ORIGINAL={'DFT','FDN','FIN','FRA','HOB','MSH','SOS','TDM','TLA','TMT'}


def write_cache(path,value):
    """Use the C JSON encoder and low compression for reproducible scratch caches."""
    def convert(v):
        if isinstance(v,set):return sorted(v)
        raise TypeError(type(v).__name__)
    payload=json.dumps(value,separators=(',',':'),default=convert,allow_nan=False).encode()
    temporary=path.with_suffix(path.suffix+'.partial')
    with gzip.open(temporary,'wb',compresslevel=1) as f:f.write(payload)
    temporary.replace(path)


def sd(values):
    mean=sum(values)/len(values)
    return math.sqrt(sum((v-mean)**2 for v in values)/len(values)) or 1.0


def basic(card):
    return card['name'] in constants.BASIC_LANDS or ('Basic' in card.get('types',[]) and 'Land' in card.get('types',[]))


def fast_scores(rows,state,names,variant,base_cls,head_cls,pack_no):
    """Only an active target return can change when its guard is removed."""
    scores=[0.0 if basic(names[r[0]]) else round(max(0.0,r[7]),1) for r in rows]
    if variant == 'baseline':return scores
    multiplier,reason=TARGETS[variant]
    suspects=[i for i,r in enumerate(rows) if abs(r[5]-multiplier)<1e-12 and not basic(names[r[0]])]
    if not suspects:return scores
    a=object.__new__(base_cls);a.__dict__.update(state);a.pool=[None]*state['pool_size']
    h=object.__new__(head_cls);h.__dict__.update(a.__dict__)
    for i in suspects:
        row=rows[i];card=names[row[0]]
        if a._calculate_composition_bonus(card,pack_no)[1] == reason:
            role=h._calculate_composition_bonus(card,pack_no)[0]
            scores[i]=round(max(0.0,(row[2]+row[3])*row[4]*role),1)
    return scores


def metrics(scores,taken_index,base_sd=None):
    order=sorted(range(len(scores)),key=lambda i:-scores[i])
    gap=scores[order[0]]-scores[taken_index]
    return {'top':order[0],'strict':len(order)<2 or scores[order[0]]>scores[order[1]],
            'top1':int(order[0]==taken_index),'top3':int(taken_index in order[:3]),
            'regret':gap/sd(scores),'fixed_regret':gap/(base_sd or sd(scores))}


def enrich(folder,source):
    target=folder/'validation-traces.json.gz'
    if target.exists():return
    # Only the scratch serialization changes; reference scoring is untouched.
    trace_module.write_gz=write_cache
    build_traces(folder,source)
    data=read_gz(folder/'traces.json.gz')
    app=App(str(folder/'dataset.json.gz'));names={c['name']:c for c in app.dataset.get_card_ratings().values()}
    Base=advisor_class(source)
    for draft in data['drafts']:
        for pick in draft['picks']:
            pack_no,pick_no,taken,state,rows=pick
            # Score maps keep the first copy of a duplicate name.
            unique={}
            for r in rows:unique.setdefault(r[0],r)
            rows=list(unique.values());pick[4]=rows
            scores=fast_scores(rows,state,names,'baseline',Base,Base,pack_no)
            ti=next(i for i,r in enumerate(rows) if r[0]==taken)
            meta=metrics(scores,ti);meta.update({'sd':sd(scores),'taken_index':ti,'scores':scores})
            pick.append(meta)
    data['validation_version']=1
    write_cache(target,data)
    print(f'VALIDATION TRACES {folder.name}: {len(data["drafts"])}',flush=True)


def features(app,state,rows,base,head,b,h,pack_no,pick_no):
    d={'pack':pack_no,'pick':pick_no,'pool_size':state['pool_size'],
       'global_mean':state['global_mean'],'global_std':state['global_std'],
       'lane_colors':len(state['main_colors']),'pack_unique_cards':len(rows),
       'base_margin':(base[b]-base[h])/sd(base),'head_margin':(head[h]-head[b])/sd(base)}
    for c in 'WUBRG':d['lane_'+c]=int(c in state['main_colors'])
    for k,v in state['pool_metrics'].items():d['pool_'+k]=len(v) if isinstance(v,(list,set)) else v
    for label,i in [('base',b),('head',h)]:
        card=app.dataset.get_data_by_name([rows[i][0]])[0]
        stats=card.get('deck_colors',{}).get('All Decks',{})
        for k in ['gihwr','iwd','alsa','samples']:
            try:d[label+'_'+k]=float(stats.get(k) or 0)
            except (TypeError,ValueError):d[label+'_'+k]=0.
        d[label+'_cmc']=get_functional_cmc(card)
        d[label+'_colors']=len(card.get('colors',[]))
        for t in ['Land','Creature','Instant','Sorcery','Artifact','Enchantment']:
            d[label+'_type_'+t]=int(t in card.get('types',[]))
        for tag in ['removal','fixing_ramp','card_draw']:
            d[label+'_tag_'+tag]=int(tag in card.get('tags',[]))
        d[label+'_cast']=rows[i][4];d[label+'_role']=rows[i][5]
    return d


def run_variant(variant,folders,out,source):
    target=out/f'{variant}.json.gz'
    if target.exists():
        if read_gz(target).get('analysis_version') == 2:return
        print('Recompute older validation output:',target,flush=True)
    Base=advisor_class(source);Head=advisor_class(variant_source(variant,source)[1])
    summaries,choices,coverage=[],[],{}
    for folder in folders:
        receipt=json.loads((folder/'receipt.json').read_text());code=receipt['set']
        app=App(str(folder/'dataset.json.gz'));names={c['name']:c for c in app.dataset.get_card_ratings().values()}
        original_by_id={d['id']:d for d in read_gz(folder/'drafts.json.gz')}
        known=set(app.full_names)|set(names)
        unmatched=Counter(p[2] for d in original_by_id.values() for p in d['picks'] if p[2] not in known)
        checks=0;counts=Counter()
        for draft in read_gz(folder/'validation-traces.json.gz')['drafts']:
            original_draft=original_by_id[draft['id']]
            original_picks={(p[0],p[1]):p for p in original_draft['picks']}
            n=0;bt=ht=0;br=hr=fr=0.;changed=0;selected=None
            for pack_no,pick_no,taken,state,rows,meta in draft['picks']:
                base=meta['scores']
                head=fast_scores(rows,state,names,variant,Base,Head,pack_no)
                # Independently execute the complete edited engine on real packs.
                if checks < 100:
                    a=object.__new__(Head);a.__dict__.update(state)
                    a.pool=[None]*state['pool_size']
                    # evaluate_pack's lane/needs-playables needs real cards; recover the logged pool.
                    original=original_picks[pack_no,pick_no]
                    a.pool=app.cards(original[4]);a.fixing_map={}
                    # Castability uses the actual fixing map; a fully initialized engine supplies it.
                    actual=score_map(Head(app.metrics,a.pool).evaluate_pack(app.cards(original[3]),pick_no,pack_no))
                    expected={r[0]:v for r,v in zip(rows,head)}
                    assert actual==expected,(folder.name,variant,actual,expected)
                    checks+=1
                hm=meta if head==base else metrics(head,meta['taken_index'],meta['sd'])
                n+=1;bt+=meta['top1'];ht+=hm['top1'];br+=meta['regret'];hr+=hm['regret'];fr+=hm['fixed_regret']
                b,h=meta['top'],hm['top'];changed+=int(b!=h)
                if b!=h:
                    counts['changed_picks']+=1
                    if not (meta['strict'] and hm['strict']):counts['tied_disagreements']+=1
                    elif selected is None:
                        original=original_picks[pack_no,pick_no]
                        if any(name not in known for name in [original[2],*original[3],*original[4]]):
                            counts['strict_disagreement_with_incomplete_card_mapping']+=1
                            continue
                        choice=1 if taken==rows[h][0] else (0 if taken==rows[b][0] else None)
                        selected={'id':draft['id'],'set':code,'format':receipt['format'],'variant':variant,
                            'skill':draft['skill'],'games':draft['games'],'wins':draft['wins'],'losses':draft['losses'],
                            'choice':choice,'base_card':rows[b][0],'head_card':rows[h][0],
                            'features':features(app,state,rows,base,head,b,h,pack_no,pick_no)}
                        selected['features']['published_skill_is_match']=int(receipt.get('skill_field','user_game_win_rate_bucket')=='user_match_win_rate_bucket')
                        try:
                            selected['features']['draft_day']=datetime.datetime.fromisoformat(original_draft['time']).date().toordinal()
                        except (TypeError,ValueError):selected['features']['draft_day']=None
            summaries.append({k:draft[k] for k in ['id','skill','games','wins','losses']}|{
                'set':code,'n':n,'base_top1':bt,'head_top1':ht,'base_regret':br/n if n else None,
                'head_regret':hr/n if n else None,'fixed_head_regret':fr/n if n else None,'changed':changed})
            if selected is not None:
                choices.append(selected);counts['drafts_with_strict_disagreement']+=1
                counts['chose_neither' if selected['choice'] is None else f'chose_{selected["choice"]}']+=1
        coverage[code]=dict(counts)|{'parity_checks':checks,'unmatched_taken_picks':sum(unmatched.values()),
            'unmatched_taken_names':dict(unmatched.most_common(20))}
        print(f'{variant}: {code}, {dict(counts)}, {checks} actual-engine parity packs',flush=True)
    write_gz(target,{'variant':variant,'base_sha':BASE_SHA,'analysis_version':2,
        'protocol_sha256':hashlib.sha256((Path(__file__).parent/'PROTOCOL.md').read_bytes()).hexdigest(),
        'drafts':summaries,'choices':choices,'coverage':coverage})
    print('COMPLETE',variant,len(summaries),'drafts',len(choices),'first disagreements',flush=True)


def prepare_all(data,source,workers,wait):
    """Parallelize unchanged-baseline preparation, never ablation runs."""
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        pending={};submitted=set()
        while True:
            folders=sorted(f for f in data.iterdir() if f.is_dir() and (f/'receipt.json').exists())
            for folder in folders:
                if folder not in submitted:
                    submitted.add(folder)
                    if not (folder/'validation-traces.json.gz').exists():
                        pending[pool.submit(enrich,folder,source)]=folder
            for future in list(pending):
                if future.done():
                    future.result();del pending[future]
            if not pending and ((data/'coverage.json').exists() or not wait):return folders
            time.sleep(3)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--prepare-traces',action='store_true');p.add_argument('--wait',action='store_true')
    p.add_argument('--trace-workers',type=int,default=4)
    a=p.parse_args();assert_baseline();a.out.mkdir(parents=True,exist_ok=True)
    source=(ROOT/ENGINE).read_text()
    folders=prepare_all(a.data,source,a.trace_workers,a.wait)
    if not a.prepare_traces:
        for variant in VARIANTS:
            # Only used for the first 100 reference packs/set; don't retain raw pools in result rows.
            run_variant(variant,folders,a.out,source)
