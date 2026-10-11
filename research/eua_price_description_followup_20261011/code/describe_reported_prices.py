"""Aggregate summaries of fixed reported-deviation samples. No regression imports or fits."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

EXPECTED={
    'strict240':('official_reported_cutoff_strict240.csv',240,154561,'7e12f25db5bb97f3b0152f264519803569edcee9914da548ff156ee7e058f4c1'),
    'noflags203':('official_reported_cutoff_noflags.csv',203,130034,'7441f31c72b220adb6fc2374d0205f510955023f9f3cb405e6660478a59c6086'),
}

def describe(values):
    values=sorted(Decimal(v) for v in values)
    if not values or any(not v.is_finite() for v in values):
        raise ValueError('An empty/non-finite observation is not a reported zero')
    n=len(values)
    def quantile(p):
        position=Decimal(n-1)*Decimal(p)
        lower=int(position);upper=min(lower+1,n-1);fraction=position-lower
        return values[lower]+fraction*(values[upper]-values[lower])
    mean=sum(values,Decimal(0))/Decimal(n)
    variance=sum(((v-mean)**2 for v in values),Decimal(0))/Decimal(n-1) if n>1 else None
    negative=sum(v<0 for v in values);positive=sum(v>0 for v in values);zero=sum(v==0 for v in values)
    if negative+positive+zero!=n:raise ValueError('Sign partition does not cover sample')
    return dict(n=n,mean=float(mean),median=float(quantile('.5')),q25=float(quantile('.25')),
                q75=float(quantile('.75')),minimum=float(values[0]),maximum=float(values[-1]),
                sample_sd=None if variance is None else float(variance.sqrt()),
                negative_count=negative,positive_count=positive,reported_zero_count=zero,
                negative_share=negative/n,positive_share=positive/n,reported_zero_share=zero/n)

def fixed_rows(root, tag):
    name,n,size,sha=EXPECTED[tag];p=root/'data'/name
    if not p.resolve().is_relative_to(root.resolve()):raise ValueError('Input leaves private root')
    body=p.read_bytes()
    if len(body)!=size or hashlib.sha256(body).hexdigest()!=sha:raise ValueError('Frozen input changed')
    reader=csv.DictReader(io.StringIO(body.decode('utf-8-sig'),newline=''))
    if not reader.fieldnames or len(set(reader.fieldnames))!=len(reader.fieldnames):raise ValueError('Invalid headers')
    rows=list(reader)
    if len(rows)!=n or any(None in r or None in r.values() for r in rows):raise ValueError('Unexpected row count/schema')
    if len({r['auction_date'] for r in rows})!=n:raise ValueError('Duplicate date')
    return rows,{'file':name,'rows':n,'bytes':size,'sha256':sha}

def build(root):
    strict,a=fixed_rows(root,'strict240');noflags,b=fixed_rows(root,'noflags203')
    index={r['auction_date']:r for r in strict}
    if any(r['auction_date'] not in index or r!=index[r['auction_date']] for r in noflags):
        raise ValueError('No-flags sample is not an unchanged strict subset')
    best=[r for r in strict if r['reference_event_type']=='last_best_bid']
    if len(best)!=236:raise ValueError('Best-bid count changed')
    table=[]
    for group,rows in [('primary240',strict),('noflags203',noflags),('bestbid236',best)]:
        quarters=len({r['auction_date'][:4]+'Q'+str((int(r['auction_date'][5:7])-1)//3+1) for r in rows})
        values=[Decimal(r['reported_deviation_percent_signed'])*100 for r in rows]
        for outcome,vector in [('signed_bp',values),('absolute_bp',[abs(v) for v in values])]:
            table.append({'sample':group,'outcome':outcome,'quarters':quarters,**describe(vector)})
    return table,{'recorded_after_aggregation':datetime.now(timezone.utc).isoformat(),'inputs':[a,b],
                 'quantiles':'Linear interpolation, type 7: position=(n-1)*p',
                 'standard_deviation':'Sample SD, denominator n-1',
                 'sign_shares':'Fractions, not percentage numbers; computed on the displayed outcome',
                 'unit':'Basis points = 100 times reported signed numeric percentage points',
                 'zero_definition':'Reported percentage equals numeric zero at source precision, including signed zero; not a certified exact market equality or no-trade state',
                 'scope':'Three previously fixed sample sets, signed and absolute descriptions; no new exclusion or model',
                 'new_market_fits':0,'table_rows':len(table)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-root',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();table,receipt=build(args.private_root)
    args.out.mkdir(parents=True,exist_ok=False)
    (args.out/'DESCRIPTIVES.json').write_text(json.dumps({'metadata':receipt,'table':table},indent=2)+'\n',encoding='utf-8')
    with (args.out/'DESCRIPTIVES.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
