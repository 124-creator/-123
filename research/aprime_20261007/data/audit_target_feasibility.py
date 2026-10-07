"""Read-only availability diagnostics. No carbon forecasting or model fitting."""
from dataclasses import dataclass
import argparse
import csv
import datetime as dt
import hashlib
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from statistics import median
import sys


REGIMES = (
    ('regime_2021', '2021-07-16', '2023-08-28', ('CEA',), None),
    ('regime_2023', '2023-08-28', '2024-10-28', ('CEA', 'CEA21', 'CEA22'),
     'https://overview.cneeex.com/c/2023-08-25/494452.shtml'),
    ('regime_2024', '2024-10-28', '2025-04-29', ('CEA', 'CEA21', 'CEA22', 'CEA23'),
     'https://overview.cneeex.com/c/2024-10-25/495718.shtml'),
    ('regime_2025', '2025-04-29', '2026-01-05', ('CEA', 'CEA21', 'CEA22', 'CEA23', 'CEA24'),
     'https://overview.cneeex.com/c/2025-04-28/496173.shtml'),
    ('regime_2026', '2026-01-05', None, ('CEA25',),
     'https://overview.cneeex.com/c/2025-12-29/496985.shtml'),
)

FILES = {'composite': 'cea_composite_live.json', 'CEA': 'cea_19_20_live.json',
         **{f'CEA{i}': f'cea_vintage_CEA{i}.json' for i in range(21, 26)}}


def verify_frozen_file(path, expected_sha256, expected_bytes):
    body = Path(path).read_bytes()
    if len(body) != expected_bytes or hashlib.sha256(body).hexdigest() != expected_sha256:
        raise ValueError('Frozen checksum or byte-length mismatch')
    return body


@dataclass(frozen=True)
class Quote:
    date: str
    open: Decimal | None
    close: Decimal | None
    low: Decimal | None
    high: Decimal | None
    quantity: Decimal | None


def reported_decimal(value):
    if value is None or str(value).strip() in ('', '--', '—'):
        return None
    try:
        result = Decimal(str(value).strip())
    except InvalidOperation as error:
        raise ValueError('Invalid numeric token') from error
    if not result.is_finite():
        raise ValueError('Nonfinite reported number')
    return result


def read_quotes(path, cutoff):
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
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
        values = [reported_decimal(value) for value in row[1:]]
        result[date] = Quote(date, *values)
    return result


def scope_statistics(calendar, target, composite, selected_dates):
    """Describe quotes without dropping calendar gaps or certifying trading."""
    records = [target[date] for date in calendar
               if date in selected_dates and date in target]
    priced = [quote for quote in records if quote.close is not None]
    pairs = [(quote, composite[quote.date]) for quote in priced
             if quote.date in composite and composite[quote.date].close is not None]
    gaps = [abs(quote.close - comp.close) for quote, comp in pairs]
    previous = None
    flat_run = longest_run = comparisons = changes = 0
    changed_with_zero_quantity = changed_with_positive_quantity = 0
    for date in calendar:
        quote = target.get(date) if date in selected_dates else None
        if quote is None or quote.close is None:
            previous = None
            flat_run = 0
            continue
        if previous is None:
            flat_run = 1
        else:
            comparisons += 1
            changed = quote.close != previous.close
            changes += int(changed)
            changed_with_zero_quantity += int(changed and quote.quantity == 0)
            changed_with_positive_quantity += int(
                changed and quote.quantity is not None and quote.quantity > 0)
            flat_run = 1 if changed else flat_run + 1
        longest_run = max(longest_run, flat_run)
        previous = quote
    return {
        'target_rows': len(records),
        'target_quote_days': len(priced),
        'missing_close_days': len(records) - len(priced),
        'date_min': min((quote.date for quote in priced), default=None),
        'date_max': max((quote.date for quote in priced), default=None),
        'common_composite_quote_days': len(pairs),
        'unique_close_values': len({quote.close for quote in priced}),
        'nonpositive_close_days': sum(quote.close <= 0 for quote in priced),
        'adjacent_calendar_comparisons': comparisons,
        'changed_close_days': changes,
        'unchanged_close_days': comparisons - changes,
        'longest_unchanged_quote_run': longest_run,
        'reported_quantity_positive_days': sum(
            quote.quantity is not None and quote.quantity > 0 for quote in records),
        'reported_quantity_zero_days': sum(quote.quantity == 0 for quote in records),
        'reported_quantity_missing_days': sum(quote.quantity is None for quote in records),
        'reported_quantity_negative_days': sum(
            quote.quantity is not None and quote.quantity < 0 for quote in records),
        'changed_close_with_zero_reported_quantity_days': changed_with_zero_quantity,
        'changed_close_with_positive_reported_quantity_days': changed_with_positive_quantity,
        'exact_composite_equal_days': sum(gap == 0 for gap in gaps),
        'gap_nonzero_days': sum(gap != 0 for gap in gaps),
        'gap_gt_one_cent_days': sum(gap > Decimal('0.01') for gap in gaps),
        'gap_max_abs': str(max(gaps)) if gaps else None,
        'gap_median_abs': str(median(gaps)) if gaps else None,
        'actual_trade_status_certified': False,
    }


def forecast_availability(calendar, target, composite, selected_dates, *, h,
                          train_quotes, calibration_origins):
    """Availability bounds only; no fitted forecasts or tested performance.

    Calendar is the union of observed official quote dates, not an independently
    certified exchange calendar. Missing rows never shorten a horizon. A full
    recent window is a conservative no-imputation diagnostic, not the sole
    legitimate missing-data protocol. Prior history may span earlier regimes.
    """
    if h < 1 or train_quotes < 1 or calibration_origins < 0:
        raise ValueError('Invalid horizon or history sizes')
    if list(calendar) != sorted(set(calendar)):
        raise ValueError('Calendar must be sorted and unique')
    required = train_quotes + calibration_origins + h - 1
    shared = [date in target and target[date].close is not None
              and date in composite and composite[date].close is not None
              for date in calendar]
    prefix = [0]
    for present in shared:
        prefix.append(prefix[-1] + int(present))
    upper = []
    complete = []
    upper_changed = complete_changed = 0
    upper_positive_origin_quantity = complete_positive_origin_quantity = 0
    for i in range(max(0, len(calendar) - h)):
        date, end_date = calendar[i], calendar[i + h]
        if date not in selected_dates or end_date not in selected_dates or not shared[i]:
            continue
        future = target.get(end_date)
        if future is None or future.close is None:
            continue
        if prefix[i + 1] < required:
            continue
        upper.append(date)
        changed = future.close != target[date].close
        positive_quantity = target[date].quantity is not None and target[date].quantity > 0
        upper_changed += int(changed)
        upper_positive_origin_quantity += int(positive_quantity)
        start = i + 1 - required
        if start >= 0 and prefix[i + 1] - prefix[start] == required:
            complete.append(date)
            complete_changed += int(changed)
            complete_positive_origin_quantity += int(positive_quantity)
    return {
        'h_observed_union_calendar_steps': h,
        'initial_training_quotes': train_quotes,
        'calibration_origins': calibration_origins,
        'required_prior_shared_quotes_including_origin': required,
        'history_count_upper_bound_origins': len(upper),
        'complete_recent_window_origins': len(complete),
        'changed_target_endpoint_upper_bound_origins': upper_changed,
        'changed_target_endpoint_complete_window_origins': complete_changed,
        'positive_reported_quantity_at_origin_upper_bound_origins': upper_positive_origin_quantity,
        'positive_reported_quantity_at_origin_complete_window_origins': complete_positive_origin_quantity,
        'first_upper_bound_origin': min(upper, default=None),
        'last_upper_bound_origin': max(upper, default=None),
        'first_complete_window_origin': min(complete, default=None),
        'last_complete_window_origin': max(complete, default=None),
        'official_calendar_independently_certified': False,
        'past_history_can_span_other_regimes': True,
        'future_trade_state_used_for_eligibility': False,
        'future_target_variation_is_retrospective_diagnostic_only': True,
        'future_composite_quote_required_for_annual_target_scoring': False,
        'forecast_skill_estimated': False,
    }


def build_audit(repo_root, train_quotes=250, calibration_origins=80):
    root = Path(repo_root)
    manifest = json.loads((root / 'metadata/local_exchange_sources.json').read_text(encoding='utf-8'))
    by_filename = {record['filename']: record for record in manifest['sources']}
    cutoff = manifest['snapshot_date']
    series = {}
    receipt = []
    for target, filename in FILES.items():
        record = by_filename[filename]
        path = root / 'data/local_only' / filename
        verify_frozen_file(path, record['sha256'], record['bytes'])
        series[target] = read_quotes(path, cutoff)
        receipt.append({'target': target, 'filename': filename,
                        'sha256': record['sha256'], 'bytes': record['bytes'],
                        'source_url': record.get('source_url'),
                        'retrieved_utc': record.get('retrieved_utc'),
                        'hash_and_bytes_verified': True})
    calendar = sorted(set().union(*(quotes.keys() for quotes in series.values())))
    scopes = {'all': set(calendar), 'multi_component': set()}
    regimes = []
    for name, start, end, active, url in REGIMES:
        dates = {date for date in calendar if date >= start and (end is None or date < end)}
        scopes[name] = dates
        if len(active) > 1:
            scopes['multi_component'].update(dates)
        differences = []
        missing_component_days = 0
        for date in sorted(dates):
            observed = series['composite'].get(date)
            if observed is None or observed.close is None:
                continue
            parts = [series[code].get(date) for code in active]
            if any(part is None or part.close is None for part in parts):
                missing_component_days += 1
                continue
            expected = sum((part.close for part in parts), Decimal(0)) / Decimal(len(active))
            differences.append(abs(observed.close - expected))
        regimes.append({'scope': name, 'effective_from': start, 'until_exclusive': end,
                        'positive_components': list(active),
                        'equal_weight_candidate': '1' if len(active) == 1 else f'1/{len(active)}',
                        'rule_url': url,
                        'union_quote_dates': len(dates),
                        'composite_days_reconstructed': len(differences),
                        'unavailable_component_days': missing_component_days,
                        'differences_gt_one_cent': sum(value > Decimal('0.01') for value in differences),
                        'max_abs_reconstruction_difference': str(max(differences)) if differences else None})
    statistics = [{'target': target, 'scope': scope,
                   **scope_statistics(calendar, quotes, series['composite'], dates)}
                  for target, quotes in series.items() for scope, dates in scopes.items()]
    availability = [{'target': target, 'scope': scope,
                     **forecast_availability(calendar, quotes, series['composite'], dates,
                                              h=h, train_quotes=train_quotes,
                                              calibration_origins=calibration_origins)}
                    for target, quotes in series.items() if target != 'composite'
                    for scope, dates in scopes.items() for h in (1, 5)]
    return {
        'snapshot_date': cutoff,
        'executed_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'python_version': sys.version,
        'model_training_ran': False,
        'old_model_results_read': False,
        'originals_modified': False,
        'national_source_files_checked': len(receipt),
        'source_receipt': receipt,
        'calendar_union_quote_dates': len(calendar),
        'calendar_date_min': min(calendar), 'calendar_date_max': max(calendar),
        'composite_missing_union_dates': sorted(set(calendar) - set(series['composite'])),
        'official_exchange_calendar_certified': False,
        'first_public_vintages_verified': False,
        'quantity_zero_certifies_no_trade': False,
        'price_column_zero_based': 2, 'reported_quantity_column_zero_based': 5,
        'field_dictionary_current_round_status': 'Await separate official frontend/rule verification',
        'publication_scope': 'aggregate diagnostics only; no full original price panel copied',
        'history_gate_note': 'Availability bounds, not fitted calibration or achieved sample precision',
        'rules': regimes,
        'target_scope_statistics': statistics,
        'forecast_availability': availability,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--train-quotes', type=int, default=250)
    parser.add_argument('--calibration-origins', type=int, default=80)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(args.repo_root.resolve()):
        raise ValueError('Output must not modify the original repository')
    if output.exists():
        raise FileExistsError('Use a new output directory; never overwrite audit results')
    result = build_audit(args.repo_root, args.train_quotes, args.calibration_origins)
    output.mkdir(parents=True)
    (output / 'target_feasibility.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    for name, rows in [('target_scope_statistics', result['target_scope_statistics']),
                       ('forecast_availability', result['forecast_availability'])]:
        with (output / (name + '.csv')).open('w', encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps({'sources_checked': result['national_source_files_checked'],
                      'calendar_dates': result['calendar_union_quote_dates'],
                      'target_scope_records': len(result['target_scope_statistics']),
                      'availability_records': len(result['forecast_availability']),
                      'model_training_ran': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
