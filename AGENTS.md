# Using this project

This repository contains portable Dagu workflows for software-engineering tasks. The current workflow resolves a GitHub issue using OpenCode; it executes trusted repository code and agent edits with the host user's permissions.

## Run issue resolution

1. Install Dagu, OpenCode, Python 3.11+, Git, and GitHub CLI. Ensure the target repository's dependencies and validation command are available.
2. Configure `GH_TOKEN`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID`, plus at least one usable inference provider. Keep credentials outside the repository; see [the workflow guide](docs/issue-resolution.md#credentials).
3. Run from the repository root, replacing the example inputs with your target and an absolute writable workspace path:

   ```bash
   dagu start workflows/issue-resolution.yaml --params \
     'repository=owner/repository issue_number=123 validation_command="make test" required_checks=test auto_merge=false workspace_root="/absolute/path/to/workspaces" deployment_env_file="/absolute/path/to/deployment.env"'
   ```

   Use `issue_number=0` to select an open issue. Start with `auto_merge=false`; inspect the resulting PR before enabling automatic merge. Never run against an untrusted repository. See [all parameters, deployment options, recovery, and safety details](docs/issue-resolution.md).

## Develop and validate

- Add deployable workflow YAML under `workflows/` and its usage guide under `docs/`.
- Keep child DAGs, prompts, and runtime glue in the workflow file; never bundle credentials or machine-specific state. Follow [contribution guidelines](CONTRIBUTING.md).
- Run `make install` once to create the local Python environment, then `make test`, `make lint`, and `make validate` before submitting changes.
