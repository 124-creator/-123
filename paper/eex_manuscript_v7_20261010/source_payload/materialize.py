"""Reconstruct reviewed text; copy aggregate evidence, never market raw data."""
from pathlib import Path,PurePosixPath
import base64,hashlib,json,lzma,shutil
ROOT=Path.cwd();TARGET=ROOT/'paper/eex_manuscript_v7_20261010'
s=''.join((TARGET/'source_payload'/f'part{i}.txt').read_text().strip() for i in (1,2,3))
b=base64.b64decode(s,validate=True)
if hashlib.sha256(b).hexdigest()!='5fd8ccb1dd6858d9651809d2f0e2e5b2637a1ae0442a39153b1147e16acaee2f':raise ValueError('Reviewed text payload differs')
data=json.loads(lzma.decompress(b,memlimit=256*1024*1024))
if len(data)!=11:raise ValueError('Unexpected reviewed source count')
for name,text in data.items():
 p=PurePosixPath(name)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe output path')
 out=TARGET/p
 if out.exists():raise FileExistsError(name)
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text,encoding='utf-8')
base=ROOT/'research/eex_evidence_strengthening_20261010/results'
for src,dst in [('point_estimates.json','strength_point_estimates.json'),('intervals.csv','strength_intervals.csv'),('distribution_balance.csv','strength_distribution_balance.csv'),('weight_summary.csv','strength_weight_summary.csv'),('newtime_2026/NEW_TIME_RESULTS.json','NEW_TIME_RESULTS.json')]:
 shutil.copy2(base/src,TARGET/'support'/dst)
shutil.copytree(ROOT/'research/eex_integration_checks_20261010/results',TARGET/'support/new_diagnostic')
shutil.copytree(ROOT/'paper/eex_formula_fix_20261010/figures',TARGET/'figures')
(TARGET/'support/SOURCE_MATERIALIZATION.json').write_text(json.dumps({'source_payload_sha256':hashlib.sha256(b).hexdigest(),'reviewed_sources':{n:hashlib.sha256(t.encode()).hexdigest() for n,t in data.items()},'new_market_estimation':False,'copied_evidence':'Prior E1/E3 and separately committed E3R aggregate outputs; no new raw source'},indent=2))
print('Reviewed v7 sources reconstructed; existing aggregate results copied.')
