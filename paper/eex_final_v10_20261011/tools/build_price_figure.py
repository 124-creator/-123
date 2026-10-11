"""Draw frozen public estimates only; no regression, resampling or network access."""
from pathlib import Path
import argparse, json, shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def build(source: Path, out: Path) -> None:
    (out/'figures').mkdir(parents=True,exist_ok=True)
    (out/'support').mkdir(parents=True,exist_ok=True)
    results=json.loads((source/'support/PRICE_RESULTS.json').read_text())
    signed=['primary_signed_240','S2_no_flags_203','S3_best_bid_236']
    fig,ax=plt.subplots(figsize=(6.4,3.5))
    values=[results[k]['observed_IQR_gap_bps'] for k in signed]
    intervals=[results[k]['observed_IQR_gap_CR1_CI95_bps'] for k in signed]
    ax.errorbar(values,[0,1,2],xerr=[[v-c[0] for v,c in zip(values,intervals)],[c[1]-v for v,c in zip(values,intervals)]],fmt='o',capsize=4,markersize=5,linewidth=1.1)
    a=results['S1_absolute_240'];v=a['observed_IQR_gap_bps'];lo,hi=a['observed_IQR_gap_CR1_CI95_bps']
    ax.errorbar(v,3.5,xerr=[[v-lo],[hi-v]],fmt='s',capsize=4,markersize=5,linewidth=1.1)
    ax.axvline(0,linestyle='--',linewidth=.9);ax.axhline(2.75,linestyle=':',linewidth=.7)
    ax.set_yticks([0,1,2,3.5],['Signed: primary (n = 240)','Signed: no row flags (n = 203)','Signed: best bid only (n = 236)','Absolute: primary (n = 240)'])
    ax.set_xlim(-30,22);ax.set_ylim(4.1,-.55)
    ax.set_xlabel('Fitted deviation contrast over an observed IQR (basis points)',fontsize=9)
    ax.tick_params(labelsize=9);fig.tight_layout(pad=1.)
    with plt.rc_context({'ps.fonttype':42,'pdf.fonttype':42}):
        for ext in ('png','svg','eps'):fig.savefig(out/f'figures/Fig2.{ext}',dpi=1200)
    plt.close(fig)
    rows=[{'specification':k,'contrast_bp':results[k]['observed_IQR_gap_bps'],'CR1_t_CI95_bp':results[k]['observed_IQR_gap_CR1_CI95_bps']} for k in signed+['S1_absolute_240']]
    (out/'support/FIG2_FROZEN_VALUES.json').write_text(json.dumps(rows,indent=2))
    for ext in ('png','svg','eps'):
        for old,new in [('Fig1','Fig1'),('Fig3','Fig3'),('Fig2','FigS1')]:shutil.copy2(source/f'figures/{old}.{ext}',out/f'figures/{new}.{ext}')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.source,a.out)
