import json,sys,numpy as np
sys.path.insert(0, sys.argv[1]); import fit_choice as F
def load(files,maxd,minwr):
    G=[]
    for p in files:
        for d in json.load(open(p)):
            c=d["candidates"]
            if d["wr_bucket"]<minwr or len(c)<2: continue
            ac=set(d["main_colors"])|set(d["splash_colors"])
            ds=[F.diff(x["cards"],d["actual"]) if set(x["colors"])==ac else 999 for x in c]
            b=min(ds)
            if b>maxd: continue
            X=np.array([[x["features"][n] for n in F.NAMES[:3]]+[x["missing_fixing"],x["sim_penalty"],x["features"]["missing_spells"]] for x in c],float)
            ch=np.array([v==b for v in ds])
            if ch.all(): continue
            G.append((d["set"],X,ch))
    return G
for md in (6,10):
    print(f"## Chosen: the drafter's colors, at most {md} cards different\n")
    g=load(sys.argv[2:],md,0); F.report(g,"All drafters")
    F.report(load(sys.argv[2:],md,0.6),"Strong drafters")
    both=[x for x in g if (x[1][:,3]>0).any() and (x[1][:,3]==0).any()]
    print(len(both),"pools with both; share short of fixing among candidates %.1f%%, among chosen %.1f%%\n"%(100*sum((X[:,3]>0).mean() for _,X,_ in both)/len(both),100*sum((X[c,3]>0).mean() for _,X,c in both)/len(both)))
