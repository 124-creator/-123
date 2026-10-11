"""Read verified auction originals; add baseline controls without fitting.
Requires the local frozen full_24quarters_2020_2025 package. No downloads.
"""
import argparse
import csv
from datetime import datetime
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import stat

import openpyxl

FIELDS = {
    'reported_cover_ratio': 'Cover Ratio',
    'minimum_bid_price_eur': 'Minimum Bid €/tCO2',
    'maximum_bid_price_eur': 'Maximum Bid €/tCO2',
    'mean_bid_price_eur': 'Mean €/tCO2',
    'median_bid_price_eur': 'Median €/tCO2',
    'bids_submitted_count': 'Number of bids submitted',
    'successful_bids_count': 'Number of successful bids',
}
EXISTING_QUANTITIES = {
    'auction_volume_tCO2': 'Auction Volume tCO2',
    'bid_volume_tCO2': 'Total Amount of Bids',
    'reported_mean_bid_volume': 'Average volume bid per bidder',
    'reported_SD_bid_volume': 'Standard deviation of bid volume per bidder',
    'reported_mean_won_volume': 'Average volume won per bidder',
    'reported_SD_won_volume': 'Standard deviation of volume won per bidder',
    'total_bidders': 'Total Number of Bidders',
    'successful_bidders': 'Number of Successful Bidders',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ordinary_path(path):
    for p in (path, *path.parents):
        if p.exists():
            st = p.lstat()
            require(not p.is_symlink() and not
                    getattr(st, 'st_file_attributes', 0) &
                    getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400),
                    'Symlink/reparse path refused')
            if p.is_file():
                require(st.st_nlink == 1, 'Hard-linked input refused')


def build(source, out):
    ordinary_path(source)
    ordinary_path(out)
    source = source.resolve()
    out = out.resolve()
    require(not out.exists(), 'Output already exists; no overwrite allowed')
    require(not out.is_relative_to(source), 'Output inside frozen input refused')
    require(not source.is_relative_to(out), 'Output encloses source')
    manifest_body = (source / 'MANIFEST.json').read_bytes()
    manifest = json.loads(manifest_body)
    records = manifest['files']
    specs = {r['path']: r for r in records}
    require(bool(specs) and len(specs) == len(records), 'Invalid input manifest')
    read_inputs = []

    def load(relative):
        require(relative in specs, 'Parser input absent from frozen manifest')
        p = source / relative
        ordinary_path(p)
        require(p.resolve().is_relative_to(source), 'Input boundary escape')
        b = p.read_bytes()
        s = specs[relative]
        require(len(b) == s['bytes'] and hashlib.sha256(b).hexdigest() == s['sha256'],
                'Source checksum or length conflict')
        read_inputs.append(dict(s))
        return b

    panel = list(csv.DictReader(io.StringIO(load(
        'data/official_reported_cutoff_all275.csv').decode('utf-8-sig'), newline='')))
    require(len(panel) == 275, 'Frozen panel row count differs')
    old_fields = list(panel[0])
    new_fields = [*FIELDS, 'cover_ratio_from_quantities', 'bid_price_range_eur']
    require(not set(new_fields) & set(old_fields), 'Output field would overwrite input')
    index = json.loads(load('EEX_ORIGINAL_INPUT_INDEX.json'))
    require({r['year'] for r in index['inputs']} == set(range(2020, 2026)),
            'Annual source coverage differs')
    require(len(index['inputs']) == 6, 'Duplicate source year')
    native = {}
    for src in index['inputs']:
        b = load(src['relative_path'])
        require(hashlib.sha256(b).hexdigest() == src['sha256'], 'Index hash conflict')
        wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
        sheet = wb['Primary Market Auction']
        sheet.reset_dimensions()
        rows = list(sheet.iter_rows(max_col=65, values_only=True))
        h = {v: i for i, v in enumerate(rows[5]) if v is not None}
        require(all(k in h for k in [*FIELDS.values(), *EXISTING_QUANTITIES.values(),
                    'Date', 'Country', 'Contract', 'Status', 'Auction Price €/tCO2']),
                'Native header missing')
        for row_no, values in enumerate(rows, 1):
            dt = values[h['Date']]
            if not isinstance(dt, datetime):
                continue
            if (values[h['Country']], values[h['Contract']], values[h['Status']]) != (
                    'DE', 'T3PA', 'successful'):
                continue
            key = dt.date().isoformat()
            require(key not in native, 'Nonunique native date')
            native[key] = (values, h, row_no, src)
        wb.close()
    require(set(native) == {r['auction_date'] for r in panel}, 'Native date set conflict')
    enriched, missing, cover_conflicts = [], {k: 0 for k in FIELDS}, []
    for old in panel:
        row = dict(old)
        values, h, physical_row, src = native[old['auction_date']]
        require(str(physical_row) == old['eex_row_1based'] and
                src['sha256'] == old['eex_original_sha256'], 'Native row identity differs')
        require(Decimal(old['auction_price_eur_tCO2']) ==
                Decimal(str(values[h['Auction Price €/tCO2']])), 'Auction price differs')
        for key, label in EXISTING_QUANTITIES.items():
            value = values[h[label]]
            require(old[key] == ('' if value is None else str(value)),
                    'Original quantity field differs')
        for key, label in FIELDS.items():
            value = values[h[label]]
            row[key] = '' if value is None else str(value)
            missing[key] += value is None
            if value is not None:
                require(Decimal(str(value)).is_finite(), 'Nonfinite source control')
        require(Decimal(old['auction_volume_tCO2']) > 0, 'Invalid volume denominator')
        ratio = Decimal(old['bid_volume_tCO2']) / Decimal(old['auction_volume_tCO2'])
        row['cover_ratio_from_quantities'] = str(ratio)
        row['bid_price_range_eur'] = ''
        if row['minimum_bid_price_eur'] and row['maximum_bid_price_eur']:
            spread = Decimal(row['maximum_bid_price_eur']) - Decimal(row['minimum_bid_price_eur'])
            require(spread >= 0, 'Reversed native price extrema')
            row['bid_price_range_eur'] = str(spread)
        if row['reported_cover_ratio'] and abs(
                Decimal(row['reported_cover_ratio']) - ratio) > Decimal('0.0050000001'):
            cover_conflicts.append(old['auction_date'])
        require(row['primary_pilot_eligible'] in {'True', 'False'}, 'Invalid eligibility')
        enriched.append(row)
    strict = [r for r in enriched if r['primary_pilot_eligible'] == 'True']
    excluded = [r for r in enriched if r['primary_pilot_eligible'] == 'False']
    noflags = [r for r in strict if not r['source_flags']]
    require((len(strict), len(excluded), len(noflags)) == (240, 35, 203), 'Partition changed')
    summary = {
        'all_rows': len(enriched), 'strict_rows': len(strict), 'excluded_rows': len(excluded),
        'no_source_flag_rows': len(noflags), 'added_raw_columns': len(FIELDS),
        'added_derived_columns': 2, 'missing_by_raw_field': missing,
        'cover_ratio_deviations_over_half_0_01_unit': cover_conflicts,
        'original_field_values_preserved': True, 'new_observations': 0, 'new_model_fits': 0,
        'native_ticks': 0, 'base_manifest_sha256': hashlib.sha256(manifest_body).hexdigest(),
        'actual_parser_inputs': read_inputs,
        'source_originals_not_bundled': True,
        'security_scope': 'Static ordinary-path checks, not TOCTOU sandbox or output transaction',
    }
    dictionary = {
        'original_fields': FIELDS,
        'derived_fields': {'cover_ratio_from_quantities': 'bid_volume_tCO2 / auction_volume_tCO2',
                           'bid_price_range_eur': 'maximum_bid_price_eur - minimum_bid_price_eur'},
        'scope': 'Completed-auction descriptive controls, not pre-auction predictors or secondary quotes',
        'price_range_warning': 'Submitted-price range, not price SD, bid-ask spread, or raw secondary benchmark',
        'missing_policy': 'Preserve blanks; do not impute zero or silently change eligibility',
        'scaling_warning': 'Raw EUR price range can vary with price level; no hidden normalization by outcome',
        'rank_warning': 'Do not include log B, log V and log(B/V) together with an intercept',
    }
    # Everything is validated in memory before an exclusive new output directory is created.
    out.mkdir(parents=True, exist_ok=False)
    (out / 'data').mkdir()
    for name, rows in [('all275', enriched), ('strict240', strict), ('excluded35', excluded),
                       ('noflags203', noflags)]:
        with (out / 'data' / ('controls_' + name + '.csv')).open(
                'x', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=old_fields + new_fields)
            writer.writeheader()
            writer.writerows(rows)
    for name, data in [('SUMMARY.json', summary), ('FIELD_DICTIONARY.json', dictionary)]:
        with (out / name).open('x', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
    entries = []
    for p in sorted(out.rglob('*')):
        if p.is_file():
            b = p.read_bytes()
            entries.append({'path': p.relative_to(out).as_posix(), 'bytes': len(b),
                            'sha256': hashlib.sha256(b).hexdigest()})
    with (out / 'MANIFEST.json').open('x', encoding='utf-8') as f:
        json.dump({'schema_version': 1, 'files': entries}, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.source_root, args.out), ensure_ascii=False))
