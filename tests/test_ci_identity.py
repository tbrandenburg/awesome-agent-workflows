"""App-bound CI success must refer to the reviewed head, never stale rollup names."""

from runtime_case import RuntimeCase


class IdentityTests(RuntimeCase):
    def test_missing_pending_failed_wrong_app_and_stale_checks_block(self) -> None:
        assess = self.runtime["ci_identities"]
        expected = [{"name": "test", "app_id": 15368}]
        check = {
            "name": "test",
            "app": {"id": 15368},
            "head_sha": "reviewed-head",
            "status": "completed",
            "conclusion": "success",
        }
        self.assertFalse(assess([], expected, "reviewed-head"))
        self.assertTrue(assess([check], expected, "reviewed-head"))
        for field, value in (
            ("head_sha", "stale-head"),
            ("app", {"id": 999}),
            ("status", "in_progress"),
            ("conclusion", "failure"),
            ("name", "unrelated-test"),
        ):
            with self.subTest(field=field):
                self.assertFalse(
                    assess([{**check, field: value}], expected, "reviewed-head")
                )
