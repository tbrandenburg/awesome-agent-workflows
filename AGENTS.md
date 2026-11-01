# Using this project

This repository contains portable Dagu workflows for software-engineering tasks. The primary deployment is a user's own Dagu instance, which can run the workflow against any GitHub repository that account can access. GitHub Actions is an optional alternative deployment, not a requirement. The current workflow resolves a GitHub issue using OpenCode; it executes trusted repository code and agent edits with the host user's permissions.

## Run issue resolution

1. On the machine running your Dagu instance, install Dagu, OpenCode, Python 3.11+, Git, and GitHub CLI. Ensure the target repository's dependencies and validation command are available.
2. Configure `GH_TOKEN`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID`, plus at least one usable inference provider. Keep credentials outside the repository; see [the workflow guide](docs/issue-resolution.md#credentials).
3. Run directly from this checkout using your Dagu CLI, replacing the example inputs with any target GitHub repository you can access and an absolute writable workspace path:

   ```bash
   dagu start workflows/issue-resolution.yaml --params \
     'repository=owner/repository issue_number=123 validation_command="make test" required_checks=test workspace_root="/absolute/path/to/workspaces" deployment_env_file="/absolute/path/to/deployment.env"'
   ```

   Use `issue_number=0` to select an open issue. `auto_merge` defaults to `true`, so the workflow can merge after its validation, independent review, required CI, and remote-state gates pass. Set `auto_merge=false` when you want to review the PR before merging. Never run against an untrusted repository. See [all parameters, deployment options, recovery, and safety details](docs/issue-resolution.md).

The local Dagu service has `DAGU_HOME=/var/lib/dagu`; its workflow is symlinked at `/var/lib/dagu/dags/issue-resolution.yaml` to `workflows/issue-resolution.yaml` in this checkout. Verify discovery with `DAGU_HOME=/var/lib/dagu dagu ls issue-resolution`. For another Dagu instance, check that service's `DAGU_HOME` and DAG directory before placing or symlinking the workflow; the interactive CLI may use different configuration. Direct CLI execution does not require a symlink or scheduler. See [local deployment](docs/issue-resolution.md#local-deployment); GitHub Actions setup is optional.

## Develop and validate

- Add deployable workflow YAML under `workflows/` and its usage guide under `docs/`.
- Keep child DAGs, prompts, and runtime glue in the workflow file; never bundle credentials or machine-specific state. Follow [contribution guidelines](CONTRIBUTING.md).
- Run `make install` once to create the local Python environment, then `make test`, `make lint`, and `make validate` before submitting changes.
