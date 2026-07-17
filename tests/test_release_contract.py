from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "mobile-native-design-system"


class ReleaseContractTests(unittest.TestCase):
    def test_plugin_exposes_four_focused_mobile_skills(self) -> None:
        expected = {
            "mobile-native-design-system",
            "mobile-native-component-forge",
            "mobile-native-motion",
            "mobile-native-audit",
        }
        skills = PLUGIN / "skills"
        self.assertTrue(skills.is_dir())
        self.assertEqual(expected, {path.name for path in skills.iterdir() if path.is_dir()})
        for name in expected:
            text = (skills / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(f"name: {name}", text)
            self.assertIn("description: Use when", text)

    def test_capability_registry_covers_all_source_families_with_mobile_rejections(self) -> None:
        registry = json.loads(
            (PLUGIN / "shared" / "assets" / "capability-registry.json").read_text(
                encoding="utf-8"
            )
        )
        required_sources = {
            "frontend-design",
            "ui-ux-pro-max",
            "design-taste-frontend",
            "shadcn-ui-mcp-server",
            "21st.dev-magic-mcp",
            "vercel-react-best-practices",
            "gsap-master",
            "motion-framer",
            "convex-create-component",
            "vercel-react-native-skills",
        }
        observed_sources = {record["source_family"] for record in registry["rules"]}
        self.assertTrue(required_sources.issubset(observed_sources))
        required_fields = {
            "id",
            "triggers",
            "priority",
            "frameworks",
            "source_family",
            "native_mapping",
            "validation_rule",
            "legal_treatment",
            "web_runtime_rejection",
        }
        for record in registry["rules"]:
            self.assertEqual(required_fields, set(record))
            self.assertTrue(record["id"])
            self.assertTrue(record["web_runtime_rejection"])

    def test_flutter_reference_translates_every_requested_source_family_to_native_apis(self) -> None:
        flutter = (PLUGIN / "skills" / "mobile-native-design-system" / "references" / "flutter.md").read_text(encoding="utf-8")
        for source in (
            "frontend-design",
            "ui-ux-pro-max",
            "design-taste-frontend",
            "shadcn-ui-mcp-server",
            "21st.dev Magic MCP",
            "vercel-react-best-practices",
            "gsap-master",
            "motion-framer",
            "convex-create-component",
            "vercel-react-native-skills",
        ):
            self.assertIn(source, flutter)
        for api in ("ThemeExtension", "LayoutBuilder", "TextScaler", "Semantics", "AnimationController", "AnimatedSwitcher"):
            self.assertIn(api, flutter)
        self.assertIn("Never install or import GSAP, Framer Motion, React, or React Native", flutter)

    def test_public_implementation_has_no_forbidden_web_runtime(self) -> None:
        forbidden = re.compile(
            r"(react-dom|next\.js|from\s+['\"]next|tailwind|framer-motion|\bgsap\b|"
            r"document\.|localStorage|sessionStorage|CSSStyleDeclaration|"
            r"platforms?:\s*\[[^\]]*web)",
            re.IGNORECASE,
        )
        source_suffixes = {".swift", ".kt", ".kts", ".ts", ".tsx", ".dart"}
        failures: list[str] = []
        for root in (PLUGIN / "shared", ROOT / "fixtures"):
            for path in root.rglob("*"):
                if not path.is_file() or any(part in {"node_modules", "Pods", "build", ".gradle", ".dart_tool"} for part in path.parts):
                    continue
                if path.suffix not in source_suffixes and path.name not in {"package.json", "pubspec.yaml", "build.gradle", "build.gradle.kts"}:
                    continue
                match = forbidden.search(path.read_text(encoding="utf-8", errors="ignore"))
                if match:
                    failures.append(f"{path.relative_to(ROOT)}: {match.group(0)}")
        self.assertEqual([], failures)

    def test_compose_fixture_applies_kotlin_two_compose_compiler_plugin(self) -> None:
        compose_root = ROOT / "fixtures" / "compose"
        root_build = (compose_root / "build.gradle.kts").read_text(encoding="utf-8")
        app_build = (compose_root / "app" / "build.gradle.kts").read_text(encoding="utf-8")
        self.assertRegex(
            root_build,
            r'id\("org\.jetbrains\.kotlin\.plugin\.compose"\) version "2\.3\.10" apply false',
        )
        self.assertIn('id("org.jetbrains.kotlin.plugin.compose")', app_build)


if __name__ == "__main__":
    unittest.main()
