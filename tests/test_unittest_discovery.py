"""Discover a real instruction/workflow-backed unittest entrypoint without a manifest."""

from runtime_case import RuntimeCase


class UnittestDiscoveryTests(RuntimeCase):
    def test_existing_documented_and_ci_command_is_discovered_once(self) -> None:
        folder = self.root / "experiments/sample"
        folder.mkdir(parents=True)
        (folder / "test_sample.py").write_text(
            "import unittest\nclass Sample(unittest.TestCase):\n"
            "    def test_sample(self):\n        self.assertEqual(2 + 2, 4)\n"
        )
        command = "python3 -m unittest discover -s experiments/sample -p 'test_*.py' -v"
        (folder / "README.md").write_text(
            "## Validate\n```bash\n" + command + "\n```\n"
        )
        workflows = self.root / ".github/workflows"
        workflows.mkdir(parents=True)
        (workflows / "ci.yml").write_text(
            "on: [pull_request]\njobs:\n  test:\n    steps:\n      - name: Test\n"
            "        run: " + command + "\n"
        )
        expected = [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "experiments/sample",
            "-p",
            "test_*.py",
            "-v",
        ]
        catalog = self.runtime["catalog"](self.root)
        self.assertEqual(catalog["tests"], [expected])
        self.assertEqual(self.runtime["resolve"](command, "tests", self.root), expected)
        self.assertEqual(catalog["lint"], [])

    def test_missing_tests_traversal_and_shell_or_unknown_flags_are_rejected(
        self,
    ) -> None:
        validate = self.runtime["unittest_command"]
        prefix = ["python3", "-m", "unittest", "discover"]
        self.assertFalse(validate(prefix, self.root))
        for arguments in (
            ["-s", ".."],
            ["-s", "/tmp"],
            ["-s", "missing"],
            ["-p", "test_*.py;touch marker"],
            ["--invented-check"],
            ["-v", "&&", "true"],
            ["-s", ".", "-s", "."],
        ):
            with self.subTest(arguments=arguments):
                self.assertFalse(validate(prefix + arguments, self.root))
        (self.root / "README.md").write_text(
            "python3 -m unittest discover -s missing\n"
        )
        with self.assertRaisesRegex(ValueError, "no matching project tests"):
            self.runtime["catalog"](self.root)
