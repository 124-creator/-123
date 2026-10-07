import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

class IntegrityTest(unittest.TestCase):
    def test_matching_checksums_cannot_hide_conflicting_manifest_lengths(self):
        root = Path(__file__).resolve().parents[1]
        pairs = [('raw_manifest.json','parsed_manifest.json'),('raw_manifest.json','publication_manifest.json'),('parsed_manifest.json','publication_manifest.json')]
        for earlier,later in pairs:
            with self.subTest(earlier=earlier,later=later):
                with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as name:
                    target = Path(name)
                    shutil.copytree(root/'data/raw',target/'data/raw')
                    shutil.copytree(root/'data/parsed',target/'data/parsed')
                    (target/'metadata').mkdir()
                    manifests = {file:json.loads((root/'metadata'/file).read_text(encoding='utf-8')) for file in ['raw_manifest.json','parsed_manifest.json']}
                    correct = dict(manifests[earlier]['files'][0])
                    # Deliberately wrong earlier length must not be masked by the later correct record.
                    manifests[earlier]['files'][0]['bytes'] += 1
                    if later not in manifests:
                        manifests[later] = {'files':[]}
                    manifests[later]['files'].append(correct)
                    for file,manifest in manifests.items():
                        (target/'metadata'/file).write_text(json.dumps(manifest),encoding='utf-8')
                    run = subprocess.run([sys.executable,'-B',str(root/'scripts/verify_repository.py'),'--root',str(target)],capture_output=True,text=True,encoding='utf-8')
                    self.assertNotEqual(run.returncode,0,'Conflicting lengths with matching sha256 must be rejected: '+run.stdout)
                    result = json.loads(run.stdout)
                    self.assertFalse(result['passed'])
                    self.assertTrue(any(error['file'] == later for error in result['errors']))

    def test_actual_originals_and_parsed_files_reject_byte_tampering(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as name:
            target=Path(name);shutil.copytree(root/'data/raw',target/'data/raw');shutil.copytree(root/'data/parsed',target/'data/parsed')
            (target/'metadata').mkdir()
            for file in ['raw_manifest.json','parsed_manifest.json']:shutil.copyfile(root/'metadata'/file,target/'metadata'/file)
            command=[sys.executable,str(root/'scripts/verify_repository.py'),'--root',str(target)]
            valid=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(valid.returncode,0,'Missing or failing integrity checker: '+valid.stderr)
            path=target/'data/raw/eia/RBRTEd.xls';body=bytearray(path.read_bytes());body[-1]^=1;path.write_bytes(body)
            altered=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
            self.assertNotEqual(altered.returncode,0,'Byte tampering must be rejected')

if __name__=='__main__':unittest.main()
