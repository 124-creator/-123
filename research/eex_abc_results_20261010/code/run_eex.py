#!/usr/bin/env python3
"""Fixed A/B/C reported-dispersion analysis. No downloads or model deserialization.

Real data are required. The test suite uses artificial fixtures in a separate file.
A current, documented field/source review is required via --gate.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
from typing import Any

import numpy as np
import scipy
from scipy.linalg import lstsq

BASE_COMMIT = '5745eb3ddca79602346053446583d794b0e09800'
START, END = '2020-01-01', '2025-12-31'
PROJECTS = ('EU', 'DE', 'PL')
REQUIRED = ('event_id','auction_date','product','project','status',
            'mean_bid','sd_bid','mean_won','sd_won','bid_volume',
            'auction_volume','bidders','successful_bidders','cover_ratio',
            'source_file','source_sheet','source_row')
NUMERIC = ('mean_bid','sd_bid','mean_won','sd_won','bid_volume',
           'auction_volume','bidders','successful_bidders','cover_ratio')
POSITIVE = ('mean_bid','mean_won','bid_volume','auction_volume',
            'bidders','successful_bidders','cover_ratio')
MISSING = {'', '--', '—', 'NA', 'N/A', 'null', 'None'}
GATES = ('source_identity_checked','field_units_mapping_checked',
         'success_status_mapping_checked','auction_volume_semantics_checked',
         'reported_ratio_interpretation_accepted')


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               allow_nan=False), encoding='utf-8')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_gate(path: Path) -> dict:
    gate = json.loads(path.read_text(encoding='utf-8'))
    unresolved = [key for key in GATES if gate.get(key) is not True]
    if unresolved:
        raise ValueError('Source/field review incomplete: ' + ', '.join(unresolved))
    if not isinstance(gate.get('evidence_note'), str) or not gate['evidence_note'].strip():
        raise ValueError('gate.evidence_note must identify the actual review evidence')
    # Unknown populations/ddof deliberately do NOT block reported-field ratios.
    return gate


def number(value: str) -> float:
    text = value.strip()
    if text in MISSING:
        raise ValueError('missing')
    # Input is a normalized CSV, so locale separators must be resolved explicitly.
    if ',' in text or '_' in text:
        raise ValueError('noncanonical_numeric_format')
    result = float(text)
    if not math.isfinite(result):
        raise ValueError('nonfinite')
    return result


def read_table(path: Path) -> tuple[list[dict], dict, list[dict]]:
    rows, exclusions = [], []
    seen = set()
    input_n = 0
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(REQUIRED) <= set(reader.fieldnames):
            raise ValueError('Missing CSV columns: ' + ', '.join(sorted(set(REQUIRED)-set(reader.fieldnames or []))))
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('Duplicate CSV column names')
        for line, raw in enumerate(reader, 2):
            input_n += 1
            if None in raw or any(raw.get(k) is None for k in REQUIRED):
                raise ValueError(f'Malformed CSV row at line {line}')
            event = raw['event_id'].strip()
            date = raw['auction_date'].strip()
            try:
                parsed = dt.date.fromisoformat(date)
            except ValueError as exc:
                raise ValueError(f'Invalid date at line {line}') from exc
            if parsed.isoformat() != date:
                raise ValueError(f'Noncanonical ISO date at line {line}')
            product, project, status = (raw[k].strip() for k in ('product','project','status'))
            key = (date, product, project, event)
            if key in seen:
                raise ValueError(f'Duplicate event key at line {line}; no silent deduplication')
            seen.add(key)
            reason = None
            if date < START or date > END:
                reason = 'outside_2020_2025'
            elif product != 'EUA':
                reason = 'not_EUA'
            elif project not in PROJECTS:
                reason = 'not_EU_DE_PL_project'
            elif status != 'success':
                reason = 'not_mapped_successful_auction'
            else:
                if not event or any(not raw[k].strip() for k in ('source_file','source_sheet','source_row')):
                    raise ValueError(f'Incomplete source locator at line {line}')
                row = {k: raw[k].strip() for k in REQUIRED if k not in NUMERIC}
                for key_n in NUMERIC:
                    try:
                        row[key_n] = number(raw[key_n])
                    except (ValueError, OverflowError):
                        reason = 'missing_or_invalid_' + key_n
                        break
                if reason is None:
                    if any(row[k] <= 0 for k in POSITIVE):
                        raise ValueError(f'Nonpositive required field at line {line}; resolve source semantics')
                    if row['sd_bid'] < 0 or row['sd_won'] < 0:
                        raise ValueError(f'Negative SD at line {line}')
                    if any(row[k] != int(row[k]) for k in ('bidders','successful_bidders')):
                        raise ValueError(f'Noninteger participant count at line {line}')
                    if row['successful_bidders'] > row['bidders']:
                        raise ValueError(f'Successful count exceeds total at line {line}')
                    row['input_line'] = line
                    text_w = raw.get('allocated_volume', '').strip()
                    row['allocated_volume'] = None if text_w in MISSING else number(text_w)
                    if row['allocated_volume'] is not None and row['allocated_volume'] <= 0:
                        raise ValueError(f'Nonpositive allocated volume at line {line}')
                    rows.append(row)
            if reason:
                exclusions.append({'input_line': line, 'event_id': event, 'reason': reason})
    rows.sort(key=lambda r: (r['auction_date'], r['project'], r['event_id']))
    if not rows:
        raise ValueError('No eligible real auction rows; do not reconstruct data from summary coefficients')
    reason_counts: dict[str,int] = {}
    for item in exclusions:
        reason_counts[item['reason']] = reason_counts.get(item['reason'], 0) + 1
    audit = {'input_rows': input_n, 'A_rows': len(rows),
             'B_C_rows': sum(r['sd_bid'] > 0 and r['sd_won'] > 0 for r in rows),
             'zero_sd_bid': sum(r['sd_bid'] == 0 for r in rows),
             'zero_sd_won': sum(r['sd_won'] == 0 for r in rows),
             'exclusion_counts': reason_counts,
             'months_present': len({r['auction_date'][:7] for r in rows}),
             'project_counts': {p: sum(r['project']==p for r in rows) for p in PROJECTS},
             'year_counts': {str(y): sum(r['auction_date'].startswith(str(y)) for r in rows) for y in range(2020,2026)},
             'date_min': rows[0]['auction_date'], 'date_max': rows[-1]['auction_date'],
             'not_forced_to_match_1281': True,
             'not_independent_sample_size': True}
    return rows, audit, exclusions


def month_index(date: str) -> int:
    return (int(date[:4])-2020)*12+int(date[5:7])-1


def month_demean(values: np.ndarray, groups: np.ndarray, m: int = 72) -> np.ndarray:
    values = np.asarray(values, float)
    was_vector = values.ndim == 1
    mat = values[:,None] if was_vector else values
    sums = np.zeros((m, mat.shape[1]))
    np.add.at(sums, groups, mat)
    counts = np.bincount(groups, minlength=m)
    means = sums / np.maximum(counts[:,None], 1)
    out = mat-means[groups]
    return out[:,0] if was_vector else out


def project_out(z: np.ndarray, targets: np.ndarray) -> tuple[np.ndarray,int,np.ndarray,float]:
    # Column scaling does not change an unpenalized projection or estimand.
    scale = np.linalg.norm(z, axis=0)
    active = scale > 0
    if not active.any():
        return targets.copy(), 0, np.array([]), 0.0
    zs = z[:,active]/scale[active]
    coef, _, rank, singular = lstsq(zs, targets, cond=None, lapack_driver='gelsd')
    residuals = targets-zs@coef
    condition = float(singular[0]/singular[-1]) if len(singular) and singular[-1]>0 else None
    if condition is not None and not math.isfinite(condition):
        condition = None
    return residuals, int(rank), singular, condition


class Prepared:
    def __init__(self, rows: list[dict], spec: str, *, constructed: bool=False, gate: dict|None=None):
        if spec not in ('A','B','C'):
            raise ValueError('Only A/B/C are allowed')
        self.spec = spec
        self.rows = rows if spec=='A' else [r for r in rows if r['sd_bid']>0 and r['sd_won']>0]
        if not self.rows:
            raise ValueError('Empty eligible specification')
        self.groups = np.array([month_index(r['auction_date']) for r in self.rows], dtype=int)
        self.projects = sorted({r['project'] for r in self.rows})
        k = np.array([r['cover_ratio'] for r in self.rows])
        v = np.array([r['auction_volume'] for r in self.rows])
        n = np.array([r['bidders'] for r in self.rows])
        s = np.array([r['successful_bidders'] for r in self.rows])
        mb = np.array([r['mean_bid'] for r in self.rows])
        mw = np.array([r['mean_won'] for r in self.rows])
        sb = np.array([r['sd_bid'] for r in self.rows])
        sw = np.array([r['sd_won'] for r in self.rows])
        if constructed:
            if gate is None:
                raise ValueError('Allocated-volume semantics require gate evidence')
            volumes=[]
            for r in self.rows:
                if r['allocated_volume'] is not None and gate.get('allocated_volume_is_actual') is True:
                    volumes.append(r['allocated_volume'])
                elif gate.get('successful_auction_volume_equals_allocated') is True:
                    volumes.append(r['auction_volume'])
                elif gate.get('reported_volume_implied_means_diagnostic') is True:
                    # Pure identity using constructed means; NOT certification of V=W.
                    volumes.append(r['auction_volume'])
                else:
                    raise ValueError('Actual allocated W unavailable/unverified; algebra check cannot assume W=V')
            v=np.array(volumes); b=np.array([r['bid_volume'] for r in self.rows])
            k=b/v; mb=b/n; mw=v/s
        rb,rw=sb/mb,sw/mw
        fn=np.log1p if spec in ('A','B') else np.log
        x,y=fn(rb),fn(rw)
        z=np.column_stack([np.log(k),np.log(v),np.log(n),np.log(s)] +
                          [np.array([float(r['project']==p) for r in self.rows]) for p in self.projects[1:]])
        if not np.isfinite(np.column_stack([x,y,z])).all():
            raise ValueError('Nonfinite transformed data')
        self.original_x, self.original_y, self.original_z = x,y,z
        self.x=month_demean(x,self.groups)
        self.y=month_demean(y,self.groups)
        self.z=month_demean(z,self.groups)

    def fit(self, weights: np.ndarray|None=None) -> dict:
        if weights is None:
            weights=np.ones(72)
        weights=np.asarray(weights,float)
        if weights.shape!=(72,) or (weights<0).any() or not np.isfinite(weights).all():
            raise ValueError('Expected 72 nonnegative month multiplicities')
        obs_w=weights[self.groups]
        present=obs_w>0
        if present.sum()<3:
            raise ValueError('insufficient_resampled_observations')
        root=np.sqrt(obs_w[present])
        zz=self.z[present]*root[:,None]
        targets=np.column_stack([self.x[present],self.y[present]])*root[:,None]
        resid,rank,sv,cond=project_out(zz,targets)
        rx,ry=resid[:,0],resid[:,1]
        sx,sy=float(rx@rx),float(ry@ry)
        tol=100*np.finfo(float).eps
        if sx<=tol*max(1.0,float(targets[:,0]@targets[:,0])):
            raise ValueError('x_not_identifiable_after_controls')
        if sy<=tol*max(1.0,float(targets[:,1]@targets[:,1])):
            raise ValueError('y_has_no_residual_variation')
        beta=float(rx@ry/sx)
        theta=float((rx@ry)/np.sqrt(sx*sy))
        if abs(theta)>1+1e-10:
            raise ValueError('invalid_partial_correlation')
        month_count=len(np.unique(self.groups[present]))
        weighted_n=int(round(float(obs_w.sum())))
        full_rank=month_count+rank+1
        return {'beta':beta,'theta':theta,'partial_r_squared':theta**2,
                'n_weighted':weighted_n,'n_distinct_rows':int(present.sum()),
                'months_present':month_count,'nuisance_within_rank':rank,
                'nuisance_within_columns':int(zz.shape[1]),
                'full_design_rank':full_rank,'residual_df':weighted_n-full_rank,
                'within_control_condition_scaled':cond,
                'nuisance_rank_deficient':rank<int(np.count_nonzero(np.linalg.norm(zz,axis=0)>0)),
                'sse_controls_only':sy,'sse_with_x':float((ry-beta*rx)@(ry-beta*rx))}


def draw_months(rng: np.random.Generator, length: int, m: int=72) -> np.ndarray:
    if not 1<=length<=m:
        raise ValueError('Invalid block length')
    starts=rng.integers(0,m-length+1,size=math.ceil(m/length))
    sampled=np.concatenate([np.arange(start,start+length) for start in starts])[:m]
    return np.bincount(sampled,minlength=m)


def algebra_check(rows: list[dict], gate: dict) -> dict:
    try:
        p=Prepared(rows,'C',constructed=True,gate=gate)
    except ValueError as exc:
        return {'status':'NOT_RUN','reason':str(exc),'not_a_fourth_empirical_specification':True}
    sb=np.log([r['sd_bid'] for r in p.rows]); sw=np.log([r['sd_won'] for r in p.rows])
    target=np.column_stack([p.x,p.y,month_demean(sb,p.groups),month_demean(sw,p.groups)])
    residuals,_,_,_=project_out(p.z,target)
    dx=float(np.max(abs(residuals[:,0]-residuals[:,2])))
    dy=float(np.max(abs(residuals[:,1]-residuals[:,3])))
    err_scale=max(1.0,float(np.max(abs(target))))
    threshold=1e-9*err_scale
    return {'status':'PASS' if max(dx,dy)<=threshold else 'FAIL',
            'rows':len(p.rows),'max_abs_x_residual_difference':dx,
            'max_abs_y_residual_difference':dy,'tolerance':threshold,
            'constructed_inputs_used':True,'reported_rounded_fields_not_overwritten':True,
            'reported_volume_only_construction':gate.get('reported_volume_implied_means_diagnostic') is True,
            'actual_allocated_volume_authenticated':gate.get('successful_auction_volume_equals_allocated') is True,
            'not_an_independent_market_finding':True}


def mean_diagnostics(rows: list[dict], gate: dict) -> dict:
    bid_diff=[r['mean_bid']-r['bid_volume']/r['bidders'] for r in rows]
    wdiff=[];kdiff=[]
    for r in rows:
        w=(r['allocated_volume'] if r['allocated_volume'] is not None and gate.get('allocated_volume_is_actual') is True
           else r['auction_volume'] if (gate.get('successful_auction_volume_equals_allocated') is True or gate.get('reported_volume_implied_means_diagnostic') is True) else None)
        if w is not None:
            wdiff.append(r['mean_won']-w/r['successful_bidders'])
            kdiff.append(r['cover_ratio']-r['bid_volume']/w)
    def stats(values):
        if not values:return {'n':0,'status':'actual_allocated_W_unverified'}
        a=np.abs(values)
        return {'n':len(values),'max_absolute_difference':float(a.max()),
                'median_absolute_difference':float(np.median(a)),
                'p95_absolute_difference':float(np.quantile(a,.95,method='linear'))}
    return {'mean_bid_vs_B_over_N':stats(bid_diff),'mean_won_vs_reported_V_over_S':stats(wdiff),
            'reported_cover_vs_B_over_reported_V':stats(kdiff),
            'scope':'Numerical differences only; no automatic population/ddof/rounding authentication'}


class Budget:
    def __init__(self, seconds=1800.0, attempts=4000):
        self.start=time.monotonic();self.seconds=seconds;self.limit=attempts;self.attempts=0
    def consume(self):
        if self.attempts>=self.limit:raise RuntimeError('fit_attempt_budget_exhausted')
        if time.monotonic()-self.start>=self.seconds:raise RuntimeError('time_budget_exhausted')
        self.attempts+=1


def empirical_run(rows: list[dict], out: Path, gate: dict, seed=20261010) -> dict:
    prepared={key:Prepared(rows,key) for key in ('A','B','C')}
    budget=Budget()
    result={'analysis':'post_exploration_supplement_not_preregistered',
            'models_trained_for_price_forecasting':0,'point_estimates_independently_recomputed_from_raw_derived_input':True,
            'base_commit':BASE_COMMIT,'seed':seed,'points':{},'intervals':{},'fit_failures':[],
            'calendar_months':72,'estimated_effect_is_conditional_not_causal':True,
            'bootstrap':'noncircular overlapping moving month blocks, original month FE labels retained',
            'inference_limit':'Approximate dependent-data inference; does not correct prior specification/target selection.',
            'minimum_abs_theta_proposal':0.10,'threshold_is_post_exploration_design':True}
    draws=[];plans={};budget_error=None
    schedule=((3,999,('A','B','C')),(1,199,('A','C')),(6,199,('A','C')))
    try:
        for key,p in prepared.items():
            budget.consume();result['points'][key]=p.fit()
        for length,count,keys in schedule:
            rng=np.random.default_rng(np.random.SeedSequence([seed,length]))
            weights_list=[draw_months(rng,length) for _ in range(count)]
            plans[str(length)]=[w.tolist() for w in weights_list]
            for draw,weights in enumerate(weights_list):
                for key in keys:
                    budget.consume()
                    try:
                        fit=prepared[key].fit(weights)
                        draws.append({'block_months':length,'draw':draw,'spec':key,
                                      'beta':fit['beta'],'theta':fit['theta'],
                                      'status':'OK','nuisance_rank_deficient':fit['nuisance_rank_deficient']})
                    except (ValueError, np.linalg.LinAlgError) as exc:
                        failure={'block_months':length,'draw':draw,'spec':key,'error':str(exc)}
                        result['fit_failures'].append(failure)
                        draws.append({'block_months':length,'draw':draw,'spec':key,
                                      'beta':None,'theta':None,'status':'FAILED',
                                      'nuisance_rank_deficient':None})
            # Keep a bounded progress checkpoint, with no raw auction values.
            write_json(out/'progress.json',{'fit_attempts':budget.attempts,
                         'block_months_completed':length,'failures':len(result['fit_failures'])})
    except RuntimeError as exc:
        budget_error=str(exc)
    for length,count,keys in schedule:
        for key in keys:
            attempted=[d for d in draws if d['block_months']==length and d['spec']==key]
            records=[d for d in attempted if d['status']=='OK']
            item={'planned':count,'attempted':len(attempted),'valid':len(records),
                  'failed':len(attempted)-len(records),'not_attempted':count-len(attempted),
                  'inference_usable_by_fixed_rule':len(attempted)==count and len(records)>=math.ceil(.95*count)}
            for metric in ('beta','theta'):
                values=[d[metric] for d in records]
                item[metric+'_percentile_95']=[float(v) for v in np.quantile(values,[.025,.975],method='linear')] if values else None
            bounds=item['theta_percentile_95']
            if not item['inference_usable_by_fixed_rule']:
                item['theta_size_diagnostic']='not_interpretable_incomplete_or_excess_failures'
            elif bounds[0]>.10:
                item['theta_size_diagnostic']='positive_beyond_post_exploration_size_threshold'
            elif bounds[1]<-.10:
                item['theta_size_diagnostic']='negative_beyond_post_exploration_size_threshold'
            elif bounds[0]>=-.10 and bounds[1]<=.10:
                item['theta_size_diagnostic']='within_post_exploration_weak_association_band'
            else:
                item['theta_size_diagnostic']='inconclusive_about_size_threshold'
            result['intervals'][f'{key}_L{length}']=item
    result['fit_attempts']=budget.attempts
    result['regression_bootstrap_seconds']=time.monotonic()-budget.start
    result['requested_fit_attempts']=3796
    result['budget_completed']=budget.attempts==3796
    result['algebra']=algebra_check(rows,gate)
    result['rounding_diagnostics']=mean_diagnostics(rows,gate)
    result['status']=('INCOMPLETE_BUDGET' if budget_error else 'BLOCKED_ALGEBRA_FAILURE'
                      if result['algebra']['status']=='FAIL' else 'COMPLETED')
    result['budget_error']=budget_error
    # No row-level original prices or individual bidder data are written here.
    write_json(out/'bootstrap_month_multiplicities.json',plans)
    with (out/'bootstrap_draws.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['block_months','draw','spec','beta','theta','status','nuisance_rank_deficient'])
        writer.writeheader();writer.writerows(draws)
    return result


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,required=True,help='Normalized, sourced auction-level CSV; not a summary')
    parser.add_argument('--gate',type=Path,required=True,help='Documented field/source review JSON')
    parser.add_argument('--out',type=Path,required=True,help='New output directory, never overwritten')
    parser.add_argument('--audit-only',action='store_true',help='Check data and algebra, fit no regressions')
    args=parser.parse_args()
    if args.out.exists():
        parser.error('Output already exists; choose a new directory')
    args.out.mkdir(parents=True)
    receipt={'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'base_commit':BASE_COMMIT,
             'script_sha256':sha(Path(__file__)),'input_name':args.data.name,
             'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
             'real_regression_run_started':False,'audit_only':args.audit_only,
             'old_model_files_read':False,'other_models_invoked':False,'data_republished':False}
    try:
        gate=read_gate(args.gate)
        receipt['gate_sha256']=sha(args.gate)
        receipt['input_sha256']=sha(args.data)
        rows,audit,excluded=read_table(args.data)
        write_json(args.out/'sample_audit.json',audit)
        private=args.out/'private';private.mkdir()
        write_json(private/'exclusion_log.json',excluded)
        algebra=algebra_check(rows,gate)
        write_json(args.out/'algebra_check.json',algebra)
        if algebra['status']=='FAIL':
            raise ValueError('Constructed algebra negative control failed; no empirical fits allowed')
        if args.audit_only:
            receipt['status']='AUDIT_ONLY_NO_REGRESSION'
        else:
            receipt['real_regression_run_started']=True
            results=empirical_run(rows,args.out,gate)
            write_json(args.out/'results.json',results)
            receipt['status']=results['status']
    except Exception as exc:
        receipt['status']='BLOCKED_OR_INCOMPLETE'
        receipt['error_type']=type(exc).__name__
        receipt['error']=str(exc)
        print(f"BLOCKED: {exc}",file=sys.stderr)
        returncode=2
    else:returncode=0
    receipt['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    write_json(args.out/'execution_receipt.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False))
    return returncode

if __name__=='__main__':
    raise SystemExit(main())
