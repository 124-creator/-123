"""Fetch public official exchange responses into git-ignored storage only."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import urllib.request
import zipfile


def fetch(url, destination):
    if destination.exists():
        raise FileExistsError('Refusing to overwrite an existing original')
    request=urllib.request.Request(url,headers={'User-Agent':'CarbonDataAudit/1.0 (public research)','Accept':'*/*'})
    with urllib.request.urlopen(request,timeout=40) as response:
        status=getattr(response,'status',None)
        if status is not None and status!=200:raise RuntimeError(f'HTTP {status}')
        body=response.read(20*1024*1024+1)
        if not body or len(body)>20*1024*1024:raise ValueError('Empty or oversized response')
        record={'source_url':url,'final_url':response.geturl(),'http_status':status,'content_type':response.headers.get('Content-Type'),'last_modified':response.headers.get('Last-Modified'),'retrieved_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes(body)
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',action='append',help='Exact filename from metadata/local_exchange_sources.json; default: composite only')
    parser.add_argument('--all',action='store_true',help='All listed exchange sources, including 225 Hubei pages')
    parser.add_argument('--output',type=Path,help='An empty/new local destination directory')
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'metadata/local_exchange_sources.json').read_text(encoding='utf-8'))
    names=set(args.only or ['cea_composite_live.json']);available={x['filename'] for x in manifest['sources']}
    if not names<=available:parser.error('Unknown exact source filename')
    destination=args.output or root/'data/local_only'/('refresh_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    if destination.exists():parser.error('Destination already exists; choose a new directory')
    destination.mkdir(parents=True);records=[];errors=[]
    for source in manifest['sources']:
        name=source['filename']
        if not args.all and name not in names:continue
        if Path(name).name!=name or '/' in name or '\\' in name:raise ValueError('Unsafe source filename')
        try:
            if name.endswith('.zip'):
                pages=destination/'hbea_pages';pages.mkdir()
                for page in range(1,source['snapshot_pages']+1):
                    file=pages/f'hb_official_{page}.html'
                    fetch(source['source_url'].format(page=page),file)
                    text=file.read_text(encoding='utf-8')
                    if '<table' not in text.lower():raise ValueError(f'Page {page}: missing table')
                    time.sleep(0.25)
                archive=destination/name
                with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
                    for page in range(1,source['snapshot_pages']+1):z.write(pages/f'hb_official_{page}.html',f'hb_official_{page}.html')
                record={'filename':name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'pages':source['snapshot_pages'],'container_hash_comparison_includes_zip_metadata':True}
            else:
                file=destination/name;record=fetch(source['source_url'],file);value=json.loads(file.read_text(encoding='utf-8'))
                if name.startswith('cea_') and (not isinstance(value,list) or not value or not all(len(x)==6 for x in value)):raise ValueError('Unexpected CEA schema')
                if name.startswith('gdea_') and not isinstance(value.get('data',{}).get('rows'),list):raise ValueError('Unexpected GDEA schema')
                record['filename']=name
            record['matches_20261007_snapshot_bytes']=record['sha256']==source['sha256'];records.append(record)
        except Exception as error:
            errors.append({'filename':name,'status':'failed_or_partial','error_type':type(error).__name__})
    output={'records':records,'errors':errors,'snapshot_overwritten':False,'note':'Remote sources may revise; never silently replace the frozen manifest or original snapshot.'}
    (destination/'fetch_receipt.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(output,ensure_ascii=False));raise SystemExit(1 if errors else 0)
