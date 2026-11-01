"""Exercise discovery-plan blockers through the real embedded CLI."""

import json
import os
import subprocess
import sys

from runtime_case import RuntimeCase, embedded_source


class PlanTests(RuntimeCase):
    def test_ambiguous_missing_and_unapproved_validation_block_plan(self) -> None:
        (self.root / "Makefile").write_text(
            "test:\n\t@printf 'tests\\n'\nlint:\n\t@printf 'lint\\n'\n"
        )
        script = self.root / "resolver.py"
        script.write_text(embedded_source())
        sources = [
            path.relative_to(self.root).as_posix()
            for path in self.runtime["sources"](self.root)
        ]
        discovery = {"sources": sources, "policy": {"checks": []}, "workflows": {}}
        (self.root / "discovery.json").write_text(json.dumps(discovery))
        checks = [
            {
                "kind": kind,
                "commands": ["make test"]
                if kind == "tests"
                else ["make lint"]
                if kind == "lint"
                else [],
                "reason": "Actual fixture Makefile targets",
            }
            for kind in ("typecheck", "lint", "tests", "build")
        ]
        original = {
            "summary": "Fix the pinned issue",
            "files": ["source.py"],
            "steps": ["Fix source and test"],
            "risks": [],
            "checks": checks,
            "report_markdown": "Investigation with repository evidence",
            "inspected_sources": sources,
            "blockers": [],
        }
        cases = [
            (
                {
                    **original,
                    "blockers": ["Instructions require an unsupported custom checker"],
                },
                "ambiguous or unavailable",
            ),
            ({**original, "inspected_sources": []}, "must inspect"),
            (
                {
                    **original,
                    "checks": [
                        {**item, "commands": []} if item["kind"] == "tests" else item
                        for item in checks
                    ],
                },
                "Tests cannot",
            ),
            (
                {
                    **original,
                    "checks": [
                        {**item, "commands": []} if item["kind"] == "lint" else item
                        for item in checks
                    ],
                },
                "cannot be omitted",
            ),
            (
                {
                    **original,
                    "checks": [
                        {**item, "commands": ["make test; touch pwned"]}
                        if item["kind"] == "tests"
                        else item
                        for item in checks
                    ],
                },
                "Unapproved",
            ),
            (original, "No applicable expected GitHub checks"),
        ]
        state = self.root / "context.json"
        for report, message in cases:
            with self.subTest(message=message):
                state.write_text(
                    json.dumps(
                        {
                            "worktree": str(self.root),
                            "base": "main",
                            "branch": "resolver/issue-1",
                            "planned": False,
                        }
                    )
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        str(script),
                        "record-plan",
                        "--state",
                        str(state),
                    ],
                    input=json.dumps(report),
                    env={"PATH": os.environ["PATH"]},
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(message, result.stderr)
                context = json.loads(state.read_text())
                self.assertFalse(context["planned"])
                self.assertEqual(context["phase"], "discovery_blocked")
                self.assertFalse((self.root / "plan.json").exists())
        self.assertFalse((self.root / "pwned").exists())

    def test_recorded_plan_cannot_be_replaced_on_repair(self) -> None:
        script = self.root / "resolver.py"
        script.write_text(embedded_source())
        state = self.root / "context.json"
        state.write_text(json.dumps({"planned": True}))
        result = subprocess.run(
            [sys.executable, "-I", str(script), "record-plan", "--state", str(state)],
            input="{}",
            env={"PATH": os.environ["PATH"]},
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("write-once", result.stderr)
        self.assertFalse((self.root / "planning-agent.txt").exists())
        self.assertTrue(json.loads(state.read_text())["planned"])
