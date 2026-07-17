from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "mobile-native-design-system" / "shared" / "scripts"
ASSETS = ROOT / "plugins" / "mobile-native-design-system" / "shared" / "assets"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BRIEF = {
    "format": "mobile-screen-brief/1",
    "name": "account-summary",
    "subject": "calm personal finance",
    "user_job": "Understand available cash and pay a bill safely.",
    "primary_action": "Pay bill",
    "hierarchy": ["available cash", "upcoming bill", "recent activity"],
    "signature_interaction": "Press feedback confirms the payment action.",
    "dials": {
        "density": "comfortable",
        "contrast": "high",
        "shape": "soft",
        "typography": "system",
        "motion": "restrained"
    },
    "components": ["button", "icon-button", "field", "card", "list-row", "sheet", "async-state"],
    "async": True
}


MOTION = {
    "format": "mobile-motion-spec/1",
    "name": "payment-confirmation",
    "kind": "presence",
    "states": ["idle", "visible", "hidden"],
    "duration_ms": 220,
    "easing": "standard",
    "distance": 16,
    "stagger_ms": 24,
    "gesture": "tap",
    "reduced_motion": "opacity"
}


class MobileToolingTests(unittest.TestCase):
    def test_design_catalog_validates_a_brief_and_returns_flutter_intelligence(self) -> None:
        design = load_module("mobile_design")
        self.assertEqual([], design.validate_brief(BRIEF))
        results = design.query_catalog("typography motion", platform="flutter")
        self.assertTrue(results)
        self.assertTrue(all("flutter" in item["frameworks"] for item in results))
        self.assertTrue(any(item["source_family"] == "ui-ux-pro-max" for item in results))

    def test_component_tool_emits_complete_native_plan(self) -> None:
        component = load_module("mobile_component")
        plan = component.create_plan(BRIEF, platform="flutter")
        self.assertEqual("flutter", plan["platform"])
        self.assertEqual("ElevatedButton", plan["components"]["button"]["native_primitive"])
        self.assertEqual(
            ["default", "pressed", "focused", "selected", "disabled", "loading", "empty", "error", "retry", "populated"],
            plan["components"]["button"]["states"],
        )
        self.assertIn("TextScaler", plan["adaptive_contract"])
        self.assertNotIn("web", json.dumps(plan).lower())

    def test_motion_tool_generates_four_native_recipes_without_source_runtimes(self) -> None:
        motion = load_module("mobile_motion")
        self.assertEqual([], motion.validate_motion(MOTION))
        with tempfile.TemporaryDirectory() as temp:
            written = motion.generate_recipes(MOTION, platform="all", output=Path(temp))
            self.assertEqual(
                {"mobile_motion.dart", "mobileMotion.ts", "MobileMotion.swift", "MobileMotion.kt"},
                {path.name for path in written},
            )
            rendered = "\n".join(path.read_text(encoding="utf-8") for path in written).lower()
        self.assertIn("animationcontroller", rendered)
        self.assertIn("animated", rendered)
        self.assertIn("animation", rendered)
        self.assertIn("tween", rendered)
        self.assertNotIn("gsap", rendered)
        self.assertNotIn("framer", rendered)

    def test_token_generator_exposes_typed_native_apis_without_renaming_public_entries(self) -> None:
        tokens = load_module("mobile_tokens")
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            document = json.loads((ASSETS / "financial-wellbeing.tokens.json").read_text(encoding="utf-8"))
            tokens.generate_all(document, output, platform="all")
            flutter = (output / "mobile_tokens.dart").read_text(encoding="utf-8")
            flutter_theme = (output / "mobile_theme_extension.dart").read_text(encoding="utf-8")
            react = (output / "tokens.ts").read_text(encoding="utf-8")
            react_theme = (output / "theme.ts").read_text(encoding="utf-8")
            swift = (output / "MobileTokens.swift").read_text(encoding="utf-8")
            swift_theme = (output / "MobileTheme.swift").read_text(encoding="utf-8")
            kotlin = (output / "MobileTokens.kt").read_text(encoding="utf-8")
            kotlin_theme = (output / "MobileTheme.kt").read_text(encoding="utf-8")

        self.assertIn("enum MobileColorToken", flutter)
        self.assertIn("class MobileTokenColors extends ThemeExtension", flutter_theme)
        self.assertIn("extension MobileTokenBuildContext on BuildContext", flutter_theme)
        self.assertIn("export type MobileColorToken", react)
        self.assertIn("export const mobileTokens", react)
        self.assertIn("export const createMobileTheme", react_theme)
        self.assertIn("public enum MobileColorToken", swift)
        self.assertIn("public struct MobileTheme", swift_theme)
        self.assertIn("enum class MobileColorToken", kotlin)
        self.assertIn("androidx.compose.ui.graphics.Color", kotlin)
        self.assertIn("staticCompositionLocalOf", kotlin_theme)

    def test_app_audit_classifies_swiftui_and_compose_and_labels_proven_findings(self) -> None:
        audit = load_module("mobile_app_audit")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            swift = root / "swift"
            (swift / "TokenGallery.xcodeproj").mkdir(parents=True)
            source = swift / "Sources" / "BalanceView.swift"
            source.parent.mkdir(parents=True)
            source.write_text("import SwiftUI\nstruct BalanceView: View { var body: some View { Text(\"Balance\") } }\n", encoding="utf-8")
            swift_report = audit.audit_project(swift, profile="full")

            compose = root / "compose"
            (compose / "app" / "src" / "main" / "java").mkdir(parents=True)
            (compose / "build.gradle.kts").write_text("plugins { id(\"com.android.application\") }\n", encoding="utf-8")
            (compose / "app" / "src" / "main" / "java" / "OverviewScreen.kt").write_text(
                "@Composable fun OverviewScreen() { Text(\"Overview\") }\n", encoding="utf-8"
            )
            compose_report = audit.audit_project(compose, profile="full")

        self.assertEqual("swiftui", swift_report["framework"])
        self.assertEqual("compose", compose_report["framework"])
        self.assertTrue(swift_report["screens"])
        self.assertTrue(compose_report["screens"])
        self.assertTrue(all(item["evidence_level"] in {"proven", "heuristic"} for item in swift_report["findings"]))
        self.assertTrue(any(item["id"] == "accessibility.semantic-review" for item in compose_report["findings"]))

    def test_app_audit_inventories_composable_root_not_named_screen(self) -> None:
        audit = load_module("mobile_app_audit")
        report = audit.audit_project(ROOT / "fixtures" / "compose", profile="quick")
        self.assertIn("TokenGalleryApp", {screen["name"] for screen in report["screens"]})


if __name__ == "__main__":
    unittest.main()
