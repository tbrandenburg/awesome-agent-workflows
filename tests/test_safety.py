"""High-signal runtime safety tests using real filesystem and Git operations."""

import json
import hashlib
import os
import subprocess
import sys
import tarfile

from runtime_case import RuntimeCase, embedded_source


def checks(command: str) -> list[dict]:
    return [
        {
            "kind": kind,
            "commands": [command] if kind == "tests" else [],
            "reason": "Isolated fixture",
        }
        for kind in ("typecheck", "lint", "tests", "build")
    ]


class SafetyTests(RuntimeCase):
    def test_lease_contention_and_release_ownership(self) -> None:
        lease = self.root / "lease"
        self.runtime["claim"](lease, "first")
        with self.assertRaisesRegex(RuntimeError, "busy or stale"):
            self.runtime["claim"](lease, "second")
        self.runtime["release"]({"lease": str(lease), "run": "second"})
        self.assertTrue(lease.exists())
        self.runtime["release"]({"lease": str(lease), "run": "first"})
        self.assertFalse(lease.exists())

    def test_ci_missing_pending_and_failing_checks_block(self) -> None:
        assess = self.runtime["assess"]
        self.assertFalse(assess([], ["test"]))
        self.assertFalse(assess([{"name": "test", "status": "IN_PROGRESS"}], ["test"]))
        self.assertTrue(
            assess(
                [{"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}],
                ["test"],
            )
        )
        with self.assertRaises(RuntimeError):
            assess([{"name": "test", "conclusion": "FAILURE"}], ["test"])
        with self.assertRaises(ValueError):
            assess([], [])

    def test_retargeted_or_changed_pr_invalidates_evidence(self) -> None:
        context = {"base": "main", "branch": "resolver/issue-1", "head": "abc123"}
        pr = {
            "state": "OPEN",
            "baseRefName": "main",
            "headRefName": "resolver/issue-1",
            "headRefOid": "abc123",
        }
        verify = self.runtime["verify_pr"]
        self.assertIsNone(verify(context, pr, "head"))
        for key, value in (
            ("baseRefName", "production"),
            ("state", "CLOSED"),
            ("headRefOid", "new"),
        ):
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                verify(context, {**pr, key: value}, "head")

    def test_changed_base_commit_invalidates_investigation(self) -> None:
        verify = self.runtime["verify_base"]
        context = {"base_sha": "investigated-base"}
        self.assertIsNone(verify(context, {"commit": {"sha": "investigated-base"}}))
        with self.assertRaisesRegex(RuntimeError, "base commit changed"):
            verify(context, {"commit": {"sha": "new-base"}})

    def test_cataloged_checks_cannot_be_omitted_or_injected(self) -> None:
        (self.root / "package.json").write_text(
            json.dumps({"scripts": {"lint": "eslint .", "test": "node test.js"}})
        )
        with self.assertRaisesRegex(ValueError, "cannot be omitted"):
            self.runtime["validate_checks"](checks("npm run test"), self.root)
        resolve = self.runtime["resolve"]
        self.assertEqual(
            resolve("npm run lint", "lint", self.root),
            ["npm", "run", "lint"],
        )
        with self.assertRaises(ValueError):
            resolve("npm run lint; echo unsafe", "lint", self.root)

    def test_failed_validation_preserves_work_and_redacts_artifacts(self) -> None:
        script = self.root / "resolver.py"
        script.write_text(embedded_source())
        marker = self.root / "unfinished.py"
        marker.write_text("print('keep')\n")
        command = "make test"
        (self.root / "Makefile").write_text(
            "test:\n\t@printf '%s' \"$$ANTHROPIC_API_KEY\"; exit 17\n"
        )
        plan = self.root / "plan.json"
        plan.write_text(json.dumps({"checks": checks(command)}))
        state = self.root / "context.json"
        state.write_text(
            json.dumps(
                {
                    "planned": True,
                    "validation_checks": checks(command),
                    "plan_digest": hashlib.sha256(plan.read_bytes()).hexdigest(),
                    "worktree": str(self.root),
                }
            )
        )
        result = subprocess.run(
            [sys.executable, "-I", str(script), "validate", "--state", str(state)],
            cwd=self.root,
            env={
                "PATH": os.environ["PATH"],
                "ANTHROPIC_API_KEY": "synthetic_private_fixture_key",
            },
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("validation command(s) failed", result.stderr)
        self.assertIn("Error 17", (self.root / "validation.log").read_text())
        self.assertEqual(marker.read_text(), "print('keep')\n")
        log = (self.root / "validation.log").read_text()
        self.assertIn("[REDACTED]", log)
        self.assertNotIn("synthetic_private_fixture_key", log)

    def test_ephemeral_recovery_captures_safe_source_only(self) -> None:
        execute = self.runtime["execute"]
        tree = self.root / "repo"
        execute(["git", "init", "-b", "main", str(tree)])
        (tree / "source.txt").write_text("before\n")
        execute(["git", "add", "."], tree)
        execute(
            [
                "git",
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-m",
                "fixture",
            ],
            tree,
        )
        (tree / "source.txt").write_text("after\n")
        (tree / "new.py").write_text("print('recover')\n")
        (tree / ".env").write_text("synthetic-credential\n")
        (tree / "link.py").symlink_to(tree / ".env")
        state = self.root / "context.json"
        self.runtime["save"](
            state,
            {
                "workspace_mode": "ephemeral",
                "worktree": str(tree),
                "repository": "owner/repo",
                "issue": 1,
                "branch": "main",
                "merged": False,
            },
        )
        self.runtime["recovery"](state)
        self.assertIn("+after", (self.root / "unfinished.patch").read_text())
        with tarfile.open(self.root / "unfinished-source.tar.gz") as archive:
            self.assertEqual(archive.getnames(), ["new.py"])
        self.assertTrue((tree / "new.py").exists())

    def test_recovery_rejects_symlinked_worktree(self) -> None:
        actual = self.root / "actual"
        actual.mkdir()
        link = self.root / "link"
        link.symlink_to(actual, target_is_directory=True)
        state = self.root / "context.json"
        self.runtime["save"](
            state,
            {"workspace_mode": "ephemeral", "worktree": str(link), "merged": False},
        )
        with self.assertRaisesRegex(RuntimeError, "symlinked"):
            self.runtime["recovery"](state)
        self.assertFalse((self.root / "unfinished-source.tar.gz").exists())

    def test_custom_config_is_not_overwritten_and_known_tokens_are_detected(
        self,
    ) -> None:
        config = self.runtime["managed_configuration"]
        self.assertTrue(config({"experimental": {"todo": True}, "providers": {}}))
        self.assertFalse(
            config(
                {
                    "experimental": {"todo": True},
                    "providers": {},
                    "instructions": ["custom.md"],
                }
            )
        )
        self.assertTrue(
            self.runtime["secret_content"](b"ghp_" + b"syntheticfixturetoken0123456789")
        )
        self.assertFalse(self.runtime["secret_content"](b"ordinary source text"))
