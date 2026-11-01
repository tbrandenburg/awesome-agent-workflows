"""Load tests from the deployable YAML, with no parallel helper implementation."""

import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "workflows/issue-resolution.yaml"


def documents() -> list[dict]:
    return list(yaml.safe_load_all(WORKFLOW.read_text()))


def embedded_source() -> str:
    entrypoint = documents()[0]
    step = next(
        item for item in entrypoint["steps"] if item["id"] == "materialize_runtime"
    )
    return step["with"]["content"]


class RuntimeCase(unittest.TestCase):
    def setUp(self) -> None:
        directory = ROOT / "workspace/tmp"
        directory.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=directory)
        self.root = Path(self.temporary.name)
        self.runtime = {"__name__": "workflow_runtime"}
        exec(compile(embedded_source(), str(WORKFLOW), "exec"), self.runtime)

    def tearDown(self) -> None:
        self.temporary.cleanup()
