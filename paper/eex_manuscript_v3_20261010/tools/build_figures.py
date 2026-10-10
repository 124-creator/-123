"""Render frozen values only; no model fit or resampling."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
    data=json.loads((ROOT/"support/figure_data.json").read_text())
    (ROOT/"figures").mkdir(exist_ok=True)
    for name,key,height in [("Fig1","pooled",3.65),("Fig2","period",3.35)]:
        rows=data[key];fig,ax=plt.subplots(figsize=(6.85,height));labels=[]
        for i,row in enumerate(rows):
            v=row["theta"];lo,hi=row["CI"]
            if not (-1 <= lo <= v <= hi <= 1): raise ValueError("Invalid frozen interval")
            ax.errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt="o" if row["spec"]=="A" else "s",capsize=4,markersize=5,linewidth=1.15)
            label=(str(row["block_months"])+"-month blocks" if key=="pooled" else ("2020–2022" if row["period"]=="early" else "2023–2025"))
            labels.append(row["spec"]+": "+label)
        ax.set_yticks(range(len(rows)),labels,fontsize=9)
        ax.set_xlim(0,1);ax.set_ylim(5.55,-.55) if key=="pooled" else ax.set_ylim(3.5,-.5)
        ax.set_xlabel("Residual correlation",fontsize=10);ax.tick_params(axis="x",labelsize=9)
        fig.tight_layout(pad=1.1)
        for ext in ("png","svg","eps"): fig.savefig(ROOT/"figures"/(name+"."+ext),dpi=600)
        plt.close(fig)
if __name__=="__main__":main()
