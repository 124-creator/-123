"""Verify frozen originals, parsed tables and optional publication inventory."""
import argparse
import hashlib
import json
from pathlib import Path

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    root=parser.parse_args().root.resolve();files={};errors=[]
    for name in ['raw_manifest.json','parsed_manifest.json','publication_manifest.json']:
        path=root/'metadata'/name
        if name=='publication_manifest.json' and not path.exists():continue
        try:
            records=json.loads(path.read_text(encoding='utf-8'))['files']
            for record in records:
                key=record['path'];resolved=(root/key).resolve()
                if not resolved.is_relative_to(root) or 'local_only' in resolved.parts:raise ValueError('Unsafe publication path')
                if key in files and files[key]['sha256']!=record['sha256']:raise ValueError('Contradictory checksums')
                if key in files and files[key]['bytes']!=record['bytes']:raise ValueError('Contradictory lengths')
                files[key]=record
        except Exception as error:
            errors.append({'file':name,'error_type':type(error).__name__})
    for key,record in sorted(files.items()):
        try:
            body=(root/key).read_bytes()
            if len(body)!=record['bytes'] or hashlib.sha256(body).hexdigest()!=record['sha256']:raise ValueError('Checksum or length mismatch')
        except Exception as error:
            errors.append({'file':key,'error_type':type(error).__name__})
    print(json.dumps({'files_checked':len(files),'passed':not errors,'errors':errors},ensure_ascii=False))
    raise SystemExit(1 if errors else 0)
