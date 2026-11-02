# Awesome Agent Workflows

Self-contained, portable [Dagu](https://github.com/dagucloud/dagu) agent workflows for software
engineering.

Start with one useful workflow, keep its behavior observable and testable, and grow the collection
with workflows worth reusing. Each workflow should be deployable by copying a single YAML file,
without a project-specific helper repository or an installed prompt collection.

## Workflows

| Workflow                                            | What it does                                                                                                                                                                      | Trigger |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| [Issue resolution](workflows/issue-resolution.yaml) | Investigate a GitHub issue, publish a plan, implement in an isolated worktree, validate, open/update a PR, independently review, check CI, optionally merge, and notify Telegram. | Manual  |

Read the [issue-resolution guide](docs/issue-resolution.md) for parameters, credentials, model
selection, recovery, and safety boundaries.

## What self-contained means

- The YAML includes its child DAG, runtime code, and agent prompts.
- No external helper scripts or local command files are required at execution time.
- Standard tools, provider authentication, repository access, and project dependencies are still
  prerequisites; secrets are never bundled.
- Workflows declare machine-specific configuration through parameters.
- Linux/POSIX is the tested execution environment. Other platforms need their own validation rather
  than an assumption of compatibility.

## Quick start

The intended deployment is your own Dagu instance. It can run this workflow against any GitHub
repository you can access; GitHub Actions is an optional alternative deployment, not a requirement.
Install Dagu 2.24.0, OpenCode V2, Python 3.12+, Bash, Git, jq, and GitHub CLI on the machine that
runs Dagu. Configure GitHub and Telegram credentials plus at least one usable inference provider.
From this checkout, start a run directly:

```bash
dagu start workflows/issue-resolution.yaml --params \
  'repository=owner/repository issue_number=123 workspace_root="/absolute/path/to/workspaces" deployment_env_file="/absolute/path/to/deployment.env"'
```

By default, `auto_merge=true`: the workflow may merge after its deterministic gates pass. Agents
investigate repository instructions, scripts/configuration and GitHub workflows. A visible native
correction loop permits re-planning, scoped repair and fresh independent review. Missing or
ambiguous validation/CI blocks publication or merging rather than guessing. Set `auto_merge=false`
to leave the PR open for manual review instead. Never run it against untrusted repositories: it
executes project code and agent-proposed edits with the host user's privileges. For a long-running
Dagu service, install or symlink the workflow file into that service's DAG directory and verify
discovery there; see the [local deployment guide](docs/issue-resolution.md#local-deployment). The
interactive CLI and service may use different Dagu configuration.

## Optional: GitHub Actions deployment

[Manual runner workflow](.github/workflows/run-issue-resolution.yml) executes the same
self-contained YAML on a pre-provisioned persistent self-hosted Linux runner and uploads run
evidence. Install tools/authentication and provision repository secrets before dispatching it;
merely forking this repository supplies no credentials. Use a **private workflow-host repository for
private targets**: plans, reviews, and source snippets in public logs/artifacts are not private
merely because tokens are masked. The runner wrapper enforces that visibility boundary.

The [validation workflow](.github/workflows/validate.yml) needs no inference credentials and makes
no model requests. It runs the same formatting, linting, and Dagu validation commands used locally;
it does not execute behavioral tests.

Acceptance testing starts on the local Dagu host, not an Actions runner. Changes to the flow require
fresh real verification of validation, publication, independent review, CI and Telegram outcomes;
prior-version evidence does not prove a new workflow. See the
[standing acceptance-test policy](/AGENTS.md#develop-and-validate).

## Developing and contributing

This is a workflow collection, not an application or test framework. Install Python 3.12+, Node.js
24+, Dagu, actionlint, and ShellCheck on the tooling host. `make install` installs pinned Python
lint dependencies and Prettier locally.

```bash
make install
make format
make validate
```

`make format-check` checks formatting without writing files. `make lint` adds strict YAML linting,
Ruff checks for the small lint adapter and declared embedded Python runtimes, plus
Actions/ShellCheck validation. `make validate` also runs native Dagu validation. The adapter only
extracts source for linting; it does not execute workflow code or introduce a testing framework.

Workflow and wrapper formatting is now included. Native Python and Bash run blocks are checked
without executing them; behavioral verification remains the executing agent's responsibility.

Behavioral verification is performed by the agent using real local workflow runs, not a checked-in
test suite. Use the approved playground target and safe merge settings described in `AGENTS.md`, and
report observed outputs and remaining limits.

See [contributing](CONTRIBUTING.md). Keep additions focused on software-engineering workflows with
explicit inputs, bounded execution, safe recovery, and reproducible evidence. An "awesome" label is
not a claim that arbitrary agent behavior is safe.

## License

[MIT](LICENSE). Dagu, OpenCode, and other prerequisites retain their own licenses; their binaries
are not redistributed in this repository.
