"""Synthetic unit fixtures only; these are NOT market observations."""
import copy
import hashlib
import html
import importlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
from decimal import Decimal

class CompositeRulesTest(unittest.TestCase):
    def test_missing_quantity_is_not_changed_to_zero(self):
        module=importlib.import_module('scripts.audit_snapshot')
        parse=getattr(module,'reported_decimal',None)
        self.assertIsNotNone(parse,'Explicit missing-value parser is missing')
        for value in [None,'','--','—']:
            self.assertIsNone(parse(value))
        self.assertEqual(parse('0'),Decimal('0'))
        self.assertEqual(parse('1,612'),Decimal('1612'))

    def test_2026_target_is_cea25_not_old_vintage_average(self):
        try:
            reconstruct = importlib.import_module('scripts.audit_snapshot').reconstructed_price
        except (ImportError, AttributeError):
            reconstruct = None
        self.assertIsNotNone(reconstruct, 'Independent reconstruction implementation is missing')
        prices = {'CEA': Decimal('10'), 'CEA21': Decimal('20'), 'CEA22': Decimal('30'), 'CEA23': Decimal('40'), 'CEA24': Decimal('50'), 'CEA25': Decimal('61.23')}
        self.assertEqual(reconstruct('2026-01-05', prices), prices['CEA25'])

    def test_earlier_effective_dates_use_their_own_constituents(self):
        reconstruct = importlib.import_module('scripts.audit_snapshot').reconstructed_price
        prices = {key: Decimal(i) for i,key in enumerate(['CEA','CEA21','CEA22','CEA23','CEA24','CEA25'],1)}
        regimes = [('2023-08-27',['CEA']),('2023-08-28',['CEA','CEA21','CEA22']),('2024-10-28',['CEA','CEA21','CEA22','CEA23']),('2025-04-29',['CEA','CEA21','CEA22','CEA23','CEA24'])]
        for date, keys in regimes:
            with self.subTest(date=date):
                expected = sum((prices[k] for k in keys), Decimal(0)) / Decimal(len(keys))
                self.assertEqual(reconstruct(date, prices), expected)

    def test_pipeline_reads_real_raw_files_without_legacy_results(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as name:
            target = Path(name)
            shutil.copytree(root/'data/raw', target/'data/raw')
            (target/'metadata').mkdir()
            shutil.copyfile(root/'metadata/raw_manifest.json', target/'metadata/raw_manifest.json')
            (target/'old_experiments').mkdir()
            (target/'old_experiments/metrics.json').write_text('INVALID UNTRUSTED TEST SENTINEL: never read', encoding='utf-8')
            run = subprocess.run([sys.executable,str(root/'scripts/audit_snapshot.py'),'--root',str(target)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertTrue((target/'metadata/audit_results.json').is_file(),'Fresh raw-file analysis output is missing')
            results = json.loads((target/'metadata/audit_results.json').read_text(encoding='utf-8'))
            self.assertFalse(results['model_training_ran'])
            self.assertEqual(results['legacy_results_status'],'UNTRUSTED_NOT_READ')
            self.assertEqual(len(results['published_datasets']),6)
            self.assertTrue(all(x['rows']>0 for x in results['published_datasets']))
            self.assertEqual(results['author_wang_sheet_check']['date_price_disagreements'],0)
            self.assertEqual(results['local_exchange_checks']['status'],'not_run_no_local_snapshot_requested')

    def test_optimized_pipeline_rejects_corrupt_original_before_export(self):
        root = Path(__file__).resolve().parents[1]
        for corruption in ['checksum', 'length']:
            with self.subTest(corruption=corruption):
                with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as name:
                    target = Path(name)
                    shutil.copytree(root/'data/raw', target/'data/raw')
                    (target/'metadata').mkdir()
                    manifest = json.loads((root/'metadata/raw_manifest.json').read_text(encoding='utf-8'))
                    path = target/'data/raw/eia/RBRTEd.xls'
                    body = bytearray(path.read_bytes())
                    if corruption == 'checksum':
                        body[-1] ^= 1
                    else:
                        body.extend(body[-1:])
                        # Deliberately match the altered hash to isolate the length check.
                        manifest['files'][0]['sha256'] = hashlib.sha256(body).hexdigest()
                    path.write_bytes(body)
                    (target/'metadata/raw_manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
                    run = subprocess.run([sys.executable,'-B','-O',str(root/'scripts/audit_snapshot.py'),'--root',str(target)],capture_output=True,text=True,encoding='utf-8')
                    exported = list((target/'data/parsed').glob('*.csv'))
                    self.assertNotEqual(run.returncode,0,f'Corrupt {corruption} accepted under -O; exported {len(exported)} CSVs: {run.stdout}')
                    self.assertIn('ValueError',run.stderr)
                    self.assertEqual(exported,[],'Invalid originals must not export any CSV')
                    self.assertFalse((target/'metadata/audit_results.json').exists())
                    self.assertFalse((target/'metadata/parsed_manifest.json').exists())

    def test_optimized_export_rejects_invalid_dates_before_writing(self):
        root = Path(__file__).resolve().parents[1]
        code = """
import csv
from pathlib import Path
import sys
from scripts.audit_snapshot import export_dataset
with Path(sys.argv[1]).open(encoding='utf-8-sig',newline='') as file:
    rows = list(csv.DictReader(file))
if sys.argv[3] == 'duplicate':
    rows.append(dict(rows[0]))
elif sys.argv[3] == 'future':
    rows[-1]['date'] = '2026-10-08'  # Deliberately invalid copy, not a market observation.
else:
    rows = []
export_dataset(Path(sys.argv[2]),'invalid_date_test',rows,'real_csv_with_test_corruption',{})
"""
        for corruption in ['duplicate', 'future', 'empty']:
            with self.subTest(corruption=corruption):
                with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as name:
                    target = Path(name)
                    run = subprocess.run([sys.executable,'-B','-O','-c',code,str(root/'data/parsed/brent_eia_daily.csv'),str(target),corruption],cwd=root,capture_output=True,text=True,encoding='utf-8')
                    self.assertNotEqual(run.returncode,0,f'Invalid {corruption} dates accepted under -O')
                    self.assertIn('ValueError',run.stderr)
                    self.assertEqual(list((target/'data/parsed').glob('*.csv')),[])

    def test_optimized_local_checks_reject_corrupt_snapshot_copies(self):
        root = Path(__file__).resolve().parents[1]
        if not (root/'data/local_only').exists():
            self.skipTest('Exchange snapshots intentionally absent from public repository')
        code = 'from pathlib import Path; import sys; from scripts.audit_snapshot import check_local_exchange_snapshots; check_local_exchange_snapshots(Path(sys.argv[1]))'
        corruptions = ['checksum','length','cea_width','cea_dates','gdea_totals','gdea_count','gdea_dates','gdea_code','gdea_name','zip_pages','zip_crc','zip_conflict']
        for corruption in corruptions:
            with self.subTest(corruption=corruption):
                with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as name:
                    target = Path(name)
                    base = target/'data/local_only'
                    shutil.copytree(root/'data/local_only',base)
                    (target/'metadata').mkdir()
                    meta = json.loads((root/'metadata/local_exchange_sources.json').read_text(encoding='utf-8'))
                    archive = next(x for x in meta['sources'] if x['filename'].endswith('.zip'))
                    if corruption in ['checksum','length']:
                        record = meta['sources'][0]
                        path = base/record['filename']
                        path.write_bytes(path.read_bytes()+b' ')
                        if corruption == 'checksum':
                            record['bytes'] = path.stat().st_size
                        else:
                            record['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                    elif corruption.startswith('cea_'):
                        path = base/'cea_composite_live.json'
                        rows = json.loads(path.read_text(encoding='utf-8'))
                        if corruption == 'cea_width':
                            rows[0].append(rows[0][-1])
                        else:
                            rows.append(list(rows[0]))
                        path.write_text(json.dumps(rows),encoding='utf-8')
                    elif corruption.startswith('gdea_'):
                        path = base/'gdea_api_page1.json'
                        response = json.loads(path.read_text(encoding='utf-8'))
                        data = response['data']
                        if corruption == 'gdea_totals':
                            data['total'] = int(data['total'])+1
                        elif corruption == 'gdea_count':
                            data['rows'].pop()
                        elif corruption == 'gdea_dates':
                            data['rows'][1]['currentDay'] = data['rows'][0]['currentDay']
                        elif corruption == 'gdea_code':
                            data['rows'][0]['productCode'] = data['rows'][0]['productName']
                        else:
                            data['rows'][0]['productName'] = data['rows'][0]['productCode']
                        path.write_text(json.dumps(response),encoding='utf-8')
                    elif corruption == 'zip_pages':
                        archive['snapshot_pages'] += 1
                    else:
                        path = base/archive['filename']
                        original = path.read_bytes()
                        altered = io.BytesIO()
                        with zipfile.ZipFile(io.BytesIO(original)) as source, zipfile.ZipFile(altered,'w') as destination:
                            for index,info in enumerate(source.infolist()):
                                body = source.read(info)
                                entry = copy.copy(info)
                                if index == 0 and corruption == 'zip_crc':
                                    # Hide one genuine page as a directory so only testzip checks its CRC.
                                    entry.filename += '/'
                                elif index == 0:
                                    text = body.decode('utf-8')
                                    official = []
                                    for tr in re.finditer(r'<tr\b[^>]*>(.*?)</tr>',text,re.S|re.I):
                                        cells = list(re.finditer(r'<td\b[^>]*>(.*?)</td>',tr.group(1),re.S|re.I))
                                        values = [html.unescape(re.sub('<[^>]+>','',x.group(1))).strip() for x in cells]
                                        if len(values) == 9 and values[0] == 'HBEA':
                                            official.append((tr,cells,values))
                                    self.assertGreater(len(official),1)
                                    first,cells,values = official[0]
                                    different = next((column,other_cells[column].group(1)) for _,other_cells,other_values in official[1:] for column in range(2,9) if other_values[column] != values[column])
                                    column,replacement = different
                                    row = first.group(1)
                                    cell = cells[column]
                                    row = row[:cell.start(1)]+replacement+row[cell.end(1):]
                                    # Duplicate a real date with a conflicting real cell, only in this invalid test copy.
                                    body = (text+'<tr>'+row+'</tr>').encode('utf-8')
                                destination.writestr(entry,body)
                        body = bytearray(altered.getvalue())
                        if corruption == 'zip_crc':
                            with zipfile.ZipFile(io.BytesIO(body)) as archive_copy:
                                entry = archive_copy.infolist()[0]
                                bad_crc = entry.CRC ^ 1
                                struct.pack_into('<I',body,entry.header_offset+14,bad_crc)
                                struct.pack_into('<I',body,archive_copy.start_dir+16,bad_crc)
                                bad_name = entry.filename
                            archive['snapshot_pages'] -= 1
                            with zipfile.ZipFile(io.BytesIO(body)) as archive_copy:
                                self.assertEqual(archive_copy.testzip(),bad_name)
                        path.write_bytes(body)
                    if corruption not in ['checksum','length']:
                        # Updated test-only hashes isolate semantic/CRC guards from byte identity guards.
                        for record in meta['sources']:
                            body = (base/record['filename']).read_bytes()
                            record['bytes'] = len(body)
                            record['sha256'] = hashlib.sha256(body).hexdigest()
                    (target/'metadata/local_exchange_sources.json').write_text(json.dumps(meta),encoding='utf-8')
                    run = subprocess.run([sys.executable,'-B','-O','-c',code,str(target)],cwd=root,capture_output=True,text=True,encoding='utf-8')
                    self.assertNotEqual(run.returncode,0,f'Corrupt {corruption} accepted under -O')
                    self.assertIn('ValueError',run.stderr)

    def test_real_local_exchange_snapshots_are_reconstructed_without_old_scores(self):
        root = Path(__file__).resolve().parents[1]
        if not (root/'data/local_only').exists():
            self.skipTest('Exchange snapshots intentionally absent from public repository')
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as name:
            target=Path(name);shutil.copytree(root/'data/raw',target/'data/raw')
            shutil.copytree(root/'data/local_only',target/'data/local_only')
            (target/'metadata').mkdir()
            for file in ['raw_manifest.json','local_exchange_sources.json']:
                shutil.copyfile(root/'metadata'/file,target/'metadata'/file)
            run=subprocess.run([sys.executable,str(root/'scripts/audit_snapshot.py'),'--root',str(target),'--include-local-exchanges'],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(run.returncode,0,run.stderr)
            result=json.loads((target/'metadata/audit_results.json').read_text(encoding='utf-8'))
            check=result['local_exchange_checks']
            self.assertEqual(check['status'],'freshly_recomputed_from_verified_original_snapshots')
            source=json.loads((root/'data/local_only/cea_composite_live.json').read_text(encoding='utf-8'))
            self.assertEqual(check['cea']['composite_observations'],len(source))
            self.assertEqual(sum(x['mismatch_days'] for x in check['cea']['regimes']),0)
            records=[]
            for n in [1,2,3]:
                records.extend(json.loads((root/f'data/local_only/gdea_api_page{n}.json').read_text(encoding='utf-8'))['data']['rows'])
            expected=sum(x.get('message')=='当日无成交' and Decimal(str(x['exchangeRate']))>0 for x in records if x.get('exchangeRate') not in (None,''))
            self.assertEqual(check['gdea']['message_quantity_conflicts'],expected)
            self.assertEqual(check['gdea']['missing_reported_quantity_rows'],sum(x.get('exchangeRate') in (None,'') for x in records))
            self.assertFalse(check['gdea']['missing_quantity_filled_with_zero'])
            self.assertFalse(result['model_training_ran'])

if __name__ == '__main__':
    unittest.main()
