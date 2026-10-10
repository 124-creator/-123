#!/usr/bin/env python3
"""Full-dummy OLS cross-checks of fixed A/B/C; no new estimands or searches."""
from __future__ import annotations
import argparse,csv,json,math,hashlib
from pathlib import Path
import numpy as np


def require(v,msg):
 if not v:raise ValueError(msg)

def full_fit(rows,spec,multiplicities):
 selected=rows if spec=='A' else [r for r in rows if float(r['sd_bid'])>0 and float(r['sd_won'])>0]
 ix=[]
 for r in selected:
  month=(int(r['auction_date'][:4])-2020)*12+int(r['auction_date'][5:7])-1
  for _ in range(int(multiplicities[month])):ix.append((r,month))
 require(len(ix)>0,'empty sample')
 months=sorted({m for _,m in ix});projects=sorted({r['project'] for r,_ in ix})
 Z=np.array([[float(m==mm) for mm in months]+[math.log(float(r[k])) for k in ('cover_ratio','auction_volume','bidders','successful_bidders')]+[float(r['project']==p) for p in projects[1:]] for r,m in ix])
 rb=np.array([float(r['sd_bid'])/float(r['mean_bid']) for r,m in ix]);rw=np.array([float(r['sd_won'])/float(r['mean_won']) for r,m in ix])
 x=np.log1p(rb) if spec in ('A','B') else np.log(rb)
 y=np.log1p(rw) if spec in ('A','B') else np.log(rw)
 X=np.column_stack((Z,x));b,_,rank,singular=np.linalg.lstsq(X,y,rcond=None)
 q,_,rz,_=np.linalg.lstsq(Z,np.column_stack((x,y)),rcond=None)
 rx,ry=(np.column_stack((x,y))-Z@q).T
 theta=float(rx@ry/math.sqrt(float(rx@rx)*float(ry@ry)))
 return {'beta':float(b[-1]),'theta':theta,'sse':float(np.sum((y-X@b)**2)),'n':len(ix),'columns':X.shape[1],'rank':int(rank),'df':len(ix)-int(rank),'condition_unscaled':float(singular[0]/singular[-1]),'nuisance_rank':int(rz)}

def run(root):
 root=Path(root);rows=list(csv.DictReader((root/'audit/verified/normalized_input.csv').open()))
 result=json.loads((root/'results/results.json').read_text());plans=json.loads((root/'results/bootstrap_month_multiplicities.json').read_text())
 draws=list(csv.DictReader((root/'results/bootstrap_draws.csv').open(encoding='utf-8-sig')))
 table={(int(d['block_months']),int(d['draw']),d['spec']):d for d in draws}
 checked=[];max_b=max_t=0.0;full_points={}
 for spec in ('A','B','C'):
  f=full_fit(rows,spec,[1]*72);v=result['points'][spec]
  db=abs(f['beta']-v['beta']);dt=abs(f['theta']-v['theta'])
  require(db<1e-10 and dt<1e-10,'Point discrepancy')
  require(abs(f['sse']-v['sse_with_x'])<1e-9,'SSE discrepancy')
  require(f['rank']==v['full_design_rank'],'Rank discrepancy')
  checked.append({'kind':'point','spec':spec,'beta_difference':db,'theta_difference':dt});full_points[spec]=f
  max_b=max(max_b,db);max_t=max(max_t,dt)
 for length,indices in ((3,(0,499,998)),(1,(0,198)),(6,(0,198))):
  for index in indices:
   weights=plans[str(length)][index]
   for spec in ('A','C'):
    f=full_fit(rows,spec,weights);v=table[(length,index,spec)]
    require(v['status']=='OK','Stored bootstrap failed')
    db=abs(f['beta']-float(v['beta']));dt=abs(f['theta']-float(v['theta']))
    require(db<1e-10 and dt<1e-10,'Bootstrap full-dummy discrepancy')
    checked.append({'kind':'bootstrap','block_months':length,'draw':index,'spec':spec,'beta_difference':db,'theta_difference':dt})
    max_b=max(max_b,db);max_t=max(max_t,dt)
 plan_checks=0
 for length_text,weights_list in plans.items():
  length=int(length_text);rng=np.random.default_rng(np.random.SeedSequence([20261010,length]))
  for weights in weights_list:
   starts=rng.integers(0,72-length+1,size=math.ceil(72/length))
   dates=[m for start in starts for m in range(int(start),int(start)+length)][:72]
   expected=[dates.count(m) for m in range(72)]
   require(expected==weights and sum(weights)==72,'Month resampling plan mismatch');plan_checks+=1
 for i in range(999):
  a,b=table[(3,i,'A')],table[(3,i,'B')]
  require(a['beta']==b['beta'] and a['theta']==b['theta'],'A and B differ despite identical sample')
 manifest=json.loads((root/'input/INPUT_MANIFEST.json').read_text())
 for r in manifest['files']:
  b=(root/'input'/r['path']).read_bytes()
  require(hashlib.sha256(b).hexdigest()==r['sha256'] and len(b)==r['bytes'],'Input mutated')
 prior=json.loads((root/'input/results/RESULTS.json').read_text())
 reference={'A':'log1p','B':'log1p','C':'ordinary_log_ratio'}
 compare={s:{'point_beta_difference_from_team':result['points'][s]['beta']-prior[k]['beta'],'SSE_difference_from_team':result['points'][s]['sse_with_x']-prior[k]['SSE'],'prior_interval': [prior[k]['CI_low'],prior[k]['CI_high']],'this_run_interval':result['intervals'][s+'_L3']['beta_percentile_95']} for s,k in reference.items()}
 out={'status':'PASS','independent_implementation':'unscaled full original month dummies + explicit repeated rows + numpy.linalg.lstsq, no within-month routine reused',
 'point_refits':3,'selected_bootstrap_refits':14,'additional_nuisance_projection_systems':17,'empirical_pipeline_requests':result['fit_attempts'],'total_counting_extra_full_and_nuisance_solves':result['fit_attempts']+34,
 'max_abs_beta_difference':max_b,'max_abs_theta_difference':max_t,'full_dummy_points':full_points,'month_plan_checks':plan_checks,'identical_A_B_paired_draws':999,'source_files_unchanged':len(manifest['files']),
 'checks':checked,'team_comparison':compare,'interval_difference_reason':'This run follows the previously supplied ready-code SeedSequence([seed,L]) stream. Team used a different seed initialization; point estimates agree, bootstrap intervals need not be identical. No seed search or repeat-until-significant run.'}
 (root/'audit/independent_check.json').write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False))
 print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);run(a.parse_args().root)
