#!/usr/bin/env python3
"""Independent read-only OOXML/CSV audit. No supplied validation code is executed.

Parses ZIP/XML using the Python standard library; does not evaluate workbook code
or formulas. Can cross-check cells against an artifact_tool value export.
"""
from __future__ import annotations
import argparse, collections, csv, datetime as dt, hashlib, io, json, math, re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from xml.etree import ElementTree as E

INPUT_COMMIT='5745eb3ddca79602346053446583d794b0e09800'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p':'http://schemas.openxmlformats.org/package/2006/relationships'}
FIELDS={
 'V':'Auction Volume tCO2','B':'Total Amount of Bids',
 'bid_count':'Number of bids submitted','successful_bid_count':'Number of successful bids',
 'mean_bids_per_bidder':'Average number of bids per bidder','mean_bid_size':'Average bid size',
 'mu_B':'Average volume bid per bidder','sd_B':'Standard deviation of bid volume per bidder',
 'mu_W':'Average volume won per bidder','sd_W':'Standard deviation of volume won per bidder',
 'R':'Cover Ratio','N':'Total Number of Bidders','S':'Number of Successful Bidders'}
IDENTITY={'contract_raw':'Contract','status_raw':'Status','venue_raw':'Country','auction_name_raw':'Auction Name'}

def require(x,msg):
 if not x: raise ValueError(msg)
def dump(path,value):
 Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(body):return hashlib.sha256(body).hexdigest()
def coord(s):
 m=re.fullmatch(r'([A-Z]+)([0-9]+)',s);require(m is not None,'Invalid cell address')
 n=0
 for c in m[1]: n=n*26+ord(c)-64
 return int(m[2]),n

def workbook_cells(body):
 with ZipFile(io.BytesIO(body)) as z:
  require(z.testzip() is None,'XLSX CRC error')
  main=E.fromstring(z.read('xl/workbook.xml'))
  wp=main.find('s:workbookPr',NS)
  epoch=dt.datetime(1904,1,1) if wp is not None and wp.get('date1904') in ('1','true') else dt.datetime(1899,12,30)
  sheets=main.findall('s:sheets/s:sheet',NS)
  require([s.get('name') for s in sheets]==['Primary Market Auction'],'Unexpected sheet set')
  rels=E.fromstring(z.read('xl/_rels/workbook.xml.rels'))
  relmap={x.get('Id'):x.get('Target') for x in rels}
  target=relmap[sheets[0].get('{'+NS['r']+'}id')]
  member=target.lstrip('/') if target.startswith('/') else str(PurePosixPath('xl')/target)
  require('..' not in PurePosixPath(member).parts,'Unsafe workbook relationship')
  shared=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS):
    shared.append(''.join(x.text or '' for x in si.iter('{'+NS['s']+'}t')))
  styles=E.fromstring(z.read('xl/styles.xml'))
  nfmt={0:'General',3:'#,##0',2:'0.00',14:'mm-dd-yy'}
  for x in styles.findall('s:numFmts/s:numFmt',NS):nfmt[int(x.get('numFmtId'))]=x.get('formatCode')
  xfs=styles.findall('s:cellXfs/s:xf',NS)
  cells={};formats={};formula_cells=[]
  sheet=E.fromstring(z.read(member))
  for x in sheet.findall('s:sheetData/s:row/s:c',NS):
   a=x.get('r');typ=x.get('t');v=x.find('s:v',NS)
   if x.find('s:f',NS) is not None:formula_cells.append(a)
   if typ=='s': value=shared[int(v.text)] if v is not None else None
   elif typ=='inlineStr':value=''.join(t.text or '' for t in x.findall('s:is//s:t',NS))
   elif v is None:value=None
   elif typ in ('str','e','d'):value=v.text
   elif typ=='b':value=v.text=='1'
   else:value=float(v.text) if v.text is not None else None
   cells[a]=value
   idx=int(x.get('s','0'));fmt=int(xfs[idx].get('numFmtId','0')) if xfs else 0
   formats[a]=nfmt.get(fmt,f'numFmtId:{fmt}')
  return cells,formats,epoch,formula_cells,sheet.find('s:dimension',NS).get('ref')

def csvrows(body):return list(csv.DictReader(io.StringIO(body.decode('utf-8-sig'))))
def loc(r):return r['file'],r['sheet'],int(r['row'])
def exclusion(r):
 reasons=[]
 if r['contract_raw']!='T3PA':reasons.append('not_EUA_contract')
 if r['venue_raw'] not in ('EU','DE','PL'):reasons.append('outside_venue')
 if r['status_raw']!='successful':reasons.append('not_explicit_successful')
 return reasons

def audit(base,out,artifact_json=None):
 base=Path(base).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False)
 manifest=json.loads((base/'INPUT_MANIFEST.json').read_text())
 sources={};checks=[]
 for r in manifest['files']:
  p=(base/r['path']).resolve();require(p.is_relative_to(base),'Path escape')
  b=p.read_bytes();require(len(b)==r['bytes'] and sha(b)==r['sha256'],'Input bytes mismatch '+r['path'])
  require(r['path'] not in sources,'Duplicate input manifest entry')
  sources[r['path']]=b;checks.append({'path':r['path'],'bytes':len(b),'sha256':sha(b),'verified':True})
 extracted=csvrows(sources['parsed/extraction_all_2020_2025.csv'])
 candidates=csvrows(sources['parsed/candidate_dispersion.csv'])
 excluded=csvrows(sources['parsed/row_exclusions.csv'])
 art=json.loads(Path(artifact_json).read_text()) if artifact_json else None
 traces=json.loads(sources['parsed/raw_field_cells.json'])
 trace_by={r['locator']:r['cells'] for r in traces}
 require(len(trace_by)==len(traces),'Duplicate trace locator')
 raw={};meta=[];comparisons=trace_comparisons=artifact_comparisons=0;formula_n=0
 for name,body in sorted(sources.items()):
  if not name.startswith('raw/'):continue
  cells,formats,epoch,formulas,dim=workbook_cells(body)
  header={str(v):re.sub('[0-9]','',a) for a,v in cells.items() if coord(a)[0]==6 and v is not None}
  require(all(x in header for x in list(FIELDS.values())+list(IDENTITY.values())+['Date']),'Required header missing')
  dates=[(a,v) for a,v in cells.items() if re.sub('[0-9]','',a)==header['Date'] and coord(a)[0]>=7 and isinstance(v,(int,float)) and not isinstance(v,bool)]
  rownum=[]
  for a,v in dates:
   rn=coord(a)[0];date=(epoch+dt.timedelta(days=v)).date().isoformat()
   require('2020-01-01'<=date<='2025-12-31','Unexpected date')
   key=(Path(name).name,'Primary Market Auction',rn)
   require(key not in raw,'Duplicate raw locator')
   r={'file':key[0],'sheet':key[1],'row':str(rn),'date':date}
   r.update({k:cells.get(header[label]+str(rn)) for k,label in IDENTITY.items()})
   for k,label in FIELDS.items():
    address=header[label]+str(rn);val=cells.get(address)
    require(address not in formulas,'Required formula cell unsupported '+address)
    require(val is None or (isinstance(val,(int,float)) and not isinstance(val,bool) and math.isfinite(val)),'Non-numeric source')
    r[k]=val
    locator=f'{key[0]}!{key[1]}!row{rn}'
    tr=trace_by[locator][label]
    require(tr['cell']==address and tr['raw']==val and tr['number_format']==formats.get(address,'General'),'Trace mismatch '+locator+label)
    trace_comparisons+=1
    if art is not None:
     ar=art[key[0]];arow,acol=coord(ar['dimension'].split(':')[0]);rr,cc=coord(address)
     av=ar['values'][rr-arow][cc-acol]
     require(av==val,'artifact_tool cell mismatch '+key[0]+address)
     artifact_comparisons+=1
   raw[key]=r;rownum.append(rn)
  meta.append({'file':Path(name).name,'sheet':'Primary Market Auction','dimension':dim,'dated_rows':len(dates),'required_header_columns':{k:header[v] for k,v in FIELDS.items()},'required_formulas':0,'date_epoch':epoch.date().isoformat()})
  formula_n+=len(formulas)
 require(len(extracted)==len(raw),'Extracted row count differs from source')
 lookup={loc(r):r for r in extracted};require(len(lookup)==len(extracted),'Duplicate extraction locator')
 require(set(raw)==set(lookup),'Extraction misses or adds dated rows')
 for key,r in raw.items():
  c=lookup[key]
  require(all(str(r[k])==c[k] for k in ['date']+list(IDENTITY)),'Identity mismatch '+str(key))
  for k in FIELDS:
   require((r[k] is None and c[k]=='') or (r[k] is not None and float(c[k])==r[k]),'Raw numerical mismatch '+str(key)+k)
   comparisons+=1
 selected={k:r for k,r in raw.items() if not exclusion(r)}
 selcsv={loc(r):r for r in candidates};excsv={loc(r):r for r in excluded}
 require(len(selcsv)==len(candidates) and len(excsv)==len(excluded),'Duplicate subset locator')
 require(set(selected)==set(selcsv),'Candidate membership differs from raw-defined rule')
 require(set(excsv)==set(raw)-set(selected),'Exclusion set mismatch')
 for k,r in selcsv.items():require(r==lookup[k],'Candidate values/metadata changed')
 for k,r in excsv.items():
  require(all(r[f]==lookup[k][f] for f in r),'Exclusion values/metadata changed')
  require(r['exclusion_reasons']==';'.join(exclusion(raw[k])),'Exclusion reason mismatch')
 eventkeys={(r['date'],r['venue_raw'],r['contract_raw'],r['status_raw']) for r in raw.values()}
 require(len(eventkeys)==len(raw),'Duplicate economic event key')
 counts=collections.Counter();years=collections.Counter();format_summary={k:set() for k in FIELDS}
 normalized=[]
 for key,r in sorted(selected.items(),key=lambda kv:(kv[1]['date'],kv[1]['venue_raw'])):
  require(all(r[k] is not None and r[k]>0 for k in ('V','B','R','N','S','mu_B','mu_W')),'Invalid required denominator')
  require(r['sd_B'] is not None and r['sd_W'] is not None and r['sd_B']>=0 and r['sd_W']>=0,'Invalid SD')
  require(r['N']>=r['S']>=1 and r['N']==int(r['N']) and r['S']==int(r['S']),'Invalid bidder counts')
  require(r['bid_count']>=r['N'] and r['successful_bid_count']>=r['S'],'Bid count is not participant count')
  counts[r['venue_raw']]+=1;years[r['date'][:4]+'_'+r['venue_raw']]+=1
  nr={'event_id':r['date']+'|'+r['venue_raw']+'|'+r['contract_raw'],'auction_date':r['date'],'product':'EUA','project':r['venue_raw'],'status':'success',
      'mean_bid':r['mu_B'],'sd_bid':r['sd_B'],'mean_won':r['mu_W'],'sd_won':r['sd_W'],'bid_volume':r['B'],'auction_volume':r['V'],'bidders':r['N'],'successful_bidders':r['S'],'cover_ratio':r['R'],
      'source_file':r['file'],'source_sheet':r['sheet'],'source_row':r['row'],'allocated_volume':''}
  normalized.append(nr)
 with (out/'normalized_input.csv').open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(normalized[0]));writer.writeheader();writer.writerows(normalized)
 summary={'status':'PASS','input_commit':INPUT_COMMIT,'source_bytes':checks,'workbooks':meta,'source_workbook_count':len(meta),'source_dated_rows':len(raw),'candidate_rows':len(selected),'excluded_rows':len(excsv),
          'raw_numeric_csv_comparisons':comparisons,'raw_field_trace_comparisons':trace_comparisons,'artifact_tool_independent_numeric_comparisons':artifact_comparisons,
          'all_53_candidate_columns_equal_extraction':True,'duplicate_event_keys':len(raw)-len(eventkeys),
          'raw_status_counts':dict(collections.Counter(r['status_raw'] for r in raw.values())),
          'exclusion_reasons':dict(collections.Counter(reason for k in excsv for reason in exclusion(raw[k]))),'project_counts':dict(sorted(counts.items())),'year_project_counts':dict(sorted(years.items())),
          'zero_sd_bid':sum(r['sd_B']==0 for r in selected.values()),'zero_sd_won':sum(r['sd_W']==0 for r in selected.values()),
          'N_equals_S':sum(r['N']==r['S'] for r in selected.values()),'calendar_months':len({r['date'][:7] for r in selected.values()}),
          'date_min':min(r['date'] for r in selected.values()),'date_max':max(r['date'] for r in selected.values()),
          'normalized_sha256':sha((out/'normalized_input.csv').read_bytes()),'provided_validator_executed':False,'old_models_executed':False,
          'source_names_and_fields_only_not_external_market_authentication':True,'sd_population':'unknown','sd_ddof':'unknown','first_release_vintages':'not_certified','new_results_not_preregistered':True}
 dump(out/'input_audit.json',summary)
 return summary

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--input',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--artifact-values',type=Path)
 x=a.parse_args();r=audit(x.input,x.out,x.artifact_values)
 print(json.dumps({k:v for k,v in r.items() if k not in ('source_bytes','workbooks')},ensure_ascii=False))
