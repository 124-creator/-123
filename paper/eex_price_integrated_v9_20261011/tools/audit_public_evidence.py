"""Audit fixed public aggregates; never load private rows or refit market models."""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.stats import t as student_t

RESULT_DIR='research/eua_local_price_execution_20261011'
DESC_DIR='research/eua_price_description_followup_20261011'

def run(root:Path,out:Path)->dict:
    checks=[]
    def check(name,ok,detail=None):
        checks.append({'check':name,'passed':bool(ok),'detail':detail})
        if not ok: raise ValueError('Public-evidence mismatch: '+name)
    def equal(name,a,b):
        check(name,bool(np.allclose(a,b,rtol=2e-11,atol=2e-10)),{'computed':np.asarray(a).tolist(),'recorded':np.asarray(b).tolist()})
    rd=root/RESULT_DIR; dd=root/DESC_DIR
    identity=[]
    for folder in [rd,dd]:
        manifest=json.loads((folder/'MANIFEST.json').read_text())
        for item in manifest['files']:
            p=folder/item['path'];raw=p.read_bytes()
            check(str(p.relative_to(root))+' identity',len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'])
            identity.append({'path':str(p.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest()})
    R=json.loads((rd/'results/RESULTS.json').read_text())
    table=list(csv.DictReader((rd/'PRICE_RESULT_TABLE.csv').open(newline='')))
    cmap={x['specification']:x for x in table}
    for name,r in R.items():
        b=r['coefficient'];se=r['CR1_standard_error'];g=r['quarters'];n=r['n']
        check(name+' rank and quarter totals',r['rank']+r['residual_df']==n and len(r['quarter_counts'])==g and sum(r['quarter_counts'].values())==n)
        interval=np.array([b-student_t.ppf(.975,g-1)*se,b+student_t.ppf(.975,g-1)*se])
        equal(name+' CR1 t interval',interval,r['CR1_t_Gminus1_CI95'])
        for prefix,iqrkey,valkey,cikey in [('observed','IQR_observed_bid_dispersion','observed_IQR_gap_bps','observed_IQR_gap_CR1_CI95_bps'),('residual','IQR_residualized_bid_dispersion','fitted_IQR_gap_bps','IQR_gap_CR1_CI95_bps')]:
            equal(name+' '+prefix+' IQR contrast',b*r[iqrkey],r[valkey])
            equal(name+' '+prefix+' IQR interval',interval*r[iqrkey],r[cikey])
        c=cmap[name]
        equal(name+' public CSV values',[b,se,*interval,r['IQR_observed_bid_dispersion'],r['observed_IQR_gap_bps'],*r['observed_IQR_gap_CR1_CI95_bps'],r['incremental_partial_R2']],
              [float(c[x]) for x in ['coefficient_bp_per_unit_x','CR1_SE','CR1_CI95_low','CR1_CI95_high','observed_x_IQR','observed_IQR_gap_bp','IQR_CI95_low','IQR_CI95_high','partial_R2']])
    p=R['primary_signed_240'];bt=p['WCR_test']
    draws=list(csv.DictReader((rd/'results/PRIMARY_WCR_DRAWS.csv').open(newline='')))
    signs=np.array(json.loads((rd/'results/PRIMARY_WCR_SIGNS.json').read_text()),dtype=np.int8)
    expected=np.random.default_rng(np.random.SeedSequence([20261011,2,240])).choice(np.array([-1,1],dtype=np.int8),size=(999,21))
    check('Stored WCR signs match locked RNG stream',signs.shape==(999,21) and np.array_equal(signs,expected))
    check('999 WCR statistics and sequential IDs',len(draws)==999 and [int(x['draw']) for x in draws]==list(range(999)) and all(math.isfinite(float(x['t'])) for x in draws))
    equal('Observed t',p['coefficient']/p['CR1_standard_error'],bt['t_observed'])
    exceed=sum(abs(float(x['t']))>=abs(bt['t_observed']) for x in draws)
    equal('WCR plus-one p',(exceed+1)/1000,bt['two_sided_plus_one_p'])
    check('Original WCR completion',bt['requested']==bt['valid']==999 and not bt['failed'])
    j=p['deletion_diagnostics']['quarter_jackknife'];v=np.array([a['coefficient'] for a in j['deletions']])
    equal('CV3J mean',v.mean(),j['delete_estimate_mean'])
    js=np.sqrt(20/21*np.sum((v-v.mean())**2))
    equal('CV3J SE',js,j['standard_error'])
    equal('CV3J t interval',[p['coefficient']-student_t.ppf(.975,20)*js,p['coefficient']+student_t.ppf(.975,20)*js],j['CI95'])
    check('Quarter omissions exhaust fixed labels',{a['omitted_quarter'] for a in j['deletions']}==set(p['quarter_counts']))
    years=p['deletion_diagnostics']['leave_year_out']
    check('Six locked year deletions',{a['omitted_year'] for a in years}==set(range(2020,2026)))
    d=json.loads((dd/'DESCRIPTIVES.json').read_text())
    dt=list(csv.DictReader((dd/'DESCRIPTIVES.csv').open(newline='')))
    check('Six descriptions',len(d['table'])==len(dt)==6)
    for row,c in zip(d['table'],dt):
        tag=row['sample']+'/'+row['outcome']
        for key,value in row.items():
            if isinstance(value,(float,int)):equal(tag+' CSV '+key,value,float(c[key]))
            else:check(tag+' CSV '+key,value==c[key])
        check(tag+' sign counts',sum(row[k] for k in ['negative_count','positive_count','reported_zero_count'])==row['n'])
        for label in ['negative','positive','reported_zero']:equal(tag+' share '+label,row[label+'_count']/row['n'],row[label+'_share'])
        check(tag+' ordered quantiles',row['minimum']<=row['q25']<=row['median']<=row['q75']<=row['maximum'])
    for sample in ['primary240','noflags203','bestbid236']:
        s=next(x for x in d['table'] if x['sample']==sample and x['outcome']=='signed_bp')
        a=next(x for x in d['table'] if x['sample']==sample and x['outcome']=='absolute_bp')
        n=s['n']; equal(sample+' signed/absolute second-moment identity',(n-1)*s['sample_sd']**2+n*s['mean']**2,(n-1)*a['sample_sd']**2+n*a['mean']**2)
        check(sample+' absolute summary constraints',abs(s['mean'])<=a['mean'] and a['reported_zero_count']==s['reported_zero_count'] and a['maximum']==max(abs(s['minimum']),abs(s['maximum'])))
    original_lock=json.loads((rd/'PREFIT_LOCK_FINAL.json').read_text())
    for f in original_lock['files']:
        body=(rd/f['path']).read_bytes();check('Final prefit identity '+f['path'],len(body)==f['bytes'] and hashlib.sha256(body).hexdigest()==f['sha256'])
    omitted=next(x for x in years if x['omitted_year']==2022)['coefficient']
    record={'scope':'Independent arithmetic audit of public aggregates, stored draw outputs and locked code identity; not private-row refitting, source-price certification or coverage validation',
       'price_result_commit':'fccd471de96548bd781c59aced4a59435aae08ac','description_commit':'33707c164c80accd7acf9fcd3f0965088a8370f6',
       'passed':True,'public_manifest_files_checked':len(identity),'arithmetic_and_identity_checks':len(checks),
       'new_market_fits':0,'new_wild_draws':0,'new_private_row_descriptions':0,'stored_wild_statistics_read':len(draws),'exceedance_count':exceed,
       'year2022_coefficient_magnitude_change_fraction':1-abs(omitted/p['coefficient']),
       'checks':checks,'verified_public_files':identity}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,ensure_ascii=False,indent=2))
    return record
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=run(a.root,a.out);print(json.dumps({k:r[k] for k in ['passed','public_manifest_files_checked','arithmetic_and_identity_checks','stored_wild_statistics_read','exceedance_count','new_market_fits']}))
