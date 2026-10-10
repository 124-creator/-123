"""Composition-standardized EEX reported-field association. No causal estimand.
Standard-library OOXML input audit; numpy/scipy estimation; no old models executed.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, time, zipfile, sys
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import numpy as np
from scipy.special import expit
from scipy.linalg import qr

NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
FIELDS={'V':'L','B':'M','bid_count':'N','successful_bid_count':'O',
'mean_bids_per_bidder':'P','mean_bid_size':'Q','mu_B':'R','sd_B':'S',
'mu_W':'T','sd_W':'U','R':'V','N':'W','S':'X'}
EXPECTED_HEADERS={'V':'Auction Volume tCO2','B':'Total Amount of Bids',
'bid_count':'Number of bids submitted','successful_bid_count':'Number of successful bids',
'mean_bids_per_bidder':'Average number of bids per bidder','mean_bid_size':'Average bid size',
'mu_B':'Average volume bid per bidder','sd_B':'Standard deviation of bid volume per bidder',
'mu_W':'Average volume won per bidder','sd_W':'Standard deviation of volume won per bidder',
'R':'Cover Ratio','N':'Total Number of Bidders','S':'Number of Successful Bidders'}
ROOT=Path(__file__).resolve().parents[1]

def dump(path, obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_csv(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def write_csv(path,rows):
    if not rows: return
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def xlsx_cells(path):
    """Read workbook cells without running formulas/macros or spreadsheet engines."""
    with zipfile.ZipFile(path) as z:
        if z.testzip(): raise ValueError('Bad XLSX CRC')
        book=ET.fromstring(z.read('xl/workbook.xml'))
        sheets=book.find('s:sheets',NS)
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rm={r.attrib['Id']:r.attrib['Target'] for r in rels}
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            sr=ET.fromstring(z.read('xl/sharedStrings.xml'))
            shared=[''.join(e.itertext()) for e in sr.findall('s:si',NS)]
            shared=[''.join(t.text or '' for t in e.findall('.//s:t',NS)) for e in sr.findall('s:si',NS)]
        result={}
        for sheet in sheets:
            rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target=rm[rid]; target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            data=ET.fromstring(z.read(target));cells={}
            for cell in data.findall('.//s:sheetData/s:row/s:c',NS):
                v=cell.find('s:v',NS); typ=cell.attrib.get('t')
                if cell.find('s:f',NS) is not None:
                    # Store metadata formulas as unevaluated text. A formula in a
                    # required numeric field will fail the numeric audit below.
                    cells[cell.attrib['r']]={'unevaluated_formula':cell.find('s:f',NS).text}
                    continue
                if typ=='s': val=shared[int(v.text)] if v is not None else None
                elif typ=='inlineStr': val=''.join(t.text or '' for t in cell.findall('.//s:t',NS))
                elif typ=='b': val=bool(int(v.text)) if v is not None else None
                else:
                    text=v.text if v is not None else None
                    if text is None: val=None
                    else:
                        try: val=float(text)
                        except ValueError: val=text
                cells[cell.attrib['r']]=val
            result[sheet.attrib['name']]=cells
    return result

def audit_inputs(inp):
    manifest=json.loads((inp/'INPUT_MANIFEST.json').read_text())
    verified={}
    for item in manifest['files']:
        p=inp/item['path']; digest=sha(p)
        if digest!=item['sha256'] or p.stat().st_size!=item['bytes']:
            raise ValueError('Input hash differs: '+item['path'])
        verified[item['path']]=digest
    allrows=read_csv(inp/'parsed/extraction_all_2020_2025.csv')
    rows=read_csv(inp/'parsed/candidate_dispersion.csv')
    exclusions=read_csv(inp/'parsed/row_exclusions.csv')
    def key(r): return (r['file'],r['sheet'],r['row'])
    if len({key(r) for r in allrows})!=len(allrows):raise ValueError('Duplicate source keys')
    bykey={key(r):r for r in allrows}
    for r in rows:
        if r!=bykey[key(r)]:raise ValueError('Candidate differs from extraction')
    eligible=[r for r in allrows if r['contract_raw']=='T3PA' and r['venue_raw'] in ('EU','DE','PL') and r['status_raw']=='successful']
    if {key(r) for r in rows}!={key(r) for r in eligible}:raise ValueError('Eligibility mismatch')
    if len(rows)!=1281 or len(allrows)!=1327 or len(exclusions)!=46:raise ValueError('Unexpected frozen counts')
    books={p.name:xlsx_cells(p) for p in sorted((inp/'raw').glob('*.xlsx'))}
    heads=[]; comparisons=0
    for filename,book in books.items():
        c=book['Primary Market Auction']
        heads.append({'file':filename,'header':{k:c.get(v+'6') for k,v in FIELDS.items()},
                      'all_row6_labels':{k:v for k,v in c.items() if k.rstrip('0123456789')+ '6' ==k}})
        for field,col in FIELDS.items():
            if c.get(col+'6')!=EXPECTED_HEADERS[field]:raise ValueError('Header differs: '+filename+' '+field)
    for r in allrows:
        cells=books[r['file']][r['sheet']]
        for field,col in FIELDS.items():
            original=cells.get(col+r['row']); text=r[field]
            parsed=None if not text else float(text)
            if original!=parsed:raise ValueError(f'Cell mismatch {r["file"]} {col+r["row"]}')
            comparisons+=1
    rows=sorted(rows,key=lambda r:(r['date'],r['venue_raw']))
    if len({r['date'] for r in rows})!=len(rows):raise ValueError('Duplicate dates')
    for r in rows:
        for f in ('V','B','N','S','R','mu_B','mu_W','sd_B','sd_W'):
            val=float(r[f])
            if not math.isfinite(val) or val<=0:raise ValueError('Nonpositive/nonfinite '+f)
        if float(r['S'])>float(r['N']):raise ValueError('Successful count > participation')
    dump(ROOT/'audit/input_audit.json',{'utc':datetime.now(timezone.utc).isoformat(),
         'hashes':verified,'workbooks':len(books),'dated_rows':len(allrows),'candidate_rows':len(rows),
         'excluded_rows':len(exclusions),'source_numeric_comparisons':comparisons,
         'header_comparisons':len(heads)*len(FIELDS),'duplicate_dates':0,
         'method':'stdlib ZIP + XML versus all CSV numeric values; not a market/vintage/population certification'})
    dump(ROOT/'audit/workbook_headers.json',heads)
    return rows,verified

class Budget:
    def __init__(self,limit=15000,seconds=1500):self.n=0;self.limit=limit;self.start=time.monotonic();self.seconds=seconds
    def take(self,k=1):
        self.n+=k
        if self.n>self.limit or time.monotonic()-self.start>self.seconds:raise RuntimeError('Budget exceeded')


def period_design(rows):
    logs=np.array([[math.log(float(r[f])) for f in ('V','N','S','R')] for r in rows])
    m=np.array([(int(r['date'][:4])-2020)*12+int(r['date'][5:7])-1 for r in rows])
    g=(m>=36).astype(float)
    means=logs.mean(axis=0);sd=logs.std(axis=0,ddof=0)
    if np.any(sd<=0):raise ValueError('Constant log covariate')
    s=(logs-means)/sd
    dummies=np.array([[float(r['venue_raw']=='DE'),float(r['venue_raw']=='PL')]+[float(int(r['date'][5:7])==j) for j in range(2,13)] for r in rows])
    P=np.column_stack([np.ones(len(rows)),s,s*s,dummies])
    names=['intercept']+['log_'+f for f in ('V','N','S','R')]+['square_zlog_'+f for f in ('V','N','S','R')]+['series_DE','series_PL']+['month_'+str(j) for j in range(2,13)]
    nuisance=np.column_stack([logs,dummies[:,:2]])
    ratio=np.array([[float(r['sd_B'])/float(r['mu_B']),float(r['sd_W'])/float(r['mu_W'])] for r in rows])
    return {'P':P,'names':names,'logs':logs,'g':g,'month':m,'Z':nuisance,
            'A':np.log1p(ratio),'C':np.log(ratio),'standardization':{'mean':means.tolist(),'sd0':sd.tolist()}}


def logistic(P,g,multiplicity=None,tol=1e-10,maxiter=200):
    """Unpenalized binomial ML using Newton + backtracking; no statistical fallback."""
    b=np.ones(len(g)) if multiplicity is None else np.asarray(multiplicity,dtype=float)
    active=b>0; X=P[active];y=g[active];w=b[active];scale=w.sum()
    if not (0<np.dot(w,y)<scale):raise ValueError('One period absent')
    # Remove only all-zero categorical columns. Other deficiencies are not hidden.
    keep=np.any(np.abs(X)>1e-14,axis=0)
    if X.shape[1] == 22:
        # If a baseline level is absent, re-reference the observed factor.
        # This changes no column space and is not a specification change.
        for start,end in ((9,11),(11,22)):
            if np.all(X[:,start:end].sum(axis=1)>0.5):
                available=np.flatnonzero(keep[start:end])+start
                if len(available):keep[available[0]]=False
    X=X[:,keep]
    if np.linalg.matrix_rank(X)<X.shape[1]:raise ValueError('Logit design rank deficient')
    beta=np.zeros(X.shape[1]);prev=np.inf
    for iteration in range(maxiter):
        eta=X@beta;p=expit(eta)
        loss=float(np.dot(w,np.logaddexp(0,eta)-y*eta)/scale)
        score=X.T@(w*(p-y))/scale
        err=float(np.max(np.abs(score)))
        if err<tol:break
        H=X.T@((w*p*(1-p))[:,None]*X)/scale
        try: step=np.linalg.solve(H,score)
        except np.linalg.LinAlgError as e:raise ValueError('Singular logit Hessian') from e
        move=float(score@step)
        if move<0 or not np.all(np.isfinite(step)):raise ValueError('Invalid Newton step')
        factor=1.
        for _ in range(50):
            trial=beta-factor*step; ev=X@trial
            loss2=float(np.dot(w,np.logaddexp(0,ev)-y*ev)/scale)
            if loss2<=loss-1e-4*factor*move+1e-15:break
            factor*=.5
        else:raise ValueError('Line search failure')
        beta=trial
        if np.max(np.abs(beta))>100:raise ValueError('Possible separated logit')
    else:raise ValueError('Logit did not converge')
    full=np.zeros(P.shape[1]);full[keep]=beta
    p=expit(P@full); eta=P@full
    # Numerically stable complements, without probability clipping.
    ow=np.where(g==1,expit(-eta),expit(eta))
    if np.any(~np.isfinite(ow)) or np.any(ow[active]<=0):raise ValueError('Invalid overlap weights')
    # ML guarantees equal weighted means of included terms, up to score tolerance.
    ww=w*np.where(y==1,expit(-(X@beta)),expit(X@beta))
    md=np.average(X[y==1],weights=ww[y==1],axis=0)-np.average(X[y==0],weights=ww[y==0],axis=0)
    if np.max(np.abs(md))>1e-6:raise ValueError('Exact balance numerical check failed')
    return ow,{'beta':full.tolist(),'iterations':iteration+1,'score_max':err,'ncols':int(keep.sum()),'max_balance_error':float(np.max(np.abs(md)))},p


def projection(Y,Z,month,w,return_residual=False):
    active=w>0;w=np.asarray(w[active],float);Y=Y[active];Z=Z[active];month=month[active]
    uniq,ix=np.unique(month,return_inverse=True);counts=np.bincount(ix,weights=w)
    M=np.column_stack([Z,Y]);den=counts[:,None]
    sums=np.column_stack([np.bincount(ix,weights=w*M[:,j],minlength=len(uniq)) for j in range(M.shape[1])])
    dm=M-sums[ix]/den[ix];nc=Z.shape[1]
    zd=dm[:,:nc]; yd=dm[:,nc:];sq=np.sqrt(w)
    # Drop only zero within-month columns, as required for absent series categories.
    use=np.sqrt(np.sum((sq[:,None]*zd)**2,axis=0))>1e-12
    design=zd[:,use]*sq[:,None]
    coef,_,rank,_=np.linalg.lstsq(design,yd*sq[:,None],rcond=None)
    if rank!=design.shape[1]:raise ValueError('Outcome nuisance rank deficient')
    resid=yd-zd[:,use]@coef
    xx=float(np.dot(w,resid[:,0]**2));yy=float(np.dot(w,resid[:,1]**2));xy=float(np.dot(w,resid[:,0]*resid[:,1]))
    if min(xx,yy)<1e-15:raise ValueError('Degenerate residual variation')
    beta=xy/xx;theta=xy/math.sqrt(xx*yy)
    out={'beta':beta,'theta':theta,'partial_R2':theta*theta,'n_active':int(active.sum()),
         'residual_df':int(active.sum()-len(uniq)-rank-1),'ess':float(w.sum()**2/(w@w))}
    if return_residual:return out,resid
    return out


def analyze(d,mult,budget):
    budget.take();ow,info,p=logistic(d['P'],d['g'],mult)
    out={'logistic':info,'points':{}}
    for spec in ('A','C'):
        out['points'][spec]={}
        for weighting,weight in [('unweighted',mult),('overlap',mult*ow)]:
            pair={}
            for period in (0,1):
                sel=d['g']==period;budget.take()
                pair[str(period)]=projection(d[spec][sel],d['Z'][sel],d['month'][sel],weight[sel])
            pair['delta_theta']=pair['1']['theta']-pair['0']['theta']
            pair['delta_beta']=pair['1']['beta']-pair['0']['beta']
            out['points'][spec][weighting]=pair
        out['points'][spec]['weighting_change_delta_theta']=out['points'][spec]['overlap']['delta_theta']-out['points'][spec]['unweighted']['delta_theta']
    return out,ow,p


def weighted_ks(x0,w0,x1,w1):
    grid=np.unique(np.r_[x0,x1])
    def cdf(x,w):
        order=np.argsort(x,kind='stable');x=x[order];w=w[order];s=np.r_[0,np.cumsum(w)/w.sum()]
        return s[np.searchsorted(x,grid,side='right')]
    return float(np.max(np.abs(cdf(x0,w0)-cdf(x1,w1))))


def diagnostics(d,ow,p):
    g=d['g'];P=d['P']; tables=[]
    for j,name in enumerate(d['names']):
        if name=='intercept':continue
        var0=np.var(P[g==0,j],ddof=0);var1=np.var(P[g==1,j],ddof=0);den=math.sqrt((var0+var1)/2)
        a=P[g==0,j].mean();b=P[g==1,j].mean();wa=np.average(P[g==0,j],weights=ow[g==0]);wb=np.average(P[g==1,j],weights=ow[g==1])
        tables.append({'term':name,'early_raw_mean':float(a),'late_raw_mean':float(b),
                      'early_ow_mean':float(wa),'late_ow_mean':float(wb),
                      'raw_SMD':float((b-a)/den) if den else 0.,'ow_SMD':float((wb-wa)/den) if den else 0.})
    distribution=[]
    for j,name in enumerate(('V','N','S','R')):
        x=d['logs'][:,j];x0=x[g==0];x1=x[g==1];w0=ow[g==0];w1=ow[g==1]
        v0=np.average((x0-np.average(x0,weights=w0))**2,weights=w0)
        v1=np.average((x1-np.average(x1,weights=w1))**2,weights=w1)
        distribution.append({'log_variable':name,'KS_raw':weighted_ks(x0,np.ones(len(x0)),x1,np.ones(len(x1))),
            'KS_ow':weighted_ks(x0,w0,x1,w1),'variance_ratio_raw':float(x1.var()/x0.var()),'variance_ratio_ow':float(v1/v0)})
    groups=[]
    for period in (0,1):
        s=g==period;w=ow[s];ess=w.sum()**2/(w@w)
        groups.append({'period':period,'n':int(s.sum()),'ESS':float(ess),'ESS_fraction':float(ess/s.sum()),
        'weight_sum':float(w.sum()),'weight_max':float(w.max()),'max_normalized_weight':float(w.max()/w.sum()),
        'p_min':float(p[s].min()),'p_Q1':float(np.quantile(p[s],.25)),'p_median':float(np.median(p[s])),
        'p_Q3':float(np.quantile(p[s],.75)),'p_max':float(p[s].max()),
        'proposed_ESS_gate':bool(ess>=max(100,.3*s.sum()))})
    return tables,distribution,groups


def draw_months(rng,L,M=36):
    starts=rng.integers(0,M-L+1,size=math.ceil(M/L))
    return (starts[:,None]+np.arange(L)).ravel()[:M]


def flatten_result(r,L,b):
    out=[]
    for spec in ('A','C'):
        for wt in ('unweighted','overlap'):
            z=r['points'][spec][wt]
            out.append({'block':L,'draw':b,'spec':spec,'weighting':wt,
                        'early_theta':z['0']['theta'],'late_theta':z['1']['theta'],'delta_theta':z['delta_theta'],
                        'early_beta':z['0']['beta'],'late_beta':z['1']['beta'],'delta_beta':z['delta_beta'],
                        'early_ESS':z['0']['ess'],'late_ESS':z['1']['ess'],
                        'change_delta_theta':r['points'][spec]['weighting_change_delta_theta'],
                        'logit_score_max':r['logistic']['score_max'],'logit_iterations':r['logistic']['iterations']})
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',type=Path,required=True);args=parser.parse_args()
    rows,hashes=audit_inputs(args.inputs);d=period_design(rows);budget=Budget()
    dump(ROOT/'audit/code_before_run.json',{'utc':datetime.now(timezone.utc).isoformat(),
       'files':{p.name:sha(p) for p in (ROOT/'code').glob('*.py')},
       'protocol_commit':'2151017871416fe0ad2505cfdbda23162aaa873e','new_results_seen_before_lock':False,
       'old_historical_results_seen':True,'preregistered':False})
    point,ow,p=analyze(d,np.ones(len(rows)),budget)
    print('POINT',json.dumps(point,ensure_ascii=False),flush=True)
    dump(ROOT/'results/point_estimates.json',point)
    # Required reproduction check against frozen period point values, not seed-sensitive intervals.
    refs={'A':[.5500637873219566,.7797580394102535,.6727741692090599,1.182470472806227],
          'C':[.5413773360052372,.7719109950999271,.6879713711013911,1.1232247074540742]}
    for spec,expected in refs.items():
        z=point['points'][spec]['unweighted'];actual=[z['0']['theta'],z['1']['theta'],z['0']['beta'],z['1']['beta']]
        if np.max(np.abs(np.array(actual)-expected))>1e-9:raise ValueError('Old baseline mismatch')
    bal,dist,grp=diagnostics(d,ow,p)
    write_csv(ROOT/'results/balance.csv',bal);write_csv(ROOT/'results/distribution_balance.csv',dist);write_csv(ROOT/'results/weight_summary.csv',grp)
    # Source row identities and weights, not the raw third-party fields.
    write_csv(ROOT/'results/row_weights.csv',[{'source_workbook':r['file'],'source_row':r['row'],'date':r['date'],'series':r['venue_raw'],
             'period':int(d['g'][i]),'p_late':float(p[i]),'overlap_weight':float(ow[i])} for i,r in enumerate(rows)])
    dump(ROOT/'results/standardization.json',d['standardization'])
    draws=[];failures=[];indices={};summaries=[]
    for L,B in [(3,999),(1,199),(6,199)]:
        rng=np.random.default_rng(np.random.SeedSequence([20261010,3,L]));idx=[];valid=0
        for b in range(B):
            i0=draw_months(rng,L);i1=draw_months(rng,L)+36;idx.append([i0.tolist(),i1.tolist()])
            counts=np.bincount(np.r_[i0,i1],minlength=72);mult=counts[d['month']].astype(float)
            try:
                fit,_,_=analyze(d,mult,budget);draws.extend(flatten_result(fit,L,b));valid+=1
            except (ValueError,np.linalg.LinAlgError) as exc:
                failures.append({'block':L,'draw':b,'error':str(exc)})
            if (b+1)%100==0:print('PROGRESS',L,b+1,valid,'requests',budget.n,'seconds',round(time.monotonic()-budget.start,1),flush=True)
        indices[str(L)]=idx
        for spec in ('A','C'):
            for wt in ('unweighted','overlap'):
                rr=[r for r in draws if r['block']==L and r['spec']==spec and r['weighting']==wt]
                for metric in ('early_theta','late_theta','delta_theta','delta_beta','change_delta_theta'):
                    vals=[r[metric] for r in rr]
                    lo,hi=np.quantile(vals,[.025,.975]);l2,h2=np.quantile(vals,[.0125,.9875])
                    z=point['points'][spec][wt]
                    val=z['0']['theta'] if metric=='early_theta' else z['1']['theta'] if metric=='late_theta' else point['points'][spec]['weighting_change_delta_theta'] if metric=='change_delta_theta' else z[metric]
                    summaries.append({'block':L,'spec':spec,'weighting':wt,'metric':metric,'point':val,
                                      'lower95':float(lo),'upper95':float(hi),'lower97_5':float(l2),'upper97_5':float(h2),
                                      'valid':len(rr),'planned':B,'success_fraction':len(rr)/B})
    write_csv(ROOT/'results/all_draws.csv',draws);write_csv(ROOT/'results/intervals.csv',summaries)
    dump(ROOT/'results/bootstrap_indices.json',indices);dump(ROOT/'results/failed_draws.json',failures)
    after={p:sha(args.inputs/p) for p in hashes}
    if after!=hashes:raise ValueError('Input changed')
    dump(ROOT/'audit/EXECUTION_RECEIPT.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),
         'elapsed_seconds':time.monotonic()-budget.start,'estimation_requests':budget.n,
         'requested_blocks':{'3':999,'1':199,'6':199},'failed_draws':len(failures),
         'input_bytes_unchanged':True,'old_baseline_reproduced':True,
         'original_manuscript_or_results_modified':False,'statistical_scope':'exploratory descriptive overlap-weighted period association',
         'source_files_after':{p.name:sha(p) for p in (ROOT/'code').glob('*.py')}})
    print('DONE',budget.n,len(failures),time.monotonic()-budget.start,flush=True)

if __name__=='__main__':main()
