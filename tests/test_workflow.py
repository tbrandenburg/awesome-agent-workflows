"""Validate the published workflow's structure and agent execution contracts."""

import json
import subprocess
import sys

from runtime_case import RuntimeCase, documents, embedded_source


class WorkflowTests(RuntimeCase):
    def test_single_file_contains_entrypoint_child_runtime_and_prompts(self) -> None:
        parent, child = documents()
        self.assertNotIn("schedule", parent)
        self.assertEqual(child["name"], "issue-resolution-attempt")
        prompts = {
            item["id"] for item in parent["steps"] if item["id"].startswith("prompt_")
        }
        self.assertEqual(
            prompts,
            {
                "prompt_plan",
                "prompt_implement",
                "prompt_publication",
                "prompt_ci_repair",
                "prompt_review",
            },
        )
        self.assertNotIn("workspace/scripts/", embedded_source())
        self.assertNotIn("/home/", embedded_source())

    def test_model_selection_precedes_clone_and_pins_child_models(self) -> None:
        parent, child = documents()
        steps = {item["id"]: item for item in parent["steps"]}
        self.assertEqual(steps["select_models"]["depends"], ["prepare"])
        self.assertEqual(steps["checkout"]["depends"], ["select_models"])
        self.assertEqual(
            steps["resolve"]["with"]["params"]["economy"],
            "${select_models.output.context.models.economy}",
        )
        self.assertEqual(
            steps["repair"]["with"]["params"]["balanced"],
            "${select_models.output.context.models.balanced}",
        )
        choices = {
            key: json.loads(value)
            for item in parent["consts"]
            for key, value in item.items()
        }
        self.assertEqual(set(choices), {"economy", "balanced", "premium"})
        self.assertEqual(choices["economy"][0], "openai/gpt-6-luna")
        self.assertEqual(choices["balanced"][0], "openai/gpt-6.1-sol")
        self.assertTrue(
            choices["economy"].index("openrouter/openai/gpt-6-luna")
            < choices["economy"].index("opencode/big-pickle")
        )
        self.assertNotIn("premium", {item["name"] for item in child["params"]})

    def test_planning_publication_and_validation_cannot_be_skipped(self) -> None:
        _, child = documents()
        steps = {item["id"]: item for item in child["steps"]}
        self.assertEqual(steps["implement"]["depends"], ["publish_plan"])
        self.assertEqual(steps["publish_pr"]["depends"], ["record_publication"])
        self.assertEqual(steps["review_gate"]["depends"], ["independent_review"])
        self.assertEqual(steps["ci_gate"]["depends"], ["review_gate"])
        models = {
            item["id"]: item["with"]["model"]
            for item in child["steps"]
            if item.get("action") == "harness.run"
        }
        self.assertEqual(models["plan"], "${params.balanced}")
        self.assertEqual(models["independent_review"], "${params.economy}")

    def test_embedded_runtime_runs_without_repository_helpers(self) -> None:
        script = self.root / "resolver with spaces.py"
        script.write_text(embedded_source())
        result = subprocess.run(
            [sys.executable, "-I", str(script), "agent", "--help"],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--model", result.stdout)
        self.assertIn("prompt", result.stdout)

    def test_invalid_repository_has_no_side_effects(self) -> None:
        parse = self.runtime["repository"]
        self.assertEqual(parse("owner/repository"), "owner/repository")
        for value in ("../repo", "owner/..", "owner/repo;id", "a/b/c"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse(value)

    def test_auth_metadata_priority_and_free_fallback(self) -> None:
        auth = self.runtime["auth_providers"](
            [{"id": "anthropic", "connections": [{"type": "credential"}]}]
        )
        self.assertEqual(auth, {"anthropic"})
        candidates = ["openai/economy", "anthropic/economy", "opencode/big-pickle"]
        select = self.runtime["resolve_tier"]
        selected = select(candidates, auth, set(candidates), lambda _: "ready")
        self.assertEqual(selected["selected"], "anthropic/economy")
        self.assertFalse(selected["degraded"])
        fallback = select(candidates, set(), set(candidates), lambda _: "ready")
        self.assertEqual(fallback["selected"], "opencode/big-pickle")
        self.assertTrue(fallback["degraded"])
        with self.assertRaisesRegex(RuntimeError, "no silent downgrade"):
            select(candidates, {"openai"}, set(candidates), lambda _: "timeout")
