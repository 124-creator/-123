"""Plot completed results only. No fitting, no source data download."""
from pathlib import Path
import csv,json
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def build(show=False):
    data=json.loads((ROOT/'KEY_RESULTS.json').read_text())
    pts=data['E1']['contrasts'];out=ROOT/'figures';out.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(8.4,4.6))
    labels=[]
    for i,p in enumerate(pts):
        val=p['delta_theta'];lo=p['lower97_5'];hi=p['upper97_5']
        ax.errorbar(val,i,xerr=[[val-lo],[hi-val]],fmt='s' if p['weighting']=='overlap' else 'o',capsize=4,markersize=6)
        labels.append(p['spec']+': '+('overlap-weighted' if p['weighting']=='overlap' else 'original equal weights'))
        ax.annotate(f'{val:.3f} [{lo:.3f}, {hi:.3f}]',(val,i),xytext=(0,12),textcoords='offset points',ha='center',fontsize=9)
    ax.set_yticks(range(4),labels);ax.set_ylim(3.7,-.65);ax.set_xlim(-.02,.46);ax.axvline(0,linestyle='--',linewidth=.8)
    ax.set_xlabel('Late-minus-early residual-correlation difference')
    fig.text(.5,.015,'97.5% exploratory intervals, 999 three-month block draws. Weights refitted each draw.\nMoment balance does not establish full distributional balance.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.09,1,1))
    for ext in ('png','svg'):fig.savefig(out/f'Fig1_composition_contrast.{ext}',dpi=250)
    if show:plt.show()
    plt.close(fig)
    dist=data['E1']['distribution_diagnostics'];fig,ax=plt.subplots(figsize=(8.4,4.3))
    yy=list(range(len(dist)))
    ax.scatter([float(r['KS_raw']) for r in dist],[i-.1 for i in yy],marker='o',s=35,label='Original')
    ax.scatter([float(r['KS_ow']) for r in dist],[i+.1 for i in yy],marker='s',s=35,label='Overlap weighted')
    for i,r in enumerate(dist):
        ax.annotate(f"{float(r['KS_raw']):.3f} → {float(r['KS_ow']):.3f}",(max(float(r['KS_raw']),float(r['KS_ow'])),i),xytext=(10,0),textcoords='offset points',fontsize=9,va='center')
    ax.axvline(.1,linestyle='--',linewidth=.9,label='Protocol diagnostic reference: 0.10')
    ax.set_yticks(range(4),['Log auction volume','Log total bidders','Log successful bidders','Log cover ratio'])
    ax.set_ylim(3.65,-.5);ax.set_xlim(0,.43);ax.set_xlabel('Empirical distribution distance (KS; not a p-value)')
    ax.legend(loc='lower right',fontsize=8,frameon=False)
    fig.text(.5,.015,'Auction-volume shape remains imbalanced despite matching its first two moments.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1))
    for ext in ('png','svg'):fig.savefig(out/f'Fig2_distribution_warning.{ext}',dpi=250)
    if show:plt.show()
    plt.close(fig)
    e=data['E3'];fig,ax=plt.subplots(figsize=(8.4,3.8))
    for i,s in enumerate(('A','C')):
        val=e['points'][s]['theta'];lo,hi=e['intervals'][s]['theta_CI95']
        ax.errorbar(val,i,xerr=[[val-lo],[hi-val]],fmt='o' if s=='A' else 's',capsize=5,markersize=6)
        ax.annotate(f'{val:.3f} [{lo:.3f}, {hi:.3f}]',(val,i),xytext=(0,14),textcoords='offset points',ha='center',fontsize=10)
    ax.set_yticks([0,1],['A: log-one-plus','C: natural log']);ax.set_ylim(1.6,-.65);ax.set_xlim(0,1)
    ax.set_xlabel('Residual correlation: Jan–Sep 2026, 166 auctions')
    fig.text(.5,.015,'Diagnostic 95% intervals only: 9 months, 7 available three-month source blocks.\nRe-estimation in a new period, not prediction by a frozen historical model.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.10,1,1))
    for ext in ('png','svg'):fig.savefig(out/f'Fig3_newtime_2026.{ext}',dpi=250)
    if show:plt.show()
    plt.close(fig)
if __name__=='__main__':build()
