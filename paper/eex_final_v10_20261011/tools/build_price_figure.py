"""Replot fixed published aggregate contrasts; never fit or access private rows."""
from pathlib import Path
import argparse,json
import matplotlib.pyplot as plt

def build(root:Path):
    results=json.loads((root/'support/PRICE_RESULTS.json').read_text())
    (root/'figures').mkdir(exist_ok=True)
    rows=[('primary_signed_240','Signed deviation: primary','o',0),('S2_no_flags_203','Signed deviation: no row flags','s',1),('S3_best_bid_236','Signed deviation: best bid','D',2),('S1_absolute_240','Absolute deviation: same sample','^',3.5)]
    fig,ax=plt.subplots(figsize=(6.85,3.75));values=[]
    for key,label,marker,y in rows:
        r=results[key];v=r['observed_IQR_gap_bps'];lo,hi=r['observed_IQR_gap_CR1_CI95_bps']
        if not lo<=v<=hi:raise ValueError('Invalid frozen interval')
        ax.errorbar(v,y,xerr=[[v-lo],[hi-v]],fmt=marker,markersize=6,capsize=4,linewidth=1.15)
        ax.annotate(f'{v:.2f} [{lo:.2f}, {hi:.2f}]',(v,y),xytext=(0,10),textcoords='offset points',ha='center',fontsize=9)
        values.append({'specification':key,'contrast_bp':v,'CI95_low':lo,'CI95_high':hi})
    ax.set_yticks([r[3] for r in rows],[r[1] for r in rows],fontsize=9)
    ax.set_xlim(-30,22);ax.set_ylim(4.1,-0.7)
    ax.axvline(0,linestyle='--',linewidth=.8);ax.axhline(2.75,linestyle=':',linewidth=.6)
    ax.set_xlabel('Fitted difference across the observed dispersion IQR (basis points)',fontsize=9)
    ax.tick_params(axis='x',labelsize=9);fig.tight_layout(pad=1.)
    for ext in ('png','svg','eps'):fig.savefig(root/'figures'/f'Fig2.{ext}',dpi=1200)
    (root/'figures/PRICE_FIGURE_DATA.json').write_text(json.dumps(values,indent=2))
    plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);build(p.parse_args().root)
