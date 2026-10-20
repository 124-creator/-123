"""Pure qualification fixtures; no market forecasts, model fitting or old outputs."""
import importlib
import importlib.util
import hashlib
import unittest
from unittest.mock import patch
from typing import Any
from fractions import Fraction
import csv
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

core: Any
try:
    core = importlib.import_module('eligibility_core')
except ModuleNotFoundError:
    core = None


class QualificationTests(unittest.TestCase):
    def test_only_matured_pairs_count_at_the_forecast_origin(self):
        self.assertTrue(callable(getattr(core, 'count_mature_pairs', None)),
                        'Mature supervised-pair counting is not implemented')
        pairs = [(0, 5), (1, 6)]
        self.assertEqual(core.count_mature_pairs(pairs, 4), 0)
        self.assertEqual(core.count_mature_pairs(pairs, 5), 1)
        self.assertEqual(core.count_mature_pairs(pairs, 6), 2)

    def test_missing_endpoint_never_shortens_a_supervision_horizon(self):
        self.assertTrue(callable(getattr(core, 'supervision_pairs', None)),
                        'Fixed-index supervision is not implemented')
        features = [True, True, True, True, True]
        labels = [True, True, False, True, True]
        self.assertEqual(core.supervision_pairs(features, labels, 2),
                         [(1, 3), (2, 4)])

    def test_validation_labels_must_mature_before_evaluation(self):
        self.assertTrue(callable(getattr(core, 'qualification_schedule', None)),
                        'Sequential qualification schedule is not implemented')
        calendar = [f'2025-01-{i + 1:02d}' for i in range(14)]
        valid = [True] * len(calendar)
        result = core.qualification_schedule(calendar, valid, valid, valid, valid,
                                             h=2, minimum_train=2, validation_count=2)
        self.assertEqual(result['validation_indices'], [3, 4])
        self.assertEqual(result['parameter_freeze_index'], 6)
        self.assertTrue(result['validation_ready'])
        self.assertEqual(result['rows'][5]['phase'], 'wait_validation_labels')
        self.assertEqual(result['rows'][6]['phase'], 'evaluation')
        self.assertTrue(result['rows'][6]['issue_eligible'])

    def test_invalid_dates_flags_and_parameters_fail_closed(self):
        calendar = ['2025-01-01', '2025-01-02', '2025-01-03']
        valid = [True] * 3
        cases = [
            (calendar, valid, valid, valid, valid, 0, 1, 1),
            (calendar, valid, valid, valid, valid, 1, 0, 1),
            (calendar, valid, valid, valid, valid, 1, 1, 0),
            (calendar[::-1], valid, valid, valid, valid, 1, 1, 1),
            (calendar, valid[:-1], valid, valid, valid, 1, 1, 1),
            (calendar, [1, 1, 1], valid, valid, valid, 1, 1, 1),
        ]
        for dates, features, shared, target, scope, h, train, validation in cases:
            with self.subTest(dates=dates, h=h, train=train, validation=validation):
                with self.assertRaises(ValueError):
                    core.qualification_schedule(dates, features, shared, target, scope,
                                                h=h, minimum_train=train,
                                                validation_count=validation)
        with self.assertRaises(ValueError):
            core.count_mature_pairs([(0, 0)], 1)
        with self.assertRaises(ValueError):
            core.count_mature_pairs([(0, 2), (0, 2)], 2)

    def test_future_scoring_gaps_do_not_filter_issuance(self):
        calendar = [f'2025-01-{i + 1:02d}' for i in range(14)]
        valid = [True] * 14
        shared = valid.copy()
        shared[8] = False
        result = core.qualification_schedule(calendar, valid, shared, valid, valid,
                                             h=2, minimum_train=2, validation_count=2)
        row = result['rows'][6]
        self.assertTrue(row['issue_eligible'])
        self.assertTrue(row['target_scorable'])
        self.assertIn('score_reason', row, 'Scoring reasons must be explicit')
        target = valid.copy()
        target[8] = False
        missing = core.qualification_schedule(calendar, valid, shared, target, valid,
                                              h=2, minimum_train=2, validation_count=2)
        self.assertTrue(missing['rows'][6]['issue_eligible'])
        self.assertFalse(missing['rows'][6]['target_scorable'])
        self.assertEqual(missing['rows'][6]['score_reason'], 'target_endpoint_missing')
        self.assertEqual(missing['rows'][12]['score_reason'], 'endpoint_outside_snapshot')

    def test_feature_lookback_preserves_gaps_and_never_uses_future(self):
        self.assertTrue(callable(getattr(core, 'complete_history', None)),
                        'Past-only feature eligibility is not implemented')
        self.assertEqual(core.complete_history([True] * 5, 2),
                         [False, False, True, True, True])
        flags = [True, True, True, False, True]
        self.assertEqual(core.complete_history(flags, 2),
                         [False, False, True, False, False])
        with self.assertRaises(ValueError):
            core.complete_history([True], -1)

    def test_other_vintage_quote_excludes_the_target_without_filling_missing(self):
        self.assertTrue(callable(getattr(core, 'leave_target_out', None)),
                        'Target-excluded quote construction is not implemented')
        weights = {'P': '1/3', 'A': '1/3', 'B': '1/3'}
        self.assertEqual(core.leave_target_out({'P': 999, 'A': 10, 'B': 14},
                                               weights, 'P'), Fraction(12))
        self.assertIsNone(core.leave_target_out({'P': 999, 'A': 10, 'B': None},
                                                weights, 'P'))
        self.assertIsNone(core.leave_target_out({'P': 999}, {'P': '1'}, 'P'))
        with self.assertRaises(ValueError):
            core.leave_target_out({'P': 2, 'A': 3}, {'P': '1/3', 'A': '1/3'}, 'P')


class SyntheticInputTests(unittest.TestCase):
    """Synthetic qualification fixture; not official/market data or forecasts."""

    @classmethod
    def setUpClass(cls):
        # Reference only the trusted repository script, never fixture-root code.
        parser_path = (Path(__file__).resolve().parents[2]
                       / 'aprime_20261007/data/audit_target_feasibility.py')
        spec = importlib.util.spec_from_file_location('_qualification_fixture_reference', parser_path)
        if spec is None or spec.loader is None:
            raise RuntimeError('Trusted fixture reference parser is unavailable')
        cls.reference = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.reference
        spec.loader.exec_module(cls.reference)
        cls.audit = importlib.import_module('audit_supervised_eligibility')

    def setUp(self):
        scratch = os.environ.get('TMPDIR')
        if not scratch:
            raise RuntimeError('Set TMPDIR to the authorized scratch directory')
        temporary = tempfile.TemporaryDirectory(prefix='synthetic_qualification_fixture_', dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name).resolve()
        self.root = self.directory / 'synthetic_qualification_fixture'
        self.local_root = self.root / 'data/local_only'
        self.local_root.mkdir(parents=True)
        self.output = self.directory / 'qualification_output'
        self.manifest_path = self.root / 'metadata/local_exchange_sources.json'
        self.manifest_path.parent.mkdir(parents=True)
        self.body = json.dumps([
            ['2025-01-01', '12.50', '12.50', '12.50', '12.50', '--'],
            ['2025-01-02', '12.50', '12.50', '12.50', '12.50', '0'],
        ]).encode('utf-8')
        sources = []
        for filename in self.reference.FILES.values():
            (self.local_root / filename).write_bytes(self.body)
            sources.append({'filename': filename,
                            'sha256': hashlib.sha256(self.body).hexdigest(),
                            'bytes': len(self.body)})
        self.manifest = {'fixture_kind': 'synthetic qualification fixture',
                         'snapshot_date': '2025-01-02', 'sources': sources}
        self.write_manifest()
        rules_path = self.root / 'research/aprime_20261007/institution/market_rules.json'
        rules_path.parent.mkdir(parents=True)
        rules_path.write_text(json.dumps({
            'fixture_kind': 'synthetic qualification fixture',
            'regimes': [{'effective_from': '2021-01-01', 'effective_to': None,
                         'weights': {'CEA': '1/3', 'CEA21': '1/3', 'CEA22': '1/3'}}],
        }), encoding='utf-8')

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding='utf-8')

    def run_cli(self):
        script = Path(__file__).with_name('audit_supervised_eligibility.py')
        optimization = ['-O'] if sys.flags.optimize else []
        return subprocess.run([sys.executable, *optimization, '-B', str(script),
                               '--repo-root', str(self.root), '--output', str(self.output)],
                              capture_output=True, text=True, check=False)

    def test_empty_source_manifest_is_rejected(self):
        self.manifest['sources'] = []
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'Missing required source'):
            self.audit.build_reports(self.root)

    def test_every_required_input_must_be_listed_in_the_manifest(self):
        complete_sources = self.manifest['sources']
        for filename in self.reference.FILES.values():
            with self.subTest(missing=filename):
                self.manifest['sources'] = [source for source in complete_sources
                                            if source['filename'] != filename]
                self.write_manifest()
                with self.assertRaisesRegex(ValueError, 'Missing required source'):
                    self.audit.build_reports(self.root)

    def test_byte_parser_preserves_trusted_decimal_and_missing_value_semantics(self):
        parse: Any = getattr(self.audit, 'read_quotes_bytes', None)
        self.assertTrue(callable(parse), 'Verified-byte quote parsing is not implemented')
        filename = self.reference.FILES['CEA22']
        expected = self.audit.original.read_quotes(self.local_root / filename, '2025-01-02')
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('Unexpected path reread')):
            with patch.object(Path, 'read_text', side_effect=AssertionError('Unexpected path reread')):
                parsed = parse(self.body, '2025-01-02')
        self.assertEqual(parsed, expected)
        self.assertIsNone(parsed['2025-01-01'].quantity)
        self.assertEqual(str(parsed['2025-01-02'].close), '12.50')

    def test_byte_parser_rejects_malformed_frozen_quote_payloads(self):
        row = ['2025-01-01', '12.50', '12.50', '12.50', '12.50', '0']
        payloads = {
            'empty_list': [], 'object': {}, 'row_not_list': ['bad_row'],
            'wrong_width': [row[:-1]], 'date_not_text': [[20250101, *row[1:]]],
            'noncanonical_date': [['2025-1-01', *row[1:]]],
            'invalid_date': [['2025-02-30', *row[1:]]],
            'after_cutoff': [['2025-01-03', *row[1:]]],
            'duplicate_date': [row, row],
            'invalid_decimal': [[row[0], 'invalid', *row[2:]]],
            'nonfinite_decimal': [[row[0], 'NaN', *row[2:]]],
        }
        bodies = {name: json.dumps(payload).encode('utf-8')
                  for name, payload in payloads.items()}
        bodies.update({'invalid_json': b'{', 'invalid_utf8': b'\xff'})
        for name, body in bodies.items():
            with self.subTest(payload=name):
                try:
                    self.audit.read_quotes_bytes(body, '2025-01-02')
                except Exception as error:
                    self.assertIsInstance(error, ValueError)
                else:
                    self.fail('Malformed frozen quote payload was accepted')

    def test_cutoff_must_be_canonical_before_quote_parsing(self):
        september = json.dumps([
            ['2025-09-30', '1', '1', '1', '1', '0'],
        ]).encode('utf-8')
        # In the failed version lexical comparison accepts September under January.
        for cutoff in ('2025-1-2', '2025-02-30', '20250102', None, 20250102):
            with self.subTest(cutoff=cutoff):
                with self.assertRaisesRegex(ValueError, 'canonical ISO'):
                    self.audit.read_quotes_bytes(september, cutoff)
        self.manifest['snapshot_date'] = '2025-1-2'
        self.write_manifest()
        completed = self.run_cli()
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(self.output.exists())

    def test_rule_boundaries_require_canonical_dates_and_only_open_end_allows_none(self):
        path = self.root / 'research/aprime_20261007/institution/market_rules.json'
        initial = json.loads(path.read_text(encoding='utf-8'))
        for field, value in (
            ('effective_from', '2021-1-1'), ('effective_from', '20210101'),
            ('effective_from', '2021-02-30'), ('effective_from', None),
            ('effective_to', '2026-1-2'), ('effective_to', '20260102'),
            ('effective_to', '2026-02-30'), ('effective_to', 20260102),
        ):
            with self.subTest(field=field, value=value):
                rules = json.loads(json.dumps(initial))
                rules['regimes'][0][field] = value
                path.write_text(json.dumps(rules), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'canonical ISO'):
                    self.audit.build_reports(self.root)
        path.write_text(json.dumps(initial), encoding='utf-8')
        self.audit.build_reports(self.root)  # None is a valid declared open end.

    def test_metadata_summaries_hash_the_buffers_actually_parsed(self):
        # Controlled returned-buffer seam; no claim of a concurrent OS attack.
        paths = {
            self.manifest_path: ('source_manifest_sha256', 'source_manifest_bytes'),
            self.root / 'research/aprime_20261007/institution/market_rules.json':
                ('compilation_rules_sha256', 'compilation_rules_bytes'),
        }
        read = self.audit.secure_read_bytes
        parsed, calls = {}, {}
        loads = json.loads

        def varied_metadata(root, path):
            body = read(root, path)
            if path in paths:
                calls[path] = calls.get(path, 0) + 1
                if calls[path] == 1:
                    parsed[path] = body
                else:
                    # The old digest reread must not redefine which bytes were used.
                    return body + b' '
            return body

        decoded = []

        def record_parse(body, *args, **kwargs):
            decoded.append(body)
            return loads(body, *args, **kwargs)

        hashed = []
        sha256 = hashlib.sha256

        def record_hash(body):
            hashed.append(body)
            return sha256(body)

        # With the later stability check, a changed post-buffer must now reject,
        # while the initially used buffers still determine parsing and hashing.
        with patch.object(self.audit, 'secure_read_bytes', side_effect=varied_metadata):
            with patch.object(self.audit.json, 'loads', side_effect=record_parse):
                with patch.object(self.audit.hashlib, 'sha256', side_effect=record_hash):
                    with self.assertRaisesRegex(ValueError, 'Metadata changed'):
                        self.audit.build_reports(self.root)
        for path, (hash_field, byte_field) in paths.items():
            self.assertIn(parsed[path].decode('utf-8'), decoded)
            self.assertIn(parsed[path], hashed)
        # Stable real buffers must yield receipts for those very same buffers;
        # no ordinary Path read is allowed anywhere in the production I/O path.
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('Path-based input read')):
            with patch.object(Path, 'read_text', side_effect=AssertionError('Path-based input read')):
                summary, _ = self.audit.build_reports(self.root)
        for path, (hash_field, byte_field) in paths.items():
            self.assertEqual(summary[hash_field], sha256(parsed[path]).hexdigest())
            self.assertEqual(summary[byte_field], len(parsed[path]))

    def test_metadata_change_during_qualification_is_rejected_without_partial_report(self):
        paths = [self.manifest_path,
                 self.root / 'research/aprime_20261007/institution/market_rules.json']
        schedule = self.audit.qualification_schedule
        for path in paths:
            with self.subTest(metadata=path.name):
                self.output = self.directory / ('metadata_mismatch_' + path.stem)
                initial = path.read_bytes()
                changed = []

                def change_version(*args, **kwargs):
                    result = schedule(*args, **kwargs)
                    path.write_bytes(initial + b' ')
                    changed.append(path)
                    return result

                arguments = ['audit_supervised_eligibility.py', '--repo-root', str(self.root),
                             '--output', str(self.output)]
                try:
                    with patch.object(sys, 'argv', arguments):
                        with patch.object(self.audit, 'qualification_schedule', side_effect=change_version):
                            with self.assertRaisesRegex(ValueError, 'Metadata changed'):
                                self.audit.main()
                    self.assertEqual(changed, [path, path], 'Both target schedules must execute')
                    self.assertFalse(self.output.exists(), 'Metadata mismatch wrote a partial report')
                finally:
                    path.write_bytes(initial)

    def test_reports_parse_only_the_bytes_returned_by_frozen_verification(self):
        expected_summary, expected_rows = self.audit.build_reports(self.root)
        changed_path = self.local_root / self.reference.FILES['CEA22']
        transient_body = json.dumps([
            ['2024-12-31', '999', '999', '999', '999', '0'],
        ]).encode('utf-8')
        verify = self.audit.verify_frozen_file
        verified_names = set()
        reads = []
        self.addCleanup(changed_path.write_bytes, self.body)

        def transient_change(path, checksum, size, authorized_root):
            name = Path(path).name
            if name in verified_names:
                # Restore before the post-check, simulating a transient change.
                changed_path.write_bytes(self.body)
            body = verify(path, checksum, size, authorized_root)
            reads.append(name)
            verified_names.add(name)
            if len(reads) == len(self.manifest['sources']):
                changed_path.write_bytes(transient_body)
            return body

        with patch.object(self.audit, 'verify_frozen_file', side_effect=transient_change):
            summary, rows = self.audit.build_reports(self.root)
        self.assertEqual(rows, expected_rows, 'Qualification used unverified transient file bytes')
        self.assertEqual(summary['axis_date_count'], expected_summary['axis_date_count'])
        self.assertEqual(summary['targets'], expected_summary['targets'])
        for filename in self.reference.FILES.values():
            self.assertEqual(reads.count(filename), 2, 'Pre/post frozen verification must remain')

    def test_resolved_source_boundary_is_rechecked_after_qualification(self):
        # Deterministic resolution-race seam; physical escape tests are separate.
        source_path = self.local_root / self.reference.FILES['CEA22']
        outside_path = self.directory / 'outside_synthetic_qualification_fixture.json'
        outside_path.write_bytes(self.body)
        resolve = Path.resolve
        verify = self.audit.verify_frozen_file
        verified_paths = []

        def record_verification(path, checksum, size, authorized_root):
            body = verify(path, checksum, size, authorized_root)
            verified_paths.append(Path(path))
            return body

        def redirected_resolution(path, *args, **kwargs):
            if len(verified_paths) >= len(self.manifest['sources']) and path == source_path:
                return outside_path
            return resolve(path, *args, **kwargs)

        with patch.object(self.audit, 'verify_frozen_file', side_effect=record_verification):
            with patch.object(Path, 'resolve', autospec=True, side_effect=redirected_resolution):
                with self.assertRaisesRegex(ValueError, 'Unsafe'):
                    self.audit.build_reports(self.root)
        self.assertNotIn(outside_path, verified_paths)

    def test_actual_escaped_manifest_paths_are_rejected_without_output(self):
        outside_path = self.root / 'data/outside_synthetic_qualification_fixture.json'
        outside_path.write_bytes(self.body)
        complete_sources = self.manifest['sources']
        for name in ('../outside_synthetic_qualification_fixture.json', str(outside_path)):
            with self.subTest(filename=name):
                self.manifest['sources'] = [*complete_sources, {
                    'filename': name, 'sha256': hashlib.sha256(self.body).hexdigest(),
                    'bytes': len(self.body),
                }]
                self.write_manifest()
                completed = self.run_cli()
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn('ValueError: Unsafe', completed.stderr)
                self.assertFalse(self.output.exists(), 'Path rejection wrote a partial report')

    def test_required_input_symlink_cannot_escape_the_local_root(self):
        outside_path = self.directory / 'outside_synthetic_qualification_fixture.json'
        outside_path.write_bytes(self.body)
        source_path = self.local_root / self.reference.FILES['CEA22']
        source_path.unlink()
        try:
            source_path.symlink_to(outside_path)
        except NotImplementedError:
            self.skipTest('Filesystem symlinks unavailable; real escaped-path rejection is tested separately')
        except OSError as error:
            if (getattr(error, 'winerror', None) == 1314
                    or error.errno in (errno.EPERM, errno.EACCES, errno.ENOSYS)):
                self.skipTest('Symlink privilege unavailable; real escaped-path rejection is tested separately')
            raise
        self.assertFalse(source_path.resolve().is_relative_to(self.local_root.resolve()))
        completed = self.run_cli()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn('ValueError: Unsafe', completed.stderr)
        self.assertFalse(self.output.exists(), 'Symlink rejection wrote a partial report')

    def test_initial_local_root_junction_with_matching_bytes_is_rejected(self):
        if os.name != 'nt':
            self.skipTest('Real junction fixture requires Windows')
        outside = self.directory / 'outside_matching_originals'
        self.local_root.rename(outside)
        completed = subprocess.run(
            ['cmd.exe', '/d', '/c', 'mklink', '/J', str(self.local_root), str(outside)],
            capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        # Remove the junction itself, never traverse/delete its target.
        self.addCleanup(os.rmdir, self.local_root)
        self.assertEqual((outside / self.reference.FILES['CEA22']).read_bytes(), self.body)
        completed = self.run_cli()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn('ValueError: Unsafe', completed.stderr)
        self.assertFalse(self.output.exists(), 'Junction rejection wrote a partial report')
        self.assertEqual((outside / self.reference.FILES['CEA22']).read_bytes(), self.body)

    def test_empty_candidate_period_is_rejected_before_creating_output(self):
        rows = json.loads(self.body.decode('utf-8'))
        for row, date in zip(rows, ('2026-01-05', '2026-01-06')):
            row[0] = date
        body = json.dumps(rows).encode('utf-8')
        for source in self.manifest['sources']:
            (self.local_root / source['filename']).write_bytes(body)
            source['sha256'] = hashlib.sha256(body).hexdigest()
            source['bytes'] = len(body)
        self.manifest['snapshot_date'] = '2026-01-06'
        self.write_manifest()
        completed = self.run_cli()
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(self.output.exists(), 'Empty candidate period left a partial report')
        self.assertIn('ValueError: No candidate-period dates', completed.stderr)
        self.assertNotIn('IndexError', completed.stderr)

    def test_manifest_hash_and_length_mismatches_block_parsing_and_output(self):
        source = next(record for record in self.manifest['sources']
                      if record['filename'] == self.reference.FILES['CEA22'])
        expected = source.copy()
        for field, value in (('sha256', '0' * 64), ('bytes', len(self.body) + 1)):
            with self.subTest(mismatch=field):
                source.update(expected)
                source[field] = value
                self.write_manifest()
                completed = self.run_cli()
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn('ValueError: Frozen checksum or byte-length mismatch', completed.stderr)
                self.assertFalse(self.output.exists(), 'Failed byte verification wrote a partial report')

    def test_persistent_source_change_is_rejected_by_postcheck_before_output(self):
        source_path = self.local_root / self.reference.FILES['CEA22']
        parse = self.audit.read_quotes_bytes
        self.addCleanup(source_path.write_bytes, self.body)

        def change_after_parsing(body, cutoff):
            quotes = parse(body, cutoff)
            source_path.write_bytes(self.body + b' ')
            return quotes

        arguments = ['audit_supervised_eligibility.py', '--repo-root', str(self.root),
                     '--output', str(self.output)]
        with patch.object(sys, 'argv', arguments):
            with patch.object(self.audit, 'read_quotes_bytes', side_effect=change_after_parsing):
                with self.assertRaisesRegex(ValueError, 'Frozen checksum or byte-length mismatch'):
                    self.audit.main()
        self.assertFalse(self.output.exists(), 'Post-check failure left a partial report')

    def test_cli_uses_only_the_trusted_repository_parser(self):
        self.assertFalse((self.root / 'research/aprime_20261007/data').exists())
        completed = self.run_cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads((self.output / 'summary.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['parameters'], {
            'h_axis_steps': 5, 'lookback_axis_steps': 20,
            'minimum_mature_supervised_pairs': 250, 'sequential_validation_origins': 80,
        })
        self.assertEqual(summary['national_files_parsed'], len(self.reference.FILES))
        self.assertTrue(all(record['verified_before'] and record['verified_after']
                            for record in summary['source_receipts']))
        self.assertFalse(summary['official_calendar_certified'])
        self.assertFalse(summary['first_public_versions_certified'])
        self.assertFalse(summary['model_training_ran'])
        with (self.output / 'origin_eligibility.csv').open(encoding='utf-8-sig', newline='') as file:
            rows = list(csv.DictReader(file))
        self.assertTrue(rows)
        self.assertEqual(summary['origin_metadata_rows'], len(rows))
        forbidden = {'price', 'close', 'quantity', 'volume', 'prediction', 'error', 'P', 'C', 'Q'}
        self.assertFalse(forbidden.intersection(rows[0]))


class RealInputCommandTests(unittest.TestCase):
    def test_verified_originals_export_no_price_or_forecast_columns(self):
        root = Path(__file__).resolve().parents[3]
        snapshot = root / 'data/local_only/cea_vintage_CEA22.json'
        if not snapshot.exists():
            self.skipTest('Licensed-local snapshot absent from the public clone')
        script = Path(__file__).with_name('audit_supervised_eligibility.py')
        self.assertTrue(script.exists(), 'Supervised-eligibility CLI is not implemented')
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as directory:
            output = Path(directory) / 'qualification'
            optimization = ['-O'] if sys.flags.optimize else []
            completed = subprocess.run([sys.executable, *optimization, '-B', str(script),
                                        '--repo-root', str(root), '--output', str(output)],
                                       capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            summary = json.loads((output / 'summary.json').read_text(encoding='utf-8'))
            self.assertEqual(summary['national_files_parsed'], 7)
            self.assertFalse(summary['model_training_ran'])
            self.assertFalse(summary['official_calendar_certified'])
            with (output / 'origin_eligibility.csv').open(encoding='utf-8-sig', newline='') as file:
                rows = list(csv.DictReader(file))
            self.assertTrue(rows)
            forbidden = {'price', 'close', 'quantity', 'volume', 'prediction', 'error', 'P', 'C', 'Q'}
            self.assertFalse(forbidden.intersection(rows[0]))
            self.assertIn('target_flat_Q_updated_stable_weights',
                          {row['origin_state'] for row in rows})
            self.assertNotIn('target_flat_other_flat_stable_weights',
                             {row['origin_state'] for row in rows})
            self.assertEqual(summary['origin_metadata_rows'], len(rows))


if __name__ == '__main__':
    unittest.main()
