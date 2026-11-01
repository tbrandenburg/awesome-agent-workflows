"""Exercise the visibility guard from the actual published Actions wrapper."""

import ast
import unittest

import yaml

from runtime_case import ROOT


class RunnerTests(unittest.TestCase):
    def test_private_tasks_cannot_publish_logs_from_a_public_host(self) -> None:
        path = ROOT / ".github/workflows/run-issue-resolution.yml"
        workflow = yaml.safe_load(path.read_text())
        step = next(
            item
            for item in workflow["jobs"]["resolve"]["steps"]
            if item.get("name") == "Run self-contained DAG"
        )
        source = step["run"].split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        tree = ast.parse(source)
        guard = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "require_private_host"
        )
        namespace = {}
        exec(
            compile(ast.Module(body=[guard], type_ignores=[]), str(path), "exec"),
            namespace,
        )
        require = namespace["require_private_host"]
        self.assertIsNone(require(False, "false"))
        self.assertIsNone(require(True, "true"))
        with self.assertRaisesRegex(ValueError, "Private targets require"):
            require(True, "false")
        with self.assertRaisesRegex(ValueError, "Cannot verify"):
            require(None, "true")
