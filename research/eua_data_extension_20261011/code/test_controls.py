"""Local real-input integration tests, not synthetic empirical results."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ControlPanelTest(unittest.TestCase):
    def test_enrich_without_changing_any_original_row_field(self):
        script = Path(__file__).with_name('build_controls.py')
        self.assertTrue(script.is_file(), 'Missing control-panel enrichment feature')
        source = Path(os.environ['EUA_FROZEN_SOURCE_ROOT'])
        scratch = Path(os.environ['TMPDIR']).resolve()
        with tempfile.TemporaryDirectory(dir=scratch, prefix='eua_controls_') as td:
            out = Path(td) / 'derived'
            optimize = ['-O'] if sys.flags.optimize else []
            cp = subprocess.run([sys.executable, '-B', *optimize, str(script), '--source-root',
                                 str(source), '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            summary = json.loads(cp.stdout)
            self.assertEqual(summary['all_rows'], 275)
            self.assertEqual(summary['strict_rows'], 240)
            self.assertEqual(summary['new_observations'], 0)
            self.assertEqual(summary['new_model_fits'], 0)
            with (source / 'data/official_reported_cutoff_all275.csv').open(
                    encoding='utf-8-sig', newline='') as f:
                original = list(csv.DictReader(f))
            with (out / 'data/controls_all275.csv').open(encoding='utf-8-sig', newline='') as f:
                enriched = list(csv.DictReader(f))
            self.assertEqual(len(enriched), len(original))
            for old, new in zip(original, enriched):
                self.assertEqual({k: new[k] for k in old}, old)
                self.assertNotEqual(new['reported_cover_ratio'], '')
                self.assertNotEqual(new['bid_price_range_eur'], '')
            manifest = json.loads((out / 'MANIFEST.json').read_text(encoding='utf-8'))
            self.assertEqual({p.relative_to(out).as_posix() for p in out.rglob('*')
                              if p.is_file() and p.name != 'MANIFEST.json'},
                             {r['path'] for r in manifest['files']})
            for r in manifest['files']:
                body = (out / r['path']).read_bytes()
                self.assertEqual(len(body), r['bytes'])
                self.assertEqual(hashlib.sha256(body).hexdigest(), r['sha256'])


if __name__ == '__main__':
    unittest.main()
