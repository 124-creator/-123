"""Read-only source audit. No workbook formula execution and no statistical fitting."""
from __future__ import annotations
import argparse, csv, hashlib, json, posixpath, zipfile
from collections import Counter
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET

NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RNS='{http://schemas.openxmlformats.org/package/2006/relationships}'
DOCREL='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
HEADERS={
 'auction_price':('G','Auction Price €/tCO2'),
 'minimum_bid_price':('H','Minimum Bid €/tCO2'),
 'maximum_bid_price':('I','Maximum Bid €/tCO2'),
 'mean_bid_price':('J','Mean €/tCO2'),
 'median_bid_price':('K','Median €/tCO2'),
 'reported_revenue':('Y','Total Revenue €'),
 'reported_time':('C','Time'),
}
OLD={'V':'L','B':'M','bid_count':'N','successful_bid_count':'O',
     'mean_bids_per_bidder':'P','mean_bid_size':'Q','mu_B':'R','sd_B':'S',
     'mu_W':'T','sd_W':'U','R':'V','N':'W','S':'X'}

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def dec(v):
    if v is None or str(v).strip() in ('','--'): raise ValueError('missing numeric value')
    d=Decimal(str(v))
    if not d.is_finite(): raise ValueError('nonfinite numeric value')
    return d

def read_sheet(path:Path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise ValueError('corrupt XLSX')
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS):
                ss.append(''.join(si.itertext()))
        book=ET.fromstring(z.read('xl/workbook.xml'))
        prop=book.find('s:workbookPr',NS)
        if prop is not None and prop.attrib.get('date1904') in ('1','true'):
            raise ValueError('Unreviewed 1904 date system')
        rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheet=next(s for s in book.findall('s:sheets/s:sheet',NS) if s.attrib['name']=='Primary Market Auction')
        target=rels[sheet.attrib[DOCREL]]
        member=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl',target))
        cells={}
        for c in ET.fromstring(z.read(member)).findall('.//s:sheetData/s:row/s:c',NS):
            ref=c.attrib['r']; typ=c.attrib.get('t'); v=c.find('s:v',NS)
            if c.find('s:f',NS) is not None:
                cells[ref]={'formula':True,'value':None};continue
            if typ=='s': value=ss[int(v.text)] if v is not None else None
            elif typ=='inlineStr': value=''.join(c.find('s:is',NS).itertext())
            else: value=v.text if v is not None else None
            cells[ref]={'formula':False,'value':value}
        return cells

def value(cells,ref):
    c=cells.get(ref,{'formula':False,'value':None})
    if c['formula']:raise ValueError('Formula in required source cell '+ref)
    return c['value']

def audit(root:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    records=json.loads((root/'INPUT_MANIFEST.json').read_text())['files']
    for r in records:
        p=root/r['path']
        if p.stat().st_size!=r['bytes'] or sha(p)!=r['sha256']:raise ValueError('Input hash mismatch '+r['path'])
    before={r['path']:sha(root/r['path']) for r in records}
    original=list(csv.DictReader((root/'parsed/extraction_all_2020_2025.csv').open(encoding='utf-8-sig')))
    candidate=list(csv.DictReader((root/'parsed/candidate_dispersion.csv').open(encoding='utf-8-sig')))
    indexed={};header_audit=[]
    for p in sorted((root/'raw').glob('*.xlsx')):
        cells=read_sheet(p);indexed[p.name]=cells
        for label,(col,expected) in HEADERS.items():
            actual=value(cells,col+'6')
            if actual!=expected:raise ValueError(f'Header mismatch {p.name}:{col}6={actual!r}')
            header_audit.append({'source_file':p.name,'cell':col+'6','field':label,'literal_header':actual})
    rebuilt=set();keys=set();exclude=Counter();old_checks=0
    for r in original:
        cells=indexed[r['file']];rn=int(r['row']);key=(r['file'],rn)
        if key in keys:raise ValueError('Duplicate source key')
        keys.add(key)
        product=value(cells,'E'+str(rn));series=value(cells,'Z'+str(rn));status=value(cells,'F'+str(rn))
        date=(datetime(1899,12,30)+timedelta(days=float(dec(value(cells,'B'+str(rn)))))).date().isoformat()
        if (date,product,series,status)!=(r['date'],r['contract_raw'],r['venue_raw'],r['status_raw']):raise ValueError('Identity mismatch')
        for field,col in OLD.items():
            a=value(cells,col+str(rn));b=r[field]
            if a in (None,'','--') and b in ('',None,'--'):pass
            elif dec(a)!=dec(b):raise ValueError('Prior numeric field mismatch '+field)
            old_checks+=1
        if product!='T3PA':exclude['other_product']+=1
        elif series not in {'EU','DE','PL'}:exclude['other_series']+=1
        elif status!='successful':exclude['not_successful']+=1
        else:rebuilt.add(key)
    if rebuilt!={(r['file'],int(r['row'])) for r in candidate}:raise ValueError('Eligibility set differs')
    rows=[];traces=[];checks=Counter();reported_time_counter=Counter();year_counts=Counter()
    revenue_max=Decimal(0);identity_values=[]
    for r in sorted(candidate,key=lambda x:(x['date'],x['venue_raw'])):
        cells=indexed[r['file']];rn=int(r['row']);xs={}
        for field,(col,_) in HEADERS.items():
            v=value(cells,col+str(rn));d=dec(v)
            xs[field]=d
            traces.append({'source_file':r['file'],'sheet':r['sheet'],'cell':col+str(rn),'field':field,'raw_numeric_value':str(d)})
        if not (xs['minimum_bid_price']<=xs['auction_price']<=xs['maximum_bid_price']):raise ValueError('Auction price outside bid limits')
        for name in ('mean_bid_price','median_bid_price'):
            if not xs['minimum_bid_price']<=xs[name]<=xs['maximum_bid_price']:raise ValueError('Price summary outside bid limits')
        if xs['auction_price']<=0 or xs['minimum_bid_price']<0:raise ValueError('Invalid primary price')
        rev=abs(xs['reported_revenue']-xs['auction_price']*dec(r['V']));revenue_max=max(revenue_max,rev)
        checks['clearing_in_bid_range']+=1; checks['mean_in_bid_range']+=1;checks['median_in_bid_range']+=1
        checks['revenue_equals_price_times_volume_within_0_01_eur']+=int(rev<=Decimal('.01'))
        t=datetime(1899,12,30)+timedelta(days=float(xs['reported_time']))
        minute=t.hour*60+t.minute+t.second/60+t.microsecond/60e6
        reported_time_counter['clock_after_11_00']+=int(minute>660)
        reported_time_counter['clock_equals_11_00']+=int(minute==660)
        reported_time_counter['clock_before_11_00']+=int(minute<660)
        year_counts[r['date'][:4]]+=1
        row={'auction_id':r['date']+'|'+r['venue_raw']+'|'+r['contract_raw'],
             'auction_date':r['date'],'auction_series':r['venue_raw'],'auction_product':r['contract_raw'],
             'source_file':r['file'],'source_sheet':r['sheet'],'source_row':rn,
             'reported_time_raw':str(xs['reported_time']),'reported_clock_unzoned':t.time().isoformat(),
             'reported_time_semantics':'unknown_not_accepted_as_bidding_close',
             'auction_price_eur_per_tco2':str(xs['auction_price']),
             'minimum_bid_price_eur_per_tco2':str(xs['minimum_bid_price']),
             'maximum_bid_price_eur_per_tco2':str(xs['maximum_bid_price']),
             'bid_price_spread_eur_per_tco2':str(xs['maximum_bid_price']-xs['minimum_bid_price']),
             'mean_bid_price_eur_per_tco2':str(xs['mean_bid_price']),
             'median_bid_price_eur_per_tco2':str(xs['median_bid_price']),
             'reported_revenue_eur':str(xs['reported_revenue'])}
        row.update({k:str(dec(r[k])) for k in OLD});rows.append(row)
    def write_csv(p,data):
        with p.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    write_csv(out/'auction_prices_local.csv',rows);write_csv(out/'price_source_cells_local.csv',traces)
    write_csv(out/'PRICE_HEADERS.csv',header_audit)
    if before!={r['path']:sha(root/r['path']) for r in records}:raise ValueError('Source modified')
    receipt={'date':'2026-10-11','scope':'price-field acquisition and eligibility audit; no price regression',
      'input_commit':'5745eb3ddca79602346053446583d794b0e09800','input_hashes_checked':len(records),
      'workbooks_read':len(indexed),'dated_rows':len(original),'eligible_auctions':len(rows),
      'exclusions':dict(exclude),'year_counts':dict(year_counts),'original_numeric_cell_comparisons':old_checks,
      'new_price_and_revenue_fields_per_auction':6,'new_price_revenue_cells_read':6*len(rows),
      'reported_time_cells_read':len(rows),'literal_header_checks':len(header_audit),
      'price_constraints':dict(checks),'revenue_product_max_abs_discrepancy_eur':str(revenue_max),
      'reported_unzoned_clock_diagnostics':dict(reported_time_counter),
      'time_semantics':'No timezone or bidding-close semantics authenticated by numeric clock values',
      'external_reference_observations':0,'eligible_price_pairs':0,'market_regressions':0,
      'hypothesis_tests':0,'source_bytes_unchanged':True,
      'local_auction_file_sha256':sha(out/'auction_prices_local.csv'),
      'new_derived_market_rows_republished':False}
    (out/'AUCTION_PRICE_AUDIT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    return receipt
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--input',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    print(json.dumps(audit(args.input,args.out),indent=2))
