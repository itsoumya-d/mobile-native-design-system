#!/usr/bin/env python3
"""Run deterministic public-release validation without native SDK assumptions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS = (
    "tests.test_release_contract",
    "tests.test_mobile_tooling",
    "tests.test_public_release",
)


def main() -> int:
    return subprocess.run([sys.executable, "-m", "unittest", *TESTS, "-v"], cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
