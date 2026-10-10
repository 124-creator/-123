#!/usr/bin/env python3
"""Post-result bounded checks of reported EEX dispersion, never a causal analysis.
No downloads, workbook execution, model deserialization or model search.
Reads the normalized input independently verified against the six raw workbooks.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, json, math, platform, time
from pathlib import Path
from typing import Any
import numpy as np
import scipy
from scipy.linalg import lstsq

TRANSFORMS=('A','C')
MODES={'FE':(), 'size_participation':('auction_volume','bidders'),
       'full':('cover_ratio','auction_volume','bidders','successful_bidders')}

def dump(p:Path,x:Any):
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def csvout(p:Path,rows:list[dict]):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def hashfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read_rows(p):
    rows=list(csv.DictReader(Path(p).open(encoding='utf-8-sig',newline='')))
    seen=set()
    numeric=('mean_bid','sd_bid','mean_won','sd_won','bid_volume','auction_volume','bidders','successful_bidders','cover_ratio')
    for r in rows:
        date=r['auction_date'];dt.date.fromisoformat(date)
        if not '2020-01-01'<=date<='2025-12-31' or r['product']!='EUA' or r['status']!='success' or r['project'] not in ('EU','DE','PL'):raise ValueError('Out-of-scope row')
        key=(date,r['product'],r['project'],r['event_id'])
        if key in seen:raise ValueError('Duplicate event')
        seen.add(key)
        for k in numeric:
            v=float(r[k])
            if not math.isfinite(v) or (v<0 if k.startswith('sd_') else v<=0):raise ValueError('Invalid numeric '+k)
            r[k]=v
        if not r['successful_bidders']<=r['bidders']:raise ValueError('Invalid counts')
        for k in ('bidders','successful_bidders'):
            if r[k]!=int(r[k]):raise ValueError('Noninteger bidders')
    return sorted(rows,key=lambda r:(r['auction_date'],r['project'],r['event_id']))

def mid(date):return (int(date[:4])-2020)*12+int(date[5:7])-1

def demean(v,g):
    v=np.asarray(v,float);s=np.zeros((72,v.shape[1]));np.add.at(s,g,v)
    n=np.bincount(g,minlength=72)
    return v-s[g]/n[g,None]

def projection(z,t):
    scale=np.linalg.norm(z,axis=0);active=scale>0
    if not active.any():return t.copy(),0,np.zeros((len(t),0)),None
    zs=z[:,active]/scale[active]
    coef,_,rank,s=lstsq(zs,t,lapack_driver='gelsd')
    if rank<zs.shape[1]:raise ValueError('Nonzero nuisance columns are rank deficient')
    u=np.linalg.qr(zs,mode='reduced')[0]
    cond=float(s[0]/s[-1])
    return t-zs@coef,int(rank),u,cond

class Design:
    def __init__(self,rows,spec,mode='full'):
        if spec not in TRANSFORMS or mode not in MODES:raise ValueError('Unplanned design')
        self.rows=list(rows);self.spec=spec;self.mode=mode
        if len(rows)<3:raise ValueError('Empty design')
        sb=np.array([r['sd_bid'] for r in rows]);sw=np.array([r['sd_won'] for r in rows]);mb=np.array([r['mean_bid'] for r in rows]);mw=np.array([r['mean_won'] for r in rows])
        if spec=='C' and ((sb<=0).any() or (sw<=0).any()):raise ValueError('Log requires common positive sample; no epsilon')
        self.g=np.array([mid(r['auction_date']) for r in rows]);self.projects=sorted({r['project'] for r in rows})
        self.rb=sb/mb;self.rw=sw/mw
        fn=np.log1p if spec=='A' else np.log
        self.x=fn(self.rb);self.y=fn(self.rw)
        columns=[np.log([r[k] for r in rows]) for k in MODES[mode]]
        columns += [np.array([float(r['project']==p) for r in rows]) for p in self.projects[1:]]
        self.z=np.column_stack(columns) if columns else np.zeros((len(rows),0))
        self.v=demean(np.column_stack((self.x,self.y,self.z)),self.g)
    def fit(self,w=None,details=False):
        w=np.ones(72) if w is None else np.asarray(w,float)
        if w.shape!=(72,) or not np.isfinite(w).all() or (w<0).any():raise ValueError('Invalid month multiplicities')
        ow=w[self.g];keep=ow>0;rt=np.sqrt(ow[keep]);v=self.v[keep]*rt[:,None]
        if keep.sum()<3:raise ValueError('Insufficient rows')
        res,rank,u,cond=projection(v[:,2:],v[:,:2]);rx,ry=res.T
        xx=float(rx@rx);yy=float(ry@ry);xy=float(rx@ry)
        tol=100*np.finfo(float).eps
        if xx<=tol*max(1.,float(v[:,0]@v[:,0])) or yy<=tol*max(1.,float(v[:,1]@v[:,1])):raise ValueError('Unidentified residual variance')
        beta=xy/xx;theta=xy/math.sqrt(xx*yy);err=ry-beta*rx;sse=float(err@err)
        k=len(np.unique(self.g[keep]))+rank+1;n=int(round(ow.sum()))
        out={'spec':self.spec,'controls':self.mode,'n':n,'distinct_rows':int(keep.sum()),'months':len(np.unique(self.g[keep])), 'rank':k,'residual_df':n-k,'beta':beta,'theta':theta,'partial_R2':theta*theta,'base_SSE':yy,'SSE':sse,'scaled_within_condition':cond,'residual_x_sd':math.sqrt(xx/max(n-1,1))}
        if details:
            if not np.all(w==1):raise ValueError('Details only for original sample')
            cm=np.bincount(self.g,minlength=72)
            hz=1/cm[self.g]+np.sum(u*u,axis=1)
            h=hz+rx*rx/xx
            singleton=cm[self.g]==1
            den=1-hz
            if np.any((den<1e-10)&(~singleton)):raise ValueError('Unusual unit nuisance leverage')
            delta=np.where(singleton,0.,1/np.maximum(den,1e-15))
            xx1=xx-rx*rx*delta;yy1=yy-ry*ry*delta;xy1=xy-rx*ry*delta
            beta1=xy1/xx1;theta1=xy1/np.sqrt(xx1*yy1)
            sigma=sse/(n-k)
            cook=np.where(singleton,0.,err**2*h/(k*sigma*np.maximum(1-h,1e-15)**2))
            out['_details']={'rx':rx,'ry':ry,'err':err,'h':h,'hz':hz,'cook':cook,'loo_beta':beta1,'loo_theta':theta1,'singleton':singleton}
        return out

class Budget:
    def __init__(self,cap,seconds):self.start=time.monotonic();self.cap=cap;self.seconds=seconds;self.attempts=0
    def fit(self,design,w=None,details=False):
        if self.attempts>=self.cap or time.monotonic()-self.start>self.seconds:raise RuntimeError('EXPERIMENT_BUDGET_REACHED')
        self.attempts+=1;return design.fit(w,details)

def month_weights(rng,length,m=72):
    starts=rng.integers(0,m-length+1,size=math.ceil(m/length))
    idx=np.concatenate([np.arange(i,i+length) for i in starts])[:m]
    return np.bincount(idx,minlength=m).astype(int)

def interval(vals,alpha=.05):
    return [float(x) for x in np.quantile(vals,[alpha/2,1-alpha/2],method='linear')] if len(vals)>0 else None

def summary(draws,keys=('beta','theta'),alpha=.05,planned=None):
    ok=[x for x in draws if x.get('status')=='OK']
    out={'attempted':len(draws),'valid':len(ok),'failed':len(draws)-len(ok),'planned':planned or len(draws), 'usable':len(draws)==(planned or len(draws)) and len(ok)>=.95*(planned or len(draws))}
    for k in keys:out[k+'_CI']=interval([x[k] for x in ok],alpha)
    return out

def full_dummy(rows,spec,mode='full',weights=None):
    # Independent explicit-row implementation, for deterministic cross-checks only.
    ix=[]
    for r in rows:ix.extend([r]*int(weights[mid(r['auction_date'])] if weights is not None else 1))
    months=sorted({r['auction_date'][:7] for r in ix});projects=sorted({r['project'] for r in ix})
    z=np.array([[float(r['auction_date'][:7]==m) for m in months]+[math.log(r[k]) for k in MODES[mode]]+[float(r['project']==p) for p in projects[1:]] for r in ix])
    fn=np.log1p if spec=='A' else np.log
    x=fn([r['sd_bid']/r['mean_bid'] for r in ix]);y=fn([r['sd_won']/r['mean_won'] for r in ix])
    coef,_,rank,_=np.linalg.lstsq(np.column_stack((z,x)),y,rcond=None)
    p,_,_,_=np.linalg.lstsq(z,np.column_stack((x,y)),rcond=None)
    rx,ry=(np.column_stack((x,y))-z@p).T
    return {'beta':float(coef[-1]),'theta':float(rx@ry/np.sqrt((rx@rx)*(ry@ry))),'rank':int(rank)}

def run(data,out,protocol,prior):
    if out.exists():raise FileExistsError('Never overwrite experiment output')
    out.mkdir(parents=True)
    start=dt.datetime.now(dt.timezone.utc).isoformat();p=json.loads(protocol.read_text());rows=read_rows(data)
    original_input_hash=hashfile(data);budget=Budget(p['limits']['max_actual_data_fits'],p['limits']['max_seconds'])
    original=json.loads(prior.read_text());result={'protocol_sha256':hashfile(protocol),'input_sha256':original_input_hash,'source_raw_revalidation':'separate input_audit.json','post_result_exploratory':True,'claim':'reported-field conditional association only','n':len(rows),'main':{},'control_ladder':[],'period_points':[],'project_points':[],'year_points':[],'leave_group_out':[],'influence':{},'cross_checks':[],'failures':[]}
    designs={}
    for s in TRANSFORMS:
        d=Design(rows,s);designs[(s,'full')]=d
        main=budget.fit(d,details=True);detail=main.pop('_details');result['main'][s]=main
        ref=original['points'][s]
        if abs(main['beta']-ref['beta'])>1e-10 or abs(main['theta']-ref['theta'])>1e-10:raise ValueError('Previous point estimate not reproduced')
        c=full_dummy(rows,s);result['cross_checks'].append({'name':'full_dummy_'+s,'beta_difference':c['beta']-main['beta'],'theta_difference':c['theta']-main['theta']})
        result['control_ladder'].append(main.copy())
        for mode in ('FE','size_participation'):
            d=Design(rows,s,mode);designs[(s,mode)]=d;result['control_ladder'].append(budget.fit(d))
        # Observed within-control scale: IQR(rx), not full raw IQR extrapolated across collinear controls.
        effect_iqr=float(np.quantile(detail['rx'],.75)-np.quantile(detail['rx'],.25));dy=main['beta']*effect_iqr
        result['main'][s]['within_x_IQR']=effect_iqr;result['main'][s]['response_log_scale_difference_at_within_IQR']=dy
        result['main'][s]['multiplicative_difference_on_one_plus_rw' if s=='A' else 'multiplicative_difference_on_rw']=float(np.expm1(dy))
        for group,key in [('month',lambda r:r['auction_date'][:7]),('year',lambda r:r['auction_date'][:4]),('project',lambda r:r['project'])]:
            for g in sorted({key(r) for r in rows}):
                subset=[r for r in rows if key(r)!=g]
                f=budget.fit(Design(subset,s));result['leave_group_out'].append({'omission_type':group,'omitted':g,**f})
        order=np.argsort(-detail['cook'],kind='stable');n_drop=math.ceil(.01*len(rows));drop=set(order[:n_drop].tolist())
        f=budget.fit(Design([r for i,r in enumerate(rows) if i not in drop],s))
        result['influence'][s]={'max_abs_single_row_beta_change':float(np.max(abs(detail['loo_beta']-main['beta']))),'loo_beta_range':[float(detail['loo_beta'].min()),float(detail['loo_beta'].max())],'loo_theta_range':[float(detail['loo_theta'].min()),float(detail['loo_theta'].max())],'singleton_month_rows':int(detail['singleton'].sum()),'max_leverage':float(detail['h'].max()),'max_Cook_distance_non_singleton':float(detail['cook'].max()),'top_1pct_Cook_omitted':n_drop,'diagnostic_not_replacement_main':True,'top_1pct_refit':f,'omitted_event_ids':[rows[i]['event_id'] for i in order[:n_drop]],'top_1pct_share_of_abs_partial_crossproduct':float(np.sum(abs(detail['rx'][list(drop)]*detail['ry'][list(drop)]))/np.sum(abs(detail['rx']*detail['ry'])))}
        # Deterministic exact leave-one-out cross-checks; no selected favourable cases.
        for i in (0,len(rows)//2,len(rows)-1):
            f=budget.fit(Design([r for j,r in enumerate(rows) if j!=i],s))
            db=f['beta']-detail['loo_beta'][i];dc=f['theta']-detail['loo_theta'][i]
            if max(abs(db),abs(dc))>1e-10:raise ValueError('Analytic deletion identity failed')
            result['cross_checks'].append({'name':f'loo_{s}_{i}','beta_difference':db,'theta_difference':dc})
        for period,a,b in [('early','2020-01-01','2022-12-31'),('late','2023-01-01','2025-12-31')]:
            subset=[r for r in rows if a<=r['auction_date']<=b];d=Design(subset,s);designs[(s,period)]=d
            f=budget.fit(d);result['period_points'].append({'period':period,**f})
            c=full_dummy(subset,s);result['cross_checks'].append({'name':f'period_full_dummy_{s}_{period}','beta_difference':c['beta']-f['beta'],'theta_difference':c['theta']-f['theta']})
        for project in ('EU','DE','PL'):
            subset=[r for r in rows if r['project']==project];d=Design(subset,s);designs[(s,project)]=d
            result['project_points'].append({'project':project,**budget.fit(d)})
        for year in range(2020,2026):
            subset=[r for r in rows if r['auction_date'][:4]==str(year)]
            result['year_points'].append({'year':year,**budget.fit(Design(subset,s))})
    # Group deletions above alter month composition; all designs were rebuilt before demeaning.
    period_draws=[];ladder_draws=[];project_draws=[];plans={}
    rng=np.random.default_rng(np.random.SeedSequence(p['bootstrap']['period_rng']))
    period_plans=[]
    for i in range(p['bootstrap']['period_repetitions']):
        w=np.concatenate([month_weights(rng,3,36),month_weights(rng,3,36)]);period_plans.append(w.tolist())
        for s in TRANSFORMS:
            record={'draw':i,'spec':s,'status':'OK'}
            try:
                e=budget.fit(designs[(s,'early')],w);l=budget.fit(designs[(s,'late')],w)
                record.update({'beta_early':e['beta'],'beta_late':l['beta'],'theta_early':e['theta'],'theta_late':l['theta'],'delta_beta':l['beta']-e['beta'],'delta_theta':l['theta']-e['theta']})
            except (ValueError,np.linalg.LinAlgError) as exc:
                record.update(status='FAILED',error=str(exc));result['failures'].append({'family':'period',**record})
            period_draws.append(record)
    plans['period']=period_plans
    for fam,rep,key,labels,target in [('ladder',p['bootstrap']['ladder_repetitions'],'ladder_rng',('FE','size_participation'),ladder_draws),('project',p['bootstrap']['project_repetitions'],'project_rng',('EU','DE','PL'),project_draws)]:
        rng=np.random.default_rng(np.random.SeedSequence(p['bootstrap'][key]));ww=[]
        for i in range(rep):
            w=month_weights(rng,3);ww.append(w.tolist())
            for s in TRANSFORMS:
                for label in labels:
                    r={'draw':i,'spec':s,'group':label,'status':'OK'}
                    try:r.update({k:v for k,v in budget.fit(designs[(s,label)],w).items() if k in ('beta','theta','residual_df')})
                    except (ValueError,np.linalg.LinAlgError) as exc:
                        r.update(status='FAILED',error=str(exc));result['failures'].append({'family':fam,**r})
                    target.append(r)
        plans[fam]=ww
    result['period_intervals']={};result['ladder_intervals']={};result['project_intervals']={}
    for s in TRANSFORMS:
        r=[d for d in period_draws if d['spec']==s]
        result['period_intervals'][s]=summary(r,('beta_early','beta_late','theta_early','theta_late','delta_beta','delta_theta'),planned=p['bootstrap']['period_repetitions'])
        result['period_intervals'][s]['delta_beta_Bonferroni97_5_CI']=interval([d['delta_beta'] for d in r if d['status']=='OK'],alpha=.025)
        for group in ('FE','size_participation'):
            result['ladder_intervals'][s+'_'+group]=summary([d for d in ladder_draws if d['spec']==s and d['group']==group],planned=p['bootstrap']['ladder_repetitions'])
        for group in ('EU','DE','PL'):
            result['project_intervals'][s+'_'+group]=summary([d for d in project_draws if d['spec']==s and d['group']==group],planned=p['bootstrap']['project_repetitions'])
    if hashfile(data)!=original_input_hash:raise ValueError('Input changed')
    maxdiff=max(max(abs(r['beta_difference']),abs(r['theta_difference'])) for r in result['cross_checks'])
    if maxdiff>1e-10:raise ValueError('Cross-check mismatch')
    result['execution']={'started_utc':start,'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'statistical_seconds':time.monotonic()-budget.start,'counted_data_fits':budget.attempts,'independent_full_dummy_fits':6,'independent_nuisance_projections':6,'analytical_leave_one_out_rows':len(rows)*2,'max_independent_difference':maxdiff,'Python':platform.python_version(),'NumPy':np.__version__,'SciPy':scipy.__version__,'script_sha256':hashfile(Path(__file__)),'fit_budget':budget.cap,'no_external_code_models_deserialized':True}
    for name,value in [('period_draws',period_draws),('ladder_draws',ladder_draws),('project_draws',project_draws),('control_ladder',result['control_ladder']),('leave_group_out',result['leave_group_out']),('period_points',result['period_points']),('project_points',result['project_points']),('year_points',result['year_points'])]:csvout(out/(name+'.csv'),value)
    dump(out/'resampling_indices.json',plans);dump(out/'extended_results.json',result)
    print(json.dumps({k:result[k] for k in ('main','period_points','period_intervals','project_points','ladder_intervals','execution','failures')},ensure_ascii=False,indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--data',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--protocol',type=Path,required=True);a.add_argument('--prior',type=Path,required=True)
    args=a.parse_args();run(args.data,args.out,args.protocol,args.prior)
