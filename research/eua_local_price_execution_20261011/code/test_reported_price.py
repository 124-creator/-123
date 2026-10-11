"""Purely artificial fixtures: no real market effects, power or coverage claims."""
import tempfile, unittest, json
from pathlib import Path
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster
from run_official_reported_price import (fit, summary, wcr_test, number, GateError, Budget, design, frozen_files)

def fixture():
    r=np.random.default_rng(8011);g=np.repeat(np.arange(21),10);n=len(g)
    X=np.column_stack((np.ones(n),r.normal(size=(n,3))))
    y=X@np.array([1,.2,-.3,.4])+r.normal(size=21)[g]+r.normal(size=n)
    return X,y,g

class Tests(unittest.TestCase):
    def test_ols_against_lstsq(self):
        X,y,g=fixture();f=fit(X,y,g)
        np.testing.assert_allclose(f['beta'],np.linalg.lstsq(X,y,rcond=None)[0],atol=1e-12)
    def test_CR1_against_statsmodels(self):
        X,y,g=fixture();f=fit(X,y,g)
        np.testing.assert_allclose(f['cov'],cov_cluster(sm.OLS(y,X).fit(),g,use_correction=True),atol=1e-12)
    def test_residual_orthogonality(self):
        X,y,g=fixture();f=fit(X,y,g);self.assertLess(np.max(abs(X.T@f['u'])),1e-10)
    def test_focal_FRL_and_partial_R2(self):
        X,y,g=fixture();s,base,full=summary(X,y,g,['a','b','c','x'],Budget())
        rx=X[:,-1]-X[:,:-1]@np.linalg.lstsq(X[:,:-1],X[:,-1],rcond=None)[0]
        self.assertAlmostEqual(s['coefficient'],float(rx@base['u']/(rx@rx)),places=12)
        self.assertAlmostEqual(s['incremental_partial_R2'],float(np.corrcoef(rx,base['u'])[0,1]**2),places=12)
    def test_rescaling_preserves_fits(self):
        X,y,g=fixture();f=fit(X,y,g);XX=X.copy();XX[:,1]=X[:,1]*1e5+1e6
        ff=fit(XX,y,g);np.testing.assert_allclose(f['fitted'],ff['fitted'],atol=1e-10)
    def test_sign_and_percentage_unit(self):
        self.assertEqual(float(number('-0.12%'))*100,-12.0);self.assertEqual(number('−0.00%'),0)
        self.assertEqual(float(number('-0,12%',','))*100,-12.0)
    def test_missing_not_zero(self):
        for x in ('','--','NA','nan','inf'):
            with self.assertRaises((GateError,ValueError)):number(x)
    def test_malformed_number_not_guessed(self):
        with self.assertRaises(GateError):number('1,200')
    def test_rank_failure(self):
        X,y,g=fixture()
        with self.assertRaises(GateError):fit(np.column_stack((X,X[:,1])),y,g)
    def test_constant_outcome_failure(self):
        X,y,g=fixture()
        with self.assertRaises(GateError):fit(X,np.ones(len(y)),g)
    def test_one_cluster_failure(self):
        X,y,g=fixture()
        with self.assertRaises(GateError):fit(X,y,np.zeros(len(y)))
    def test_budget_stop(self):
        b=Budget(fits=1);b.tick()
        with self.assertRaises(GateError):b.tick()
    def test_WCR_null_generation_and_studentization(self):
        X,y,g=fixture();b=Budget();s,base,full=summary(X,y,g,['a','b','c','x'],b)
        test,draws,signs=wcr_test(X,y,g,base,full,b,draws=9)
        self.assertEqual(test['valid'],9);self.assertTrue(test['not_a_bootstrap_confidence_interval'])
        model0=sm.OLS(y,X[:,:-1]).fit()
        for j in range(9):
            ys=model0.fittedvalues+model0.resid*signs[j][g]
            m=sm.OLS(ys,X).fit();se=np.sqrt(cov_cluster(m,g)[-1,-1])
            self.assertAlmostEqual(draws[j]['t'],float(m.params[-1]/se),places=11)
        count=sum(abs(r['t'])>=abs(test['t_observed']) for r in draws)
        self.assertEqual(test['two_sided_plus_one_p'],(count+1)/10)
    def test_WCR_repeatability(self):
        X,y,g=fixture();b=Budget();s,ba,f=summary(X,y,g,['a','b','c','x'],b)
        t1,d1,w1=wcr_test(X,y,g,ba,f,b,draws=5)
        t2,d2,w2=wcr_test(X,y,g,ba,f,b,draws=5)
        self.assertEqual(d1,d2);np.testing.assert_array_equal(w1,w2)
    def test_subset_trade_indicator_rule(self):
        rows=[dict(year=2020+i%6,lv=1.,ln=2.,ls=1.,lr=.2,spread=.4,lp=4.,trade=0,x=.3,y=2.,quarter=str(i)) for i in range(24)]
        X,n,y,g=design(rows);self.assertNotIn('reference_last_trade',n);self.assertEqual(X.shape[1],13)
        rows[0]['trade']=1;X,n,y,g=design(rows);self.assertEqual(X.shape[1],14)
    def test_no_private_rows_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(GateError):frozen_files(Path(td))
    def test_private_hash_failure(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'official_reported_cutoff_all275.csv').write_text('dummy\nnot_market_data\n')
            with self.assertRaises(GateError):frozen_files(Path(td))

if __name__=='__main__':unittest.main(verbosity=2)
