"""Tests for regulatory and mobile onboarding compliance packs."""
import importlib.util
import json
import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "plugins" / "mobile-native-design-system" / "shared" / "scripts"
PACKS_DIR = REPO_ROOT / "packs"

NOT_OFFICIAL_PATTERN = re.compile(
    r"wikipedia|medium\.com|blog|chatgpt|openai\.com|reddit|quora|stackoverflow|investopedia|linkedin",
    re.I,
)


def load_compliance_module():
    spec = importlib.util.spec_from_file_location("mobile_compliance_pack", SCRIPTS_DIR / "mobile_compliance_pack.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_compliance_module()
list_supported_countries = mod.list_supported_countries
load_country_pack = mod.load_country_pack
evaluate_compliance = mod.evaluate_compliance


def test_list_supported_countries():
    countries = list_supported_countries(PACKS_DIR)
    assert "global" in countries
    assert "in" in countries


def test_load_country_pack_schema():
    pack = load_country_pack("in", PACKS_DIR)
    assert pack.get("format") == "mobile-native-compliance-pack/1"
    assert pack.get("country") == "in"
    assert isinstance(pack.get("rules"), list)
    assert len(pack["rules"]) >= 3


def test_india_pack_official_sources():
    pack = load_country_pack("in", PACKS_DIR)
    rules = pack.get("rules", [])
    assert len(rules) >= 3

    for rule in rules:
        source_url = rule.get("source_url")
        assert source_url, f"Rule {rule.get('id')} must contain source_url"
        assert source_url.startswith("http"), f"Invalid source_url: {source_url}"
        assert not NOT_OFFICIAL_PATTERN.search(source_url), f"Unofficial source: {source_url}"
        assert any(
            gov_domain in source_url for gov_domain in ["rbi.org.in", "uidai.gov.in", "meity.gov.in"]
        ), f"Source URL must be an official regulator/gov portal: {source_url}"
        assert rule.get("checked_on") == "2026-11-27"


def test_unknown_country_raises_error():
    with pytest.raises(ValueError) as excinfo:
        load_country_pack("xyz", PACKS_DIR)
    assert "Unknown country compliance pack" in str(excinfo.value)
    assert "in" in str(excinfo.value)


def test_evaluate_vcip_geotag_compliance():
    # Pass case
    pass_ctx = {
        "user_in_india": True,
        "liveness_verified": True,
    }
    res = evaluate_compliance(
        "in.rbi.vcip-geotag-livetrack", pass_ctx, country="in", packs_dir=PACKS_DIR
    )
    assert res["compliant"] is True
    assert res["source_url"] == "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566"

    # Fail case - user not in India
    fail_ctx = {
        "user_in_india": False,
        "liveness_verified": True,
    }
    res_fail = evaluate_compliance(
        "in.rbi.vcip-geotag-livetrack", fail_ctx, country="in", packs_dir=PACKS_DIR
    )
    assert res_fail["compliant"] is False
    assert any("geolocation" in issue.lower() for issue in res_fail["issues"])


def test_evaluate_aadhaar_masking_compliance():
    # Pass case: masked number with consent
    pass_ctx = {
        "consent_given": True,
        "displayed_id_text": "XXXX-XXXX-5678",
    }
    res_pass = evaluate_compliance(
        "in.uidai.aadhaar-masking-consent", pass_ctx, country="in", packs_dir=PACKS_DIR
    )
    assert res_pass["compliant"] is True
    assert res_pass["source_url"] == "https://uidai.gov.in/en/legal-framework.html"

    # Fail case: plaintext Aadhaar number
    fail_ctx = {
        "consent_given": True,
        "displayed_id_text": "123456789012",
    }
    res_fail = evaluate_compliance(
        "in.uidai.aadhaar-masking-consent", fail_ctx, country="in", packs_dir=PACKS_DIR
    )
    assert res_fail["compliant"] is False
    assert any("exposed" in issue.lower() for issue in res_fail["issues"])


def test_evaluate_digital_lending_kfs_and_permissions():
    # Fail case: requesting contact list
    fail_ctx = {
        "kfs_displayed_before_sign": True,
        "requested_permissions": ["android.permission.CAMERA", "android.permission.READ_CONTACTS"],
    }
    res_fail = evaluate_compliance(
        "in.rbi.digital-lending-kfs", fail_ctx, country="in", packs_dir=PACKS_DIR
    )
    assert res_fail["compliant"] is False
    assert any("contacts" in issue.lower() for issue in res_fail["issues"])
