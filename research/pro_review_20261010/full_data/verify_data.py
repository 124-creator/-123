"""Verify the complete uploaded data against each original workbook cell."""
from pathlib import Path
import csv
from datetime import datetime
import hashlib
import io
import json
import math
import sys

import openpyxl

FIELDS = {
    "V": "Auction Volume tCO2", "B": "Total Amount of Bids",
    "bid_count": "Number of bids submitted", "successful_bid_count": "Number of successful bids",
    "mean_bids_per_bidder": "Average number of bids per bidder", "mean_bid_size": "Average bid size",
    "mu_B": "Average volume bid per bidder", "sd_B": "Standard deviation of bid volume per bidder",
    "mu_W": "Average volume won per bidder", "sd_W": "Standard deviation of volume won per bidder",
    "R": "Cover Ratio", "N": "Total Number of Bidders", "S": "Number of Successful Bidders",
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def rows_from_buffer(body):
    return list(csv.DictReader(io.StringIO(body.decode("utf-8-sig"))))


def verify(base):
    base = Path(base).resolve()
    manifest = json.loads((base / "INPUT_MANIFEST.json").read_bytes())
    records = manifest["files"]
    require(len(records) == 11 and len({r["path"] for r in records}) == 11, "Input manifest count/duplicate failure")
    buffers = {}
    for record in records:
        path = (base / record["path"]).resolve()
        require(path.is_relative_to(base), "Data path escape")
        body = path.read_bytes()
        require(len(body) == record["bytes"] and hashlib.sha256(body).hexdigest() == record["sha256"], "Source hash/length mismatch: " + record["path"])
        buffers[record["path"]] = body
    original_rows = {}
    for name, body in sorted(buffers.items()):
        if not name.startswith("raw/"):
            continue
        workbook = openpyxl.load_workbook(io.BytesIO(body), read_only=True, data_only=True, keep_links=False)
        require(workbook.sheetnames == ["Primary Market Auction"], "Unexpected sheet set")
        sheet = workbook["Primary Market Auction"]
        headers = next(sheet.iter_rows(min_row=6, max_row=6, values_only=True))
        index = {value: i for i, value in enumerate(headers) if value}
        require(all(value in index for value in FIELDS.values()), "Required header absent")
        for number, values in enumerate(sheet.iter_rows(min_row=7, values_only=True), 7):
            date = values[index["Date"]]
            if not isinstance(date, datetime):
                continue
            item = {field: values[index[label]] for field, label in FIELDS.items()}
            item.update(date=date.date().isoformat(), contract_raw=values[index["Contract"]], status_raw=values[index["Status"]], venue_raw=values[index["Country"]])
            original_rows[(Path(name).name, sheet.title, number)] = item
        workbook.close()
    extracted = rows_from_buffer(buffers["parsed/extraction_all_2020_2025.csv"])
    candidates = rows_from_buffer(buffers["parsed/candidate_dispersion.csv"])
    excluded = rows_from_buffer(buffers["parsed/row_exclusions.csv"])
    require(len(original_rows) == len(extracted) == 1327, "Full original extraction mismatch")
    require(len(candidates) == 1281 and len(excluded) == 46, "Candidate/exclusion count mismatch")
    seen = set()
    for row in extracted:
        key = (row["file"], row["sheet"], int(row["row"]))
        require(key not in seen and key in original_rows, "Duplicate or missing cell locator")
        seen.add(key)
        raw = original_rows[key]
        for field in FIELDS:
            value = raw[field]
            if value is None:
                require(row[field] == "", "Missing original was filled: " + field)
            else:
                require(float(row[field]) == float(value), "Original numeric value mismatch: " + field)
        require(all(row[field] == str(raw[field]) for field in ["date", "contract_raw", "status_raw", "venue_raw"]), "Original identity mismatch")
    def locator(row):
        return row["file"], row["sheet"], row["row"]
    selected = [row for row in extracted if row["contract_raw"] == "T3PA" and row["status_raw"] == "successful" and row["venue_raw"] in {"EU", "DE", "PL"}]
    require({locator(r) for r in selected} == {locator(r) for r in candidates}, "Sample selection differs from original rule")
    lookup = {locator(row): row for row in extracted}
    require(all(row == lookup[locator(row)] for row in candidates), "Candidate numeric/metadata content changed")
    require({locator(r) for r in candidates}.isdisjoint({locator(r) for r in excluded}), "Candidate and exclusion overlap")
    require({locator(r) for r in candidates} | {locator(r) for r in excluded} == set(lookup), "Exclusion ledger incomplete")
    positive = sum(all(math.isfinite(float(row[k])) and float(row[k]) > 0 for k in ["V", "B", "R", "N", "S", "mu_B", "mu_W", "sd_B", "sd_W"]) for row in candidates)
    require(positive == 1281, "Invalid candidate values")
    return {"passed": True, "original_workbooks": 6, "full_original_dated_rows": 1327, "candidate_rows": 1281, "excluded_rows": 46, "numeric_cells_compared": len(extracted) * len(FIELDS), "scope": "Source bytes, raw cell values, and complete sample selection; not official SD population/ddof or innovation certification"}


if __name__ == "__main__":
    print(json.dumps(verify(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent), ensure_ascii=False))
