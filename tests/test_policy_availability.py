"""Distinguish explicit policy-feature absence from unavailable policy discovery."""

from runtime_case import RuntimeCase


class PolicyAvailabilityTests(RuntimeCase):
    def test_proven_feature_absence_is_narrow_and_never_empty_ci_success(self) -> None:
        absent = self.runtime["policy_feature_absent"]
        branch = {"protected": False}
        repository = {
            "private": True,
            "owner": {"type": "User"},
            "permissions": {"admin": True},
        }
        error = {
            "status": "403",
            "message": "Upgrade to GitHub Pro or make this repository public to enable this feature.",
        }
        self.assertTrue(absent(branch, repository, [error, error]))
        self.assertTrue(absent(branch, repository, [[error], error]))
        for change in (
            {"private": False},
            {"owner": {"type": "Organization"}},
            {"permissions": {"admin": False}},
        ):
            with self.subTest(change=change):
                self.assertFalse(
                    absent(branch, {**repository, **change}, [error, error])
                )
        self.assertFalse(absent({"protected": True}, repository, [error, error]))
        self.assertFalse(absent(branch, repository, [error]))
        self.assertFalse(
            absent(
                branch,
                repository,
                [
                    error,
                    {
                        "status": 403,
                        "message": "Resource not accessible by integration",
                    },
                ],
            )
        )
        self.assertFalse(absent(branch, repository, [error, {"status": 404}]))
        with self.assertRaisesRegex(ValueError, "No applicable"):
            self.runtime["expected_ci"](
                {"policy": {"checks": []}, "workflows": {}},
                "main",
                "resolver/issue-1",
                ["source.py"],
            )
