"""Artificial implementation checks only; never market evidence."""
import unittest
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch
import run_official_reported_price as model
import audit_auction_prices as audit
import numpy as np
from scipy.stats import t as student_t

def diagnostic_rows():
    rng=np.random.default_rng(1209)
    rows=[]
    for year in range(2020,2026):
        for quarter in range(1,5):
            for j in range(8):
                z=rng.normal(size=7)
                rows.append(dict(year=year,quarter=f'{year}Q{quarter}',lv=z[0],ln=z[1],ls=z[2],lr=z[3],spread=z[4],lp=z[5],x=z[6],trade=int(j%5==0),y=float(.6*z[6]+rng.normal())))
    return rows

class BridgeTests(unittest.TestCase):
    def test_incomplete_wcr_is_nonzero_exit(self):
        self.assertEqual(model.completion_exit_code('COMPLETED_EXPLORATORY'),0)
        self.assertNotEqual(model.completion_exit_code('COMPLETED_WITH_INCOMPLETE_WCR'),0)

    def test_manifest_requires_all_consumed_paths_once(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);body=b'a\n1\n';(root/'one.csv').write_bytes(body)
            entry={'path':'one.csv','bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
            self.assertEqual(audit.manifest_buffers(root,[entry],{'one.csv'})['one.csv'],body)
            for records,required in [([],{'one.csv'}),([entry,entry],{'one.csv'}),([entry],{'other.csv'})]:
                with self.assertRaises(ValueError):audit.manifest_buffers(root,records,required)

    def test_candidate_quantities_and_duplicate_keys_rejected(self):
        cells={c+'7':{'formula':False,'value':'1'} for c in audit.OLD.values()}
        cells.update({'B7':{'formula':False,'value':'43840'},'E7':{'formula':False,'value':'T3PA'},'Z7':{'formula':False,'value':'DE'},'F7':{'formula':False,'value':'successful'}})
        row={k:'1' for k in audit.OLD}
        row.update(file='example.xlsx',row='7',date='2020-01-10',contract_raw='T3PA',venue_raw='DE',status_raw='successful',sheet='Primary Market Auction')
        audit.verify_candidate_rows([row],{'example.xlsx':cells})
        changed=dict(row,sd_B='2')
        for rows in [[row,row],[changed]]:
            with self.assertRaises(ValueError):audit.verify_candidate_rows(rows,{'example.xlsx':cells})

    def test_actual_csv_checks_bid_volume_not_nonexistent_cover_column(self):
        self.assertEqual(model.QUANTITIES, ('V','B','N','S','mu_B','sd_B','mu_W','sd_W'))

    def test_verified_csv_uses_one_read_and_exact_length(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'sample.csv';body=b'a,b\n1,2\n';p.write_bytes(body)
            original=Path.read_bytes
            calls=[]
            def tracked(path):
                calls.append(path)
                return original(path)
            with patch.object(Path,'read_bytes',tracked):
                rows,headers=model.read_csv(p,expected_sha=hashlib.sha256(body).hexdigest(),expected_bytes=len(body))
            self.assertEqual(rows,[{'a':'1','b':'2'}]);self.assertEqual(headers,['a','b'])
            self.assertEqual(len(calls),1)
            with self.assertRaises(model.GateError):
                model.read_csv(p,expected_sha=hashlib.sha256(body).hexdigest(),expected_bytes=len(body)+1)

    def test_short_csv_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'sample.csv';p.write_text('a,b\n1\n',encoding='utf-8')
            with self.assertRaises(model.GateError):model.read_csv(p)

    def test_leave_year_design_rebases_fixed_effects(self):
        rows=diagnostic_rows()
        for omitted in range(2020,2026):
            sub=[r for r in rows if r['year']!=omitted]
            X,names,y,g=model.design(sub)
            self.assertEqual(np.linalg.matrix_rank(X),X.shape[1])
            self.assertNotIn(f'year_{omitted}',names)
            self.assertIn('log_auction_price',names)

    def test_delete_quarter_jackknife_matches_independent_ols(self):
        rows=diagnostic_rows();budget=model.Budget()
        X,names,y,g=model.design(rows);full=model.fit(X,y,g,budget)
        got=model.deletion_diagnostics(rows,full,budget)
        values=[]
        for q in sorted(set(g)):
            XX,_,yy,_=model.design([r for r in rows if r['quarter']!=q])
            values.append(np.linalg.lstsq(XX,yy,rcond=None)[0][-1])
        values=np.array(values);G=len(values)
        se=np.sqrt((G-1)/G*np.sum((values-values.mean())**2))
        self.assertAlmostEqual(got['quarter_jackknife']['standard_error'],se,places=11)
        np.testing.assert_allclose(got['quarter_jackknife']['CI95'],full['beta'][-1]+student_t.ppf(.975,G-1)*se*np.array([-1,1]),atol=1e-10)
        self.assertEqual(len(got['leave_year_out']),6)
        self.assertEqual(budget.fits,1+G+6)

    def test_iqr_contrast_distinguishes_observed_and_partial_scales(self):
        X,names,y,g=model.design(diagnostic_rows())
        result,_,_=model.summary(X,y,g,names,model.Budget())
        raw=float(np.diff(np.quantile(X[:,-1],[.25,.75]))[0])
        self.assertAlmostEqual(result['IQR_observed_bid_dispersion'],raw)
        self.assertAlmostEqual(result['observed_IQR_gap_bps'],raw*result['coefficient'])
        self.assertIn('IQR_residualized_bid_dispersion',result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
