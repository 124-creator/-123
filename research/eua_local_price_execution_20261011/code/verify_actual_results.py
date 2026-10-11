import csv,json,sys,hashlib
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster
from scipy.stats import t
root=Path(sys.argv[1]);private=Path(sys.argv[2])
results=json.loads((root/'real_results/RESULTS.json').read_text())
status=json.loads((root/'real_results/EXECUTION_STATUS.json').read_text())
if status['status']!='COMPLETED_EXPLORATORY' or status['real_price_model_fits']!=1034:raise ValueError('Incomplete execution')
original=list(csv.DictReader((root/'private_auction_base_reviewed/auction_prices_local.csv').open(encoding='utf-8')))
a={r['auction_date']:r for r in original if r['auction_series']=='DE' and r['auction_product']=='T3PA'}
s=list(csv.DictReader((private/'data/official_reported_cutoff_strict240.csv').open(encoding='utf-8-sig')))
nf={r['auction_date'] for r in csv.DictReader((private/'data/official_reported_cutoff_noflags.csv').open(encoding='utf-8-sig'))}
configs={'primary_signed_240':s,'S1_absolute_240':s,'S2_no_flags_203':[r for r in s if r['auction_date'] in nf],'S3_best_bid_236':[r for r in s if r['reference_event_type']=='last_best_bid']}
checks=[]
for tag,rows in configs.items():
    X=[];y=[];clusters=[]
    varying=len({r['reference_event_type'] for r in rows})>1
    for r in rows:
        d=r['auction_date'];z=a[d];v=[1.]+[float(np.log(float(z[k]))) for k in ['V','N','S','R']]
        v+=[float(Decimal(z['maximum_bid_price_eur_per_tco2'])-Decimal(z['minimum_bid_price_eur_per_tco2'])),float(np.log(float(z['auction_price_eur_per_tco2'])))]
        v += [float(int(d[:4])==yr) for yr in range(2021,2026)]
        if varying:v += [float(r['reference_event_type']=='last_trade')]
        v += [float(np.log1p(float(r['reported_SD_bid_volume'])/float(r['reported_mean_bid_volume'])))]
        X.append(v);yy=float(Decimal(r['reported_deviation_percent_signed'])*100)
        y.append(abs(yy) if tag=='S1_absolute_240' else yy)
        clusters.append(d[:4]+'Q'+str((int(d[5:7])-1)//3+1))
    X=np.array(X);y=np.array(y);clusters=np.array(clusters)
    fit=sm.OLS(y,X).fit();cov=cov_cluster(fit,clusters,use_correction=True)
    beta=float(fit.params[-1]);se=float(np.sqrt(cov[-1,-1]));res=results[tag]
    if not np.isclose(beta,res['coefficient'],rtol=1e-10,atol=1e-8):raise ValueError('Independent coefficient mismatch')
    if not np.isclose(se,res['CR1_standard_error'],rtol=1e-9,atol=1e-8):raise ValueError('Independent CR1 mismatch')
    xr=X[:,-1]-X[:,:-1]@np.linalg.lstsq(X[:,:-1],X[:,-1],rcond=None)[0]
    yr=y-X[:,:-1]@np.linalg.lstsq(X[:,:-1],y,rcond=None)[0]
    partial=float(np.corrcoef(xr,yr)[0,1]**2)
    if not np.isclose(partial,res['incremental_partial_R2'],rtol=1e-9,atol=1e-10):raise ValueError('Partial R2 mismatch')
    checks.append({'specification':tag,'n':len(rows),'independent_beta':beta,'beta_abs_difference':abs(beta-res['coefficient']),'CR1_SE_abs_difference':abs(se-res['CR1_standard_error']),'partial_R2_difference':abs(partial-res['incremental_partial_R2'])})
primary=results['primary_signed_240'];bt=primary['WCR_test']
draws=list(csv.DictReader((root/'real_results/PRIMARY_WCR_DRAWS.csv').open()))
signs=np.array(json.loads((root/'real_results/PRIMARY_WCR_SIGNS.json').read_text()))
if len(draws)!=999 or signs.shape!=(999,21) or not np.isin(signs,[-1,1]).all():raise ValueError('Draw/sign count mismatch')
exceed=sum(abs(float(r['t']))>=abs(bt['t_observed']) for r in draws)
if (exceed+1)/(len(draws)+1)!=bt['two_sided_plus_one_p']:raise ValueError('WCR p replay mismatch')
d=primary['deletion_diagnostics'];vals=np.array([r['coefficient'] for r in d['quarter_jackknife']['deletions']])
if len(vals)!=21 or len(d['leave_year_out'])!=6:raise ValueError('Missing deletion estimate')
jse=float(np.sqrt(20/21*np.sum((vals-vals.mean())**2)))
if not np.isclose(jse,d['quarter_jackknife']['standard_error'],rtol=1e-12):raise ValueError('Jackknife replay mismatch')
unchanged=0
for r in json.loads((private/'MANIFEST.json').read_text())['files']:
    b=(private/r['path']).read_bytes()
    if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Frozen source changed')
    unchanged+=1
lock=json.loads((root/'PREFIT_LOCK_FINAL.json').read_text())
if datetime.fromisoformat(lock['recorded_before_any_real_price_fit'])>=datetime.fromisoformat(status['recorded_utc']):raise ValueError('Lock was not before fit')
for r in lock['files']:
    b=(root/r['path']).read_bytes()
    if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Locked code changed during fit')
print(json.dumps({'passed':True,'recorded_after_actual_verification':datetime.now().astimezone().isoformat(),'independent_verification_regressions':4,'no_additional_research_specification':True,'bootstrap_reruns':0,'fixed_models':checks,'bootstrap_draw_count':len(draws),'exceedance_count':exceed,'quarter_delete_estimates':len(vals),'year_delete_estimates':len(d['leave_year_out']),'frozen_objects_unchanged':unchanged,'prefit_lock_precedes_run':True,'original_estimation_requests':status['real_price_model_fits'],'scope':'Independent statsmodels estimators, manually constructed design from original-derived inputs; not a second source authentication or causal certificate'},indent=2))
