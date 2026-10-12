"""Export reviewed DOCX to readable Markdown. Never use the export to rebuild equations."""
from pathlib import Path
import argparse, json, re, subprocess

def export(root: Path) -> None:
    title=json.loads((root/'REVISION_PLAN.json').read_text())['title']
    meta=(f'# {title}\n\n*Conditional associations and historical scope*\n\n'
          'Zhongfei Tian · Xiang Wang  \nZhengzhou University of Aeronautics, Zhengzhou, Henan, China  \n'
          'Corresponding author: Zhongfei Tian · 15517837680@163.com\n\n')
    configs=[('MANUSCRIPT_EN_v10.docx','MANUSCRIPT_EN.md',['Fig1','Fig2','Fig3'],meta),
             ('ONLINE_RESOURCE_1_v10.docx','ONLINE_RESOURCE_1.md',['FigS1'],f'# Online Resource 1\n\n## {title}\n\n'),
             ('TITLE_PAGE_v10.docx','TITLE_PAGE.md',[],meta)]
    for source,name,figures,heading in configs:
        text=subprocess.run(['pandoc',str(root/source),'-t','gfm','--wrap=none'],check=True,text=True,capture_output=True).stdout
        found=list(re.finditer(r'<img\b[^>]*>',text))
        if len(found)!=len(figures):raise ValueError('Unexpected image inventory: '+name)
        for hit,figure in reversed(list(zip(found,figures))):
            tag=hit.group(0)
            alt=re.search(r'alt="([^"]*)"',tag)
            label=alt.group(1) if alt else ('Fixed price contrasts with separate signed and absolute outcomes' if figure=='Fig2' else 'Quantity conditioning-set sensitivity')
            text=text[:hit.start()]+f'![{label}](figures/{figure}.png)'+text[hit.end():]
        (root/name).write_text(heading+text,encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);export(p.parse_args().root)
