import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_manifest.py"


class AuditManifestTests(unittest.TestCase):
    def run_audit(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPT), str(path), "--json"], text=True, capture_output=True)

    def test_valid_manifest(self):
        payload = {"products": [{"id": "p1", "title": "Shirt", "source_url": "https://example.com/p1", "images": ["https://example.com/p1.jpg"], "claims": [{"text": "Cotton", "evidence": {"source_url": "https://example.com/p1", "field": "material"}}]}]}
        result = self.run_audit(payload)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["errors"], 0)

    def test_duplicate_and_unsupported_claim_fail(self):
        product = {"id": "p1", "title": "Shirt", "source_url": "https://example.com/p1", "claims": [{"text": "Best ever"}]}
        result = self.run_audit([product, product])
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertGreaterEqual(report["errors"], 4)


if __name__ == "__main__":
    unittest.main()
