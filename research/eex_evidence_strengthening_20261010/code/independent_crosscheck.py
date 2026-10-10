"""Alternate numerical checks on fixed cases; no selection of favorable draws."""
from pathlib import Path
import sys,math,json,csv
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from scipy.linalg import lstsq
from run_strengthening import period_design,read_csv,logistic,projection,dump,ROOT

def independent(P,g,m):
    idx=np.repeat(np.arange(len(g)),m.astype(int));X=P[idx];y=g[idx]
    # Preserve column space, including absent references, via a QR-selected basis.
    from scipy.linalg import qr
    _,r,piv=qr(X,mode='economic',pivoting=True)
    rank=np.linalg.matrix_rank(X); cols=np.sort(piv[:rank]);X=X[:,cols]
    # Orthonormal coordinates improve optimization without changing the model span.
    X=np.linalg.qr(X,mode='reduced')[0]
    fun=lambda b: np.mean(np.logaddexp(0,X@b)-y*(X@b))
    grad=lambda b: X.T@(expit(X@b)-y)/len(y)
    hess=lambda b: X.T@((expit(X@b)*expit(-X@b))[:,None]*X)/len(y)
    fit=minimize(fun,np.zeros(X.shape[1]),jac=grad,hess=hess,method='trust-exact',options={'gtol':1e-12,'maxiter':1000})
    if np.max(np.abs(grad(fit.x)))>1e-7:raise ValueError('Independent trust-region score')
    p=expit(X@fit.x);w=np.where(y==1,expit(-X@fit.x),p)
    return idx,w,float(np.max(np.abs(grad(fit.x)))),fit.message

def full_projection(Y,Z,month,w):
    unique,ix=np.unique(month,return_inverse=True);design=np.c_[Z,np.eye(len(unique))[ix]]
    sq=np.sqrt(w);coef,_,_,_=lstsq(design*sq[:,None],Y*sq[:,None],lapack_driver='gelsy')
    rr=Y-design@coef;a,b=rr.T
    xx=np.dot(w,a*a);yy=np.dot(w,b*b);xy=np.dot(w,a*b)
    return {'beta':float(xy/xx),'theta':float(xy/math.sqrt(xx*yy))}

if __name__=='__main__':
    rows=read_csv(Path(sys.argv[1])/'parsed/candidate_dispersion.csv');rows.sort(key=lambda r:(r['date'],r['venue_raw']))
    d=period_design(rows);indices=json.loads((ROOT/'results/bootstrap_indices.json').read_text())
    cases=[('point',np.ones(len(rows)))]
    for L,j in [(3,0),(3,17),(3,498),(3,998),(1,0),(6,0)]:
        selected=np.ravel(indices[str(L)][j]);mult=np.bincount(selected,minlength=72)[d['month']]
        cases.append((f'L{L}_draw{j}',mult))
    records=[]
    for name,m in cases:
        ow,info,p=logistic(d['P'],d['g'],m)
        idx,w,score,message=independent(d['P'],d['g'],m)
        err=float(np.max(np.abs(w-ow[idx])))
        print(name, 'p-difference',err, 'score',score,'message',message,flush=True)
        if err>1e-6:raise ValueError('Optimizer predictions disagree')
        maxbeta=maxtheta=0.
        for spec in ('A','C'):
            for period in (0,1):
                sel=d['g']==period;si=d['g'][idx]==period
                a=projection(d[spec][sel],d['Z'][sel],d['month'][sel],(m*ow)[sel])
                b=full_projection(d[spec][idx][si],d['Z'][idx][si],d['month'][idx][si],w[si])
                maxbeta=max(maxbeta,abs(a['beta']-b['beta']));maxtheta=max(maxtheta,abs(a['theta']-b['theta']))
        if max(maxbeta,maxtheta)>2e-6:raise ValueError('Alternative outcome calculation disagrees')
        records.append({'case':name,'max_weight_difference':err,'max_beta_difference':maxbeta,'max_theta_difference':maxtheta,
        'independent_score_max':score,'optimizer_status':str(message)})
    dump(ROOT/'audit/independent_crosscheck.json',{'method':'own Newton ML + within-month projection versus SciPy trust-exact in orthonormal coordinates + explicit repeated rows + full dummy scipy gelsy',
    'cases':records,'all_passed':True,'additional_estimation_requests':70,
    'note':'Numerical cross-check on same data, not new market evidence. Optimizer status accepted only with explicit small score and prediction agreement.'})
    print(json.dumps(records,indent=2))
