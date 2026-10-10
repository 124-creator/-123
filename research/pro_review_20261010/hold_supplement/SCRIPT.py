import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import csv,io,json,hashlib,sys,time,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
O=Path(__file__).resolve().parent
ROOT=O.parent
T=time.perf_counter()
def sha(b): return hashlib.sha256(b).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def require(ok,msg):
 if not ok: raise RuntimeError(msg)
def validate(b,e):
 require(len(b)==e['bytes'] and sha(b)==e['sha256'],'hash/length mismatch')
 return b

def design(c,x,months,venues):
 return np.column_stack([np.ones(len(x)),x,c]+[(venues==v).astype(float) for v in sorted(set(venues))[1:]]+[(months==m).astype(float) for m in sorted(set(months))[1:]])
def fit(c,x,y,months,venues,detail=True):
 a=design(c,x,months,venues);coef,_,rank,s=np.linalg.lstsq(a,y,rcond=None)
 require(rank==a.shape[1],'rank failure')
 if not detail:return float(coef[1])
 base=np.delete(a,1,axis=1);q=np.column_stack([x,y]);res=q-base@np.linalg.lstsq(base,q,rcond=None)[0];xr,yr=res.T
 e=y-a@coef;sse=float(e@e);bsse=float(yr@yr)
 beta_fwl=float(xr@yr/(xr@xr));require(abs(beta_fwl-coef[1])<1e-9,'FWL mismatch')
 return dict(beta=float(coef[1]),n=len(x),columns=a.shape[1],rank=int(rank),residual_df=len(x)-int(rank),condition_full_dummy_unscaled=float(s[0]/s[-1]),residual_x_sd=float(np.sqrt(xr@xr/len(x))),SSE=sse,base_SSE=bsse,incremental_SSE=bsse-sse,partial_R2=(bsse-sse)/bsse,FWL_beta=beta_fwl),res

def selftest():
 rng=np.random.default_rng(777);n=240;B=rng.uniform(1e5,1e6,n);V=rng.uniform(1e4,1e5,n);N=rng.integers(10,40,n);S=rng.integers(2,10,n);dB=rng.uniform(1e3,1e5,n);dW=rng.uniform(1e3,1e5,n)
 c=np.log(np.column_stack([B/V,V,N,S]));m=np.repeat(np.arange(12),20);v=np.tile(np.array(['DE','EU','PL']),80)
 fr,rr=fit(c,np.log(dB/(B/N)),np.log(dW/(V/S)),m,v)
 fs,rs=fit(c,np.log(dB),np.log(dW),m,v)
 require(np.max(np.abs(rr-rs))<1e-10 and abs(fr['beta']-fs['beta'])<1e-10,'synthetic algebra failure')
 for b,e in [(b'abc',dict(bytes=4,sha256=sha(b'abc'))),(b'abc',dict(bytes=3,sha256=sha(b'abd')))]:
  try:validate(b,e)
  except RuntimeError:pass
  else:raise RuntimeError('corrupt input accepted')
 print(json.dumps(dict(synthetic_algebra=True,OLS_FWL=True,corruption_refused=True,optimized=not __debug__)))
if '--self-test' in sys.argv:
 selftest();sys.exit(0)
protocol_bytes=(O/'PROTOCOL.json').read_bytes();p=json.loads(protocol_bytes)
require(p['status']=='POST_RESULT_EXPLORATORY' and p['reps']==999 and p['seed']==20261010 and p['block_months']==3,'protocol settings')
inputs={};buffers={}
for e in p['inputs']:
 path=Path(e['path']).resolve();require(path.parent==Path(e['directory']).resolve(),'boundary');require(str(path) not in inputs,'duplicate input')
 b=validate(path.read_bytes(),e);inputs[str(path)]=e;buffers[e['id']]=b
require(set(buffers)=={'candidate','definition_manifest','old_protocol','old_results','old_manifest'},'coverage')
sm=json.loads(buffers['definition_manifest']);om=json.loads(buffers['old_manifest'])
for id,manifest,name in [('candidate',sm,'candidate_dispersion.csv'),('old_protocol',om,'PROTOCOL.json'),('old_results',om,'MAIN_ESTIMATES.json')]:
 matches=[e for e in manifest if e['file']==name];require(len(matches)==1,'manifest coverage');validate(buffers[id],matches[0])
oldp=json.loads(buffers['old_protocol']);old=json.loads(buffers['old_results'])['main']
require(oldp['bootstrap']['primary_L']==3 and oldp['bootstrap']['primary_reps']==999 and oldp['bootstrap']['seed']==p['seed'],'old bootstrap mismatch')
rows=list(csv.DictReader(io.StringIO(buffers['candidate'].decode('utf-8-sig'))));rows.sort(key=lambda r:(r['date'],r['venue_raw']))
require(len(rows)==1281 and len(set((r['date'],r['venue_raw'],r['contract_raw'],r['status_raw']) for r in rows))==1281,'sample')
require(all('2020-01-01'<=r['date']<='2025-12-31' and r['venue_raw'] in ['DE','EU','PL'] and r['contract_raw']=='T3PA' and r['status_raw']=='successful' for r in rows),'scope')
f={k:np.array([float(r[k]) for r in rows]) for k in ['sd_B','sd_W','mu_B','mu_W','B','V','R','N','S']}
require(all(np.all(np.isfinite(z)) and np.all(z>0) for z in f.values()),'nonpositive/nonfinite')
m=np.array([int(r['date'][:4])*12+int(r['date'][5:7])-1 for r in rows]);v=np.array([r['venue_raw'] for r in rows]);axis=np.arange(2020*12,2026*12);require(len(axis)==72,'calendar axis')
c=np.log(np.column_stack([f[k] for k in ['R','V','N','S']]))
x1=np.log1p(f['sd_B']/f['mu_B']);y1=np.log1p(f['sd_W']/f['mu_W']);x=np.log(f['sd_B']/f['mu_B']);y=np.log(f['sd_W']/f['mu_W'])
f1,r1=fit(c,x1,y1,m,v);require(abs(f1['beta']-old['beta'])<1e-9 and abs(f1['SSE']-old['SSE'])<1e-9,'original mismatch')
fl,rl=fit(c,x,y,m,v);fs,rs=fit(c,np.log(f['sd_B']),np.log(f['sd_W']),m,v)
# Pure algebra uses implied means AND implied cover ratio, not rounded reported R.
ci=c.copy();ci[:,0]=np.log(f['B']/f['V']);xi=np.log(f['sd_B']/(f['B']/f['N']));yi=np.log(f['sd_W']/(f['V']/f['S']))
fi,ri=fit(ci,xi,yi,m,v);fa,ra=fit(ci,np.log(f['sd_B']),np.log(f['sd_W']),m,v)
algebra=dict(beta_difference=fi['beta']-fa['beta'],max_abs_residual_difference=float(np.max(np.abs(ri-ra))),SSE_difference=fi['SSE']-fa['SSE'],label='PURE_ALGEBRA_NOT_NEW_ECONOMIC_FINDING')
require(abs(algebra['beta_difference'])<1e-9 and algebra['max_abs_residual_difference']<1e-9,'implied algebra')
rng=np.random.default_rng(p['seed']);groups=[np.flatnonzero(m==z) for z in axis];draws=[];fail=[]
for rep in range(p['reps']):
 require(time.perf_counter()-T<1200,'execution deadline')
 starts=rng.integers(0,len(axis)-3+1,size=int(np.ceil(len(axis)/3)));selected=(starts[:,None]+np.arange(3)[None,:]).ravel()[:72];idx=np.concatenate([groups[j] for j in selected])
 try:b=fit(c[idx],x[idx],y[idx],m[idx],v[idx],False)
 except RuntimeError as e:fail.append(dict(replicate=rep,error=str(e)));continue
 draws.append(dict(replicate=rep,beta=b))
require(len(draws)+len(fail)==999 and len(draws)>0,'bootstrap accounting')
ci95=list(map(float,np.quantile([d['beta'] for d in draws],[.025,.975],method='linear')))
fl['CI_low'],fl['CI_high']=ci95;f1['CI_low']=old['CI_low'];f1['CI_high']=old['CI_high'];f1['CI_provenance']='prior independent result; not rerun'
with (O/'BOOTSTRAP.csv').open('w',newline='',encoding='utf-8') as h:
 w=csv.DictWriter(h,fieldnames=['replicate','beta']);w.writeheader();w.writerows(draws)
rounding=dict(max_abs_log_muB_minus_log_BN=float(np.max(np.abs(np.log(f['mu_B'])-np.log(f['B']/f['N'])))),max_abs_log_muW_minus_log_VS=float(np.max(np.abs(np.log(f['mu_W'])-np.log(f['V']/f['S'])))),max_abs_log_R_minus_log_BV=float(np.max(np.abs(np.log(f['R'])-np.log(f['B']/f['V'])))),reported_ratio_vs_raw_beta_difference=fl['beta']-fs['beta'],reported_max_abs_residual_difference=float(np.max(np.abs(rl-rs))))
result=dict(status='COMPLETE',decision='HOLD',scope='post-result exploratory reported-field association; no causal/CV/population certification',sample_n=1281,zero_sd_B=0,zero_sd_W=0,log1p=f1,ordinary_log_ratio=fl,ordinary_log_SD_same_reported_controls=fs,algebra_implied_ratio=fi,algebra_implied_raw_SD=fa,algebra=algebra,rounding=rounding,bootstrap=dict(attempted=999,valid=len(draws),failed=len(fail),failures=fail,seed=p['seed'],block_months=3,axis_months=72,empty_months=sum(len(g)==0 for g in groups),CI=ci95,method='noncircular moving 3-calendar-month blocks, joint platforms, original FE labels, each draw refit'),transform_positive_association_survives=fl['beta']>0 and ci95[0]>0)
save('RESULTS.json',result)
fields=['model','beta','n','rank','columns','residual_df','condition_full_dummy_unscaled','residual_x_sd','SSE','base_SSE','incremental_SSE','partial_R2','CI_low','CI_high','CI_provenance']
with (O/'TABLE.csv').open('w',newline='',encoding='utf-8-sig') as h:
 w=csv.DictWriter(h,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for name,z in [('log1p_reported_ratio',f1),('log_reported_ratio',fl),('log_reported_SD',fs),('algebra_implied_ratio',fi),('algebra_raw_SD_implied_R',fa)]:w.writerow(dict(model=name,**z))
tests=[]
for flags in [[],['-O']]:
 run=subprocess.run([sys.executable,'-B']+flags+[str(O/'SCRIPT.py'),'--self-test'],capture_output=True,text=True,timeout=60);require(run.returncode==0,'selftests failed');tests.append(dict(flags=flags,exit_code=run.returncode,stdout=run.stdout.strip()))
unchanged=True
for path,e in inputs.items():validate(Path(path).read_bytes(),e)
require((O/'PROTOCOL.json').read_bytes()==protocol_bytes,'protocol changed')
save('VERIFICATION.json',dict(passed=True,input_unchanged=True,protocol_sha256=sha(protocol_bytes),tests=tests,bootstrap_accounting=True,original_point_reproduced=True,OLS_FWL_equivalence=True,algebra_verified=True,elapsed_seconds=time.perf_counter()-T,python=sys.version,numpy=np.__version__,executable=sys.executable,network=False,installs=False,old_code_executed=False,limitations='ordinary static boundary; no directory-object security certification'))
report=f'''# EEX分散度限定分母/变换检查\n\n## HOLD（测量关联稳健性条件GO；投稿/创新/经济含义仍HOLD）\n本次是见到原结果后的post-result exploratory，不是原预设、预注册或未触碰验证集。全部同一1281场成功EUA、EU/DE/PL、2020—2025；两SD零值均0，无删行。控制固定logR/logV/logN/logS和平台、年月FE。\n\n|检查|beta|95% percentile CI|说明|\n|---|---:|---|---|\n|原log1p字段比值|{f1['beta']:.9f}|[{old['CI_low']:.9f},{old['CI_high']:.9f}]|只重算点估计；CI引用原独立复核|\n|普通log字段比值|{fl['beta']:.9f}|[{ci95[0]:.9f},{ci95[1]:.9f}]|新3自然月bootstrap999；有效{len(draws)}，失败{len(fail)}|\n|普通log SD、同报告控制|{fs['beta']:.9f}|未另bootstrap|分母残差等价对照；真实舍入非精确恒等|\n\n普通log正向关联是否保持：{result['transform_positive_association_survives']}。这支持核心正向条件关联不只依赖单一log1p；不同变换的beta和区间不在相同尺度，不能直接按大小比较经济效应。partial R2固定定义为(base SSE−full SSE)/base SSE，仅为样本内条件拟合信息，不是因果或样本外增益。完整dummy未缩放条件数、rank、df及残余X SD见TABLE.csv。\n\n## 分母与代数\nmu_B≈B/N、mu_W≈V/S、R≈B/V只是在显示精度下吻合，不是精确字段恒等、不是官方群体认证。普通log字段比值与log SD用相同报告控制的beta差={rounding['reported_ratio_vs_raw_beta_difference']:.12g}，残差最大差={rounding['reported_max_abs_residual_difference']:.12g}。真实字段舍入解释其非精确性；不能断言所有差异只因舍入而不披露定义未知。\n以隐含均值B/N、V/S及隐含R=B/V构造，log均值严格在截距与logR/logV/logN/logS张成空间内，残差代数等价：beta差={algebra['beta_difference']:.12g}，残差最大差={algebra['max_abs_residual_difference']:.12g}。这是纯代数和浮点容差验证，不是额外经济发现或新增回归情景。原log1p不是线性分母抵消，不能把这个恒等式套到原log1p。\n\n## 边界与裁决\n本轮不构成全NO-GO：数据可计算、普通log的关联可估计。报告统计量测量稳健性条件GO；整体研究/投稿建议HOLD，不保证投稿。未知SD群体和ddof继续保留，不能猜n/n−1，不称认证CV、公平、集中、不平等压缩或因果。同期结果控制、成功样本选择及共同冲击仍限制经济解释；创新和直接近邻尚未认证。未新增数据、预测/神经模型、分平台/分时期回归、联网或发布。\n\n## 执行验证\n每个实际解析输入在冻结PROTOCOL内唯一列示，校验bytes/hash后从同一buffer解析；candidate及旧协议/结果另与既有manifest匹配。72月连续轴保留空月位置、联合平台、原月FE标签，每次999抽样重新拟合，失败不重抽。普通及-O测试覆盖synthetic代数、OLS/FWL与长度/hash冲突拒绝。全部输入执行后hash不变。PROTOCOL哈希验证当前冻结字节，不声称独立时间戳预注册。全部输出仅本scratch，原项目只读。\n'''
(O/'REPORT.md').write_text(report,encoding='utf-8');(O/'SUMMARY.md').write_text(report,encoding='utf-8')
manifest=[dict(file=z.name,bytes=len(z.read_bytes()),sha256=sha(z.read_bytes())) for z in sorted(O.iterdir()) if z.is_file() and z.name!='MANIFEST.json'];save('MANIFEST.json',manifest)
print(json.dumps(dict(log1p=f1,ordinary=fl,raw=fs,algebra=algebra,bootstrap=result['bootstrap'],elapsed=time.perf_counter()-T),ensure_ascii=False,indent=2))
