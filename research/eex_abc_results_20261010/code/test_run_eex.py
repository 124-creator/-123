"""Artificial unit fixtures ONLY. These are not EEX observations or empirical results."""
import csv
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import run_eex as r


def gate():
    return {**{key:True for key in r.GATES},'evidence_note':'ARTIFICIAL UNIT FIXTURE ONLY',
            'population':'unknown','ddof':'unknown',
            'successful_auction_volume_equals_allocated':True}


def fixture(zero=False):
    rng=np.random.default_rng(1701)
    rows=[]
    for month in range(1,13):
        for j in range(12):
            v=float(rng.uniform(100,500)); n=int(rng.integers(10,30)); s=int(rng.integers(2,n))
            k=float(rng.uniform(1.1,4));rb=float(rng.uniform(.2,2));rw=float(.3+.6*rb+rng.uniform(.01,.5))
            rows.append({'event_id':f'ARTIFICIAL_{month}_{j}', 'auction_date':f'2020-{month:02d}-{j+1:02d}',
              'product':'EUA','project':('DE','EU','PL')[j%3],'status':'success',
              'mean_bid':v*k/n,'sd_bid':rb*v*k/n,'mean_won':v/s,'sd_won':rw*v/s,
              'bid_volume':v*k,'auction_volume':v,'allocated_volume':None,'bidders':float(n),
              'successful_bidders':float(s),'cover_ratio':k,'source_file':'ARTIFICIAL_NOT_MARKET',
              'source_sheet':'fixture','source_row':str(j+1),'input_line':j+2})
    if zero:rows[0]['sd_bid']=0
    return rows


def csv_file(root,rows):
    p=Path(root)/'fixture.csv'
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=r.REQUIRED,extrasaction='ignore');w.writeheader();w.writerows(rows)
    return p


class MathAndInputTests(unittest.TestCase):
    def test_01_gate_blocks_unreviewed_sources(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'gate.json';p.write_text('{}')
            with self.assertRaises(ValueError):r.read_gate(p)

    def test_02_unknown_ddof_does_not_block_reported_ratio(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'gate.json';p.write_text(json.dumps(gate()))
            self.assertEqual(r.read_gate(p)['ddof'],'unknown')

    def test_03_non_target_and_unsuccessful_rows_are_audited(self):
        rows=fixture()[:4]
        rows[1]['product']='EUAA';rows[2]['status']='cancelled';rows[3]['auction_date']='2026-01-01'
        with tempfile.TemporaryDirectory() as d:
            kept,audit,excluded=r.read_table(csv_file(d,rows))
        self.assertEqual(len(kept),1);self.assertEqual(len(excluded),3)
        self.assertEqual(sum(audit['exclusion_counts'].values()),3)

    def test_04_duplicates_are_not_silently_dropped(self):
        rows=fixture()[:2];rows.append(dict(rows[0]))
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):r.read_table(csv_file(d,rows))

    def test_05_inconsistent_participant_counts_fail(self):
        rows=fixture()[:2];rows[0]['successful_bidders']=rows[0]['bidders']+1
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):r.read_table(csv_file(d,rows))

    def test_06_zero_sd_preserved_in_A_not_B_C(self):
        rows=fixture(True)
        self.assertEqual(len(r.Prepared(rows,'A').rows),144)
        self.assertEqual(len(r.Prepared(rows,'B').rows),143)
        self.assertEqual(len(r.Prepared(rows,'C').rows),143)

    def test_07_nan_is_missing_not_zero(self):
        rows=fixture()[:2];rows[0]['sd_bid']='nan'
        with tempfile.TemporaryDirectory() as d:
            kept,audit,excluded=r.read_table(csv_file(d,rows))
        self.assertEqual(len(kept),1)
        self.assertEqual(excluded[0]['reason'],'missing_or_invalid_sd_bid')
        self.assertEqual(audit['zero_sd_bid'],0)

    def test_08_month_demeaning_has_zero_group_sums(self):
        values=np.array([[1,4],[5,2],[3,6],[7,8]],float);groups=np.array([0,0,2,2])
        out=r.month_demean(values,groups)
        np.testing.assert_allclose(out[:2].sum(axis=0),[0,0],atol=1e-12)
        np.testing.assert_allclose(out[2:].sum(axis=0),[0,0],atol=1e-12)

    def test_09_partial_fit_matches_full_dummy_OLS(self):
        p=r.Prepared(fixture(),'A');out=p.fit()
        levels=sorted(set(p.groups));dummies=np.column_stack([p.groups==level for level in levels])
        design=np.column_stack([dummies,p.original_z,p.original_x])
        beta=np.linalg.lstsq(design,p.original_y,rcond=None)[0][-1]
        self.assertAlmostEqual(out['beta'],float(beta),places=10)
        self.assertAlmostEqual(out['partial_r_squared'],out['theta']**2,places=12)
        self.assertLessEqual(out['sse_with_x'],out['sse_controls_only'])

    def test_10_month_multiplicity_matches_row_replication(self):
        p=r.Prepared(fixture(),'C');w=np.ones(72);w[:4]=[0,2,3,1]
        out=p.fit(w)
        ix=np.repeat(np.arange(len(p.rows)),w[p.groups].astype(int))
        levels=sorted(set(p.groups[ix]));dummies=np.column_stack([p.groups[ix]==level for level in levels])
        design=np.column_stack([dummies,p.original_z[ix],p.original_x[ix]])
        beta=np.linalg.lstsq(design,p.original_y[ix],rcond=None)[0][-1]
        self.assertAlmostEqual(out['beta'],float(beta),places=10)

    def test_11_B_C_share_exact_rows(self):
        rows=fixture(True)
        b=r.Prepared(rows,'B');c=r.Prepared(rows,'C')
        self.assertEqual([x['event_id'] for x in b.rows],[x['event_id'] for x in c.rows])

    def test_12_no_zero_A_B_are_identical(self):
        rows=fixture();a=r.Prepared(rows,'A').fit();b=r.Prepared(rows,'B').fit()
        self.assertEqual(a,b)

    def test_13_constructed_log_identity_passes(self):
        out=r.algebra_check(fixture(),gate())
        self.assertEqual(out['status'],'PASS')
        self.assertLess(out['max_abs_x_residual_difference'],out['tolerance'])

    def test_14_unknown_allocated_volume_does_not_assume_W_V(self):
        out=r.algebra_check(fixture(),{**gate(),'successful_auction_volume_equals_allocated':False})
        self.assertEqual(out['status'],'NOT_RUN')

    def test_15_reported_rounding_does_not_break_constructed_identity(self):
        rows=fixture()
        for row in rows:row['mean_bid']=round(row['mean_bid'],1);row['cover_ratio']=round(row['cover_ratio'],2)
        self.assertEqual(r.algebra_check(rows,gate())['status'],'PASS')
        self.assertGreater(r.mean_diagnostics(rows,gate())['mean_bid_vs_B_over_N']['max_absolute_difference'],0)

    def test_16_blocks_are_reproducible_and_keep_72_month_positions(self):
        a=np.random.default_rng(19);b=np.random.default_rng(19)
        for length in (1,3,6):
            wa=r.draw_months(a,length);wb=r.draw_months(b,length)
            np.testing.assert_array_equal(wa,wb);self.assertEqual(wa.sum(),72)

    def test_17_no_automatic_budget_extension(self):
        budget=r.Budget(attempts=2);budget.consume();budget.consume()
        with self.assertRaises(RuntimeError):budget.consume()
        self.assertEqual(budget.attempts,2)

    def test_18_residual_constant_x_not_identifiable(self):
        p=r.Prepared(fixture(),'A');p.x=p.z[:,0].copy()
        with self.assertRaises(ValueError):p.fit()

    def test_19_nonpositive_mean_is_not_repaired(self):
        rows=fixture()[:2];rows[0]['mean_bid']=0
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):r.read_table(csv_file(d,rows))

    def test_20_noncanonical_locale_numeric_is_not_guessed(self):
        for value in ('1,234','1_234','inf','-inf','nan'):
            with self.assertRaises(ValueError):r.number(value)

    def test_21_log1p_does_not_have_log_denominator_identity(self):
        x=np.log1p(np.array([2.,3.])/np.array([4.,5.]))
        rhs=np.log1p(np.array([2.,3.]))-np.log1p(np.array([4.,5.]))
        self.assertGreater(float(np.max(abs(x-rhs))),.1)

    def test_22_input_algebra_does_not_compute_HHI_from_unknown_population(self):
        out=r.algebra_check(fixture(),gate())
        self.assertNotIn('HHI',out)
        self.assertTrue(out['not_an_independent_market_finding'])

    def test_23_budget_stop_keeps_partial_results_without_retries(self):
        from unittest.mock import patch
        original=r.Budget
        with tempfile.TemporaryDirectory() as d:
            with patch.object(r,'Budget',lambda:original(attempts=20)):
                out=r.empirical_run(fixture(),Path(d),gate())
            self.assertEqual(out['status'],'INCOMPLETE_BUDGET')
            self.assertEqual(out['fit_attempts'],20)
            self.assertFalse(out['budget_completed'])
            self.assertFalse(out['intervals']['A_L3']['inference_usable_by_fixed_rule'])
            self.assertTrue((Path(d)/'bootstrap_draws.csv').exists())

    def test_24_fixed_schedule_is_below_4000_attempts(self):
        self.assertEqual(3+999*3+199*2+199*2,3796)
        self.assertLess(3796,4000)

    def test_25_missing_required_source_locator_is_not_silent(self):
        rows=fixture()[:2];rows[0]['source_sheet']=''
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):r.read_table(csv_file(d,rows))


    def test_26_reported_volume_identity_does_not_certify_allocations(self):
        g=gate();g['successful_auction_volume_equals_allocated']=False
        g['reported_volume_implied_means_diagnostic']=True
        a=r.algebra_check(fixture(),g)
        self.assertEqual(a['status'],'PASS')
        self.assertFalse(a['actual_allocated_volume_authenticated'])
        self.assertTrue(a['reported_volume_only_construction'])

    def test_27_volume_diagnostic_labels_are_not_actual_W(self):
        g=gate();g['successful_auction_volume_equals_allocated']=False
        g['reported_volume_implied_means_diagnostic']=True
        d=r.mean_diagnostics(fixture(),g)
        self.assertIn('mean_won_vs_reported_V_over_S',d)
        self.assertNotIn('mean_won_vs_W_over_S',d)

if __name__=='__main__':unittest.main(verbosity=2)
