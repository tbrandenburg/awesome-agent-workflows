# Using this project

This repository contains portable Dagu workflows for software-engineering tasks. The primary
deployment is a user's own Dagu instance, which can run the workflow against any GitHub repository
that account can access. GitHub Actions is an optional alternative deployment, not a requirement.
The current workflow resolves a GitHub issue using OpenCode; it executes trusted repository code and
agent edits with the host user's permissions.

## Repository boundary

- This is a personal workflow collection, not an application, SDK, or test platform. Keep deployable
  workflows and concise guides as the primary artifacts.
- Use standard formatting, linting, and native workflow validation. Do not add a checked-in
  behavioral test framework, fixtures, mocks, coverage/mutation infrastructure, or another workflow
  runner unless explicitly requested.
- The agent verifies behavior by executing the canonical workflow locally and inspecting real
  outputs, side effects, and meaningful failure/recovery paths. Keep disposable harnesses and
  private run evidence outside the tracked repository.
- Small lint-only extraction glue is allowed for embedded code; YAML validity alone does not
  validate Python literal blocks. Do not expand this glue into a parser or execution framework.
- Prefer native Dagu actions and concise runtime glue. Changes to tooling must not rewrite workflow
  sources unless explicitly in scope. The two current executable workflow files are excluded from
  automatic formatting for this surrounding-tooling cleanup; remove those exclusions only during an
  authorized workflow-formatting change.
- Collection-level cleanup must preserve workflow runtime safety: repository-backed validation,
  independent review, current head/base checks, expected CI, credential protection, bounded repair,
  recovery, and verified merge/issue closure. Target repositories still need their real tests.

## Run issue resolution

1. On the machine running your Dagu instance, install Dagu, OpenCode, Python 3.11+ with PyYAML
   6.0.3, GNU env, Git, and GitHub CLI. Ensure the target repository's dependencies and validation
   tools are available.
2. Configure `GH_TOKEN`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID`, plus at least one usable
   inference provider. Keep credentials outside the repository; see
   [the workflow guide](docs/issue-resolution.md#credentials).
3. Run directly from this checkout using your Dagu CLI, replacing the example inputs with any target
   GitHub repository you can access and an absolute writable workspace path:

   ```bash
   dagu start workflows/issue-resolution.yaml --params \
     'repository=owner/repository issue_number=123 workspace_root="/absolute/path/to/workspaces" deployment_env_file="/absolute/path/to/deployment.env"'
   ```

   Use `issue_number=0` to select an open issue. Repository validation and CI expectations are
   discovered during investigation and verified deterministically. `auto_merge` defaults to `true`;
   merging still requires validation, independent review, expected CI, and remote-state gates to
   pass. Set `auto_merge=false` to leave the PR open for manual review. Never run against an
   untrusted repository. See
   [parameters, deployment options, recovery, and safety details](docs/issue-resolution.md).

The local Dagu service has `DAGU_HOME=/var/lib/dagu`; its workflow is symlinked at
`/var/lib/dagu/dags/issue-resolution.yaml` to `workflows/issue-resolution.yaml` in this checkout.
Verify discovery with `DAGU_HOME=/var/lib/dagu dagu ls issue-resolution`. For another Dagu instance,
check that service's `DAGU_HOME` and DAG directory before placing or symlinking the workflow; the
interactive CLI may use different configuration. Direct CLI execution does not require a symlink or
scheduler. See [local deployment](docs/issue-resolution.md#local-deployment); GitHub Actions setup
is optional.

## Develop and validate

- The standing approved acceptance-test repository is `tbrandenburg/playground`. Create clearly
  labeled dummy issues there when needed; workflow commits, pushes, PRs, issue/PR comments, and
  Telegram outcome notifications are authorized for these tests. Do not modify unrelated playground
  work. Keep `auto_merge=false` unless merging is explicitly authorized for the test.
- The first acceptance-test host is this local system running the canonical YAML with Dagu. Verify
  local runtime evidence, the resulting PR, validation/review, downstream CI, and Telegram delivery
  before claiming success. GitHub Actions is an optional secondary deployment target, not the
  primary test host or a prerequisite for local testing.
- This test-target approval does not authorize committing or pushing changes to this workflow
  repository; that still requires an explicit request.
- Add deployable workflow YAML under `workflows/` and its usage guide under `docs/`.
- Keep child DAGs, prompts, and runtime glue in the workflow file; never bundle credentials or
  machine-specific state. Follow [contribution guidelines](CONTRIBUTING.md).
- Tooling needs Python 3.12+, Node.js 24+, Dagu, actionlint, and ShellCheck on the host.
  `make install` installs the pinned Python and Prettier dependencies into this checkout; it does
  not install or reconfigure the host Dagu service.
- Use `make format` to format surrounding files, `make format-check` for read-only formatting
  checks, and `make validate` for formatting, linting, and Dagu schema validation. There is no
  collection-level behavioral test target.
- `scripts/lint_embedded.py` passes the declared `materialize_runtime` Python blocks to Ruff without
  executing or rewriting them. Other embedded languages need appropriate direct tool checks when
  introduced, not a generic test harness.
