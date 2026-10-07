"""Unit fixtures only; not market data and not a forecasting experiment."""
import json
import hashlib
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

try:
    import audit_target_feasibility as audit
except ModuleNotFoundError:
    audit = None


class QuoteParsingTests(unittest.TestCase):
    def test_reads_close_and_preserves_unknown_quantity(self):
        self.assertIsNotNone(audit, "Quote parser has not been implemented")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.json'
            path.write_text(json.dumps([
                ['2026-01-05', '10', '12.25', '0', '0', '--'],
                ['2026-01-06', '12.25', '12.25', '12', '13', '0'],
            ]), encoding='utf-8')
            quotes = audit.read_quotes(path, cutoff='2026-10-07')
        self.assertEqual(str(quotes['2026-01-05'].close), '12.25')
        self.assertIsNone(quotes['2026-01-05'].quantity)
        self.assertEqual(str(quotes['2026-01-06'].quantity), '0')

    def test_rejects_length_conflict_even_with_matching_hash(self):
        self.assertTrue(callable(getattr(audit, 'verify_frozen_file', None)),
                        'Frozen file verification has not been implemented')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.json'
            body = b'[]'
            path.write_bytes(body)
            digest = hashlib.sha256(body).hexdigest()
            self.assertEqual(audit.verify_frozen_file(path, digest, 2), body)
            with self.assertRaises(ValueError):
                audit.verify_frozen_file(path, digest, 3)


class ScopeStatisticsTests(unittest.TestCase):
    def test_missing_calendar_date_breaks_change_and_flat_run(self):
        self.assertTrue(callable(getattr(audit, 'scope_statistics', None)),
                        'Calendar-preserving scope statistics are not implemented')
        calendar = ['2026-01-05', '2026-01-06', '2026-01-07', '2026-01-08']
        def quote(date, price, quantity):
            return audit.Quote(date, Decimal(price), Decimal(price), None, None,
                               None if quantity is None else Decimal(quantity))
        target = {calendar[0]: quote(calendar[0], '10', '0'),
                  calendar[2]: quote(calendar[2], '12', None),
                  calendar[3]: quote(calendar[3], '12', '1')}
        composite = {date: quote(date, '10', '1') for date in calendar}
        stats = audit.scope_statistics(calendar, target, composite, set(calendar))
        self.assertEqual(stats['target_quote_days'], 3)
        self.assertEqual(stats['adjacent_calendar_comparisons'], 1)
        self.assertEqual(stats['changed_close_days'], 0)
        self.assertEqual(stats['longest_unchanged_quote_run'], 2)
        self.assertEqual(stats['reported_quantity_zero_days'], 1)
        self.assertEqual(stats['reported_quantity_missing_days'], 1)
        self.assertEqual(stats['reported_quantity_positive_days'], 1)
        self.assertEqual(stats['gap_gt_one_cent_days'], 2)


class ForecastAvailabilityTests(unittest.TestCase):
    def test_keeps_calendar_horizons_and_exposes_history_gaps(self):
        self.assertTrue(callable(getattr(audit, 'forecast_availability', None)),
                        'Forecast-origin availability is not implemented')
        calendar = [f'2026-01-{day:02d}' for day in range(5, 11)]
        def quote(date):
            return audit.Quote(date, Decimal('10'), Decimal('10'), None, None, None)
        target = {date: quote(date) for i, date in enumerate(calendar) if i != 2}
        composite = {date: quote(date) for date in calendar}
        simple = audit.forecast_availability(calendar, target, composite,
                                             set(calendar), h=1, train_quotes=1,
                                             calibration_origins=0)
        self.assertEqual(simple['history_count_upper_bound_origins'], 3)
        gated = audit.forecast_availability(calendar, target, composite,
                                            set(calendar), h=1, train_quotes=2,
                                            calibration_origins=1)
        self.assertEqual(gated['history_count_upper_bound_origins'], 2)
        self.assertEqual(gated['complete_recent_window_origins'], 0)
        self.assertEqual(gated['first_upper_bound_origin'], calendar[3])

    def test_endpoint_variation_is_diagnostic_not_a_selection_filter(self):
        calendar = [f'2026-01-{day:02d}' for day in range(5, 9)]
        target = {date: audit.Quote(date, Decimal('10'), Decimal('10'), None, None,
                                    Decimal('0')) for date in calendar}
        result = audit.forecast_availability(calendar, target, target, set(calendar),
                                            h=1, train_quotes=1, calibration_origins=0)
        self.assertIn('changed_target_endpoint_upper_bound_origins', result,
                      'Retrospective endpoint diagnostics are not implemented')
        self.assertEqual(result['history_count_upper_bound_origins'], 3)
        self.assertEqual(result['changed_target_endpoint_upper_bound_origins'], 0)
        self.assertFalse(result['future_trade_state_used_for_eligibility'])


class AuditCommandTests(unittest.TestCase):
    def test_command_exports_only_aggregate_counts_from_verified_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / 'repo'
            raw = repo / 'data' / 'local_only'
            raw.mkdir(parents=True)
            specs = [('composite', 'cea_composite_live.json'), ('CEA', 'cea_19_20_live.json')]
            specs.extend((f'CEA{i}', f'cea_vintage_CEA{i}.json') for i in range(21, 26))
            records = []
            for _, filename in specs:
                body = json.dumps([
                    ['2026-01-05', '10', '10', '0', '0', '0'],
                    ['2026-01-06', '10', '10', '0', '0', '0'],
                ]).encode('utf-8')
                (raw / filename).write_bytes(body)
                records.append({'filename': filename, 'bytes': len(body),
                                'sha256': hashlib.sha256(body).hexdigest()})
            (repo / 'metadata').mkdir()
            (repo / 'metadata' / 'local_exchange_sources.json').write_text(
                json.dumps({'snapshot_date': '2026-10-07', 'sources': records}), encoding='utf-8')
            output = Path(directory) / 'output'
            completed = subprocess.run([
                sys.executable, str(Path(__file__).with_name('audit_target_feasibility.py')),
                '--repo-root', str(repo), '--output', str(output),
                '--train-quotes', '1', '--calibration-origins', '0',
            ], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((output / 'target_feasibility.json').is_file(),
                            'Aggregate audit command has not been implemented')
            result = json.loads((output / 'target_feasibility.json').read_text(encoding='utf-8'))
            self.assertFalse(result['model_training_ran'])
            self.assertEqual(result['national_source_files_checked'], 7)
            self.assertEqual(result['calendar_union_quote_dates'], 2)
            self.assertEqual(len(result['target_scope_statistics']), 49)
            self.assertEqual(len(result['forecast_availability']), 84)
            cea25 = next(item for item in result['target_scope_statistics']
                         if item['target'] == 'CEA25' and item['scope'] == 'regime_2026')
            self.assertEqual(cea25['exact_composite_equal_days'], 2)


if __name__ == '__main__':
    unittest.main()
