"""Transport test uses a real licensed workbook, not a fabricated response."""
import hashlib
import importlib
import os
from pathlib import Path
import tempfile
import unittest

class DownloadTest(unittest.TestCase):
    def test_transport_keeps_actual_original_workbook_bytes(self):
        try:fetch=importlib.import_module('scripts.fetch_exchange_sources').fetch
        except ImportError:fetch=None
        self.assertIsNotNone(fetch,'Source download implementation is missing')
        root=Path(__file__).resolve().parents[1]
        original=root/'data/raw/eia/RBRTEd.xls'
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as name:
            destination=Path(name)/'RBRTEd.xls'
            result=fetch(original.as_uri(),destination)
            self.assertEqual(destination.read_bytes(),original.read_bytes())
            self.assertEqual(result['sha256'],hashlib.sha256(original.read_bytes()).hexdigest())
            self.assertEqual(result['bytes'],original.stat().st_size)

if __name__=='__main__':unittest.main()
