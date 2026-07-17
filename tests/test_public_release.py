from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_public_release.py"


class PublicReleaseTests(unittest.TestCase):
    def test_staging_contains_only_public_allowlist_and_repo_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "release"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--out", str(destination)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

            manifest = json.loads(
                (destination / "plugins" / "mobile-native-design-system" / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )
            marketplace = json.loads((destination / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))

            self.assertEqual("1.0.0", manifest["version"])
            self.assertEqual("mobile-native-design-system", marketplace["name"])
            self.assertTrue((destination / "README.md").is_file())
            self.assertTrue((destination / "SECURITY.md").is_file())
            self.assertTrue((destination / "audit" / "sources.lock.json").is_file())
            self.assertTrue((destination / "audit" / "line-audit.jsonl").is_file())
            self.assertTrue((destination / "audit" / "forward-routing-tests.md").is_file())
            self.assertEqual(
                {"__init__.py", "test_mobile_tooling.py", "test_public_release.py", "test_release_contract.py"},
                {path.name for path in (destination / "tests").glob("*.py")},
            )
            self.assertFalse((destination / "upstream").exists())
            self.assertFalse(any(path.name in {"node_modules", ".worktrees", "__pycache__"} for path in destination.rglob("*")))


if __name__ == "__main__":
    unittest.main()
