"""Validate external reference pairs before any E2 estimation. No statistical model.
Approval flags are review records, not automated proof of source authenticity or rights.
"""
from __future__ import annotations
import argparse,csv,json,math
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

REF_FIELDS=['auction_id','reference_timestamp','reference_product','reference_maturity',
 'reference_quote_type','reference_bid_eur','reference_ask_eur','reference_source_id','reference_row_id']
CAL_FIELDS=['auction_id','bidding_close_timestamp','calendar_source_id']

def timestamp(s:str)->datetime:
    try:d=datetime.fromisoformat(str(s).replace('Z','+00:00'))
    except (ValueError,TypeError):raise ValueError('invalid_timestamp')
    if d.tzinfo is None or d.utcoffset() is None:raise ValueError('timestamp_missing_timezone')
    return d.astimezone(timezone.utc)

def number(x):
    try:y=float(x)
    except (ValueError,TypeError):raise ValueError('invalid_number')
    if not math.isfinite(y):raise ValueError('nonfinite_number')
    return y

def validate_pair(auction,reference,calendar,contract):
    if contract.get('status')!='LOCKED_AFTER_SOURCE_REVIEW':raise ValueError('source_contract_not_locked')
    allowed=contract.get('reference_sources',{})
    sid=reference['reference_source_id']
    if sid not in allowed:raise ValueError('unreviewed_reference_source')
    source=allowed[sid]
    if not source.get('lawful_access_reviewed') or not source.get('method_evidence'):
        raise ValueError('reference_rights_or_method_unreviewed')
    if not source.get('product_compatibility_reviewed'):raise ValueError('product_compatibility_unreviewed')
    if reference['reference_product']!=source.get('product') or reference['reference_maturity']!=source.get('maturity'):
        raise ValueError('reference_product_or_maturity_mismatch')
    if reference['reference_quote_type']!='midpoint' or source.get('quote_type')!='midpoint':
        raise ValueError('quote_type_not_locked_midpoint')
    if not str(reference.get('reference_row_id','')).strip():raise ValueError('reference_locator_missing')
    if calendar['calendar_source_id'] not in contract.get('calendar_sources',{}):
        raise ValueError('unreviewed_calendar_source')
    if not contract['calendar_sources'][calendar['calendar_source_id']].get('close_semantics_reviewed'):
        raise ValueError('unreviewed_bidding_close_semantics')
    if auction['auction_id']!=reference['auction_id'] or auction['auction_id']!=calendar['auction_id']:
        raise ValueError('auction_key_mismatch')
    close=timestamp(calendar['bidding_close_timestamp']);ref=timestamp(reference['reference_timestamp'])
    if close.date().isoformat()!=auction['auction_date']:raise ValueError('calendar_date_mismatch')
    age=(close-ref).total_seconds();limit=contract.get('max_quote_age_seconds')
    if not isinstance(limit,(int,float)) or isinstance(limit,bool) or not 0<=limit<=300:
        raise ValueError('staleness_rule_not_locked')
    if age<0:raise ValueError('reference_after_bidding_close')
    if age>limit:raise ValueError('stale_reference')
    bid=number(reference['reference_bid_eur']);ask=number(reference['reference_ask_eur'])
    if not 0<bid<=ask:raise ValueError('invalid_or_crossed_reference_quote')
    price=number(auction['auction_price_eur_per_tco2'])
    if price<=0:raise ValueError('invalid_auction_price')
    mean=number(auction['mu_B']);sd=number(auction['sd_B'])
    if mean<=0 or sd<0:raise ValueError('invalid_reported_bid_ratio')
    for k in ('V','N','S','R'):
        if number(auction[k])<=0:raise ValueError('invalid_control')
    lo=number(auction['minimum_bid_price_eur_per_tco2']);hi=number(auction['maximum_bid_price_eur_per_tco2'])
    if lo>hi:raise ValueError('negative_bid_price_spread')
    reference_price=(bid+ask)/2
    return {'auction_id':auction['auction_id'],'reference_midpoint_eur':reference_price,
            'reference_age_seconds':age,'price_deviation_bp':10000*(price-reference_price)/reference_price,
            'x_bid_log1p':math.log1p(sd/mean),'bid_price_spread_eur':hi-lo,
            'classification':'paired_report_outcomes_not_preauction_prediction'}

def read_csv(p:Path):
    if not p.exists():return []
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def gate(auctions,references,calendars,contract):
    def index_unique(rows,name):
        idx={}
        for r in rows:
            key=r.get('auction_id','')
            if not key or key in idx:raise ValueError('duplicate_or_empty_'+name+'_key')
            idx[key]=r
        return idx
    aidx=index_unique(auctions,'auction');ridx=index_unique(references,'reference');cidx=index_unique(calendars,'calendar')
    counts=Counter();eligible=[];excluded=[]
    for key,a in aidx.items():
        if key not in ridx:reason='missing_external_reference'
        elif key not in cidx:reason='missing_verified_calendar_close'
        else:
            try:eligible.append(validate_pair(a,ridx[key],cidx[key],contract));continue
            except (KeyError,ValueError) as e:reason=str(e)
        counts[reason]+=1;excluded.append({'auction_id':key,'reason':reason})
    unknown=(set(ridx)|set(cidx))-set(aidx)
    if unknown:raise ValueError('unmatched_external_event_keys')
    months=sorted({aidx[r['auction_id']]['auction_date'][:7] for r in eligible})
    summary={'date':'2026-10-11','auction_rows':len(auctions),'reference_rows':len(references),
      'calendar_rows':len(calendars),'eligible_pairs':len(eligible),'eligible_months':len(months),
      'excluded_reasons':dict(counts),'status':'SAMPLE_SCHEMA_PASS_ONLY' if eligible else 'HOLD_NO_ELIGIBLE_PAIR',
      'model_fits':0,'effect_estimates':None,'human_source_review_not_proven_by_software':True,
      'formal_analysis_release':'NOT_AUTHORIZED_BY_A_SCHEMA_PASS; freeze source-specific protocol first'}
    return summary,eligible,excluded
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--auctions',type=Path,required=True);p.add_argument('--references',type=Path,required=True)
    p.add_argument('--calendar',type=Path,required=True);p.add_argument('--contract',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    s,eligible,excluded=gate(read_csv(a.auctions),read_csv(a.references),read_csv(a.calendar),json.loads(a.contract.read_text()))
    (a.out/'PAIR_GATE_RESULT.json').write_text(json.dumps(s,indent=2))
    if eligible:
        with (a.out/'eligible_pairs_LOCAL_ONLY.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(eligible[0]));w.writeheader();w.writerows(eligible)
    with (a.out/'pair_exclusions_LOCAL_ONLY.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['auction_id','reason']);w.writeheader();w.writerows(excluded)
    print(json.dumps(s,indent=2))
