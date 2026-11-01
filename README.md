# Awesome Agent Workflows

Self-contained, portable [Dagu](https://github.com/dagucloud/dagu) agent workflows
for software engineering.

Start with one useful workflow, keep its behavior observable and testable, and
grow the collection with workflows worth reusing. Each workflow should be
deployable by copying a single YAML file, without a project-specific helper
repository or an installed prompt collection.

## Workflows

| Workflow | What it does | Trigger |
| --- | --- | --- |
| [Issue resolution](workflows/issue-resolution.yaml) | Investigate a GitHub issue, publish a plan, implement in an isolated worktree, validate, open/update a PR, independently review, check CI, optionally merge, and notify Telegram. | Manual |

Read the [issue-resolution guide](docs/issue-resolution.md) for parameters,
credentials, model selection, recovery, and safety boundaries.

## What self-contained means

- The YAML includes its child DAG, runtime code, and agent prompts.
- No external helper scripts or local command files are required at execution time.
- Standard tools, provider authentication, repository access, and project
  dependencies are still prerequisites; secrets are never bundled.
- Workflows declare machine-specific configuration through parameters.
- Linux/POSIX is the tested execution environment. Other platforms need their
  own validation rather than an assumption of compatibility.

## Quick start

The intended deployment is your own Dagu instance. It can run this workflow
against any GitHub repository you can access; GitHub Actions is an optional
alternative deployment, not a requirement. Install Dagu, OpenCode V2, Python
3.11+ with PyYAML (`python3 -m pip install PyYAML==6.0.3`), Git, and GitHub CLI on the machine that runs Dagu. Configure GitHub and
Telegram credentials plus at least one usable inference provider. From this
checkout, start a run directly:

```bash
dagu start workflows/issue-resolution.yaml --params \
  'repository=owner/repository issue_number=123 workspace_root="/absolute/path/to/workspaces" deployment_env_file="/absolute/path/to/deployment.env"'
```

By default, `auto_merge=true`: the workflow may merge after its deterministic gates pass.
Agents investigate repository instructions, scripts/configuration and GitHub workflows;
one verified discovery plan drives validation, repair and independent review. Missing
or ambiguous validation/CI blocks publication or merging rather than guessing.
Set `auto_merge=false` to leave the PR open for manual review instead. Never run it
against untrusted repositories: it executes project code and agent-proposed edits
with the host user's privileges.
For a long-running Dagu service, install or symlink the workflow file into that
service's DAG directory and verify discovery there; see the [local deployment
guide](docs/issue-resolution.md#local-deployment). The interactive CLI and service
may use different Dagu configuration.

## Optional: GitHub Actions deployment

[Manual runner workflow](.github/workflows/run-issue-resolution.yml) installs
pinned Dagu/OpenCode versions, executes the same self-contained YAML on a fresh
Ubuntu runner, and uploads evidence/recovery artifacts. Provision repository
secrets before dispatching it; merely forking this repository supplies no credentials.
Use a **private workflow-host repository for private targets**: plans, reviews,
and source snippets in public logs/artifacts are not private merely because tokens
are masked. The runner wrapper enforces that visibility boundary.

The [validation workflow](.github/workflows/validate.yml) needs no inference
credentials and makes no model requests. It checks deployable YAML and tests
the runtime extracted from the published artifact itself.

Acceptance testing starts on the local Dagu host, not an Actions runner. The
flow has been exercised with real discovered validation, a published PR, independent
review, expected CI, confirmed Telegram delivery, and an explicitly authorized
merge with verified issue closure. See the
[standing acceptance-test policy](/AGENTS.md#develop-and-validate).

## Developing and contributing

```bash
make install
make test
make lint
make validate
```

See [contributing](CONTRIBUTING.md). Keep additions focused on software-engineering
workflows with explicit inputs, bounded execution, safe recovery, and reproducible
evidence. An "awesome" label is not a claim that arbitrary agent behavior is safe.

## License

[MIT](LICENSE). Dagu, OpenCode, and other prerequisites retain their own licenses;
their binaries are not redistributed in this repository.
