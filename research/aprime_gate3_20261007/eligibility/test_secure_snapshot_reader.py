"""Real Windows scratch fixtures plus separately labelled deterministic seams."""
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import secure_snapshot_reader as reader


class SecureReaderTests(unittest.TestCase):
    def setUp(self):
        scratch = os.environ.get('TMPDIR')
        if not scratch or any(os.environ.get(key) != scratch for key in ('TEMP', 'TMP')):
            raise RuntimeError('TMPDIR/TEMP/TMP must identify the authorized scratch')
        temporary = tempfile.TemporaryDirectory(prefix='secure_reader_fixture_', dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name).resolve()
        self.root = self.directory / 'authorized'
        self.folder = self.root / 'nested'
        self.folder.mkdir(parents=True)
        self.path = self.folder / 'payload.json'
        self.body = b'ordinary synthetic snapshot'
        self.path.write_bytes(self.body)

    def test_mismatching_final_handle_path_is_rejected_before_reading(self):
        # Controlled API seam; not an OS race/stress test.
        opened, closed = {}, []
        open_handle, close_handle = reader._WindowsAPI._open, reader._WindowsAPI._close

        def record_open(api, path, directory):
            handle = open_handle(api, path, directory)
            opened[handle] = (path, directory)
            return handle

        def record_close(api, handle):
            closed.append(handle)
            return close_handle(api, handle)

        def mismatching_final(api, handle):
            path, directory = opened[handle]
            actual = path if directory else str(self.directory / 'outside.json')
            return '\\\\?\\' + actual

        with patch.object(reader._WindowsAPI, '_open', record_open):
            with patch.object(reader._WindowsAPI, '_close', record_close):
                with patch.object(reader._WindowsAPI, '_final_path', mismatching_final, create=True):
                    with patch.object(reader._WindowsAPI, '_read_handle', return_value=self.body) as read:
                        with self.assertRaisesRegex(ValueError, 'final path'):
                            reader.secure_read_bytes(self.root, self.path)
                        read.assert_not_called()
        self.assertEqual(set(opened), set(closed))
        self.assertEqual(len(opened), len(closed), 'Each acquired handle must close once')
        self.path.write_bytes(self.body)

    def test_children_are_opened_relative_to_held_parents_without_full_path_reopens(self):
        # API-call boundary property, not a claimed real-world exploit.
        open_handle = reader._WindowsAPI._open
        full_paths = []

        def only_drive_root(api, path, directory):
            full_paths.append(path)
            self.assertEqual(path, str(self.path)[:3], 'Child opened by a full path instead of parent object')
            return open_handle(api, path, directory)

        with patch.object(reader._WindowsAPI, '_open', only_drive_root):
            self.assertEqual(reader.secure_read_bytes(self.root, self.path), self.body)
        self.assertEqual(full_paths, [str(self.path)[:3]])

    def test_real_rename_and_replacement_attempts_are_denied_while_reading(self):
        if os.name != 'nt':
            self.skipTest('Windows OS-sharing test')
        replacement = self.root / 'replacement.json'
        replacement.write_bytes(b'replacement')
        child = '''import json, os, sys
from pathlib import Path
folder, file, replacement = map(Path, sys.argv[1:4])
phase = sys.argv[4]
results = {}
operations = (("directory_rename", folder),) if phase == "before_open" else (("directory_rename", folder), ("file_rename", file))
for label, source in operations:
    destination = source.with_name(source.name + "_moved")
    try:
        source.rename(destination)
    except OSError as error:
        results[label] = [error.winerror, error.errno]
    else:
        results[label] = "allowed"
        destination.rename(source)
if phase == "before_open":
    print(json.dumps(results))
    sys.exit(0)
try:
    os.replace(replacement, file)
except OSError as error:
    results["file_replace"] = [error.winerror, error.errno]
else:
    results["file_replace"] = "allowed"
try:
    with file.open("wb") as stream:
        stream.write(b"changed")
except OSError as error:
    results["file_write"] = [error.winerror, error.errno]
else:
    results["file_write"] = "allowed"
print(json.dumps(results))
'''
        read = reader._WindowsAPI._read_handle
        open_handle = reader._WindowsAPI._open
        attempts = []

        def attempt(phase):
            optimization = ['-O'] if sys.flags.optimize else []
            completed = subprocess.run(
                [sys.executable, *optimization, '-B', '-c', child,
                 str(self.folder), str(self.path), str(replacement), phase],
                capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            attempts.append((phase, json.loads(completed.stdout)))

        def interleave_open(api, path, directory):
            if not directory:
                attempt('before_open')
            return open_handle(api, path, directory)

        def interleave(api, handle):
            attempt('during_read')
            return read(api, handle)

        with patch.object(reader._WindowsAPI, '_read_handle', interleave):
            with patch.object(reader._WindowsAPI, '_open', interleave_open):
                self.assertEqual(reader.secure_read_bytes(self.root, self.path), self.body)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(set(attempts[0][1]), {'directory_rename'})
        self.assertEqual(set(attempts[1][1]), {
            'directory_rename', 'file_rename', 'file_replace', 'file_write'})
        for phase, results in attempts:
            for operation, error in results.items():
                self.assertNotEqual(error, 'allowed', f'{phase}/{operation} was allowed')
                self.assertTrue(error[0] in (5, 32) or error[1] == 13, (phase, operation, error))
        # After finally closes all handles, normal fixture operations work.
        moved = self.folder.with_name('after_close')
        self.folder.rename(moved)
        moved.rename(self.folder)
        self.path.write_bytes(self.body)


if __name__ == '__main__':
    unittest.main()
