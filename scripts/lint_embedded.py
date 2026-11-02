"""Lint native Python/Bash run blocks without executing workflow code."""

import argparse
import subprocess
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ruff", default="ruff")
    parser.add_argument("paths", nargs="+", type=Path)
    arguments = parser.parse_args()
    for path in arguments.paths:
        for document in yaml.safe_load_all(path.read_text()):
            steps = [*document.get("steps", []), *document.get("handler_on", {}).values()]
            steps += [
                step for job in document.get("jobs", {}).values() for step in job.get("steps", [])
            ]
            for step in steps:
                language = step.get("shell") or step.get("with", {}).get("shell")
                source = step.get("run", "")
                if language in ("python", "python3"):
                    print(f"Linting native Python: {path}", flush=True)
                    for command in (["check"], ["format", "--check"]):
                        subprocess.run(
                            [
                                arguments.ruff,
                                *command,
                                "--stdin-filename",
                                str(path.with_suffix(".py")),
                                "-",
                            ],
                            input=source,
                            text=True,
                            check=True,
                            timeout=30,
                        )
                if language == "bash":
                    print(f"Linting native Bash: {path}", flush=True)
                    subprocess.run(
                        ["shellcheck", "--shell=bash", "-"],
                        input=source,
                        text=True,
                        check=True,
                        timeout=30,
                    )


if __name__ == "__main__":
    main()
