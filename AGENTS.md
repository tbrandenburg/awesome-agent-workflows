# Using this project

This repository contains portable Dagu workflows for software-engineering tasks. The primary deployment is a user's own Dagu instance, which can run the workflow against any GitHub repository that account can access. GitHub Actions is an optional alternative deployment, not a requirement. The current workflow resolves a GitHub issue using OpenCode; it executes trusted repository code and agent edits with the host user's permissions.

## Run issue resolution

1. On the machine running your Dagu instance, install Dagu, OpenCode, Python 3.11+ with PyYAML 6.0.3, GNU env, Git, and GitHub CLI. Ensure the target repository's dependencies and validation tools are available.
2. Configure `GH_TOKEN`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID`, plus at least one usable inference provider. Keep credentials outside the repository; see [the workflow guide](docs/issue-resolution.md#credentials).
3. Run directly from this checkout using your Dagu CLI, replacing the example inputs with any target GitHub repository you can access and an absolute writable workspace path:

   ```bash
   dagu start workflows/issue-resolution.yaml --params \
     'repository=owner/repository issue_number=123 workspace_root="/absolute/path/to/workspaces" deployment_env_file="/absolute/path/to/deployment.env"'
   ```

   Use `issue_number=0` to select an open issue. Repository validation and CI expectations are discovered during investigation and verified deterministically. `auto_merge` defaults to `true`; merging still requires validation, independent review, expected CI, and remote-state gates to pass. Set `auto_merge=false` to leave the PR open for manual review. Never run against an untrusted repository. See [parameters, deployment options, recovery, and safety details](docs/issue-resolution.md).

The local Dagu service has `DAGU_HOME=/var/lib/dagu`; its workflow is symlinked at `/var/lib/dagu/dags/issue-resolution.yaml` to `workflows/issue-resolution.yaml` in this checkout. Verify discovery with `DAGU_HOME=/var/lib/dagu dagu ls issue-resolution`. For another Dagu instance, check that service's `DAGU_HOME` and DAG directory before placing or symlinking the workflow; the interactive CLI may use different configuration. Direct CLI execution does not require a symlink or scheduler. See [local deployment](docs/issue-resolution.md#local-deployment); GitHub Actions setup is optional.

## Develop and validate

- The standing approved acceptance-test repository is `tbrandenburg/playground`. Create clearly labeled dummy issues there when needed; workflow commits, pushes, PRs, issue/PR comments, and Telegram outcome notifications are authorized for these tests. Do not modify unrelated playground work. Keep `auto_merge=false` unless merging is explicitly authorized for the test.
- The first acceptance-test host is this local system running the canonical YAML with Dagu. Verify local runtime evidence, the resulting PR, validation/review, downstream CI, and Telegram delivery before claiming success. GitHub Actions is an optional secondary deployment target, not the primary test host or a prerequisite for local testing.
- This test-target approval does not authorize committing or pushing changes to this workflow repository; that still requires an explicit request.
- Add deployable workflow YAML under `workflows/` and its usage guide under `docs/`.
- Keep child DAGs, prompts, and runtime glue in the workflow file; never bundle credentials or machine-specific state. Follow [contribution guidelines](CONTRIBUTING.md).
- Run `make install` once to create the local Python environment, then `make test`, `make lint`, and `make validate` before submitting changes.
