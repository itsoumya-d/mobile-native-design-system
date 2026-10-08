#!/usr/bin/env python3
"""Exercise token generation and expected guard failures in a temporary directory."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py"
SOURCE = ROOT / "plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json"


def run(*args: str, expected_code: int = 0) -> dict:
    result = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)
    if result.returncode != expected_code:
        raise RuntimeError(f"Expected exit {expected_code}, got {result.returncode}: {result.stdout}{result.stderr}")
    return json.loads(result.stdout if result.stdout else result.stderr)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="mobile-token-parity-") as temporary:
        output = Path(temporary) / "generated"
        generate = ("generate", str(SOURCE), "--platform", "all", "--out", str(output))
        parity = ("parity", str(SOURCE), str(output), "--platform", "all")
        run(*generate)
        before = {path.name: path.read_bytes() for path in output.iterdir()}
        run(*generate)
        require(before == {path.name: path.read_bytes() for path in output.iterdir()}, "Generation was not byte-stable")
        require(run(*parity)["ok"], "Fresh generation did not pass")

        artifact = output / "tokens.ts"
        original = artifact.read_text(encoding="utf-8")
        edited = original.replace('"spacing.4":4', '"spacing.4":999')
        require(original != edited, "Fixture edit did not change a token")
        artifact.write_text(edited, encoding="utf-8")
        manifest_path = output / "tokens.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"]["tokens.ts"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        edited_report = run(*parity, expected_code=1)
        require("artifact source mismatch: tokens.ts" in edited_report["errors"], "Edited output was not detected")

        run(*generate)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"] = {}
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        require(not run(*parity, expected_code=1)["ok"], "Empty artifact manifest passed")

        invalid_source = Path(temporary) / "invalid.tokens.json"
        document = json.loads(SOURCE.read_text(encoding="utf-8"))
        document["$extensions"]["org.mobile-native"]["profiles"]["android"]["overrides"]["touchTarget.minimum"] = 1
        invalid_source.write_text(json.dumps(document), encoding="utf-8")
        require(not run("validate", str(invalid_source), expected_code=1)["ok"], "Invalid touch target passed")

    print(json.dumps({"ok": True, "checks": ["byte-stable generation", "four-target parity", "edited artifact with updated hash rejected", "empty artifact manifest rejected", "invalid touch target rejected"]}, indent=2))


if __name__ == "__main__":
    main()
