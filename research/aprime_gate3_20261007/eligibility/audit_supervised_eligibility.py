"""Recount supervised qualification from frozen originals; never fit forecasts."""
import argparse
from collections import Counter
import csv
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from eligibility_core import complete_history, leave_target_out, qualification_schedule
from secure_snapshot_reader import secure_read_bytes, validate_root


def _load_trusted_original():
    """Load parser definitions from this repository, not from --repo-root."""
    parser_path = (Path(__file__).resolve().parents[2]
                   / 'aprime_20261007/data/audit_target_feasibility.py')
    spec = importlib.util.spec_from_file_location('_supervised_eligibility_original', parser_path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Trusted quote parser is unavailable')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


original = _load_trusted_original()


def canonical_date(value):
    """Reject source tokens rather than repairing lexical date comparisons."""
    if type(value) is not str:
        raise ValueError('Date must retain canonical ISO format')
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as error:
        raise ValueError('Date must retain canonical ISO format') from error
    if parsed.isoformat() != value:
        raise ValueError('Date must retain canonical ISO format')
    return value


def read_quotes_bytes(body, cutoff):
    """Parse a verified UTF-8 snapshot without reopening its source path."""
    canonical_date(cutoff)
    raw = json.loads(body.decode('utf-8'))
    if not isinstance(raw, list) or not raw:
        raise ValueError('Expected a nonempty list of six-column quotes')
    result = {}
    for row in raw:
        if not isinstance(row, list) or len(row) != 6:
            raise ValueError('Unexpected quote row width')
        date = row[0]
        if not isinstance(date, str) or dt.date.fromisoformat(date).isoformat() != date:
            raise ValueError('Date must retain canonical ISO format')
        if date > cutoff:
            raise ValueError('Observation later than frozen cutoff')
        if date in result:
            raise ValueError('Duplicate date must not be silently deduplicated')
        values = [original.reported_decimal(value) for value in row[1:]]
        result[date] = original.Quote(date, *values)
    return result


def verify_frozen_file(path, expected_sha256, expected_bytes, authorized_root):
    body = secure_read_bytes(authorized_root, path)
    if len(body) != expected_bytes or hashlib.sha256(body).hexdigest() != expected_sha256:
        raise ValueError('Frozen checksum or byte-length mismatch')
    return body


def source_path(local_root, name):
    if (type(name) is not str or not name or Path(name).name != name
            or '/' in name or '\\' in name):
        raise ValueError('Unsafe original filename')
    path = local_root / name
    # Additional fail-closed diagnostic only. Never use resolve as I/O authority.
    if not path.resolve().is_relative_to(local_root):
        raise ValueError('Unsafe original filename boundary')
    return path


def build_reports(repo_root, *, h=5, lookback=20, minimum_train=250, validation_count=80):
    root = validate_root(repo_root)

    manifest_path = root / 'metadata/local_exchange_sources.json'
    rules_path = root / 'research/aprime_20261007/institution/market_rules.json'
    manifest_body = secure_read_bytes(root, manifest_path)
    rules_body = secure_read_bytes(root, rules_path)
    manifest_sha256 = hashlib.sha256(manifest_body).hexdigest()
    rules_sha256 = hashlib.sha256(rules_body).hexdigest()
    manifest = json.loads(manifest_body.decode('utf-8'))
    canonical_date(manifest['snapshot_date'])
    rules = json.loads(rules_body.decode('utf-8'))['regimes']
    for rule in rules:
        canonical_date(rule['effective_from'])
        if rule['effective_to'] is not None:
            canonical_date(rule['effective_to'])
            if rule['effective_to'] < rule['effective_from']:
                raise ValueError('Compilation regime ends before it begins')
    sources = manifest['sources']
    if not sources:
        raise ValueError('Missing required source manifest entries')
    local_root = root / 'data/local_only'
    frozen_bytes = {}
    receipts = []
    for source in sources:
        name = source['filename']
        path = source_path(local_root, name)
        if name in frozen_bytes:
            raise ValueError('Unsafe or duplicate original filename')
        frozen_bytes[name] = verify_frozen_file(path, source['sha256'], source['bytes'], local_root)
        receipts.append({'filename': name, 'sha256': source['sha256'],
                         'bytes': source['bytes'], 'verified_before': True})
    missing = sorted(set(original.FILES.values()) - frozen_bytes.keys())
    if missing:
        raise ValueError('Missing required source manifest entries: ' + ', '.join(missing))
    series = {code: read_quotes_bytes(frozen_bytes[filename], manifest['snapshot_date'])
              for code, filename in original.FILES.items()}
    calendar = sorted(set().union(*(quotes.keys() for quotes in series.values())))
    period = [date >= '2023-08-28' and date < '2026-01-05' for date in calendar]
    if not any(period):
        raise ValueError('No candidate-period dates in the frozen quote snapshot')
    regimes = []
    for date in calendar:
        matches = [rule for rule in rules if date >= rule['effective_from']
                   and (rule['effective_to'] is None or date <= rule['effective_to'])]
        if len(matches) != 1:
            raise ValueError('Compilation regimes do not uniquely cover the date axis')
        regimes.append(matches[0])
    target_results = []
    all_rows = []
    for target in ('CEA22', 'CEA21'):
        p = [series[target][date].close if date in series[target] else None for date in calendar]
        c = [series['composite'][date].close if date in series['composite'] else None for date in calendar]
        q = []
        for i, date in enumerate(calendar):
            weights = regimes[i]['weights']
            prices = {code: series[code][date].close if date in series[code] else None
                      for code in weights}
            q.append(leave_target_out(prices, weights, target))
        p_history = complete_history([value is not None for value in p], lookback)
        c_history = complete_history([value is not None for value in c], lookback)
        q_history = complete_history([value is not None for value in q], lookback)
        features = [p_history[i] and c_history[i] and q_history[i] and period[i]
                    for i in range(len(calendar))]
        shared_labels = [p[i] is not None and c[i] is not None for i in range(len(calendar))]
        target_labels = [value is not None for value in p]
        schedule = qualification_schedule(calendar, features, shared_labels, target_labels, period,
                                          h=h, minimum_train=minimum_train,
                                          validation_count=validation_count)
        rows = []
        for row in schedule['rows']:
            i, end = row['origin_index'], row['endpoint_index']
            if not period[i]:
                continue
            reasons = []
            if not p_history[i]:
                reasons.append('target_history_incomplete')
            if not c_history[i]:
                reasons.append('composite_history_incomplete')
            if not q_history[i]:
                reasons.append('non_target_vintages_history_incomplete')
            state = 'state_unknown'
            if i > 0 and all(value is not None for value in (p[i], p[i - 1], q[i], q[i - 1])):
                if regimes[i]['weights'] != regimes[i - 1]['weights']:
                    state = 'weight_change_at_origin'
                elif p[i] != p[i - 1]:
                    state = 'target_updated_stable_weights'
                elif q[i] != q[i - 1]:
                    state = 'target_flat_Q_updated_stable_weights'
                else:
                    state = 'target_flat_Q_flat_stable_weights'
            origin_regime = regimes[i]['effective_from']
            endpoint_regime = regimes[end]['effective_from'] if end < len(calendar) else None
            rows.append({**row, 'target': target,
                         'axis': 'observed_quote_date_union_uncertified',
                         'feature_missing_reasons': ';'.join(reasons),
                         'origin_regime': origin_regime, 'endpoint_regime': endpoint_regime,
                         'cross_regime_horizon': endpoint_regime is not None and endpoint_regime != origin_regime,
                         'origin_state': state,
                         'actual_forecast_produced': False})
        evaluation = [row for row in rows if row['phase'] == 'evaluation']
        scored = [row for row in evaluation if row['target_scorable']]
        validation = [row for row in rows if row['phase'] == 'validation']
        freeze = schedule['parameter_freeze_index']
        target_results.append({
            'target': target, 'candidate_period_metadata_rows': len(rows),
            'phase_counts': dict(sorted(Counter(row['phase'] for row in rows).items())),
            'validation_origin_count': len(validation),
            'validation_targets_available': schedule['validation_ready'],
            'first_validation_origin': validation[0]['origin_date'] if validation else None,
            'last_validation_origin': validation[-1]['origin_date'] if validation else None,
            'parameter_selection_not_before_date_on_axis': calendar[freeze] if freeze is not None else None,
            'evaluation_issue_eligible_count': len(evaluation),
            'evaluation_scorable_count': len(scored),
            'evaluation_unscorable_reasons': dict(sorted(Counter(
                row['score_reason'] for row in evaluation if not row['target_scorable']).items())),
            'first_scorable_evaluation_origin': scored[0]['origin_date'] if scored else None,
            'last_scorable_evaluation_origin': scored[-1]['origin_date'] if scored else None,
            'scorable_cross_regime_count': sum(row['cross_regime_horizon'] for row in scored),
            'scorable_by_origin_state': dict(sorted(Counter(row['origin_state'] for row in scored).items())),
            'scorable_by_origin_regime': dict(sorted(Counter(row['origin_regime'] for row in scored).items())),
        })
        all_rows.extend(rows)
    for receipt in receipts:
        path = source_path(local_root, receipt['filename'])
        verify_frozen_file(path, receipt['sha256'], receipt['bytes'], local_root)
        receipt['verified_after'] = True
    if secure_read_bytes(root, manifest_path) != manifest_body:
        raise ValueError('Metadata changed during qualification: source manifest')
    if secure_read_bytes(root, rules_path) != rules_body:
        raise ValueError('Metadata changed during qualification: compilation rules')
    summary = {
        'schema_version': 1, 'snapshot_date': manifest['snapshot_date'],
        'executed_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'python_version': sys.version, 'model_training_ran': False,
        'old_scores_used': False, 'actual_forecasts_produced': 0,
        'national_files_parsed': len(series), 'frozen_files_verified': len(receipts),
        'source_receipts': receipts,
        'source_manifest_sha256': manifest_sha256,
        'source_manifest_bytes': len(manifest_body),
        'compilation_rules_sha256': rules_sha256,
        'compilation_rules_bytes': len(rules_body),
        'axis_type': 'observed_quote_date_union_uncertified',
        'axis_date_count': len(calendar), 'official_calendar_certified': False,
        'first_public_versions_certified': False, 'session_quote_publication_times_certified': False,
        'historical_target_selection_used_full_snapshot': True,
        'research_gate': 'pause_for_official_calendar_and_nearest_neighbor_judgment',
        'protocol_execution_approved': False,
        'parameters': {'h_axis_steps': h, 'lookback_axis_steps': lookback,
                       'minimum_mature_supervised_pairs': minimum_train,
                       'sequential_validation_origins': validation_count},
        'training_label_rule': 'Common P and C endpoint availability for matched direct/split supervision',
        'validation_scoring_rule': 'P endpoint only; no future C or Q required',
        'issuance_rule': 'Past-complete P/C/Q input, matured shared labels, sequential phase; no future variation/trade filter',
        'quantity_missing_rule': 'Quantity is not an eligibility filter; future training needs explicit missing indicators',
        'provisional_day_availability_assumption': 'A frozen quote is treated as known after its dated session; actual timestamps unverified',
        'origin_metadata_rows': len(all_rows), 'targets': target_results,
        'public_payload': 'Date/qualification/state metadata only; no price, quantity, forecasts or forecast errors',
    }
    return summary, all_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--h', type=int, default=5)
    parser.add_argument('--lookback', type=int, default=20)
    parser.add_argument('--minimum-train', type=int, default=250)
    parser.add_argument('--validation-count', type=int, default=80)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(args.repo_root.resolve()) or output.exists():
        raise ValueError('Use a new output directory outside the source repository')
    summary, rows = build_reports(args.repo_root, h=args.h, lookback=args.lookback,
                                  minimum_train=args.minimum_train,
                                  validation_count=args.validation_count)
    output.mkdir(parents=True)
    (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    with (output / 'origin_eligibility.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({'targets': summary['targets'], 'model_training_ran': False,
                      'official_calendar_certified': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
