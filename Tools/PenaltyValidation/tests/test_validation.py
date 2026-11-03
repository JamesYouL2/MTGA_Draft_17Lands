import csv
import io
import gzip
import tarfile
import random
from unittest.mock import Mock
import numpy as np
from Tools.PenaltyValidation.prepare import sample,SALT,export_csv
from Tools.AdvisorReplay.sample import sample_drafts,draft_priority
from Tools.PenaltyValidation.evaluate import fast_scores,VARIANTS,metrics
from Tools.PenaltyValidation.report import ratio_contrast,complete,pseudo_outcomes
from variants import ROOT,ENGINE,traced_class,advisor_class,variant_source


def test_sampler_matches_full_csv_reference_with_exclusions_and_quoted_names():
    out=io.StringIO();w=csv.writer(out)
    w.writerow(['expansion','event_type','draft_id','draft_time','user_game_win_rate_bucket','user_n_games_bucket',
        'event_match_wins','event_match_losses','pack_number','pick_number','pick','pack_card_A, B','pool_A, B'])
    for i in range(80):
        for pick in range(2):w.writerow(['TST','PremierDraft',f'draft{i}','2026-01-01',.6,100,4,3,0,pick,'A, B',1,pick])
    text=out.getvalue();excluded={'draft2','draft3','draft4'}
    got,coverage=sample(iter(io.StringIO(text)),20,excluded)
    expected=sample_drafts(io.StringIO(text),80,SALT)
    expected=sorted([d for d in expected if d['id'] not in excluded],key=lambda d:draft_priority(d['id'],SALT))[:20]
    expected=sorted(expected,key=lambda d:d['id'])
    assert [{k:v for k,v in d.items() if k!='time'} for d in got]==expected
    assert coverage['prior_drafts_excluded']==3


def test_old_tar_export_and_plain_gzip_are_read_identically(tmp_path):
    text='user_game_win_rate_bucket,user_n_games_bucket,draft_id\n0.6,100,abc123\n'
    plain=tmp_path/'plain.csv.gz'
    with gzip.open(plain,'wt') as f:f.write(text)
    wrapped=tmp_path/'actually-tar.csv.gz'
    with tarfile.open(wrapped,'w:gz') as t:
        m=tarfile.TarInfo('draft.csv');b=text.encode();m.size=len(b);t.addfile(m,io.BytesIO(b))
    for path in [plain,wrapped]:
        with export_csv(path) as f:assert f.read()==text


def test_older_match_bucket_column_names_are_preserved_in_provenance():
    text='user_match_win_rate_bucket,user_n_matches_bucket,draft_id,draft_time,event_match_wins,event_match_losses,pack_number,pick_number,pick,pack_card_A,pool_A\n.64,100,abc123,2021-11-01,4,3,0,0,A,1,0\n'
    drafts,coverage=sample(iter(io.StringIO(text)),10,set())
    assert drafts[0]['skill']==.64 and drafts[0]['games']==100
    assert coverage['skill_field']=='user_match_win_rate_bucket'
    assert coverage['historical_count_field']=='user_n_matches_bucket'


def test_target_return_fast_path_matches_complete_edited_engine_with_fallthrough():
    source=(ROOT/ENGINE).read_text();Trace=traced_class(source);Base=advisor_class(source)
    heads={v:advisor_class(variant_source(v,source)[1]) for v in VARIANTS}
    m=Mock();m.get_metrics.return_value=(55.,4.)
    rng=random.Random(99);changed={v:0 for v in VARIANTS}
    for trial in range(300):
        pack=[]
        for i in range(8):
            colors=rng.choice([['R'],['G'],['U'],['W','B'],[]])
            pack.append({'name':f'Card {i}','types':[rng.choice(['Land','Creature','Instant'])],
                'cmc':rng.randint(1,7),'mana_cost':'{2}'+''.join('{'+c+'}' for c in colors),'colors':colors,
                'tags':[rng.choice(['removal','fixing_ramp','','synergy_artifacts'])],
                'deck_colors':{'All Decks':{'gihwr':rng.uniform(45,70),'iwd':rng.uniform(0,8)}}})
        pack.append({'name':'Forest','types':['Basic','Land'],'cmc':0,'colors':[],
            'deck_colors':{'All Decks':{'gihwr':60.,'iwd':0.}}})
        a=Trace(m,[pack[0]]*rng.randint(1,40));a.main_colors=['R','G'];a.main_archetype='RG'
        for k,v in a.pool_metrics.items():a.pool_metrics[k]={'U'} if isinstance(v,set) else rng.randint(0,12)
        a._trace=[];pn=rng.randint(1,3);pick=rng.randint(1,14);a.evaluate_pack(pack,pick,pn)
        rows=[[r[0]['name'],*r[1:]] for r in a._trace];names={c['name']:c for c in pack}
        state=dict(a.__dict__,pool_size=len(a.pool));base=fast_scores(rows,state,names,'baseline',Base,Base,pn)
        for v,Head in heads.items():
            h=object.__new__(Head);h.__dict__.update(a.__dict__)
            expected={r.card_name:r.contextual_score for r in h.evaluate_pack(pack,pick,pn)}
            result=fast_scores(rows,state,names,v,Base,Head,pn)
            assert dict(zip([r[0] for r in rows],result))==expected,(trial,v)
            changed[v]+=result!=base
    assert all(n>0 for n in changed.values())


def test_ratio_influence_matches_delete_one_jackknife():
    rng=np.random.default_rng(52);n=5000
    phi=np.empty((n,2,3))
    phi[:,:,1]=rng.uniform(3,10,(n,2));phi[:,:,0]=phi[:,:,1]*rng.uniform(.2,.8,(n,2));phi[:,:,2]=phi[:,:,0]/phi[:,:,1]
    result=ratio_contrast(phi,['SET']*n)
    totals=phi.sum(axis=0);deleted=totals[None,:,:]-phi
    estimates=deleted[:,1,0]/deleted[:,1,1]-deleted[:,0,0]/deleted[:,0,1]
    jackknife=np.sqrt((n-1)/n*np.sum((estimates-estimates.mean())**2))
    assert np.isclose(result['draft_se_pp']/100,jackknife,rtol=.002)
    assert result['simultaneous_set_cluster_ci_pp'] is None


def test_adjustment_recovers_known_effect_with_either_correct_nuisance():
    # Choice and outcome share a confounder. The raw contrast is biased, but
    # either exact propensities OR exact outcomes recover the known effect.
    n=20000;level=np.repeat(np.arange(4),n//4)
    p=np.repeat([.1,.3,.7,.9],n//4)
    a=np.concatenate([np.r_[np.ones(int(5000*v)),np.zeros(5000-int(5000*v))] for v in [.1,.3,.7,.9]]).astype(int)
    m=np.empty((n,2,3))
    for arm in [0,1]:
        m[:,arm,0]=2.+level*.5+arm*.1;m[:,arm,1]=6.;m[:,arm,2]=m[:,arm,0]/6.
    y=m[np.arange(n),a]
    raw=y[a==1,0].mean()/6-y[a==0,0].mean()/6
    assert raw>.05
    for known_p,known_m in [(p,np.zeros_like(m)),(np.full(n,.5),m)]:
        phi=pseudo_outcomes(a,y,known_p,known_m)
        estimate=ratio_contrast(phi,['TEST']*n)['difference_pp']
        assert np.isclose(estimate,100*.1/6)


def test_completed_event_and_strict_tie_guards():
    assert complete({'wins':7,'losses':1})
    assert complete({'wins':0,'losses':3})
    assert not complete({'wins':4,'losses':2})
    assert not complete({'wins':None,'losses':3})
    assert not complete({'wins':7.5,'losses':3})
    assert not metrics([10,10],0)['strict']
