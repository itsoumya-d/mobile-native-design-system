"""Tests for India country pack and regulatory mobile journey evaluation."""

import pytest
import sys
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "plugins" / "mobile-native-design-system" / "shared" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from country_pack import (
    get_supported_countries,
    load_country_pack,
    evaluate_mobile_journey_rules,
)


def test_get_supported_countries():
    countries = get_supported_countries()
    assert "in" in countries


def test_load_india_pack():
    pack = load_country_pack("in")
    assert pack["country"] == "in"
    assert "rules" in pack
    assert len(pack["rules"]) >= 3

    for rule in pack["rules"]:
        assert "id" in rule
        assert "decision" in rule
        assert "values" in rule
        assert "source_url" in rule
        assert "checked_on" in rule
        assert "rbi.org.in" in rule["source_url"]


def test_unknown_country_raises_value_error():
    with pytest.raises(ValueError, match="Unsupported country pack"):
        load_country_pack("unknown_jurisdiction")


def test_evaluate_mobile_journey_compliant():
    journey = {
        "is_financial_transaction": True,
        "auth_factors": ["possession_device", "biometric_or_otp"],
        "domestic_storage": True,
        "blocks_rooted_devices": True,
    }
    findings = evaluate_mobile_journey_rules(journey, country="in")
    assert len(findings) == 3
    assert all(f["status"] == "PASS" for f in findings)


def test_evaluate_mobile_journey_violations():
    journey = {
        "is_financial_transaction": True,
        "auth_factors": ["password_only"],
        "domestic_storage": False,
        "blocks_rooted_devices": False,
    }
    findings = evaluate_mobile_journey_rules(journey, country="in")
    assert len(findings) == 3
    assert all(f["status"] == "FAIL" for f in findings)
