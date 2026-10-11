"""Bounded official-reported price-gap extension. No network, raw publication or model search.

The four private CSVs are NOT supplied in this package. Use --inspect to see their
actual headers before completing the explicit mapping file. No header is guessed.
Method: OLS, quarter CR1/CV1 t intervals and one null-imposed wild-cluster t test.
Synthetic tests verify implementation, not coverage or the real data pipeline.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, time
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import numpy as np
from scipy.linalg import solve_triangular
from scipy.stats import t as student_t

EXPECTED = {
 'all275':('official_reported_cutoff_all275.csv',275,'b168de79301d99003e95d62779bd75d02a97a34d1b876034f3f26bf23273abed'),
 'strict240':('official_reported_cutoff_strict240.csv',240,'7e12f25db5bb97f3b0152f264519803569edcee9914da548ff156ee7e058f4c1'),
 'excluded35':('official_reported_cutoff_excluded35.csv',35,'7e332bb5be5f1cb1ebb9b83def7d9c2dabc0e846d81de698930de1751e7dbecb'),
 'noflags203':('official_reported_cutoff_noflags.csv',203,'7441f31c72b220adb6fc2374d0205f510955023f9f3cb405e6660478a59c6086')}
QUANTITIES = ('V','R','N','S','mu_B','sd_B','mu_W','sd_W')

class GateError(ValueError): pass
class Budget:
    def __init__(self, seconds=900, fits=1100):
        self.start=time.monotonic();self.seconds=seconds;self.max_fits=fits;self.fits=0
    def tick(self):
        if time.monotonic()-self.start>self.seconds or self.fits>=self.max_fits:
            raise GateError('Locked estimation/time budget exceeded')
        self.fits+=1

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_csv(p):
    with Path(p).open(encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):
            raise GateError('Missing or duplicate CSV field names')
        rows=list(reader)
        if any(None in r for r in rows): raise GateError('Malformed CSV row')
        return rows,reader.fieldnames

def number(x, decimal_separator='.'):
    text=str(x).strip().replace('\u2212','-').replace('\u00a0','')
    if text.endswith('%'):text=text[:-1].strip()
    if text in ('','--','NA','None'):raise GateError('Missing numeric input, not a zero')
    if decimal_separator==',':
        if '.' in text:raise GateError('Ambiguous decimal/thousands punctuation')
        text=text.replace(',','.')
    elif ',' in text:raise GateError('Explicit mapping required for decimal punctuation')
    try:v=Decimal(text)
    except Exception:raise GateError('Invalid numeric token') from None
    if not v.is_finite():raise GateError('Non-finite number')
    return v

def frozen_files(root):
    out={};receipt={}
    for tag,(name,n,sha) in EXPECTED.items():
        p=Path(root)/'data'/name
        if not p.exists():p=Path(root)/name
        if not p.exists():raise GateError('Private row file unavailable: '+name)
        if digest(p)!=sha:raise GateError('Frozen input hash differs: '+name)
        rows,headers=read_csv(p)
        if len(rows)!=n:raise GateError('Frozen row count differs: '+name)
        out[tag]=rows;receipt[tag]={'basename':name,'rows':len(rows),'sha256':sha,'headers':headers}
    return out,receipt

def load_rows(private_root, mapping_path, auction_path):
    groups,receipt=frozen_files(private_root)
    cfg=json.loads(Path(mapping_path).read_text())
    required=('date','auction_price','deviation_percent','reference_type')
    fields=cfg.get('fields',{})
    if any(not isinstance(fields.get(k),str) or not fields[k] for k in required):
        raise GateError('Complete mapping from actual private CSV headers first')
    if cfg.get('percentage_encoding')!='numeric_percentage_points':
        raise GateError('Reported percent must be explicitly mapped as percentage points')
    traces=cfg.get('trace_columns',[])
    if not traces or not cfg.get('definition_evidence'):
        raise GateError('Source locator and sign/unit definition record required')
    qmap=cfg.get('quantity_fields',{})
    if any(not qmap.get(q) for q in QUANTITIES):raise GateError('Eight quantity mappings required')
    headers=set(receipt['all275']['headers'])
    if not (set(fields.values())|set(qmap.values())|set(traces)).issubset(headers):
        raise GateError('Mapping references a nonexistent source column')
    date_fmt=cfg.get('date_format','%Y-%m-%d');sep=cfg.get('decimal_separator','.')
    def key(r):
        try:return datetime.strptime(r[fields['date']],date_fmt).date().isoformat()
        except Exception:raise GateError('Date does not match the fixed explicit format') from None
    indexed={}
    for tag,rows in groups.items():
        indexed[tag]={key(r):r for r in rows}
        if len(indexed[tag])!=len(rows):raise GateError('Duplicate auction date in '+tag)
    allset=set(indexed['all275']);ss=set(indexed['strict240']);es=set(indexed['excluded35'])
    if ss & es or ss|es != allset or not set(indexed['noflags203'])<=ss:
        raise GateError('Strict/excluded/no-flag set reconciliation failed')
    checkfields=list(fields.values())+list(qmap.values())
    for tag in ('strict240','excluded35','noflags203'):
        for date,r in indexed[tag].items():
            if any(r[k]!=indexed['all275'][date][k] for k in checkfields):
                raise GateError('Subset alters a source field: '+tag)
    if digest(auction_path)!='b1d737d7dc7d1af53b989560ccb13d8cad52345747441ab34f77c320edbe498f':
        raise GateError('Audited historical auction-price table hash mismatch')
    old,_=read_csv(auction_path)
    old={r['auction_date']:r for r in old if r['auction_series']=='DE' and r['auction_product']=='T3PA'}
    if set(old)!=allset:raise GateError('275-date set does not equal the existing German EUA set')
    for date,r in indexed['all275'].items():
        a=old[date]
        if number(r[fields['auction_price']],sep)!=number(a['auction_price_eur_per_tco2']):
            raise GateError('Reported auction price does not match original EEX price')
        if any(number(r[qmap[q]],sep)!=number(a[q]) for q in QUANTITIES):
            raise GateError('Reported quantity does not match original EEX source')
    data=[]
    types=cfg.get('reference_type_values',{})
    for date in sorted(ss):
        r=indexed['strict240'][date];a=old[date]
        if any(not str(r.get(k,'')).strip() for k in traces):raise GateError('Missing source-row locator')
        typ=types.get(r[fields['reference_type']])
        if typ not in ('last_best_bid','last_trade'):raise GateError('Unmapped reference type')
        pct=number(r[fields['deviation_percent']],sep)
        v={q:float(number(a[q])) for q in QUANTITIES}
        if any(v[q]<=0 for q in ('V','R','N','S','mu_B')) or v['sd_B']<0:
            raise GateError('Invalid positive/log input')
        if v['S']>v['N']:raise GateError('Successful count exceeds total count')
        for q in ('N','S'):
            if not v[q].is_integer():raise GateError('Noninteger bidder count')
        p=float(number(a['auction_price_eur_per_tco2']))
        spread=float(number(a['maximum_bid_price_eur_per_tco2'])-number(a['minimum_bid_price_eur_per_tco2']))
        if p<=0 or spread<0:raise GateError('Invalid price control')
        y=int(date[:4]);quarter=f'{y}Q{(int(date[5:7])-1)//3+1}'
        data.append(dict(date=date,year=y,quarter=quarter,y=100*float(pct),x=float(np.log1p(v['sd_B']/v['mu_B'])),
                         lv=float(np.log(v['V'])),ln=float(np.log(v['N'])),ls=float(np.log(v['S'])),lr=float(np.log(v['R'])),
                         spread=spread,lp=float(np.log(p)),trade=int(typ=='last_trade'),noflag=date in indexed['noflags203']))
    if Counter(r['year'] for r in data)!=dict(zip(range(2020,2026),(46,45,35,36,34,44))):
        raise GateError('Strict-year set differs from fixed transfer contract')
    if len(set(r['quarter'] for r in data))!=21 or sum(r['trade'] for r in data)!=4:
        raise GateError('Quarter/type counts differ from fixed transfer contract')
    receipt.update({'auction_table_sha256':digest(auction_path),'mapping_sha256':digest(mapping_path),
                    'rows_republished':False,'native_ticks_required_for_this_reported_layer':False,
                    'source_definition_independently_authenticated_by_this_program':False})
    return data,receipt

def design(rows):
    # Only the trade indicator may be omitted when constant by the fixed subset rule.
    names=['intercept','log_volume','log_total_bidders','log_successful_bidders','log_cover_ratio',
           'bid_price_spread_eur','log_auction_price']+[f'year_{y}' for y in range(2021,2026)]
    X=np.array([[1,r['lv'],r['ln'],r['ls'],r['lr'],r['spread'],r['lp']]+[int(r['year']==y) for y in range(2021,2026)] for r in rows],float)
    if len(set(r['trade'] for r in rows))>1:
        X=np.column_stack((X,[r['trade'] for r in rows]));names+=['reference_last_trade']
    X=np.column_stack((X,[r['x'] for r in rows]));names+=['bid_dispersion_log1p']
    return X,names,np.array([r['y'] for r in rows]),np.array([r['quarter'] for r in rows])

def fit(X,y,clusters,budget=None):
    if budget:budget.tick()
    X=np.asarray(X,float);y=np.asarray(y,float);clusters=np.asarray(clusters)
    n,k=X.shape
    if y.shape!=(n,) or len(clusters)!=n or n<=k:raise GateError('Invalid model dimensions')
    if not np.isfinite(X).all() or not np.isfinite(y).all():raise GateError('Non-finite design/outcome')
    if not np.allclose(X[:,0],1):raise GateError('Intercept must be first')
    means=X.mean(0);scales=X.std(0);means[0]=0;scales[0]=1
    if np.any(scales<=np.finfo(float).eps):raise GateError('Constant nonintercept regressor')
    Z=(X-means)/scales
    if np.linalg.matrix_rank(Z)!=k:raise GateError('Target/design is not full column rank')
    Q,R=np.linalg.qr(Z,mode='reduced');ri=solve_triangular(R,np.eye(k))
    b=solve_triangular(R,Q.T@y);u=y-Z@b
    if np.dot(y-y.mean(),y-y.mean())<=1e-24 or np.dot(u,u)<=1e-24:raise GateError('Degenerate outcome/residual variance')
    bread=ri@ri.T;levels,inv=np.unique(clusters,return_inverse=True);g=len(levels)
    if g<2:raise GateError('Fewer than two source-quarter clusters')
    scores=np.zeros((g,k));np.add.at(scores,inv,Z*u[:,None])
    covariance=(g/(g-1))*((n-1)/(n-k))*bread@(scores.T@scores)@bread
    T=np.diag(1/scales);T[0,1:]=-means[1:]/scales[1:]
    beta=T@b;cov=T@covariance@T.T;se=np.sqrt(np.maximum(np.diag(cov),0))
    if not np.isfinite(se).all():raise GateError('Invalid covariance estimate')
    return dict(beta=beta,cov=cov,se=se,u=u,fitted=y-u,n=n,k=k,g=g,levels=levels,
                condition_scaled=float(np.linalg.cond(Z)),condition_raw=float(np.linalg.cond(X)),
                Q=Q,partial_cluster_scores=scores,cluster_index=inv)

def plain_projection(X,y):
    # Stable nuisance projection used for non-estimation scale diagnostics.
    means=X.mean(0);scales=X.std(0);means[0]=0;scales[0]=1
    if np.any(scales<=np.finfo(float).eps):raise GateError('Degenerate nuisance column')
    Z=(X-means)/scales
    if np.linalg.matrix_rank(Z)!=Z.shape[1]:raise GateError('Rank-deficient nuisance projection')
    q,_=np.linalg.qr(Z,mode='reduced');return y-q@(q.T@y)

def summary(X,y,clusters,names,budget):
    base=fit(X[:,:-1],y,clusters,budget);full=fit(X,y,clusters,budget)
    xr=plain_projection(X[:,:-1],X[:,-1]);iqr=float(np.diff(np.quantile(xr,[.25,.75]))[0])
    if full['se'][-1]<=0:raise GateError('Degenerate focal cluster variance')
    crit=float(student_t.ppf(.975,full['g']-1));b=float(full['beta'][-1]);se=float(full['se'][-1]);ci=[b-crit*se,b+crit*se]
    info=np.bincount(full['cluster_index'],weights=xr*xr);info=info/info.sum()
    out={'n':full['n'],'quarters':full['g'],'rank':full['k'],'residual_df':full['n']-full['k'],
         'coefficient':b,'CR1_standard_error':se,'CR1_t_Gminus1_CI95':ci,
         'IQR_residualized_bid_dispersion':iqr,'fitted_IQR_gap_bps':b*iqr,'IQR_gap_CR1_CI95_bps':[c*iqr for c in ci],
         'incremental_partial_R2':1-float(full['u']@full['u'])/float(base['u']@base['u']),
         'scaled_condition_number':full['condition_scaled'],'unscaled_condition_number':full['condition_raw'],
         'max_quarter_share_of_focal_partial_leverage':float(info.max()),
         'focal_partial_leverage_effective_quarters':float(1/(info@info)),
         'quarter_counts':dict(Counter(clusters)),
         'all_coefficients':dict(zip(names,[float(v) for v in full['beta']])),
         'uncertainty_label':'Exploratory CR1/CV1 t approximation; independence across quarters is an assumption, not established',
         'outcome_unit':'basis points of the reported percentage deviation; not reconstructed native quotes'}
    return out,base,full

def wcr_test(X,y,clusters,base,full,budget,draws=999,seed=20261011):
    rng=np.random.default_rng(np.random.SeedSequence([seed,2,240]))
    signs=rng.choice(np.array([-1,1],dtype=np.int8),size=(draws,full['g']))
    t_obs=float(full['beta'][-1]/full['se'][-1]);values=[];failures=[]
    for j,s in enumerate(signs):
        ys=base['fitted']+base['u']*s[full['cluster_index']]
        try:
            fs=fit(X,ys,clusters,budget)
            if fs['se'][-1]<=0:raise GateError('Degenerate bootstrap focal variance')
            values.append({'draw':j,'t':float(fs['beta'][-1]/fs['se'][-1])})
        except GateError as e:
            failures.append({'draw':j,'reason':str(e)})
            if 'budget' in str(e).lower():break
    exceed=sum(abs(r['t'])>=abs(t_obs) for r in values)
    p=(1+exceed)/(draws+1) if len(values)==draws else None
    return {'null':'coefficient on bid_dispersion_log1p equals zero',
            'method':'null-imposed quarter wild-cluster t; Rademacher; CV1/CR1 studentization',
            'requested':draws,'valid':len(values),'failed':failures,'t_observed':t_obs,
            'two_sided_plus_one_p':p,'not_a_bootstrap_confidence_interval':True,
            'conditional_MC_SE_approx':None if p is None else float(np.sqrt(p*(1-p)/draws)),
            'coverage_or_untouched_test_certified':False},values,signs

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--private-root',type=Path,required=True);a.add_argument('--auction-prices',type=Path)
    a.add_argument('--mapping',type=Path);a.add_argument('--out',type=Path,required=True)
    a.add_argument('--inspect',action='store_true');args=a.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    status={'recorded_utc':datetime.now(timezone.utc).isoformat(),'real_price_model_fits':0,'scope':'official-reported German EUA subset, not native ticks','estimates':None}
    budget=Budget()
    try:
        if args.inspect:
            _,rec=frozen_files(args.private_root)
            (args.out/'INPUT_HEADERS.json').write_text(json.dumps(rec,indent=2))
            status['status']='HEADERS_INSPECTED_NO_FITS'
        else:
            if args.mapping is None or args.auction_prices is None:raise GateError('Explicit mapping and audited original auction table required')
            data,receipt=load_rows(args.private_root,args.mapping,args.auction_prices)
            configs={'primary_signed_240':data,'S1_absolute_240':data,'S2_no_flags_203':[r for r in data if r['noflag']],
                     'S3_best_bid_236':[r for r in data if not r['trade']]}
            outcomes={};draws=[];signs=None
            for name,rows in configs.items():
                X,names,y,cluster=design(rows)
                if name=='S1_absolute_240':y=np.abs(y)
                out,base,full=summary(X,y,cluster,names,budget);out['outcome_absolute']=name=='S1_absolute_240'
                if name=='primary_signed_240':
                    test,draws,signs=wcr_test(X,y,cluster,base,full,budget);out['WCR_test']=test
                outcomes[name]=out
                (args.out/'RESULTS.json').write_text(json.dumps(outcomes,indent=2))
            (args.out/'RESULTS.json').write_text(json.dumps(outcomes,indent=2))
            (args.out/'INPUT_GATE.json').write_text(json.dumps(receipt,indent=2))
            with (args.out/'PRIMARY_WCR_DRAWS.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['draw','t']);w.writeheader();w.writerows(draws)
            (args.out/'PRIMARY_WCR_SIGNS.json').write_text(json.dumps(signs.tolist()))
            status.update(status=('COMPLETED_EXPLORATORY' if len(draws)==999 else 'COMPLETED_WITH_INCOMPLETE_WCR'),estimates='RESULTS.json',real_price_model_fits=budget.fits)
    except (GateError,FileNotFoundError,KeyError,ValueError) as e:
        status.update(status='BLOCKED_INPUT_OR_DIAGNOSTIC',reason=str(e),real_price_model_fits=budget.fits)
    status['seconds']=time.monotonic()-budget.start
    (args.out/'EXECUTION_STATUS.json').write_text(json.dumps(status,indent=2))
    print(json.dumps(status,indent=2));return 0 if status['status'].startswith(('COMPLETED','HEADERS')) else 3

if __name__=='__main__':raise SystemExit(main())
