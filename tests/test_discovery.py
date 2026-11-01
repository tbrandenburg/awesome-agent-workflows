"""Repository-backed discovery and fail-closed CI from the deployable runtime."""

import hashlib
import json
import os
import subprocess
import sys

from runtime_case import RuntimeCase, documents, embedded_source


class DiscoveryTests(RuntimeCase):
    def fixture(self) -> dict:
        (self.root / "Makefile").write_text("test:\n\t@printf 'verified\\n'\n")
        folder = self.root / ".github/workflows"
        folder.mkdir(parents=True)
        (folder / "ci.yml").write_text(
            "on: [pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - run: make test\n"
        )
        return {
            "catalog": self.runtime["catalog"](self.root),
            "sources": [
                path.relative_to(self.root).as_posix()
                for path in self.runtime["sources"](self.root)
            ],
            "workflows": self.runtime["workflow_documents"](self.root),
            "policy": {"checks": []},
        }

    def test_generic_contract_and_merge_enabled_by_default(self) -> None:
        parent, child = documents()
        names = {item["name"] for item in parent["params"]}
        self.assertEqual(
            names,
            {
                "deployment_env_file",
                "workspace_root",
                "workspace_mode",
                "git_author_name",
                "git_author_email",
                "repository",
                "issue_number",
                "base_branch",
                "auto_merge",
            },
        )
        self.assertTrue(
            next(item for item in parent["params"] if item["name"] == "auto_merge")[
                "default"
            ]
        )
        steps = {item["id"]: item for item in child["steps"]}
        self.assertEqual(steps["plan"]["depends"], ["discover"])
        self.assertEqual(steps["discover"]["depends"], ["diagnose"])
        self.assertEqual(steps["implement"]["with"]["model"], "${params.economy}")
        self.assertEqual(
            steps["publication_metadata"]["with"]["model"], "${params.economy}"
        )

    def test_successful_discovery_and_actual_validation(self) -> None:
        discovery = self.fixture()
        self.assertEqual(discovery["catalog"]["tests"], [["make", "test"]])
        expected = self.runtime["expected_ci"](
            discovery, "main", "resolver/issue-1", ["source.py"]
        )
        self.assertEqual(expected, [{"name": "test", "app_id": 15368}])
        checks = [
            {
                "kind": kind,
                "commands": ["make test"] if kind == "tests" else [],
                "reason": "Makefile test target; no other configured checks",
            }
            for kind in ("typecheck", "lint", "tests", "build")
        ]
        plan = self.root / "plan.json"
        plan.write_text(json.dumps({"checks": checks, "discovery": discovery}))
        context = {
            "planned": True,
            "validation_checks": checks,
            "plan_digest": hashlib.sha256(plan.read_bytes()).hexdigest(),
        }
        result = self.runtime["run_checks"](
            context, str(self.root), self.root, "validation"
        )
        self.assertEqual(result, [{"command": "make test", "exit_code": 0}])
        self.assertIn("verified", (self.root / "validation.log").read_text())
        plan.write_text(json.dumps({"checks": checks}))
        with self.assertRaisesRegex(RuntimeError, "plan changed"):
            self.runtime["run_checks"](context, str(self.root), self.root, "validation")

    def test_missing_validation_blocks_real_runtime_subprocess(self) -> None:
        script = self.root / "resolver.py"
        script.write_text(embedded_source())
        state = self.root / "context.json"
        state.write_text(json.dumps({"worktree": str(self.root), "planned": True}))
        result = subprocess.run(
            [sys.executable, "-I", str(script), "validate", "--state", str(state)],
            env={"PATH": os.environ["PATH"]},
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("validation checks missing", result.stderr)
        self.assertEqual(json.loads(state.read_text())["phase"], "validation_failed")
        self.assertEqual(self.runtime["catalog"](self.root)["tests"], [])

    def test_missing_local_discovery_blocks_before_network_or_agent(self) -> None:
        script = self.root / "resolver.py"
        script.write_text(embedded_source())
        state = self.root / "context.json"
        state.write_text(json.dumps({"worktree": str(self.root), "planned": False}))
        result = subprocess.run(
            [sys.executable, "-I", str(script), "discover", "--state", str(state)],
            env={"PATH": os.environ["PATH"]},
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("No repository-backed", result.stderr)
        self.assertEqual(json.loads(state.read_text())["phase"], "discovery_blocked")
        self.assertFalse((self.root / "discovery.json").exists())

    def test_catalog_nested_checks_and_shell_injection(self) -> None:
        folder = self.root / "packages/api"
        folder.mkdir(parents=True)
        (folder / "package.json").write_text(
            json.dumps({"scripts": {"test:e2e": "node test.js", "lint": "eslint ."}})
        )
        catalog = self.runtime["catalog"](self.root)
        self.assertEqual(
            catalog["tests"], [["env", "-C", "packages/api", "npm", "run", "test:e2e"]]
        )
        self.assertEqual(
            catalog["lint"], [["env", "-C", "packages/api", "npm", "run", "lint"]]
        )
        for command in (
            "npm run invented",
            "make test; touch pwned",
            "env -C .. make test",
        ):
            with self.subTest(command=command), self.assertRaises(ValueError):
                self.runtime["resolve"](command, "tests", self.root)
        self.assertFalse((self.root / "pwned").exists())

    def test_matrix_include_exclude_and_reusable_jobs(self) -> None:
        workflows = {
            ".github/workflows/called.yml": {
                "on": {"workflow_call": {}},
                "jobs": {
                    "test": {
                        "name": "test ${{ matrix.node }}",
                        "strategy": {
                            "matrix": {
                                "node": ["20", "22"],
                                "include": [{"node": "24"}],
                                "exclude": [{"node": "20"}],
                            }
                        },
                    }
                },
            }
        }
        caller = {"jobs": {"call": {"uses": "./.github/workflows/called.yml"}}}
        self.assertEqual(
            self.runtime["job_names"](caller, workflows),
            ["call / test 22", "call / test 24"],
        )
        default = {"jobs": {"test": {"strategy": {"matrix": {"os": ["linux", "mac"]}}}}}
        self.assertEqual(
            self.runtime["job_names"](default, {}), ["test (linux)", "test (mac)"]
        )

    def test_filters_and_policy_checks_are_not_skipped(self) -> None:
        discovery = self.fixture()
        discovery["workflows"][".github/workflows/ci.yml"]["on"] = {
            "pull_request": {"branches": ["main"], "paths": ["src/**", "!src/docs/**"]}
        }
        expected = self.runtime["expected_ci"]
        self.assertEqual(
            expected(discovery, "main", "resolver/issue-1", ["src/app.py"]),
            [{"name": "test", "app_id": 15368}],
        )
        for base, paths in (
            ("release", ["src/app.py"]),
            ("main", ["src/docs/readme.md"]),
        ):
            with (
                self.subTest(base=base),
                self.assertRaisesRegex(ValueError, "No applicable"),
            ):
                expected(discovery, base, "resolver/issue-1", paths)
        discovery["policy"]["checks"] = [{"name": "protected-test", "app_id": None}]
        self.assertEqual(
            expected(discovery, "main", "resolver/issue-1", ["README.md"]),
            [{"name": "protected-test", "app_id": None}],
        )

    def test_ambiguous_and_missing_ci_fail_closed(self) -> None:
        names = self.runtime["job_names"]
        for job in (
            {"strategy": {"matrix": "${{ fromJSON(needs.setup.outputs.matrix) }}"}},
            {"name": "${{ inputs.name }}"},
            {"if": "${{ github.event_name == 'push' }}"},
            {"continue-on-error": "true"},
            {"uses": "owner/repo/.github/workflows/ci.yml@main"},
        ):
            with self.subTest(job=job), self.assertRaises(ValueError):
                names({"jobs": {"test": job}}, {})
        with self.assertRaisesRegex(ValueError, "No applicable"):
            self.runtime["expected_ci"](
                {"workflows": {}, "policy": {"checks": []}},
                "main",
                "resolver/issue-1",
                ["x"],
            )
        assess = self.runtime["assess"]
        self.assertFalse(assess([], ["test"]))
        self.assertFalse(assess([{"name": "test", "status": "IN_PROGRESS"}], ["test"]))
        self.assertFalse(
            assess(
                [{"name": "test", "conclusion": "SKIPPED", "status": "COMPLETED"}],
                ["test"],
            )
        )
        with self.assertRaisesRegex(RuntimeError, "CI failed"):
            assess([{"name": "test", "conclusion": "FAILURE"}], ["test"])
        with self.assertRaisesRegex(ValueError, "empty CI"):
            assess([], [])

    def test_unrelated_manual_resolver_is_not_an_automatic_ci_prerequisite(
        self,
    ) -> None:
        discovery = self.fixture()
        discovery["workflows"][".github/workflows/manual-resolver.yml"] = {
            "on": {"workflow_dispatch": {"inputs": {"legacy_argument": {}}}},
            "jobs": {"manual": {"if": "${{ inputs.run }}", "steps": []}},
        }
        self.assertEqual(
            self.runtime["expected_ci"](
                discovery, "main", "resolver/issue-1", ["source.py"]
            ),
            [{"name": "test", "app_id": 15368}],
        )
        self.assertFalse(
            self.runtime["triggered"](
                discovery["workflows"][".github/workflows/manual-resolver.yml"],
                "main",
                "resolver/issue-1",
                ["source.py"],
            )
        )
