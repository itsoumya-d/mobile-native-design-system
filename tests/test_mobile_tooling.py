from __future__ import annotations

import importlib.util
import hashlib
import subprocess
import sys
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


class TokenParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tokens = load_module("mobile_tokens")
        self.document = json.loads((ASSETS / "financial-wellbeing.tokens.json").read_text(encoding="utf-8"))
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name) / "generated"
        self.tokens.generate_all(self.document, self.output)
        self.manifest_path = self.output / "tokens.manifest.json"

    def edit_manifest(self, edit) -> None:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        edit(manifest)
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def assert_parity_fails(self, expected: str, **kwargs) -> None:
        report = self.tokens.check_parity(self.document, self.output, **kwargs)
        self.assertFalse(report["ok"], report)
        self.assertIn(expected, "\n".join(report["errors"]))

    def test_empty_artifact_manifest_does_not_pass(self) -> None:
        self.edit_manifest(lambda manifest: manifest.update(artifacts={}))
        self.assert_parity_fails("artifacts must be a non-empty object")

    def test_changed_artifact_with_updated_hash_does_not_pass(self) -> None:
        artifact = self.output / "tokens.ts"
        original = artifact.read_text(encoding="utf-8")
        edited = original.replace('"spacing.4":4', '"spacing.4":999')
        self.assertNotEqual(original, edited)
        artifact.write_text(edited, encoding="utf-8")
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        self.edit_manifest(lambda manifest: manifest["artifacts"].update({"tokens.ts": digest}))
        self.assert_parity_fails("artifact source mismatch: tokens.ts")

    def test_removed_target_cannot_hide_behind_manifest(self) -> None:
        def remove_target(manifest):
            for filename in self.tokens.PLATFORM_FILES["flutter"]:
                del manifest["artifacts"][filename]
                (self.output / filename).unlink()
        self.edit_manifest(remove_target)
        self.assert_parity_fails("missing artifact entry: mobile_tokens.dart")

    def test_missing_file_and_incomplete_pair_fail(self) -> None:
        (self.output / "theme.ts").unlink()
        self.assert_parity_fails("missing artifact: theme.ts")
        self.edit_manifest(lambda manifest: manifest["artifacts"].pop("theme.ts"))
        self.assert_parity_fails("missing artifact entry: theme.ts")

    def test_legacy_manifest_accepts_complete_targets_and_explicit_target_scope(self) -> None:
        self.tokens.generate_all(self.document, self.output, "react-native")
        self.edit_manifest(lambda manifest: manifest.pop("platforms", None))
        self.assertTrue(self.tokens.check_parity(self.document, self.output)["ok"])
        self.assertTrue(self.tokens.check_parity(self.document, self.output, platform="react-native")["ok"])
        self.assert_parity_fails("missing artifact entry: MobileTokens.swift", platform="all")

    def test_manifest_structure_errors_return_reports(self) -> None:
        original = self.manifest_path.read_text(encoding="utf-8")
        for value in ([], None, "manifest", {"format": "other"}):
            with self.subTest(value=value):
                self.manifest_path.write_text(json.dumps(value), encoding="utf-8")
                self.assert_parity_fails("manifest")
        for field, value in (("artifacts", []), ("platforms", []), ("platforms", ["web"]), ("platforms", ["swift", "swift"]), ("platforms", [None])):
            with self.subTest(field=field, value=value):
                self.manifest_path.write_text(original, encoding="utf-8")
                self.edit_manifest(lambda manifest: manifest.update({field: value}))
                self.assertFalse(self.tokens.check_parity(self.document, self.output)["ok"])

    def test_unknown_paths_are_rejected_without_reading_outside_output(self) -> None:
        self.edit_manifest(lambda manifest: manifest["artifacts"].update({"../outside.txt": "0" * 64}))
        self.assert_parity_fails("unexpected artifact entry: ../outside.txt")

    def test_unreadable_artifact_returns_a_report(self) -> None:
        artifact = self.output / "theme.ts"
        artifact.unlink()
        artifact.mkdir()
        self.assert_parity_fails("cannot read artifact: theme.ts")

    def test_invalid_source_fails_even_when_manifest_hash_is_updated(self) -> None:
        self.document["$extensions"]["org.mobile-native"]["profiles"]["android"]["overrides"]["touchTarget.minimum"] = 1
        self.edit_manifest(lambda manifest: manifest.update(source_hash=self.tokens._source_hash(self.document)))
        self.assert_parity_fails("Android touchTarget.minimum must be at least 48 dp")

    def test_generation_is_byte_stable_and_parity_is_read_only(self) -> None:
        snapshot = {path.name: path.read_bytes() for path in self.output.iterdir()}
        self.tokens.generate_all(self.document, self.output)
        self.assertEqual(snapshot, {path.name: path.read_bytes() for path in self.output.iterdir()})
        reordered = dict(reversed(list(self.document.items())))
        self.tokens.generate_all(reordered, self.output)
        self.assertEqual(snapshot, {path.name: path.read_bytes() for path in self.output.iterdir()})
        for platform in ("all", *self.tokens.PLATFORM_FILES):
            with self.subTest(platform=platform):
                self.tokens.generate_all(self.document, self.output, platform)
                before = {path.name: path.read_bytes() for path in self.output.iterdir()}
                self.assertTrue(self.tokens.check_parity(self.document, self.output, platform=platform)["ok"])
                self.assertEqual(before, {path.name: path.read_bytes() for path in self.output.iterdir()})

    def test_existing_native_fixture_adapters_match_the_current_generator(self) -> None:
        fixtures = {
            "flutter": "fixtures/flutter/lib/generated",
            "react-native": "fixtures/react-native/src/generated",
            "swift": "fixtures/swiftui/TokenGallery/Sources/Generated",
            "kotlin": "fixtures/compose/app/src/main/java/mobile/tokens",
        }
        for platform, path in fixtures.items():
            with self.subTest(platform=platform):
                report = self.tokens.check_parity(self.document, ROOT / path, platform=platform)
                self.assertTrue(report["ok"], report)

    def test_runnable_failure_fixture(self) -> None:
        completed = subprocess.run([sys.executable, str(ROOT / "fixtures/token-parity/check.py")], capture_output=True, text=True)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["ok"])

    def test_manifest_and_source_drift_are_rejected(self) -> None:
        self.edit_manifest(lambda manifest: manifest.update(token_paths=[], profiles=[]))
        self.assert_parity_fails("semantic token path mismatch")
        self.assert_parity_fails("resolver profile mismatch")
        self.document["spacing"]["4"]["$value"] = 5
        self.assert_parity_fails("source hash mismatch")

    def test_invalid_json_and_missing_manifest_return_reports(self) -> None:
        for content in (b"{", b"\xff"):
            self.manifest_path.write_bytes(content)
            self.assert_parity_fails("Invalid manifest")
        self.manifest_path.unlink()
        self.assert_parity_fails("tokens.manifest.json is missing")

    def test_cli_failure_is_machine_readable_and_nonzero(self) -> None:
        self.edit_manifest(lambda manifest: manifest.update(artifacts={}))
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "mobile_tokens.py"), "parity", str(ASSETS / "financial-wellbeing.tokens.json"), str(self.output)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, completed.returncode, completed.stdout + completed.stderr)
        self.assertFalse(json.loads(completed.stdout)["ok"])
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
