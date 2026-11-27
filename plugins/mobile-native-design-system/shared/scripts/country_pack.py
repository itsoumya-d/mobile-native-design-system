"""Country pack loader and regulatory journey evaluator for mobile neobank and financial applications."""

import json
import pathlib
from typing import Any, Dict, List, Optional

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
_DEFAULT_PACKS_DIR = _REPO_ROOT / "packs"


def get_supported_countries(packs_dir: Optional[pathlib.Path] = None) -> List[str]:
    """Returns a sorted list of supported country codes that have rules.json."""
    base = pathlib.Path(packs_dir) if packs_dir else _DEFAULT_PACKS_DIR
    if not base.exists():
        return []
    countries = []
    for p in base.iterdir():
        if p.is_dir() and (p / "rules.json").is_file():
            countries.append(p.name.lower())
    return sorted(countries)


def load_country_pack(country: str = "in", packs_dir: Optional[pathlib.Path] = None) -> Dict[str, Any]:
    """Loads and validates the regulatory country pack for a given jurisdiction.

    Raises:
        ValueError: If country is not supported or rules.json is missing or invalid.
    """
    if not country or not isinstance(country, str):
        raise ValueError("Country code must be a non-empty string.")

    code = country.strip().lower()
    base = pathlib.Path(packs_dir) if packs_dir else _DEFAULT_PACKS_DIR
    rules_file = base / code / "rules.json"

    if not rules_file.exists():
        supported = get_supported_countries(base)
        raise ValueError(
            f"Unsupported country pack '{country}'. Supported country codes: {supported if supported else 'none'}"
        )

    try:
        data = json.loads(rules_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Failed to parse country pack '{country}': {exc}") from exc

    if not isinstance(data, dict) or "rules" not in data or not isinstance(data["rules"], list):
        raise ValueError(f"Invalid country pack schema for '{country}': missing 'rules' array.")

    return data


def evaluate_mobile_journey_rules(journey: Dict[str, Any], country: str = "in") -> List[Dict[str, Any]]:
    """Evaluates a mobile flow/journey against the specified country's regulatory rules.

    Returns a list of compliance findings (violations or passing evaluations).
    """
    pack = load_country_pack(country=country)
    findings = []
    rules = pack.get("rules", [])

    is_financial = journey.get("is_financial_transaction", False)
    auth_factors = journey.get("auth_factors", [])
    stores_data_locally = journey.get("domestic_storage", True)
    blocks_rooted = journey.get("blocks_rooted_devices", False)

    for rule in rules:
        rule_id = rule.get("id")
        if rule_id == "IN-NEOBANK-2FA-01":
            if is_financial and len(auth_factors) < 2:
                findings.append({
                    "rule_id": rule_id,
                    "status": "FAIL",
                    "reason": "Two-factor authentication required for financial transactions",
                    "source_url": rule.get("source_url")
                })
            else:
                findings.append({
                    "rule_id": rule_id,
                    "status": "PASS",
                    "reason": "2FA compliance satisfied or transaction non-financial",
                    "source_url": rule.get("source_url")
                })
        elif rule_id == "IN-DATA-LOCALIZATION-02":
            if not stores_data_locally:
                findings.append({
                    "rule_id": rule_id,
                    "status": "FAIL",
                    "reason": "Transaction telemetry must reside within India",
                    "source_url": rule.get("source_url")
                })
            else:
                findings.append({
                    "rule_id": rule_id,
                    "status": "PASS",
                    "reason": "Domestic storage requirement satisfied",
                    "source_url": rule.get("source_url")
                })
        elif rule_id == "IN-DEVICE-SECURITY-03":
            if not blocks_rooted:
                findings.append({
                    "rule_id": rule_id,
                    "status": "FAIL",
                    "reason": "Device root/jailbreak detection and restricted access required",
                    "source_url": rule.get("source_url")
                })
            else:
                findings.append({
                    "rule_id": rule_id,
                    "status": "PASS",
                    "reason": "Client root detection policy enforced",
                    "source_url": rule.get("source_url")
                })

    return findings
