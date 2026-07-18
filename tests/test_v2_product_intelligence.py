from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "mobile-native-design-system"
SCRIPTS = PLUGIN / "shared" / "scripts"
ASSETS = PLUGIN / "shared" / "assets"

SOURCE_FAMILIES = {
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
FRAMEWORKS = {"flutter", "react-native", "swiftui", "compose"}
RECOMMENDATION_FIELDS = {
    "id",
    "screen_id",
    "title",
    "score",
    "current_code_evidence",
    "user_benefit",
    "selected_capabilities",
    "native_implementation",
    "files_likely_affected",
    "behavior_invariants",
    "accessibility",
    "motion",
    "risk",
    "confidence",
    "verification_commands",
    "acceptance_criteria",
}


def load_module(name: str):
    path = SCRIPTS / f"{name}.py"
    if not path.is_file():
        raise AssertionError(f"missing v2 module: {path}")
    spec = importlib.util.spec_from_file_location(f"v2_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_flutter_product(root: Path) -> Path:
    app = root / "calm_money"
    (app / "lib" / "features" / "home").mkdir(parents=True)
    (app / "lib" / "features" / "detail").mkdir(parents=True)
    (app / "lib" / "data").mkdir(parents=True)
    (app / "lib" / "theme").mkdir(parents=True)
    (app / "lib" / "l10n").mkdir(parents=True)
    (app / "test").mkdir(parents=True)
    (app / "assets" / "images").mkdir(parents=True)
    (app / "pubspec.yaml").write_text(
        """
name: calm_money
environment:
  sdk: ">=3.6.0 <4.0.0"
dependencies:
  flutter:
    sdk: flutter
  go_router: ^16.0.0
  flutter_riverpod: ^3.0.0
flutter:
  uses-material-design: true
  assets:
    - assets/images/
""".lstrip(),
        encoding="utf-8",
    )
    (app / "lib" / "app_router.dart").write_text(
        """
import 'package:go_router/go_router.dart';
import 'features/home/home_screen.dart';
import 'features/detail/detail_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/home',
  routes: [
    GoRoute(path: '/home', name: 'home', builder: (context, state) => const HomeScreen()),
    GoRoute(path: '/detail/:id', name: 'detail', builder: (context, state) => DetailScreen(id: state.pathParameters['id']!)),
  ],
);
""".lstrip(),
        encoding="utf-8",
    )
    (app / "lib" / "features" / "home" / "home_screen.dart").write_text(
        """
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/items_repository.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Available cash')),
      body: SafeArea(
        child: ListView(
          children: [
            Semantics(
              button: true,
              label: 'Open savings details',
              child: ListTile(
                title: const Text('Savings'),
                onTap: () {
                  Analytics.track('open_detail');
                  context.push('/detail/savings');
                },
              ),
            ),
            FilledButton(
              onPressed: () => ref.read(itemsRepositoryProvider).refresh(),
              child: const Text('Refresh'),
            ),
          ],
        ),
      ),
    );
  }
}
""".lstrip(),
        encoding="utf-8",
    )
    (app / "lib" / "features" / "detail" / "detail_screen.dart").write_text(
        """
import 'package:flutter/material.dart';

class DetailScreen extends StatelessWidget {
  const DetailScreen({required this.id, super.key});
  final String id;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Details')),
    body: LayoutBuilder(builder: (context, constraints) => Text(id)),
  );
}
""".lstrip(),
        encoding="utf-8",
    )
    (app / "lib" / "data" / "items_repository.dart").write_text(
        """
final itemsRepositoryProvider = Provider((ref) => ItemsRepository());
class ItemsRepository {
  Future<void> refresh() async {}
}
class Analytics {
  static void track(String event) {}
}
""".lstrip(),
        encoding="utf-8",
    )
    (app / "lib" / "theme" / "app_theme.dart").write_text(
        """
import 'package:flutter/material.dart';
const brandBlue = Color(0xFF165DFF);
const spacingM = 16.0;
final appTheme = ThemeData(
  colorScheme: ColorScheme.fromSeed(seedColor: brandBlue),
  textTheme: const TextTheme(titleLarge: TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
  cardTheme: const CardThemeData(shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(16)))),
);
""".lstrip(),
        encoding="utf-8",
    )
    (app / "lib" / "l10n" / "app_en.arb").write_text(
        json.dumps({"availableCash": "Available cash"}) + "\n",
        encoding="utf-8",
    )
    (app / "test" / "home_screen_test.dart").write_text(
        "void main() { testWidgets('opens detail', (tester) async {}); }\n",
        encoding="utf-8",
    )
    (app / "assets" / "images" / "wallet.txt").write_text("fixture\n", encoding="utf-8")
    return app


class ProductIntelligenceV2Tests(unittest.TestCase):
    def test_documented_v2_cli_pipeline_runs_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temporary = Path(temp)
            app = write_flutter_product(temporary)
            project = temporary / "project-model.json"
            design = temporary / "design-language.json"
            plan_directory = temporary / "redesign-plan"
            screen_plan = temporary / "screen-plan.json"
            baseline = temporary / "baseline.json"
            receipt = temporary / "change-receipt.json"

            commands = [
                [
                    sys.executable,
                    str(SCRIPTS / "mobile_project.py"),
                    "scan",
                    str(app),
                    "--profile",
                    "full",
                    "--out",
                    str(project),
                ],
                [
                    sys.executable,
                    str(SCRIPTS / "mobile_design.py"),
                    "synthesize",
                    str(project),
                    "--out",
                    str(design),
                ],
                [
                    sys.executable,
                    str(SCRIPTS / "mobile_plan.py"),
                    "create",
                    str(project),
                    "--scope",
                    "app",
                    "--out",
                    str(plan_directory),
                ],
                [
                    sys.executable,
                    str(SCRIPTS / "mobile_plan.py"),
                    "screen",
                    str(project),
                    "HomeScreen",
                    "--out",
                    str(screen_plan),
                ],
            ]
            for command in commands:
                completed = subprocess.run(command, text=True, capture_output=True)
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )

            approved = json.loads(screen_plan.read_text(encoding="utf-8"))
            approved["approval"] = {
                "status": "approved",
                "approved_scope": "HomeScreen",
            }
            screen_plan.write_text(
                json.dumps(approved, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            for command in (
                [
                    sys.executable,
                    str(SCRIPTS / "mobile_guard.py"),
                    "baseline",
                    str(app),
                    str(screen_plan),
                    "--out",
                    str(baseline),
                ],
                [
                    sys.executable,
                    str(SCRIPTS / "mobile_guard.py"),
                    "verify",
                    str(app),
                    str(screen_plan),
                    str(baseline),
                    "--out",
                    str(receipt),
                ],
            ):
                completed = subprocess.run(command, text=True, capture_output=True)
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )

            self.assertEqual(
                "mobile-native-project/2",
                json.loads(project.read_text(encoding="utf-8"))["format"],
            )
            self.assertEqual(
                "mobile-native-design-language/1",
                json.loads(design.read_text(encoding="utf-8"))["format"],
            )
            self.assertTrue(
                json.loads(receipt.read_text(encoding="utf-8"))["ok"]
            )

    def test_scan_reconstructs_flutter_product_with_relative_evidence(self) -> None:
        project_tool = load_module("mobile_project")
        with tempfile.TemporaryDirectory() as temp:
            app = write_flutter_product(Path(temp))
            model = project_tool.scan_project(app, profile="full")

        self.assertEqual("mobile-native-project/2", model["format"])
        self.assertEqual("flutter", model["framework"]["id"])
        self.assertIn("go_router", model["dependencies"]["direct"])
        self.assertIn("flutter_riverpod", model["dependencies"]["direct"])
        self.assertEqual("mobile-native-screen-graph/1", model["screen_graph"]["format"])
        self.assertEqual(
            {"/home", "/detail/:id"},
            {route["path"] for route in model["screen_graph"]["routes"]},
        )
        self.assertIn("HomeScreen", {screen["name"] for screen in model["screen_graph"]["screens"]})
        self.assertEqual("mobile-native-behavior-contract/1", model["behavior_contract"]["format"])
        action_kinds = {action["kind"] for action in model["behavior_contract"]["actions"]}
        self.assertTrue({"navigation", "analytics", "data-write"}.issubset(action_kinds))
        self.assertEqual("mobile-native-design-language/1", model["design_language"]["format"])
        self.assertTrue(model["design_language"]["colors"])
        self.assertTrue(model["assets"])
        self.assertTrue(model["localization"])
        self.assertTrue(model["tests"])
        self.assertIn("flutter analyze", model["build_commands"])
        self.assertIn("flutter test", model["build_commands"])
        self.assertTrue(model["source_hashes"])
        for evidence in model["evidence"]:
            self.assertFalse(Path(evidence["path"]).is_absolute())
            self.assertGreater(evidence["line"], 0)
            self.assertIn(evidence["confidence"], {"high", "medium", "low"})
            self.assertIn(evidence["evidence_type"], {"parser", "manifest", "pattern", "toolchain"})

    def test_scan_detects_all_supported_fixture_frameworks(self) -> None:
        project_tool = load_module("mobile_project")
        expected = {
            "flutter": "flutter",
            "react-native": "react-native",
            "swiftui": "swiftui",
            "compose": "compose",
        }
        for fixture, framework in expected.items():
            with self.subTest(framework=framework):
                model = project_tool.scan_project(ROOT / "fixtures" / fixture, profile="full")
                self.assertEqual(framework, model["framework"]["id"])
                self.assertTrue(model["screen_graph"]["screens"])
                self.assertTrue(model["source_hashes"])
                self.assertTrue(model["build_commands"])
                if framework == "swiftui":
                    self.assertTrue(
                        all(
                            "-scheme TokenGallery" in command
                            for command in model["build_commands"]
                        ),
                        model["build_commands"],
                    )

    def test_production_shaped_fixtures_expose_the_same_semantic_flow(self) -> None:
        project_tool = load_module("mobile_project")
        required_screens = {
            "SignInScreen",
            "HomeScreen",
            "DetailScreen",
            "CheckInFormScreen",
            "SettingsScreen",
        }
        for fixture in ("flutter", "react-native", "swiftui", "compose"):
            with self.subTest(framework=fixture):
                model = project_tool.scan_project(
                    ROOT / "fixtures" / fixture,
                    profile="full",
                )
                observed = {
                    screen["name"] for screen in model["screen_graph"]["screens"]
                }
                self.assertTrue(required_screens.issubset(observed), observed)
                self.assertGreaterEqual(len(model["screen_graph"]["routes"]), 4)
                action_kinds = {
                    action["kind"]
                    for action in model["behavior_contract"]["actions"]
                }
                self.assertIn("navigation", action_kinds)
                self.assertIn("data-write", action_kinds)
                self.assertTrue(model["localization"])
                self.assertTrue(model["tests"])

    def test_design_synthesis_and_app_plan_are_evidence_backed(self) -> None:
        project_tool = load_module("mobile_project")
        design_tool = load_module("mobile_design")
        plan_tool = load_module("mobile_plan")
        with tempfile.TemporaryDirectory() as temp:
            app = write_flutter_product(Path(temp))
            model = project_tool.scan_project(app, profile="full")
            language = design_tool.synthesize_design_language(model)
            app_plan = plan_tool.create_app_plan(model)

        self.assertEqual("mobile-native-design-language/1", language["format"])
        self.assertEqual("flutter", language["framework"])
        self.assertTrue(language["design_read"]["preserve"])
        self.assertTrue(language["design_read"]["improve"])
        self.assertEqual("mobile-native-app-plan/1", app_plan["format"])
        self.assertEqual("app", app_plan["scope"])
        self.assertTrue(app_plan["recommendations"])
        self.assertEqual(
            SOURCE_FAMILIES,
            {entry["source_family"] for entry in app_plan["capability_coverage"]},
        )
        self.assertTrue(
            all(entry["status"] in {"selected", "available", "conditional", "not-applicable"}
                for entry in app_plan["capability_coverage"])
        )
        for recommendation in app_plan["recommendations"]:
            self.assertTrue(RECOMMENDATION_FIELDS.issubset(recommendation))
            self.assertTrue(recommendation["current_code_evidence"])
            self.assertTrue(recommendation["selected_capabilities"])
            self.assertTrue(recommendation["verification_commands"])
            self.assertTrue(recommendation["acceptance_criteria"])

    def test_screen_plan_and_guard_preserve_behavior_one_screen_at_a_time(self) -> None:
        project_tool = load_module("mobile_project")
        plan_tool = load_module("mobile_plan")
        guard_tool = load_module("mobile_guard")
        with tempfile.TemporaryDirectory() as temp:
            app = write_flutter_product(Path(temp))
            model = project_tool.scan_project(app, profile="full")
            screen_plan = plan_tool.create_screen_plan(model, "HomeScreen")

            self.assertEqual("mobile-native-screen-plan/1", screen_plan["format"])
            self.assertEqual("approval-required", screen_plan["approval"]["status"])
            self.assertEqual(
                ["lib/features/home/home_screen.dart"],
                screen_plan["file_scope"]["allowed"],
            )
            self.assertTrue(screen_plan["behavior_invariants"])
            self.assertTrue(screen_plan["acceptance_criteria"])
            with self.assertRaises(guard_tool.GuardError):
                guard_tool.capture_baseline(app, screen_plan)

            screen_plan["approval"] = {"status": "approved", "approved_scope": "HomeScreen"}
            baseline = guard_tool.capture_baseline(app, screen_plan)
            source = app / "lib" / "features" / "home" / "home_screen.dart"
            original = source.read_text(encoding="utf-8")
            source.write_text(original.replace("Available cash", "Your available cash"), encoding="utf-8")
            receipt = guard_tool.verify_change(app, screen_plan, baseline)
            self.assertEqual("mobile-native-change-receipt/1", receipt["format"])
            self.assertTrue(receipt["ok"])
            self.assertEqual(
                ["lib/features/home/home_screen.dart"],
                receipt["changed_files"],
            )
            self.assertTrue(all(item["preserved"] for item in receipt["invariants"]))

            source.write_text(original, encoding="utf-8")
            baseline = guard_tool.capture_baseline(app, screen_plan)
            source.write_text(
                original.replace("context.push('/detail/savings')", "context.push('/home')"),
                encoding="utf-8",
            )
            receipt = guard_tool.verify_change(app, screen_plan, baseline)
            self.assertFalse(receipt["ok"])
            self.assertTrue(any(not item["preserved"] for item in receipt["invariants"]))

            source.write_text(original, encoding="utf-8")
            baseline = guard_tool.capture_baseline(app, screen_plan)
            unapproved = (
                app
                / "lib"
                / "features"
                / "home"
                / "unapproved_widget.dart"
            )
            unapproved.write_text(
                "class UnapprovedWidget {}\n",
                encoding="utf-8",
            )
            receipt = guard_tool.verify_change(app, screen_plan, baseline)
            self.assertFalse(receipt["ok"])
            self.assertIn(
                "lib/features/home/unapproved_widget.dart",
                receipt["added_source_files"],
            )
            self.assertTrue(
                any(
                    violation["id"] == "file-scope.source-added"
                    for violation in receipt["violations"]
                )
            )

    def test_registry_is_atomic_native_and_complete_for_all_ten_families(self) -> None:
        registry = json.loads(
            (ASSETS / "capability-registry.json").read_text(encoding="utf-8")
        )
        self.assertEqual("mobile-native-capability-registry/2", registry["format"])
        self.assertEqual(2, registry["schema_version"])
        self.assertGreaterEqual(len(registry["rules"]), 30)
        required_fields = {
            "id",
            "triggers",
            "priority",
            "frameworks",
            "source_family",
            "required_project_evidence",
            "native_mapping",
            "benefit",
            "validation_rule",
            "legal_treatment",
            "rejection_conditions",
            "provenance",
        }
        by_source: dict[str, list[dict[str, object]]] = {}
        for rule in registry["rules"]:
            self.assertTrue(required_fields.issubset(rule))
            self.assertTrue(rule["required_project_evidence"])
            self.assertTrue(rule["rejection_conditions"])
            self.assertNotIn("web", rule["frameworks"])
            by_source.setdefault(rule["source_family"], []).append(rule)
        self.assertEqual(SOURCE_FAMILIES, set(by_source))
        for source, rules in by_source.items():
            self.assertGreaterEqual(len(rules), 3, source)
            covered = {framework for rule in rules for framework in rule["frameworks"]}
            self.assertEqual(FRAMEWORKS, covered, source)

    def test_v2_schema_defines_every_versioned_artifact_and_evidence_contract(self) -> None:
        path = ASSETS / "product-intelligence.schema.json"
        self.assertTrue(path.is_file(), path)
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema",
            schema["$schema"],
        )
        expected = {
            "evidence",
            "project",
            "screenGraph",
            "behaviorContract",
            "designLanguage",
            "appPlan",
            "screenPlan",
            "changeReceipt",
        }
        self.assertTrue(expected.issubset(schema["$defs"]))
        evidence = schema["$defs"]["evidence"]
        self.assertTrue(
            {"path", "line", "symbol", "confidence", "evidence_type"}.issubset(
                evidence["required"]
            )
        )
        self.assertIn(
            "added_source_files",
            schema["$defs"]["changeReceipt"]["required"],
        )

    def test_design_intelligence_is_searchable_across_every_family_and_framework(self) -> None:
        design = load_module("mobile_design")
        catalog = json.loads(
            (ASSETS / "design-intelligence.json").read_text(encoding="utf-8")
        )
        self.assertEqual("mobile-design-intelligence/2", catalog["format"])
        self.assertGreaterEqual(len(catalog["records"]), 20)
        self.assertEqual(SOURCE_FAMILIES, {record["source_family"] for record in catalog["records"]})
        for framework in FRAMEWORKS:
            results = design.query_catalog(
                "screen component motion accessibility state navigation",
                platform=framework,
            )
            self.assertTrue(results, framework)
            self.assertTrue(all(framework in result["frameworks"] for result in results))

    def test_motion_v2_models_interruption_gestures_and_reduced_motion(self) -> None:
        motion = load_module("mobile_motion")
        spec = {
            "format": "mobile-motion-spec/2",
            "name": "card-to-detail",
            "kind": "shared-transition",
            "variants": {
                "rest": {"opacity": 1.0, "scale": 1.0},
                "pressed": {"opacity": 0.94, "scale": 0.98},
                "detail": {"opacity": 1.0, "scale": 1.0},
            },
            "timeline": [
                {"label": "press", "from": "rest", "to": "pressed", "duration_ms": 90},
                {"label": "open", "from": "pressed", "to": "detail", "duration_ms": 240},
            ],
            "gesture": {"kind": "tap", "threshold": 0, "cancel_behavior": "return-to-rest"},
            "interruption": {"policy": "retarget", "resting_state": "rest"},
            "shared_transition": {"id": "account-card", "enabled": True},
            "haptic_intent": "selection",
            "performance_budget": {"max_simultaneous_animations": 8, "prefer_compositor": True},
            "reduced_motion": {"strategy": "opacity", "preserve_information": True, "disable_stagger": True},
        }
        self.assertEqual([], motion.validate_motion(spec))
        with tempfile.TemporaryDirectory() as temp:
            written = motion.generate_recipes(spec, platform="all", output=Path(temp))
            rendered = {path.name: path.read_text(encoding="utf-8") for path in written}
        self.assertIn("AnimationController", rendered["mobile_motion.dart"])
        self.assertIn("AccessibilityInfo", rendered["mobileMotion.ts"])
        self.assertIn("accessibilityReduceMotion", rendered["MobileMotion.swift"])
        self.assertIn("MotionDurationScale", rendered["MobileMotion.kt"])
        self.assertNotIn("LocalMotionDurationScale", rendered["MobileMotion.kt"])
        self.assertTrue(all("account-card" in value for value in rendered.values()))

    def test_generated_component_and_motion_sources_are_fixture_build_inputs(self) -> None:
        component = load_module("mobile_component")
        motion = load_module("mobile_motion")
        brief = json.loads(
            (ASSETS / "starter-component-brief.json").read_text(encoding="utf-8")
        )
        spec = json.loads(
            (ASSETS / "starter-motion-spec.json").read_text(encoding="utf-8")
        )
        expected_component_paths = {
            "flutter": ROOT / "fixtures/flutter/lib/generated/native_component.dart",
            "react-native": ROOT / "fixtures/react-native/src/generated/nativeComponent.tsx",
            "swiftui": ROOT
            / "fixtures/swiftui/TokenGallery/Sources/Generated/NativeComponent.swift",
            "compose": ROOT
            / "fixtures/compose/app/src/main/java/mobile/component/NativeComponent.kt",
        }
        expected_motion_paths = {
            "mobile_motion.dart": ROOT
            / "fixtures/flutter/lib/generated/mobile_motion.dart",
            "mobileMotion.ts": ROOT
            / "fixtures/react-native/src/generated/mobileMotion.ts",
            "MobileMotion.swift": ROOT
            / "fixtures/swiftui/TokenGallery/Sources/Generated/MobileMotion.swift",
            "MobileMotion.kt": ROOT
            / "fixtures/compose/app/src/main/java/mobile/motion/MobileMotion.kt",
        }
        with tempfile.TemporaryDirectory() as temp:
            temporary = Path(temp)
            for framework, fixture_path in expected_component_paths.items():
                generated = component.generate_component_source(
                    brief,
                    platform=framework,
                )
                self.assertEqual(
                    fixture_path.read_text(encoding="utf-8"),
                    generated,
                    framework,
                )
            written = motion.generate_recipes(spec, platform="all", output=temporary)
            for path in written:
                self.assertEqual(
                    expected_motion_paths[path.name].read_text(encoding="utf-8"),
                    path.read_text(encoding="utf-8"),
                    path.name,
                )

    def test_audit_consumes_project_model_and_component_forge_uses_screen_context(self) -> None:
        audit_tool = load_module("mobile_app_audit")
        project_tool = load_module("mobile_project")
        component_tool = load_module("mobile_component")
        brief = {
            "format": "mobile-screen-brief/1",
            "name": "home-account-card",
            "subject": "calm personal finance",
            "user_job": "Open one account without losing context.",
            "primary_action": "Open savings",
            "hierarchy": ["available cash", "accounts", "recent activity"],
            "signature_interaction": "Account card preserves identity into detail.",
            "dials": {
                "density": "comfortable",
                "contrast": "high",
                "shape": "soft",
                "typography": "system",
                "motion": "restrained",
            },
            "components": ["card", "list-row", "async-state"],
        }
        with tempfile.TemporaryDirectory() as temp:
            app = write_flutter_product(Path(temp))
            project = project_tool.scan_project(app, profile="full")
            audit = audit_tool.audit_project(app, profile="full")
            component = component_tool.create_plan(
                brief,
                platform="flutter",
                project_context=project,
                screen_id="HomeScreen",
            )

        self.assertEqual("mobile-native-project/2", audit["project_model"]["format"])
        self.assertEqual(
            audit["screens"],
            audit["project_model"]["screen_graph"]["screens"],
        )
        self.assertTrue(audit["findings"])
        self.assertTrue(
            all("current_code_evidence" in finding for finding in audit["findings"])
        )
        self.assertEqual("mobile-component-plan/2", component["format"])
        self.assertEqual("HomeScreen", component["screen_id"])
        self.assertTrue(component["project_context"]["existing_components"])
        self.assertTrue(component["behavior_invariants"])
        self.assertEqual(
            ["lib/features/home/home_screen.dart"],
            component["file_scope"]["allowed"],
        )

    def test_plugin_routes_seven_progressively_disclosed_skills(self) -> None:
        expected = {
            "mobile-native-design-system",
            "mobile-native-understand",
            "mobile-native-plan",
            "mobile-native-component-forge",
            "mobile-native-motion",
            "mobile-native-audit",
            "mobile-native-implement",
        }
        skills = PLUGIN / "skills"
        self.assertEqual(expected, {path.name for path in skills.iterdir() if path.is_dir()})
        router = (skills / "mobile-native-design-system" / "SKILL.md").read_text(encoding="utf-8")
        for skill in sorted(expected - {"mobile-native-design-system"}):
            self.assertIn(f"${skill}", router)
        for name in expected:
            skill = skills / name
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertTrue((skill / "agents" / "openai.yaml").is_file())

    def test_clean_context_routing_matrix_is_mobile_only_and_progressive(self) -> None:
        router = load_module("mobile_route")
        cases = (
            (
                "Understand every Flutter route and screen before suggesting changes.",
                "mobile-native-understand",
                "flutter",
            ),
            (
                "Create a prioritized React Native whole-product redesign plan.",
                "mobile-native-plan",
                "react-native",
            ),
            (
                "Audit this SwiftUI checkout screen for accessibility and hierarchy.",
                "mobile-native-audit",
                "swiftui",
            ),
            (
                "Design an interruptible shared transition in Jetpack Compose.",
                "mobile-native-motion",
                "compose",
            ),
            (
                "Forge a Flutter async status card with loading, retry, and empty states.",
                "mobile-native-component-forge",
                "flutter",
            ),
            (
                "Implement the approved Kotlin screen plan in this dirty worktree.",
                "mobile-native-implement",
                "compose",
            ),
        )
        for prompt, skill, framework in cases:
            with self.subTest(prompt=prompt):
                decision = router.route_request(prompt)
                self.assertEqual("mobile-native-route/1", decision["format"])
                self.assertEqual("mobile", decision["scope"])
                self.assertEqual(skill, decision["skill"])
                self.assertEqual(framework, decision["framework"])
                self.assertEqual(1, len(decision["skills_to_load"]))
                self.assertNotIn("web", decision["references"])

        ambiguous = router.route_request(
            "Redesign this mobile onboarding flow without changing behavior."
        )
        self.assertEqual("needs-project-evidence", ambiguous["framework"])
        self.assertEqual("mobile-native-understand", ambiguous["skill"])
        web = router.route_request(
            "Build a Next.js marketing page with Tailwind and browser animations."
        )
        self.assertEqual("out-of-scope", web["scope"])
        self.assertEqual([], web["skills_to_load"])
        self.assertTrue(web["rejected_runtimes"])


if __name__ == "__main__":
    unittest.main()
