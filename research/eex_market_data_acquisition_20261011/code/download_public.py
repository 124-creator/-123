"""Acquire the single licensed author original, or verify existing bytes."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--proxy", help="Optional local network proxy; TLS verification stays enabled")
    parser.add_argument("--tempdir", type=Path, help="Existing permitted scratch directory for a new download")
    parser.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    root = arguments.root.resolve()
    contract = json.loads((root / "SOURCE_CONTRACT.json").read_text(encoding="utf-8"))
    if len(contract.get("sources", [])) != 1:
        raise ValueError("Exactly one frozen public source is required")
    record = contract["sources"][0]
    if record["source_url"] != "https://ndownloader.figshare.com/files/53279591":
        raise ValueError("Unapproved download endpoint")
    if record["sha256"] != "8617b185007c3f27c2bad593636aac2a6afc602d90ab048f5395bde048556985":
        raise ValueError("Unknown source version")
    original_path = (root / record["path"]).resolve()
    if not original_path.is_relative_to(root):
        raise ValueError("Frozen original path escapes the package")
    target = arguments.output.resolve() if arguments.output else original_path
    reused = target.exists()
    if reused:
        body = target.read_bytes()
    else:
        if arguments.verify_only:
            raise FileNotFoundError("No existing original to verify")
        curl = shutil.which("curl")
        if curl is None:
            raise RuntimeError("curl is required for a new download")
        scratch = arguments.tempdir or (Path(os.environ["TMPDIR"]) if os.environ.get("TMPDIR") else None)
        if scratch is None or not scratch.is_dir():
            raise ValueError("Provide an existing permitted --tempdir or TMPDIR")
        with tempfile.TemporaryDirectory(prefix="eua_public_download_", dir=scratch) as temporary:
            partial = Path(temporary) / "original.xlsx"
            command = [curl, "--fail", "--location", "--http1.1", "--silent", "--show-error",
                       "--connect-timeout", "12", "--max-time", "45", "--output", str(partial)]
            if arguments.proxy:
                command += ["--proxy", arguments.proxy]
            command += [record["source_url"]]
            subprocess.run(command, check=True, timeout=55)
            body = partial.read_bytes()
    if (len(body) != record["bytes"] or hashlib.sha256(body).hexdigest() != record["sha256"]
            or hashlib.md5(body).hexdigest() != record["publisher_md5"]):
        raise ValueError("Downloaded/existing bytes do not match the frozen original")
    if not reused:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as destination:
            destination.write(body)
    print(json.dumps({"verified": True, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                      "reused_existing_original": reused, "tls_verification_disabled": False}))
