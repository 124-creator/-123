"""Synthetic mathematical checks; never evidence about the auction market."""
import unittest
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import lstsq
from scipy.special import expit
from run_strengthening import logistic, projection, draw_months, weighted_ks

class Tests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(7271);self.P=np.c_[np.ones(600),rng.normal(size=(600,3))]
        self.g=rng.binomial(1,expit(self.P@np.array([0,.6,-.3,.2])))
        self.Z=rng.normal(size=(600,3));self.month=np.repeat(np.arange(20),30)
        self.Y=rng.normal(size=(600,2))+np.c_[self.Z.sum(1),self.Z.sum(1)]
        self.w=rng.uniform(.1,2,600)
    def test_balance(self):
        w,d,p=logistic(self.P,self.g)
        means=[np.average(self.P[self.g==g],weights=w[self.g==g],axis=0) for g in (0,1)]
        np.testing.assert_allclose(means[0],means[1],atol=1e-8)
    def test_probability_bounds(self):
        w,d,p=logistic(self.P,self.g);self.assertTrue(np.all((w>0)&(w<1)))
    def test_propensity_direction(self):
        w,d,p=logistic(self.P,self.g);np.testing.assert_allclose(w,np.where(self.g,p*0+1-p,p))
    def test_complement(self):
        a,_,p=logistic(self.P,self.g);b,_,q=logistic(self.P,1-self.g)
        np.testing.assert_allclose(a,b,atol=1e-10);np.testing.assert_allclose(p+q,1,atol=1e-10)
    def test_logit_independent_optimizer(self):
        w,d,p=logistic(self.P,self.g);X=self.P;y=self.g
        f=lambda b:np.mean(np.logaddexp(0,X@b)-y*(X@b))
        jac=lambda b:X.T@(expit(X@b)-y)/len(y)
        fit=minimize(f,np.zeros(X.shape[1]),jac=jac,method='BFGS',options={'gtol':1e-11,'maxiter':1000})
        np.testing.assert_allclose(expit(X@fit.x),p,atol=2e-7)
    def test_logit_multiplicity(self):
        c=np.tile([0,1,2],200);idx=np.repeat(np.arange(600),c)
        w,_,p=logistic(self.P,self.g,c);v,_,q=logistic(self.P[idx],self.g[idx])
        np.testing.assert_allclose(w[idx],v,atol=1e-8)
    def test_projection_full_dummies(self):
        out=projection(self.Y,self.Z,self.month,self.w)
        X=np.c_[self.Z,np.eye(20)[self.month]];sqrt=np.sqrt(self.w)
        coef=lstsq(X*sqrt[:,None],self.Y*sqrt[:,None],lapack_driver='gelsy')[0]
        r=self.Y-X@coef;a,b=r.T
        self.assertAlmostEqual(out['beta'],np.dot(self.w,a*b)/np.dot(self.w,a*a),12)
    def test_projection_multiplicity(self):
        c=np.tile([0,1,2],200);idx=np.repeat(np.arange(600),c)
        a=projection(self.Y,self.Z,self.month,c);b=projection(self.Y[idx],self.Z[idx],self.month[idx],np.ones(len(idx)))
        self.assertAlmostEqual(a['theta'],b['theta'],12)
    def test_weight_scaling(self):
        a=projection(self.Y,self.Z,self.month,self.w);b=projection(self.Y,self.Z,self.month,self.w*29)
        self.assertAlmostEqual(a['theta'],b['theta'],12);self.assertAlmostEqual(a['ess'],b['ess'],9)
    def test_swapped_outcome(self):
        a=projection(self.Y,self.Z,self.month,self.w);b=projection(self.Y[:,::-1],self.Z,self.month,self.w)
        self.assertAlmostEqual(a['theta'],b['theta'],12)
    def test_R2(self):
        a=projection(self.Y,self.Z,self.month,self.w);self.assertAlmostEqual(a['partial_R2'],a['theta']**2,14)
    def test_degenerate(self):
        with self.assertRaises(ValueError):projection(np.zeros_like(self.Y),self.Z,self.month,self.w)
    def test_single_period(self):
        with self.assertRaises(ValueError):logistic(self.P,np.ones(600))
    def test_block_axis(self):
        for L in (1,3,6):
            a=draw_months(np.random.default_rng(1),L);self.assertEqual(len(a),36);self.assertTrue(np.all((a>=0)&(a<36)))
    def test_KS(self):
        x=np.array([1.,2.,3.]);w=np.ones(3)
        self.assertEqual(weighted_ks(x,w,x,w),0.);self.assertEqual(weighted_ks(x,w,x+10,w),1.)
    def test_ESS(self):
        a=projection(self.Y,self.Z,self.month,np.ones(600));self.assertEqual(a['ess'],600.)
    def test_zero_weight_removal(self):
        w=self.w.copy();w[:30]=0;sel=w>0
        a=projection(self.Y,self.Z,self.month,w);b=projection(self.Y[sel],self.Z[sel],self.month[sel],w[sel])
        self.assertEqual(a['theta'],b['theta'])
    def test_missing_reference_category(self):
        rng=np.random.default_rng(3);l=rng.normal(size=(600,4));proj=rng.integers(0,2,600)
        months=rng.integers(2,13,600)
        P=np.c_[np.ones(600),l,l*l,(proj==0),(proj==1),np.column_stack([months==j for j in range(2,13)])]
        w,d,p=logistic(P,self.g);self.assertEqual(d['ncols'],20);self.assertLess(d['max_balance_error'],1e-6)

if __name__=='__main__':unittest.main(verbosity=2)
