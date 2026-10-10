"""Draw reviewed figure inputs only. No estimation, raw data, or resampling."""
from pathlib import Path
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def build_figures(show=False):
    data=json.loads((ROOT/'support/figure_data.json').read_text())
    saved=[]
    settings={'font.family':'sans-serif','font.sans-serif':['Arimo','DejaVu Sans'],
              'font.size':10,'axes.labelsize':10,'xtick.labelsize':9,
              'ytick.labelsize':9,'axes.linewidth':0.8,'svg.fonttype':'path',
              'ps.fonttype':42,'pdf.fonttype':42}
    with plt.rc_context(settings):
        designs=[('Fig1',3.05,'Reported SD / reported mean (dimensionless)',(0,2.0),'D'),
                 ('Fig2',3.65,'Residual correlation after the stated controls',(0,1),'o'),
                 ('Fig3',2.65,'Residual-correlation difference: late minus early',(-0.05,0.45),'s')]
        for name,height,xlabel,xlimits,marker in designs:
            rows=data[name]['rows']
            values=np.array([r['point'] for r in rows]);lo=np.array([r['low'] for r in rows]);hi=np.array([r['high'] for r in rows])
            if not (np.all(lo<=values) and np.all(values<=hi)):raise ValueError('Point outside display range')
            fig,ax=plt.subplots(figsize=(174/25.4,height))
            ax.errorbar(values,np.arange(len(rows)),xerr=np.array([values-lo,hi-values]),fmt=marker,markersize=5.5,capsize=4,linewidth=1.1)
            ax.set_yticks(range(len(rows)),[r['label'] for r in rows]);ax.set_ylim(len(rows)-0.35,-0.65)
            ax.set_xlim(*xlimits);ax.set_xlabel(xlabel)
            if name=='Fig3':ax.axvline(0,linestyle='--',linewidth=0.8)
            ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
            # Row labels carry every group distinction; no inference depends on hue.
            if name=='Fig3':
                for i,r in enumerate(rows):
                    ax.annotate(f"{r['point']:.4f} [{r['low']:.4f}, {r['high']:.4f}]",(r['point'],i),xytext=(0,13),textcoords='offset points',ha='center',fontsize=9)
            fig.tight_layout(pad=1.05)
            for ext in ('png','svg','eps'):
                filename=ROOT/'figures'/f'{name}.{ext}'
                fig.savefig(filename,dpi=1200,metadata={'Creator':'EEX frozen-value presentation builder'} if ext=='eps' else None)
                saved.append(str(filename.relative_to(ROOT)))
            if show:plt.show()
            plt.close(fig)
    (ROOT/'support/figure_build_receipt.json').write_text(json.dumps({'figures':3,'files':saved,'source_width_mm':174,'embedded_width_mm':162.56,'png_dpi':1200,'minimum_linewidth_pt':0.8,'font_size_pt_at_source':[9,10],'font_embedding':'EPS Type42; SVG glyph outlines','colors':'matplotlib defaults, not a data dimension','new_fits':0,'new_statistics':0,'matplotlib_version':matplotlib.__version__},indent=2))
    return saved

if __name__=='__main__':build_figures()
