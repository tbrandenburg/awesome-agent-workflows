"""Verify actual Dagu materialization, not only the YAML parser's runtime text."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from runtime_case import RuntimeCase, WORKFLOW, embedded_source


class MaterializationTests(RuntimeCase):
    def test_dagu_preserves_runtime_and_matrix_expression_matching(self) -> None:
        binary = shutil.which("dagu")
        self.assertIsNotNone(
            binary, "Dagu is required for the materialization regression"
        )
        dotenv = self.root / "synthetic.env"
        dotenv.write_text(
            "GH_TOKEN=synthetic-github\nTELEGRAM_BOT_TOKEN=synthetic-telegram\n"
            "TELEGRAM_CHAT_ID=synthetic-chat\n"
        )
        params = {
            "repository": "fixture/disposable",
            "workspace_root": str(self.root / "workspaces"),
            "deployment_env_file": str(dotenv),
        }
        home = self.root / "dagu"
        result = subprocess.run(
            [
                binary,
                "start",
                str(WORKFLOW),
                "--only",
                "materialize_runtime",
                "--params",
                json.dumps(params),
            ],
            env={
                "PATH": str(Path(sys.executable).parent)
                + os.pathsep
                + os.environ["PATH"],
                "HOME": str(self.root),
                "DAGU_HOME": str(home),
            },
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        files = list((home / "data/artifacts").glob("**/resolver.py"))
        self.assertEqual(len(files), 1)
        source = files[0].read_text()
        self.assertEqual(source, embedded_source())
        runtime = {"__name__": "materialized_runtime"}
        exec(compile(source, str(files[0]), "exec"), runtime)
        job = {
            "jobs": {
                "test": {
                    "name": "test ${{ matrix.node }}",
                    "strategy": {"matrix": {"node": ["20", "22"]}},
                }
            }
        }
        self.assertEqual(runtime["job_names"](job, {}), ["test 20", "test 22"])
        self.assertFalse((self.root / "workspaces").exists())
