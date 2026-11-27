"""Mobile Native Compliance Pack Loader & Evaluator.

Provides jurisdiction-specific mobile onboarding, identity verification,
and UX compliance rule packs loaded from external data specifications.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_default_packs_dir() -> Path:
    """Find the root packs directory from repository relative paths."""
    # Try traversing up from this script file
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir.parents[3] / "packs",
        script_dir.parents[2] / "packs",
        Path.cwd() / "packs",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def list_supported_countries(packs_dir: Optional[Path] = None) -> List[str]:
    """Return a sorted list of supported country codes from packs/ directory."""
    root = packs_dir or get_default_packs_dir()
    if not root.is_dir():
        return []
    countries = []
    for p in root.iterdir():
        if p.is_dir() and (p / "rules.json").is_file():
            countries.append(p.name.lower())
    return sorted(countries)


def load_country_pack(country: str = "global", packs_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load and parse the specified country compliance pack JSON.

    Args:
        country: Two-letter ISO country code or 'global'.
        packs_dir: Optional path to the packs directory.

    Returns:
        The parsed dictionary representing the country's rules pack.

    Raises:
        ValueError: If the country pack does not exist.
    """
    country_code = (country or "").strip().lower()
    root = packs_dir or get_default_packs_dir()
    rule_file = root / country_code / "rules.json"

    if not rule_file.is_file():
        supported = list_supported_countries(root)
        raise ValueError(
            f"Unknown country compliance pack: '{country}'. Supported countries: {supported}"
        )

    with open(rule_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "rules" not in data:
        raise ValueError(f"Invalid pack schema in {rule_file}: must contain a 'rules' list.")

    return data


def evaluate_compliance(
    rule_id: str,
    context: Dict[str, Any],
    country: str = "global",
    packs_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Evaluate a mobile application context against a specific compliance rule.

    Args:
        rule_id: The unique identifier of the rule to evaluate.
        context: Context dictionary describing the screen, onboarding, or client state.
        country: Two-letter ISO country code or 'global'.
        packs_dir: Optional path to the packs directory.

    Returns:
        Evaluation summary with status, reasons, and verified official source URL.
    """
    pack = load_country_pack(country=country, packs_dir=packs_dir)
    matched_rule = next((r for r in pack.get("rules", []) if r.get("id") == rule_id), None)
    if not matched_rule:
        raise KeyError(f"Rule ID '{rule_id}' not found in '{country}' pack.")

    values = matched_rule.get("values", {})
    compliant = True
    issues: List[str] = []

    # RBI V-CIP Geotagging check
    if rule_id == "in.rbi.vcip-geotag-livetrack":
        if values.get("geo_fencing_required") and not context.get("user_in_india", False):
            compliant = False
            issues.append("User geolocation is not verified within India.")
        if values.get("live_face_liveness") and not context.get("liveness_verified", False):
            compliant = False
            issues.append("Audio-visual liveness detection not confirmed.")

    # UIDAI Aadhaar masking check
    elif rule_id == "in.uidai.aadhaar-masking-consent":
        if values.get("affirmative_consent_required") and not context.get("consent_given", False):
            compliant = False
            issues.append("Affirmative Aadhaar collection consent not captured.")
        displayed_id = context.get("displayed_id_text", "")
        if values.get("mask_first_eight_digits") and displayed_id:
            # Check if 12-digit number is unmasked
            digits = "".join(ch for ch in displayed_id if ch.isdigit())
            if len(digits) == 12 and not displayed_id.startswith("XXXX-XXXX"):
                compliant = False
                issues.append("Aadhaar first 8 digits are exposed in plaintext.")

    # MeitY DPDP Multilingual notice check
    elif rule_id == "in.meity.dpdp-multilingual-notice":
        supported_langs = context.get("notice_languages", [])
        if values.get("scheduled_languages_support") and len(supported_langs) < 2:
            compliant = False
            issues.append("Consent notice must offer multilingual options alongside English.")
        if values.get("accessible_withdrawal_mechanism") and not context.get("has_withdrawal_path", False):
            compliant = False
            issues.append("Accessible consent withdrawal mechanism missing.")

    # RBI Digital lending KFS check
    elif rule_id == "in.rbi.digital-lending-kfs":
        if values.get("kfs_pre_contract_display") and not context.get("kfs_displayed_before_sign", False):
            compliant = False
            issues.append("Key Fact Statement (KFS) not displayed prior to contract execution.")
        permissions = [p.lower() for p in context.get("requested_permissions", [])]
        if values.get("forbid_contacts_permission") and any("contact" in p for p in permissions):
            compliant = False
            issues.append("Prohibited mobile contacts permission requested.")

    # Global Touch target check
    elif rule_id == "global.w3c.touch-target-size":
        w = context.get("touch_width_dp", 0)
        h = context.get("touch_height_dp", 0)
        if w < values.get("min_width_dp", 44) or h < values.get("min_height_dp", 44):
            compliant = False
            issues.append(f"Touch target ({w}x{h}dp) below required minimum 44x44dp.")

    return {
        "rule_id": rule_id,
        "country": country,
        "title": matched_rule.get("title"),
        "compliant": compliant,
        "issues": issues,
        "source_url": matched_rule.get("source_url"),
        "checked_on": matched_rule.get("checked_on"),
    }
