"""Verify this data-delivery package; never run models or source notebooks."""
import argparse
import hashlib
import json
from pathlib import Path


def verify(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    records = manifest.get("files")
    if manifest.get("schema_version") != 1 or not isinstance(records, list) or not records:
        raise ValueError("A nonempty version-1 manifest is required")
    seen = set()
    for record in records:
        source = (root / record["path"]).resolve()
        if not source.is_relative_to(root):
            raise ValueError("Manifest path escapes the package")
        if source in seen:
            raise ValueError("Duplicate manifest path")
        seen.add(source)
        body = source.read_bytes()
        if len(body) != record["bytes"] or hashlib.sha256(body).hexdigest() != record["sha256"]:
            raise ValueError("File length or checksum differs: " + record["path"])
    return {"files_checked": len(records), "passed": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    print(json.dumps(verify(parser.parse_args().root), ensure_ascii=False))
