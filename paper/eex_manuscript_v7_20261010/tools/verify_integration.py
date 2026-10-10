"""Read-only document/number/finite-distribution checks; no statistical model fitting."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json,re,zipfile
import numpy as np
from docx import Document

ROOT=Path(__file__).resolve().parents[1]
def readcsv(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ledger=[]
    def add(place,key,value,source,locator,decimals=4):
        ledger.append({'display_location':place,'quantity':key,'source_value':repr(float(value)),'display_value':f'{value:.{decimals}f}','source':source,'locator':locator})
    pts=json.loads((ROOT/'support/strength_point_estimates.json').read_text())
    intervals=readcsv('support/strength_intervals.csv')
    balances=readcsv('support/strength_distribution_balance.csv')
    def interval(spec,metric,weight='overlap',block=3):
        return next(r for r in intervals if r['spec']==spec and r['metric']==metric and r['weighting']==weight and int(r['block'])==block)
    expected_main=[];expected_s7=[];expected_s8=[];expected_s9=[]
    for s in ('A','C'):
        row=interval(s,'delta_theta');p=pts['points'][s]['overlap']
        vals=[p['0']['theta'],p['1']['theta'],p['delta_theta'],float(row['lower97_5']),float(row['upper97_5'])]
        expected_main.append([s,*[f'{x:.4f}' for x in vals[:3]],f'[{vals[3]:.4f}, {vals[4]:.4f}]'])
        for metric,val in zip(('early theta','late theta','delta theta'),vals[:3]):add('Table 5 panel A',s+' '+metric,val,'support/strength_point_estimates.json','points.'+s+'.overlap')
        for k in ('lower97_5','upper97_5'):add('Table 5 panel A',s+' delta theta '+k,float(row[k]),'support/strength_intervals.csv',f'block=3,spec={s},weighting=overlap,metric=delta_theta,{k}')
        for met,label in [('delta_theta','Weighted difference'),('change_delta_theta','Weighting-induced change')]:
            r=interval(s,met,'overlap')
            expected_s7.append([s,label,f"{float(r['point']):.4f}",f"[{float(r['lower95']):.4f}, {float(r['upper95']):.4f}]",f"[{float(r['lower97_5']):.4f}, {float(r['upper97_5']):.4f}]"])
            for k in ('point','lower95','upper95','lower97_5','upper97_5'):add('Table S7',s+' '+met+' '+k,float(r[k]),'support/strength_intervals.csv',f'block=3,spec={s},metric={met},{k}')
    bn={'V':'Auction volume','N':'Total bidders','S':'Successful bidders','R':'Cover ratio'}
    expected_balance=[]
    for r in balances:
        expected_balance.append([bn[r['log_variable']],f"{float(r['KS_raw']):.4f}",f"{float(r['KS_ow']):.4f}"])
        for k in ('KS_raw','KS_ow'):add('Table 5 panel B',r['log_variable']+' '+k,float(r[k]),'support/strength_distribution_balance.csv',r['log_variable']+'.'+k)
    for b in (1,3,6):
        row=[str(b),str(999 if b==3 else 199)]
        for s in ('A','C'):
            r=interval(s,'delta_theta',block=b);row.append(f"[{float(r['lower97_5']):.4f}, {float(r['upper97_5']):.4f}]")
            for k in ('lower97_5','upper97_5'):add('Table S8',f'{s} L={b} '+k,float(r[k]),'support/strength_intervals.csv',f'block={b},spec={s},weighting=overlap,metric=delta_theta,{k}')
        expected_s8.append(row)
    new=json.loads((ROOT/'support/new_diagnostic/E3R_RESULTS.json').read_text());old=json.loads((ROOT/'support/NEW_TIME_RESULTS.json').read_text())
    labels=['Slope β','Residual correlation θ','Original 999-draw θ interval','Non-circular finite θ percentiles','Circular finite θ percentiles','Leave-one-month-out θ range']
    for ix,label in enumerate(labels):
        row=[label]
        for s in ('A','C'):
            if ix<2:
                k=('beta','theta')[ix];v=old['points'][s][k];row.append(f'{v:.4f}');add('Table S9',s+' '+k,v,'support/NEW_TIME_RESULTS.json',f'points.{s}.{k}')
            else:
                if ix==2:v=old['intervals'][s]['theta_CI95'];source='support/NEW_TIME_RESULTS.json';loc=f'intervals.{s}.theta_CI95'
                elif ix in (3,4):
                    scheme=('noncircular','circular')[ix-3];q=new['schemes'][scheme]['statistics'][s]['theta_q025_median_q975'];v=[q[0],q[2]];source='support/new_diagnostic/E3R_RESULTS.json';loc=f'schemes.{scheme}.statistics.{s}.theta_q025_median_q975'
                else:v=new['leave_month_ranges'][s]['theta'];source='support/new_diagnostic/E3R_RESULTS.json';loc=f'leave_month_ranges.{s}.theta'
                row.append(f'[{v[0]:.4f}, {v[1]:.4f}]')
                for j,z in enumerate(v):add('Table S9',s+' '+label+f' bound{j}',z,source,loc)
        expected_s9.append(row)
    m=Document(ROOT/'MANUSCRIPT_EN_v7.docx');si=Document(ROOT/'ONLINE_RESOURCE_1_v7.docx')
    def actual(t):return [[c.text for c in r.cells] for r in t.rows[1:]]
    # New table values must equal their independent source extraction.
    for t,expected in [(m.tables[-2],expected_main),(m.tables[-1],expected_balance),(si.tables[-3],expected_s7),(si.tables[-2],expected_s8),(si.tables[-1],expected_s9)]:
        if actual(t)!=expected:raise ValueError('New table/source discrepancy: '+str(actual(t))+' != '+str(expected))
    enums=readcsv('support/new_diagnostic/enumerated_projections.csv');quantiles=0
    for scheme,n in [('noncircular',343),('circular',729)]:
        mult=json.loads((ROOT/f'support/new_diagnostic/{scheme}_month_multiplicities.json').read_text())
        assert len(mult)==n and len(set(map(tuple,mult)))==new['schemes'][scheme]['distinct_month_weight_vectors']
        assert np.allclose(np.mean(mult,axis=0),new['schemes'][scheme]['expected_month_multiplicity'],atol=1e-15)
        for s in ('A','C'):
            rr=[r for r in enums if r['scheme']==scheme and r['spec']==s];assert len(rr)==n
            for k in ('beta','theta'):
                q=np.quantile([float(r[k]) for r in rr],[.025,.5,.975],method='linear')
                assert np.allclose(q,new['schemes'][scheme]['statistics'][s][k+'_q025_median_q975'],rtol=0,atol=1e-14);quantiles+=3
    text='\n'.join(p.text for p in m.paragraphs)
    abstract=text.split('Abstract\n',1)[1].split('\nKeywords:',1)[0]
    assert 150<=len(abstract.split())<=250
    assert 'Funding: The authors received no financial support for this research.' in text
    assert text.index('Zhongfei Tian')<text.index('Xiang Wang')
    assert sum('late' in r.text and r.font.subscript is True for p in m.paragraphs for r in p.runs)>=2
    assert sum('early' in r.text and r.font.subscript is True for p in m.paragraphs for r in p.runs)>=2
    for d in (m,si):
        assert not d._element.xpath('.//w:ins | .//w:del')
    assert all('Author-review v6' not in p.text for p in si.paragraphs)
    with (ROOT/'tables/INTEGRATED_NUMERIC_LEDGER.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(ledger[0]));w.writeheader();w.writerows(ledger)
    receipt={'new_numeric_ledger_entries':len(ledger),'new_table_objects_compared':5,'finite_quantile_endpoints_recomputed':quantiles,'enumerated_rows_read':len(enums),'abstract_words':len(abstract.split()),'old_table_and_math_checks':'See DOCUMENT_STRUCTURE_QA.json; old blocks byte/canonical-identical, not a new market replication','preserved_repaired_inline_subscript_words':True,'new_fits_in_document_audit':0,'new_market_tests_in_document_audit':0,'E3R_runner_fits':new['fits'],'E2_price_regressions':0,'funding':'none, user confirmed','review':'Xiang Wang reviewed preceding version; integrated revision not automatically approved','publication_probability_claim':False}
    (ROOT/'support/INTEGRATION_NUMERIC_QA.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
