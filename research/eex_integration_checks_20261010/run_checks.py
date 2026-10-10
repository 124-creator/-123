"""Post-result diagnostic; no price regression without matched references."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
from itertools import product
import collections,csv,hashlib,json,math,subprocess,sys,tempfile,time
import numpy as np

ROOT=Path(__file__).resolve().parent
HELP=ROOT.parent/'eex_evidence_strengthening_20261010/code/run_strengthening.py'
if hashlib.sha256(HELP.read_bytes()).hexdigest()!='a90bc0b33a88219e489612748b92e756741f210842e660f74c52f09ec86c531b':
    raise ValueError('Reviewed numerical helper differs')
sys.path.insert(0,str(HELP.parent))
from run_strengthening import xlsx_cells,FIELDS,EXPECTED_HEADERS,projection
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
EEX='https://public.eex-group.com/eex/eua-auction-report/emission-spot-primary-market-auction-report-2026-data.xlsx'
EC='https://climate.ec.europa.eu/document/download/f3199005-4ca8-461b-9499-e5d37e5d2c93_en?filename=cap_report_202312_en.pdf&prefLang=et'
# Exact URL below is the newly accessed official source, not a denied endpoint.
EC='https://climate.ec.europa.eu/document/download/f3199005-4ca8-461b-9499-e5f3846ea4a5_en?filename=cap_report_202312_en.pdf&prefLang=et'
EXPECTED='54e6fb649872d229333adb29b62a3ff5b7fddd7393facc047050fb8f87a1bf3d'

def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def csvout(name,rows):
    if rows:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def download(url,path):
    run=subprocess.run(['curl','--fail','--location','--max-time','90','--max-filesize','15000000','--silent','--show-error',url,'-o',str(path)],capture_output=True,text=True)
    r={'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'returncode':run.returncode,'stderr':run.stderr[-1500:],'attempts':1}
    if run.returncode==0:r.update(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return r

def tuples(circular):
    for starts in product(range(9 if circular else 7),repeat=3):
        months=np.array([(s+j)%9 for s in starts for j in range(3)])
        yield starts,np.bincount(months,minlength=9)

def numerical_tests():
    checks=[]
    a=list(tuples(False));b=list(tuples(True))
    if len(a)!=343 or len(b)!=729:raise ValueError('Enumeration count')
    checks.append('343 and 729 equiprobable ordered tuples')
    if not all(w.sum()==9 for _,w in a+b):raise ValueError('Wrong total multiplicity')
    checks.append('Every tuple has nine month positions')
    if not np.allclose(np.mean([w for _,w in a],axis=0),np.array([3,6,9,9,9,9,9,6,3])/7):raise ValueError('Edge multiplicity')
    checks.append('Non-circular expected month multiplicities')
    if not np.allclose(np.mean([w for _,w in b],axis=0),np.ones(9)):raise ValueError('Circular multiplicity')
    checks.append('Circular equal marginal month inclusion')
    rng=np.random.default_rng(493);m=np.repeat(np.arange(9),12);Z=rng.normal(size=(108,3));Y=rng.normal(size=(108,2));w=np.tile(np.arange(1,13),9)
    p=projection(Y,Z,m,w);q=direct(Y,Z,m,w)
    if max(abs(p[k]-q[k]) for k in ('theta','beta'))>1e-10:raise ValueError('Synthetic WLS mismatch')
    checks.append('Synthetic weighted within/dummy projection agreement')
    q=direct(np.repeat(Y,w,axis=0),np.repeat(Z,w,axis=0),np.repeat(m,w),np.ones(int(w.sum())))
    if max(abs(p[k]-q[k]) for k in ('theta','beta'))>1e-10:raise ValueError('Explicit replication mismatch')
    checks.append('Synthetic multiplicity equals explicit repeated rows')
    dump('UNIT_TESTS.json',{'passed':len(checks),'checks':checks,'synthetic_not_market_evidence':True})

def direct(Y,Z,m,w):
    sel=w>0;Y,Z,m,w=Y[sel],Z[sel],m[sel],w[sel];u=np.unique(m)
    X=np.c_[Z,np.column_stack([m==j for j in u])];s=np.sqrt(w)
    co=np.linalg.lstsq(X*s[:,None],Y*s[:,None],rcond=None)[0];R=Y-X@co
    xx=float(w@(R[:,0]**2));yy=float(w@(R[:,1]**2));xy=float(w@(R[:,0]*R[:,1]))
    return {'beta':xy/xx,'theta':xy/math.sqrt(xx*yy)}

def run_e3(path,receipt):
    status={'classification':'post-result finite resampling sensitivity; not exact coverage','source':receipt,'fits':0}
    if receipt['returncode'] or receipt.get('sha256')!=EXPECTED or receipt.get('bytes')!=72742:
        status.update(status='HOLD',reason='Exact prior raw snapshot not retrieved');dump('E3R_RESULTS.json',status);return
    cells=xlsx_cells(path)['Primary Market Auction']
    if {k:cells.get(c+'6') for k,c in FIELDS.items()}!=EXPECTED_HEADERS:raise ValueError('Header mismatch')
    rows=[];excluded=collections.Counter();dated=0
    for r in sorted({int(c[1:]) for c in cells if c.startswith('B') and c[1:].isdigit() and int(c[1:])>=7}):
        serial=cells.get('B'+str(r))
        if not isinstance(serial,(int,float)) or not 42000<serial<60000:continue
        d=(datetime(1899,12,30)+timedelta(days=int(serial))).date();dated+=1
        if not(datetime(2026,1,1).date()<=d<=datetime(2026,9,30).date()):excluded['outside_fixed_dates']+=1;continue
        if cells.get('E'+str(r))!='T3PA' or cells.get('Z'+str(r)) not in ('EU','DE','PL') or cells.get('F'+str(r))!='successful':raise ValueError('Prior eligibility differs')
        v={k:cells.get(c+str(r)) for k,c in FIELDS.items()}
        for k in ('V','N','S','R','mu_B','sd_B','mu_W','sd_W'):
            if not isinstance(v[k],(float,int)) or not math.isfinite(v[k]) or v[k]<=0:raise ValueError('Invalid required field')
        if v['S']>v['N']:raise ValueError('Invalid bidder counts')
        rows.append((str(d),cells['Z'+str(r)],v))
    rows.sort();n=len(rows)
    if n!=166 or len({r[0] for r in rows})!=166:raise ValueError('Prior selected sample differs')
    m=np.array([int(r[0][5:7])-1 for r in rows]);Z=np.c_[[[math.log(r[2][k]) for k in ('V','N','S','R')] for r in rows],[[r[1]=='DE',r[1]=='PL'] for r in rows]]
    rat=np.array([[r[2]['sd_B']/r[2]['mu_B'],r[2]['sd_W']/r[2]['mu_W']] for r in rows]);Y={'A':np.log1p(rat),'C':np.log(rat)}
    start=time.monotonic()
    def fit(spec,w):
        status['fits']+=1
        if status['fits']>2300 or time.monotonic()-start>300:raise RuntimeError('Fixed budget exceeded')
        return projection(Y[spec],Z,m,w)
    points={s:fit(s,np.ones(n)) for s in ('A','C')}
    prior=json.loads((ROOT.parent/'eex_evidence_strengthening_20261010/results/newtime_2026/NEW_TIME_RESULTS.json').read_text())
    if max(abs(points[s][k]-prior['points'][s][k]) for s in ('A','C') for k in ('beta','theta'))>1e-9:raise ValueError('Baseline differs')
    allrows=[];failures=[];schemes={};cross=[]
    for circular in (False,True):
        name='circular' if circular else 'noncircular';weights=[];valid={'A':[],'C':[]}
        for i,(starts,mult) in enumerate(tuples(circular)):
            weights.append(mult.tolist());w=mult[m].astype(float)
            for s in ('A','C'):
                try:
                    p=fit(s,w);row={'scheme':name,'tuple':i,'start1':starts[0],'start2':starts[1],'start3':starts[2],'spec':s,**p};allrows.append(row);valid[s].append(p)
                    if i in (0,50):
                        status['fits']+=1;q=direct(Y[s],Z,m,w);err=max(abs(p[k]-q[k]) for k in ('beta','theta'));cross.append(err)
                        if err>1e-9:raise RuntimeError('Independent numerical mismatch')
                except (ValueError,np.linalg.LinAlgError) as e:failures.append({'scheme':name,'tuple':i,'spec':s,'error':str(e)})
        schemes[name]={'ordered_tuples':len(weights),'distinct_month_weight_vectors':len(set(tuple(w) for w in weights)),'expected_month_multiplicity':np.mean(weights,axis=0).tolist(),'statistics':{}}
        for s in ('A','C'):
            schemes[name]['statistics'][s]={'valid':len(valid[s])}
            for k in ('theta','beta'):schemes[name]['statistics'][s][k+'_q025_median_q975']=np.quantile([x[k] for x in valid[s]],[.025,.5,.975],method='linear').tolist()
        dump(name+'_month_multiplicities.json',weights)
    deletion=[]
    for mo in range(9):
        for s in ('A','C'):deletion.append({'omitted_month':mo+1,'spec':s,**fit(s,(m!=mo).astype(float))})
    status.update(status='COMPLETED_DIAGNOSTIC',n=n,months=9,dated_rows=dated,excluded=dict(excluded),points=points,schemes=schemes,leave_month_ranges={s:{k:[min(r[k] for r in deletion if r['spec']==s),max(r[k] for r in deletion if r['spec']==s)] for k in ('theta','beta')} for s in ('A','C')},failures=len(failures),independent_crosschecks=len(cross),max_crosscheck_difference=max(cross),compute_seconds=time.monotonic()-start,prior_intervals_preserved=True,exact_coverage_claim=False)
    csvout('enumerated_projections.csv',allrows);csvout('leave_month.csv',deletion);dump('FAILURES.json',failures);dump('E3R_RESULTS.json',status)

def main():
    numerical_tests()
    with tempfile.TemporaryDirectory(prefix='eex-private-') as tmp:
        tmp=Path(tmp);p=tmp/'2026.xlsx';r=download(EEX,p);dump('EEX_DOWNLOAD.json',r)
        try:run_e3(p,r)
        except Exception as e:dump('E3R_RESULTS.json',{'status':'FAILED_NOT_RETRIED','reason':str(e),'source':r})
        p=tmp/'ec_q4_2023.pdf';r=download(EC,p);r['price_regressions']=0
        if r['returncode']==0:
            import fitz
            with fitz.open(p) as doc:
                text='\n'.join(p.get_text() for p in doc);r['pages']=len(doc)
                # Only short field labels, counts and booleans; no third-party full text is republished.
                annex='\n'.join(doc[j].get_text() for j in range(31,min(35,len(doc))))
                labels=['Auction Clearing Price','Lowest Bid','Highest Bid','Mean Bid','Median Bid','Cover Ratio','Secondary','Reference']
                r['annex_label_counts']={x:annex.lower().count(x.lower()) for x in labels}
                r['midpoint_method_present']='midpoint' in text.lower()
                r['targeted_pages']=[8,32,33,34,35]
                r['gate']='HOLD: monthly reference-price comparisons; inspected individual tables supply auction/bid prices, not a per-auction secondary-market reference'
        else:r['gate']='HOLD: no PDF bytes; no reference-price observations'
        dump('E2_OFFICIAL_SOURCE_GATE.json',r)
    dump('RAW_HANDLING.json',{'new_raw_files_committed':False,'temporary_sources_removed':True,'exact_snapshot_hash_required':EXPECTED})
if __name__=='__main__':main()
