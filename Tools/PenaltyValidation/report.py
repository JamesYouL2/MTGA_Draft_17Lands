"""Cross-fitted observational win-rate validation, with explicit causal limits."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.stats import norm, t
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(HERE.parent/'Ablations'),str(ROOT)]
from Tools.PenaltyValidation.evaluate import VARIANTS, ORIGINAL
from run import read_gz
from Tools.PenaltyValidation.prepare import digest, write_json

SEED=20261103
ALPHA=.05/3


def complete(r):
    w,l=r.get('wins'),r.get('losses')
    return (w is not None and l is not None and float(w).is_integer() and float(l).is_integer()
        and 0<=w<=7 and 0<=l<=3 and w+l>0 and (w==7 or l==3))


def matrix(rows):
    keys=sorted({k for r in rows for k in r['features']})
    sets=sorted({r['set'] for r in rows});si={s:i for i,s in enumerate(sets)}
    x=np.array([[si[r['set']],float(r['skill']) if r['skill'] is not None else np.nan,
        math.log1p(r['games']) if r['games'] is not None and r['games']>=0 else np.nan,
        *[r['features'].get(k,np.nan) for k in keys]] for r in rows],dtype=float)
    return x,['set_category','skill_bucket','log_historical_games',*keys]


def pseudo_outcomes(a,y,p,m):
    clipped=np.clip(p,.05,.95)
    phi=m.copy()
    for arm in [0,1]:
        prob=clipped if arm else 1-clipped
        phi[:,arm,:]+=(a==arm)[:,None]/prob[:,None]*(y-m[:,arm,:])
    return phi


def nuisance(rows):
    x,columns=matrix(rows)
    a=np.array([r['choice'] for r in rows],dtype=int)
    wins=np.array([r['wins'] for r in rows],dtype=float)
    games=np.array([r['wins']+r['losses'] for r in rows],dtype=float)
    y=np.column_stack([wins,games,wins/games])
    folds=np.array([int(hashlib.sha256(('confirm-fold'+r['id']).encode()).hexdigest()[:8],16)%5 for r in rows])
    p=np.full(len(rows),np.nan);m=np.full((len(rows),2,3),np.nan)
    options=dict(max_iter=150,max_depth=4,min_samples_leaf=30,l2_regularization=10.,
                 early_stopping=False,categorical_features=[0],random_state=SEED)
    for fold in range(5):
        train,test=folds!=fold,folds==fold
        assert test.any() and min(np.bincount(a[train],minlength=2))>=30,'Insufficient arm support for five-fold adjustment'
        model=HistGradientBoostingClassifier(**options).fit(x[train],a[train])
        p[test]=model.predict_proba(x[test])[:,1]
        for arm in [0,1]:
            mask=train&(a==arm)
            for outcome in range(3):
                reg=HistGradientBoostingRegressor(**options).fit(x[mask],y[mask,outcome])
                pred=reg.predict(x[test]);lower,upper=[(0.,7.),(1.,10.),(0.,1.)][outcome]
                m[test,arm,outcome]=np.clip(pred,lower,upper)
        print(f'  nuisance fold {fold+1}/5 complete',flush=True)
    assert np.isfinite(p).all() and np.isfinite(m).all()
    clipped=np.clip(p,.05,.95)
    phi=pseudo_outcomes(a,y,p,m)
    observed=m[np.arange(len(rows)),a,:]
    diagnostics={'rows':len(rows),'arms':dict(Counter(map(int,a))),
        'propensity_min':float(p.min()),'propensity_max':float(p.max()),
        'propensity_clipped_percent':100*float(np.mean((p<.05)|(p>.95))),
        'outcome_crossfit_rmse':dict(zip(['event_wins','event_games','event_win_fraction'],
            map(float,np.sqrt(np.mean((y-observed)**2,axis=0))))),
        'propensity_brier':float(np.mean((p-a)**2)),
        'effective_arm_samples':{str(arm):float((lambda w:w.sum()**2/(w*w).sum())(
            (a==arm)/(clipped if arm else 1-clipped))) for arm in [0,1]},'features':columns}
    return phi,p,diagnostics


def ratio_contrast(phi,sets):
    """Ratio-of-mean game rates and their paired influence functions."""
    n=len(phi);rates=[];influences=[]
    for arm in [0,1]:
        w,g=phi[:,arm,0],phi[:,arm,1]
        rate=w.mean()/g.mean()
        rates.append(float(rate));influences.append((w-rate*g)/g.mean())
    influence=influences[1]-influences[0]
    se=float(influence.std(ddof=1)/np.sqrt(n)) if n>1 else None
    critical=float(norm.ppf(1-ALPHA/2));difference=rates[1]-rates[0]
    grouped={s:float(influence[np.array(sets)==s].sum()) for s in set(sets)}
    k=len(grouped)
    cluster_se=math.sqrt(k/(k-1)*sum(v*v for v in grouped.values())/n**2) if k>1 else None
    cluster_critical=float(t.ppf(1-ALPHA/2,k-1)) if k>1 else None
    interval=lambda error,c:[100*(difference-c*error),100*(difference+c*error)] if error is not None else None
    frac=phi[:,1,2]-phi[:,0,2]
    return {'drafts':n,'sets':k,'baseline_rate_percent':100*rates[0],'removal_rate_percent':100*rates[1],
        'difference_pp':100*difference,'draft_se_pp':100*se if se is not None else None,
        'simultaneous_draft_ci_pp':interval(se,critical),
        'set_cluster_se_pp':100*cluster_se if cluster_se is not None else None,
        'simultaneous_set_cluster_ci_pp':interval(cluster_se,cluster_critical),
        'event_average_fraction_difference_pp':100*float(frac.mean()),
        'event_average_fraction_se_pp':100*float(frac.std(ddof=1)/np.sqrt(n)) if n>1 else None}


def raw_rates(rows):
    result={}
    for arm in [0,1]:
        rr=[r for r in rows if r['choice']==arm];w=sum(r['wins'] for r in rr);g=sum(r['wins']+r['losses'] for r in rr)
        result[str(arm)]={'drafts':len(rr),'wins':w,'games':g,'win_rate_percent':100*w/g if g else None}
    if all(result[str(a)]['games'] for a in [0,1]):result['difference_pp']=result['1']['win_rate_percent']-result['0']['win_rate_percent']
    return result


def secondary(drafts):
    out={}
    for label,rs in [('all',drafts),('strong',[r for r in drafts if (r['skill'] or 0)>=.6 and (r['games'] or 0)>=50])]:
        n=sum(r['n'] for r in rs)
        out[label]={'picks':n,'agreement_difference_pp':100*sum(r['head_top1']-r['base_top1'] for r in rs)/n if n else None}
    rs=[r for r in drafts if complete(r) and r['n']]
    if len(rs)>=100:
        sys.path.insert(0,str(HERE.parent/'AdvisorReplay'))
        # Use the original fixed controls, with the actual observed win fraction.
        import importlib.util
        spec=importlib.util.spec_from_file_location('original_replay_report',HERE.parent/'AdvisorReplay/report.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        ctrl=mod.controls(rs,[r['set'] for r in rs])
        y=np.array([r['wins']/(r['wins']+r['losses']) for r in rs])
        out['win_fraction_regret_slopes']={f:float(mod.wins_slope(np.array([r[f] for r in rs]),y,ctrl)) for f in ['base_regret','head_regret','fixed_head_regret']}
    return out


def analyze(path):
    data=read_gz(path)
    valid=[r for r in data['choices'] if r['choice'] is not None and complete(r)]
    exclusions={'sampled_drafts':len(data['drafts']),'first_strict_disagreements':len(data['choices']),
        'chose_neither':sum(r['choice'] is None for r in data['choices']),
        'missing_or_incomplete_selected_outcomes':sum(r['choice'] is not None and not complete(r) for r in data['choices'])}
    result={'variant':data['variant'],'selection':exclusions,'coverage':data['coverage'],
        'secondary':secondary(data['drafts']),'raw':raw_rates(valid)}
    try:phi,p,diag=nuisance(valid)
    except AssertionError as e:
        result['adjustment_error']=str(e);return result,None
    sets=np.array([r['set'] for r in valid]);result['diagnostics']=diag
    result['adjusted']=ratio_contrast(phi,sets)
    for name,mask in [('original_sets',np.isin(sets,list(ORIGINAL))),('new_sets',~np.isin(sets,list(ORIGINAL))),
                      ('overlap_only',(p>=.1)&(p<=.9))]:
        if mask.sum()>1:result[name]=ratio_contrast(phi[mask],sets[mask])
    result['per_set']={s:ratio_contrast(phi[sets==s],sets[sets==s])|{'raw':raw_rates([r for r in valid if r['set']==s])} for s in sorted(set(sets))}
    predictions=[{'id':r['id'],'set':r['set'],'choice':r['choice'],'wins':r['wins'],'losses':r['losses'],
        'propensity':float(p[i]),'pseudo_outcomes':phi[i].tolist()} for i,r in enumerate(valid)]
    return result,predictions


def markdown(results,coverage):
    good=[r for r in coverage if r['status']=='prepared'];bad=[r for r in coverage if r['status']!='prepared']
    lines=['# All-set validation of three pick rules','',
        '**These are adjusted observational associations, not measured policy win-rate effects.**',
        'The available data cannot establish whether removing a rule increases or decreases actual drafting-policy strength. That requires randomized rule-on/rule-off drafts and played games.','',
        f"Catalog: {len(coverage)} sets. Matching ratings plus draft/outcome exports: {len(good)} sets, {sum(r['drafts'] for r in good):,} fresh drafts. Prior-screen draft IDs are excluded.",'',
        'Tested sets: '+', '.join(r['set'] for r in good)+'.','',
        '## Primary recorded-outcome comparison','',
        'One first strict disagreement per draft; only completed events where the human took one of the two recommendations. Positive differences favor removal. Intervals are 98.333% per comparison (95% familywise across three rules).','',
        '| Rule removed | Compared drafts / sets | Adjusted win-rate association (points) | Draft interval | Set-cluster interval | New-set association |',
        '|---|---:|---:|---|---|---:|']
    for r in results:
        if 'adjusted' not in r:
            lines.append(f"| {r['variant']} | — | Adjustment unavailable: {r.get('adjustment_error')} | — | — | — |");continue
        a=r['adjusted'];ci=lambda v:'—' if v is None else f'[{v[0]:+.2f}, {v[1]:+.2f}]'
        new=r.get('new_sets',{}).get('difference_pp')
        new_cell=f'{new:+.2f}' if new is not None else '—'
        lines.append(f"| {r['variant']} | {a['drafts']:,} / {a['sets']} | {a['difference_pp']:+.2f} | {ci(a['simultaneous_draft_ci_pp'])} | {ci(a['simultaneous_set_cluster_ci_pp'])} | {new_cell} |")
    lines+=['','## Coverage exclusions','', '| Set | Rating format | Reason |','|---|---|---|']
    for r in bad:lines.append(f"| {r['set']} | {r['format']} | {r['reason']} |")
    lines+=['','QuickDraft ratings are not substituted into PremierDraft outcome evaluation. Cube uses the export name documented in 17Lands’ public catalog.','',
        'The primary comparison requires a fully mapped pack and pre-choice pool. Current Cube ratings and the older Cube export have different inventories. Its partial replay is not evidence validating unmapped states; per-rule comparison counts show whether any usable Cube evidence remains.','',
        '## Interpretation','',
        '- Human agreement is a secondary metric. It does not measure wins gained by following a recommendation.',
        '- The same observed human outcome cannot be assigned to both counterfactual policies. This evaluates one observed choice with subsequent human drafting/deck-building, not a full replacement policy.',
        '- Five-fold outcome/propensity adjustment uses only out-of-fold predictions. Unmeasured skill, later decisions, matchmaking, choice selection and completed-event selection can still confound results.',
        '- Player IDs are absent; player clustering is unavailable. The public skill bucket and rating snapshots may include the evaluated games, so this is not a fully chronological out-of-sample test.',
        '- Full details, per-set estimates, overlap/precision diagnostics, subgroup sensitivities and raw contrasts are in summary.json. The frozen analysis specification is PROTOCOL.md.',
        '- No application rule is removed by this validation branch. A causal strength verdict requires a prospective randomized test.','',
        'Data: 17Lands public datasets, CC BY 4.0, https://www.17lands.com/public_datasets.','']
    return '\n'.join(lines)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--reports',type=Path,required=True)
    a=p.parse_args();a.reports.mkdir(parents=True,exist_ok=True)
    coverage=json.loads((a.data/'coverage.json').read_text())
    results=[]
    from run import write_gz
    for v in VARIANTS:
        print('ANALYZE',v,flush=True);result,preds=analyze(a.out/f'{v}.json.gz');results.append(result)
        write_json(a.reports/f'{v}.json',result)
        if preds:write_gz(a.out/f'{v}-crossfit.json.gz',preds)
    write_json(a.reports/'summary.json',results);write_json(a.reports/'coverage.json',coverage)
    (a.reports/'RESULTS.md').write_text(markdown(results,coverage))
    import shutil
    shutil.copy(HERE/'PROTOCOL.md',a.reports/'PROTOCOL.md')
    write_json(a.reports/'manifest.json',{'protocol_sha256':digest(HERE/'PROTOCOL.md'),
        'package_versions':{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','numba','pydantic']},
        'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in HERE.glob('*.py')},
        'raw_output_sha256':{p.name:digest(p) for p in a.out.glob('*.json.gz')}})
    print('ALL VALIDATION REPORTS COMPLETE',flush=True)
