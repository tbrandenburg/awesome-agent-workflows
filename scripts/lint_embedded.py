"""Pass declared Python runtime blocks to Ruff without executing or rewriting them."""

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
            for step in document.get("steps", []):
                if step.get("id") != "materialize_runtime":
                    continue
                print(f"Linting embedded Python: {path}", flush=True)
                subprocess.run(
                    [
                        arguments.ruff,
                        "check",
                        "--stdin-filename",
                        str(path.with_suffix(".py")),
                        "-",
                    ],
                    input=step["with"]["content"],
                    text=True,
                    check=True,
                    timeout=30,
                )


if __name__ == "__main__":
    main()
