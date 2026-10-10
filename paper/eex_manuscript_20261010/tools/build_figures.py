"""Render frozen estimates. No data fitting, confidence-interval recomputation or new tests."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype'] = 'none'

ROOT = Path(__file__).resolve().parents[1]

def main():
    data = json.loads((ROOT / 'support/figure_data.json').read_text(encoding='utf-8'))
    out = ROOT / 'figures'
    out.mkdir(exist_ok=True)
    for number, rows in ((1, data['pooled']), (2, data['periods'])):
        fig, ax = plt.subplots(figsize=(6.45, 2.75 if number == 1 else 3.55))
        for position, row in enumerate(rows):
            value = row['theta']
            lower, upper = row['interval']
            if not lower <= value <= upper:
                raise ValueError('Frozen interval does not contain the point; inspect source rather than adjusting it')
            ax.errorbar(value, position, xerr=[[value-lower], [upper-value]],
                        fmt='o' if row['spec']=='A' else 's', markersize=5,
                        capsize=4, linewidth=1.2)
            ax.annotate(f'{value:.3f}  [{lower:.3f}, {upper:.3f}]', (value, position),
                        xytext=(0, 11), textcoords='offset points', ha='center', fontsize=9)
        labels = (['A: log(1 + ratio)', 'C: log(ratio)'] if number == 1 else
                  [f"{r['spec']}: {'2020–2022' if r['period']=='early' else '2023–2025'}" for r in rows])
        ax.set_yticks(range(len(rows)), labels, fontsize=10)
        ax.set_ylim(len(rows)-0.5, -0.6)
        ax.set_xlim(0, 1)
        ax.set_xlabel('Residual correlation', fontsize=10)
        ax.tick_params(axis='x', labelsize=9)
        fig.tight_layout()
        for suffix in ('png', 'svg', 'eps'):
            fig.savefig(out / f'Fig{number}.{suffix}', dpi=600)
        plt.close(fig)
    print('Rendered two figures from saved estimates; no statistical fits.')

if __name__ == '__main__':
    main()
