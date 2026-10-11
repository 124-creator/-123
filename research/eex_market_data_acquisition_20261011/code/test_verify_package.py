"""Tests for the new data-delivery verifier; fixtures are NOT market data."""
import importlib.util
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path


class PackageChecks(unittest.TestCase):
    def test_empty_manifest_cannot_pass(self):
        module_path = Path(__file__).with_name("verify_package.py")
        if not module_path.exists():
            self.fail("The package verifier is not implemented yet")
        spec = importlib.util.spec_from_file_location("market_package_verifier", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Cannot load the package verifier")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        scratch = Path(os.environ["TMPDIR"])
        with tempfile.TemporaryDirectory(prefix="market_delivery_test_", dir=scratch) as directory:
            root = Path(directory)
            (root / "MANIFEST.json").write_text(
                json.dumps({"schema_version": 1, "files": []}), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                module.verify(root)

    def test_corrupted_file_cannot_pass(self):
        module_path = Path(__file__).with_name("verify_package.py")
        spec = importlib.util.spec_from_file_location("market_package_verifier", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Cannot load the package verifier")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix="market_delivery_test_", dir=Path(os.environ["TMPDIR"])) as directory:
            root = Path(directory)
            body = b"unit-test fixture, not market observations\n"
            (root / "fixture.txt").write_bytes(body + b"CORRUPTED")
            (root / "MANIFEST.json").write_text(json.dumps({
                "schema_version": 1,
                "files": [{"path": "fixture.txt", "bytes": len(body),
                           "sha256": hashlib.sha256(body).hexdigest()}],
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                module.verify(root)
    def test_duplicate_manifest_paths_cannot_inflate_count(self):
        spec = importlib.util.spec_from_file_location("market_package_verifier", Path(__file__).with_name("verify_package.py"))
        if spec is None or spec.loader is None:
            raise RuntimeError("Cannot load the package verifier")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix="market_delivery_test_", dir=Path(os.environ["TMPDIR"])) as directory:
            root = Path(directory)
            body = b"unit-test fixture, not market observations\n"
            (root / "fixture.txt").write_bytes(body)
            record = {"path": "fixture.txt", "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}
            (root / "MANIFEST.json").write_text(json.dumps({"schema_version": 1, "files": [record, record]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                module.verify(root)

    def test_manifest_cannot_escape_package_directory(self):
        spec = importlib.util.spec_from_file_location("market_package_verifier", Path(__file__).with_name("verify_package.py"))
        if spec is None or spec.loader is None:
            raise RuntimeError("Cannot load the package verifier")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix="market_delivery_test_", dir=Path(os.environ["TMPDIR"])) as directory:
            parent = Path(directory)
            root = parent / "package"
            root.mkdir()
            body = b"outside unit-test fixture, not market observations\n"
            (parent / "outside.txt").write_bytes(body)
            (root / "MANIFEST.json").write_text(json.dumps({
                "schema_version": 1,
                "files": [{"path": "../outside.txt", "bytes": len(body),
                           "sha256": hashlib.sha256(body).hexdigest()}],
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                module.verify(root)


if __name__ == "__main__":
    unittest.main()
