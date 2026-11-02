"""Independent arithmetic/statistical checks. No production module imports."""
from pathlib import Path
from collections import Counter
import csv, json, math
import numpy as np
from scipy.special import betaln, digamma, gammaln
from scipy.optimize import brentq, minimize
from scipy.stats import beta as beta_dist

# Published copy: the reviewer's absolute project path is replaced by a path relative to this file
# (the only edit; see AUDIT-2026-11-02.md).
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
def rows(p):
    return list(csv.DictReader((ROOT/p).open(encoding='utf-8')))

# Independently read from the displayed page image, not the transcription.
page = {
 'chicago': (278,1124,[133,43,24,12,11,14,5,3,9,1,23],[None,46,23,14,10,7,5,4,3,3,30]),
 'chem': (6891,22939,[3991,1059,493,287,184,131,113,85,64,65,419],[4050,1160,522,288,179,120,86,64,49,38,335]),
 'physicists': (1325,3396,[784,204,127,50,33,28,19,19,6,7,48],[824,217,94,50,30,20,14,10,8,6,52]),
 'econometrica': (721,1759,[436,107,61,40,14,23,6,11,1,0,22],[453,119,51,27,16,11,7,5,4,3,25])
}
pt={(r['table'],r['set'],r['kind'],r['row']):r['printed'] for r in rows('data/printed_tables.csv')}
recipes={}; tails={}; manual_cells=0
for name,(n,k,actual,printed) in page.items():
    rho=actual[0]/(n-actual[0]) if name=='chicago' else k/(k-n)
    f=[actual[0] if name=='chicago' else n/(2-n/k)]
    for i in range(2,11): f.append(f[-1]*(i-1)/(i+rho))
    f.append(n-sum(f)); recipes[name]=f
    assert n-sum(p or actual[0] for p in printed[:-1])==printed[-1]
    for kind, vals in [('actual',actual),('estimate',printed)]:
        for i,v in enumerate(vals,1):
            if v is not None:
                assert float(pt[('T3',name,kind,str(i) if i<11 else '11+')])==v
                manual_cells+=1
    tails[name]={'rho':rho,'observed':actual[-1],'printed':printed[-1],'recipe':f[-1],'printed_head_shortfall':sum(f[:-1])-sum(p or actual[0] for p in printed[:-1])}

# Full source spectra loaded without project loaders.
spectra={}
spectra['chicago']=Counter({int(r['n']):int(r['persons']) for r in rows('data/sources/davis1941_p429_chicago.csv') if r['n']!='Total'})
for name,tab in [('chem','chem'),('physicists','auerbach')]:
    f=Counter()
    for r in rows('data/sources/davis1941_p431.csv'):
        if r['table']==tab and r['n']!='Total': f[int(r['n'])]+=int(r['persons'])
    spectra[name]=f
f=Counter({int(r['i']):int(r['stated_count']) for r in rows('data/sources/eldridge1911_list5_headers.csv') if r['i']})
for r in rows('data/sources/eldridge1911_list5_counts.csv'): f[int(r['count'])]+=1
spectra['eldridge']=f

def probs(rho,c=11):
    x=np.arange(1,c,dtype=float)
    return np.r_[rho*np.exp(betaln(x,rho+1)),np.exp(betaln(c-1,rho+1))*(c-1)]
def cens_mle(obs,c=11):
    i=np.arange(1,c,dtype=float); n=sum(obs)
    def score(r):
        return np.dot(obs[:-1],1/r+digamma(r+1)-digamma(i+r+1))+obs[-1]*(digamma(r+1)-digamma(c+r))
    return brentq(score,.05,20,xtol=1e-12)
def full_mle(xs,ms):
    n=sum(ms)
    return brentq(lambda r:n/r+n*digamma(r+1)-np.dot(ms,digamma(xs+r+1)),.05,20,xtol=1e-12)
def x2(obs,r):
    e=sum(obs)*probs(r); return float(np.sum((obs-e)**2/e))
def ci(h,b):
    return [float(beta_dist.ppf(.025,h,b-h+1)) if h else 0.,float(beta_dist.ppf(.975,h+1,b-h)) if h<b else 1.]

summary=json.loads((ROOT/'results/stage4-summary.json').read_text())
checks={}
for name in ['chicago','chem','physicists','econometrica','eldridge']:
    if name=='econometrica':
        obs=np.array(page[name][2]); r=cens_mle(obs)
    else:
        f=spectra[name]; xs=np.array(list(f),dtype=float); ms=np.array(list(f.values()),dtype=float)
        r=full_mle(xs,ms); obs=np.array([f[i] for i in range(1,11)]+[sum(v for i,v in f.items() if i>=11)])
    stat=x2(obs,r)
    assert abs(r-summary['fits'][name]['yule']['params'][0])<1e-5
    assert abs(stat-summary['gof'][name]['yule']['x2_obs'])<1e-4
    b=json.loads((ROOT/f'results/stage4/{name}__yule.json').read_text())
    h=sum(v['x2']>=summary['gof'][name]['yule']['x2_obs'] for v in b)
    assert h/len(b)==summary['gof'][name]['yule']['x2_p']
    checks[name]={'n':int(sum(obs)),'rho':r,'x2':stat,'bootstrap_hits':h,'B':len(b),'p':h/len(b),'mc_95_interval':ci(h,len(b))}

all_boot=0
for name,models in summary['gof'].items():
    for model,g in models.items():
        b=json.loads((ROOT/f'results/stage4/{name}__{model}.json').read_text()); assert len(b)==g['B']==500
        ok=[r for r in b if not r['fail']]
        assert len(ok)==500
        for stat in ['x2','ks']:
            if stat+'_p' in g: assert sum(r[stat]>=g[stat+'_obs'] for r in ok)/500==g[stat+'_p']
        all_boot+=len(b)

# Chem ENB likelihood re-optimization, independent formula/optimizer.
f=spectra['chem']; xs=np.array(list(f),dtype=float); ms=np.array(list(f.values()),dtype=float)
def negll(v):
    r,t=v
    lp=gammaln(xs+r)-gammaln(xs+1)-gammaln(r)+xs*np.log(t)-np.log(abs(np.expm1(-r*np.log1p(-t))))
    return -float(np.dot(ms,lp))
enb=min((minimize(negll,v,method='Nelder-Mead',bounds=[(-.999,-.000001),(.000001,.999999)],options={'xatol':1e-11,'fatol':1e-9,'maxiter':3000}) for v in [(-.8,.9),(-.4,.99),(-.1,.95)]),key=lambda a:a.fun)
enb_aic=4+2*enb.fun
assert abs(enb_aic-summary['fits']['chem']['enb']['aic'])<1e-5

# Check all plotted recipe/MLE values, including both Table 2 datasets.
s3=json.loads((ROOT/'results/stage3-summary.json').read_text())
external={(r['set'],r['quantity']):int(r['value']) for r in rows('data/external_inputs.csv')}
plot_errors=[]
for p in rows('results/stage6-series.csv'):
    name=p['set']; row=p['row']; val=float(p['value']); series=p['series']
    if series in ('observed','printed'):
        want=float(pt[(p['table'],name,{'observed':'actual','printed':'estimate'}[series],row)])
    elif series=='recipe':
        if p['table']=='T3': want=recipes[name][10 if row=='11+' else int(row)-1]
        else:
            n=external[name,'n_k']; k=external[name,'k']; r=k/(k-n)
            want=n*r*np.exp(betaln(int(row),r+1))
    else:
        n=s3['observed'][name]['n']
        c=4 if name=='ulysses' else 11
        if name in spectra:
            f=spectra[name]; obs=np.array([f[i] for i in range(1,c)]+[sum(v for i,v in f.items() if i>=c)])
        elif name=='econometrica': obs=np.array(page[name][2])
        else:
            head=[float(pt['T2',name,'actual',str(i)]) for i in range(1,4)]; obs=np.array(head+[n-sum(head)])
        r=cens_mle(obs,c)
        want=n*(10*np.exp(betaln(10,r+1)) if row=='11+' else r*np.exp(betaln(int(row),r+1)))
    tol=.00501 if series=='recipe' else (1e-3 if series=='mle' else 0)
    if abs(val-want)>tol: plot_errors.append([p,want])
assert not plot_errors,plot_errors

result={'tail_recompute':tails,'page_cells_checked':manual_cells,'yule_gof':checks,'bootstrap_rows_checked':all_boot,'P7a_independent':{'params':enb.x.tolist(),'aic_enb':enb_aic,'aic_yule':summary['fits']['chem']['yule']['aic'],'advantage':summary['fits']['chem']['yule']['aic']-enb_aic},'plot_points_checked':len(rows('results/stage6-series.csv')),'plot_errors':plot_errors}
(OUT/'independent-checks.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps(result,indent=2))

# Supplemental check only: independent exact Beta-Geometric sampler, 10,000 refits.
# The original 500-replicate record is retained unchanged.
name='physicists'; f=spectra[name]; n=sum(f.values()); r=checks[name]['rho']; stat=checks[name]['x2']
rng=np.random.default_rng(20261102); B=10000; hits=0
for j in range(B):
    q=rng.beta(r,1,n); sample=rng.geometric(q)
    xs,ms=np.unique(sample,return_counts=True)
    rb=full_mle(xs,ms)
    obs=np.bincount(np.minimum(sample,11),minlength=12)[1:]
    hits+=x2(obs,rb)>=stat
mc={'set':name,'seed':20261102,'sampler':'exact beta-geometric','B':B,'hits':int(hits),'p':float(hits/B),'mc_95_interval':ci(hits,B)}
(OUT/'physicists-supplemental-bootstrap.json').write_bytes((json.dumps(mc,indent=2)+'\n').encode())
print(json.dumps(mc,indent=2))
