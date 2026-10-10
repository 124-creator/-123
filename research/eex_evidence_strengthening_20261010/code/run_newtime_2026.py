"""One fixed Jan–Sep 2026 association check; original bytes stay off the repository."""
from __future__ import annotations
import argparse,collections,json,math,zipfile
from datetime import datetime,timedelta,timezone
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from run_strengthening import xlsx_cells,FIELDS,EXPECTED_HEADERS,projection,draw_months,dump,sha,write_csv

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    status={'retrieved_utc':datetime.now(timezone.utc).isoformat(),'period':'2026-01-01 through 2026-09-30',
    'classification':'new-time descriptive re-estimation, not untouched holdout or model forecast',
    'raw_republished':False,'fits':0,'source_url':'https://public.eex-group.com/eex/eua-auction-report/emission-spot-primary-market-auction-report-2026-data.xlsx'}
    try:
        status.update(input_sha256=sha(args.input),input_bytes=args.input.stat().st_size)
        with zipfile.ZipFile(args.input) as z:
            book=ET.fromstring(z.read('xl/workbook.xml'));ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            prop=book.find('s:workbookPr',ns)
            if prop is not None and prop.attrib.get('date1904','0') in ('1','true'):raise ValueError('Unsupported 1904 date system')
        sheets=xlsx_cells(args.input)
        if 'Primary Market Auction' not in sheets:raise ValueError('Sheet schema changed')
        cells=sheets['Primary Market Auction'];headers={k:cells.get(c+'6') for k,c in FIELDS.items()}
        status['headers']=headers
        if headers!=EXPECTED_HEADERS:raise ValueError('Required literal header mismatch')
        rows=[];excluded=collections.Counter();contracts=collections.Counter();dates=[];source_rows=[];candidates=[]
        rownums=sorted({int(c[1:]) for c in cells if c.startswith('B') and c[1:].isdigit() and int(c[1:])>=7})
        for row in rownums:
            serial=cells.get('B'+str(row))
            if not isinstance(serial,(int,float)) or not 42000<serial<60000:continue
            day=(datetime(1899,12,30)+timedelta(days=int(serial))).date();dates.append(str(day))
            product=cells.get('E'+str(row));venue=cells.get('Z'+str(row));s=cells.get('F'+str(row));contracts[str(product)]+=1
            reason=None
            if day.year!=2026 or day.month>9:reason='outside_fixed_Jan_Sep_2026'
            elif product!='T3PA':reason='outside_frozen_product_code'
            elif venue not in ('EU','DE','PL'):reason='outside_frozen_series'
            elif s!='successful':reason='not_explicit_successful'
            if reason:excluded[reason]+=1;continue
            vals={k:cells.get(col+str(row)) for k,col in FIELDS.items()}
            for k in ('V','B','N','S','R','mu_B','mu_W','sd_B','sd_W'):
                if not isinstance(vals[k],(int,float)) or not math.isfinite(vals[k]) or vals[k]<=0:
                    raise ValueError('Invalid numeric eligible observation; no silent deletion')
            if vals['S']>vals['N']:raise ValueError('Invalid bidder counts')
            rows.append((str(day),venue,vals));source_rows.append(row)
        rows.sort(key=lambda r:(r[0],r[1]));n=len(rows)
        if n<60:raise ValueError('Fewer than 60 eligible observations; insufficient gate')
        if len({r[0] for r in rows})!=n:raise ValueError('Duplicate dates')
        month=np.array([int(r[0][5:7])-1 for r in rows]);unique=np.unique(month)
        if len(unique)!=9:raise ValueError('Not all nine fixed calendar months represented')
        logs=np.array([[math.log(r[2][k]) for k in ('V','N','S','R')] for r in rows])
        Z=np.c_[logs,[[float(r[1]=='DE'),float(r[1]=='PL')] for r in rows]]
        ratio=np.array([[r[2]['sd_B']/r[2]['mu_B'],r[2]['sd_W']/r[2]['mu_W']] for r in rows])
        Y={'A':np.log1p(ratio),'C':np.log(ratio)};points={}
        for spec in ('A','C'):
            status['fits']+=1;points[spec]=projection(Y[spec],Z,month,np.ones(n))
        status.update(status='COMPLETED_WITH_SHORT_TIME_AXIS_LIMITATION',dated_rows=len(dates),eligible_n=n,
           earliest_source=min(dates),latest_source=max(dates),cutoff='2026-09-30',
           first_eligible=rows[0][0],last_eligible=rows[-1][0],exclusions=dict(excluded),product_counts=dict(contracts),
           month_counts=dict(collections.Counter(r[0][:7] for r in rows)),series_counts=dict(collections.Counter(r[1] for r in rows)),
           repeated_date_count=0,points=points)
        draws=[];failed=[];indices=[];rng=np.random.default_rng(np.random.SeedSequence([20261010,3,2026]))
        for b in range(999):
            idx=draw_months(rng,3,9);indices.append(idx.tolist());w=np.bincount(idx,minlength=9)[month].astype(float)
            for spec in ('A','C'):
                status['fits']+=1
                try:
                    est=projection(Y[spec],Z,month,w);draws.append({'draw':b,'spec':spec,**est})
                except (ValueError,np.linalg.LinAlgError) as exc:failed.append({'draw':b,'spec':spec,'error':str(exc)})
        intervals={}
        for spec in ('A','C'):
            rr=[r for r in draws if r['spec']==spec]
            intervals[spec]={'valid':len(rr),'planned':999}
            for metric in ('theta','beta'):
                intervals[spec][metric+'_CI95']=np.quantile([r[metric] for r in rr],[.025,.975]).tolist()
        status['intervals']=intervals;status['failed_draws']=len(failed)
        status['inference_limit']='Only 9 months / 7 possible contiguous 3-month blocks; percentile intervals are fragile diagnostics, not confirmatory replication.'
        write_csv(out/'newtime_draws.csv',draws);dump(out/'indices.json',indices);dump(out/'failures.json',failed)
    except Exception as exc:
        status['status']='HOLD';status['reason']=str(exc)
    dump(out/'NEW_TIME_RESULTS.json',status)
    print(json.dumps(status,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
