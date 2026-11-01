# Issue resolution

[Workflow](../workflows/issue-resolution.yaml) ·
[GitHub runner](../.github/workflows/run-issue-resolution.yml)

## Process

```text
basic preflight + repository ownership lease
  -> inspect OpenCode auth/catalog -> readiness probes -> pin model tiers
  -> clone/fetch target repository -> select one exact issue/PR
  -> create/reuse persistent issue worktree
  -> investigate -> validate and publish implementation plan
  -> implement -> actual project checks -> rich commit/PR metadata
  -> commit/push -> create/update linked PR
  -> separate review worktree -> independent review and validation
  -> wait for required GitHub CI -> optional bounded repair attempt
  -> recheck PR head/base and CI -> optional merge -> verify issue closure
  -> clean merged worktree -> Telegram outcome -> release lease
```

The workflow has no schedule. Default `auto_merge=true` permits merging only after validation,
independent review, expected CI, and current head/base checks pass. Explicitly set it to `false` to
leave the validated, reviewed PR open for manual review.

## Prerequisites

- Dagu 2.24.0 and OpenCode 2.0.28 are the versions exercised by the runner example.
- Python 3.11+ with PyYAML 6.0.3, Bash, Git, and GitHub CLI are available to the execution user.
- Project dependencies and project validation commands are available. The workflow does not guess
  dependency-install commands.
- Target-repository GitHub access and Telegram bot/chat credentials are configured.
- At least one candidate inference route must pass its actual readiness request.

## Parameters

| Parameter             | Default / contract                                                                                                                     |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `repository`          | Required GitHub `owner/name`; public and accessible private repositories are supported.                                                |
| `issue_number`        | `0`: select an open issue, preferring a resolver PR already in progress. Set a number to pin it explicitly.                            |
| `base_branch`         | Empty: detect the target repository's default branch.                                                                                  |
| `auto_merge`          | `true`; merging requires validation/review/CI and remote-state checks. Set to `false` for manual review.                               |
| `workspace_root`      | `/var/lib/dagu/workspaces`; override with an absolute writable directory on your host.                                                 |
| `workspace_mode`      | `persistent` or `ephemeral`; runner example uses ephemeral.                                                                            |
| `deployment_env_file` | `/var/lib/dagu/issue-resolver.env`; override with your protected dotenv file, or an empty file when injecting environment credentials. |
| `git_author_name`     | `Dagu Issue Resolver`.                                                                                                                 |
| `git_author_email`    | `dagu-resolver@users.noreply.github.com`; set your desired commit identity.                                                            |

An issue is selected once. Later agents cannot switch to a newly opened "latest" issue or publish
duplicate PRs by rediscovering work independently.

## Credentials

Required variables:

```text
GH_TOKEN
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Optional inference credentials:

```text
OPENAI_API_KEY
ANTHROPIC_API_KEY
OPENROUTER_API_KEY
```

OpenCode's existing stored authentication can also make a provider eligible. The workflow uses
`opencode auth list --standalone --format json`, not `auth export`. It does not copy OAuth sessions
to another machine. A GitHub repository token is not a Copilot inference credential.

If credentials come from the parent process environment rather than the DAG dotenv scope, configure
Dagu to forward only the optional inference names:

```yaml
env_passthrough:
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
  - OPENROUTER_API_KEY
```

The runner example writes this nonsecret deployment configuration. Keep dotenv files mode 0600 and
outside the repository. Native GitHub/Telegram secret providers and the embedded launcher protect
known credential values from logs; never instruct a model to inspect credentials or dump its
environment.

## Model tiers

Candidates are defined once in the workflow's `consts` and tried in order:

| Tier     | Ordered routes                                                                                                                               |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| economy  | OpenAI GPT-6 Luna → Copilot GPT-6 Luna → Anthropic Haiku 5.5 → Copilot Haiku 5.5 → OpenRouter GPT-6 Luna → Big Pickle                        |
| balanced | OpenAI GPT-6.1 Sol → Copilot GPT-6.1 Sol → Anthropic Sonnet 5.5 → Copilot Sonnet 5.5 → OpenRouter GPT-6.1 Sol → Big Pickle                   |
| premium  | OpenAI GPT-6 Astra → Copilot GPT-6 Astra → Anthropic Opus 5.5 → Copilot Opus 5.5 → OpenRouter GPT-6 Astra → OpenRouter Opus 5.5 → Big Pickle |

Issue resolution selects only economy and balanced. Planning uses balanced; implementation,
publication metadata, and review use economy. Premium is defined but not probed or used. Big Pickle
is marked degraded, not capability-equivalent.

Auth metadata and a catalog entry are necessary but not sufficient: a bounded, no-tools readiness
request must succeed. Auth/model-unavailable errors allow the next candidate; network errors,
timeouts, metadata failures, and unexpected responses are surfaced. Once selected, models stay
pinned through repair.

Selected IDs and safe eligibility evidence appear in `model-selection.json` and the Telegram
outcome. Readiness probes are billable when the provider bills them, and still execute before the
no-work path. Reasoning effort is not silently changed; tier names are a policy, not a guarantee of
benchmark performance.

## Local deployment

Run the file directly with explicit parameters, or install a file symlink into the running Dagu
service's actual DAG directory. Do not assume the interactive CLI uses the same `DAGU_HOME`,
`DAGU_DAGS_DIR`, or `--dags` setting as that service.

External-target file links require this service configuration:

```yaml
dag_discovery:
  symlinks: true
```

Verify discovery through that service/context. Dagu does not traverse symlinked directories. Direct
file execution needs neither a symlink nor a scheduler.

## GitHub Actions

Provision these secrets in the repository hosting the manual runner:

- `RESOLVER_GH_TOKEN`: GitHub App token or suitable scoped PAT for the target's content/issue/PR
  operations and downstream CI triggering.
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- Any available inference API keys from the optional list above.

Then dispatch `run-issue-resolution.yml`. It installs pinned tools, checks the Dagu release
checksum, runs the same YAML on Ubuntu 24.04, and uploads run evidence/recovery artifacts even after
a task failure. It has read-only wrapper permissions, does not persist checkout credentials, and
serializes target-repository runs without canceling an earlier one.

**Private targets must use a private repository to host this Actions wrapper.** Public Actions logs
and uploaded artifacts can contain issue text, source snippets, plans, and review data even when
credentials are redacted. The supplied wrapper checks visibility and rejects private targets from a
public workflow host before inference. Copy it into a private host repository, or run the YAML
locally, for private projects. Do not treat secret masking as protection for private task data.

Fresh hosted runners do not inherit your local OAuth state. The built-in `GITHUB_TOKEN` is not
assumed to support arbitrary cross-repository targets or trigger their CI. Keep secrets scoped to
the repositories you intentionally allow.

## Validation and recovery

The caller supplies a repository and optionally an issue number, not project checks. During
mandatory investigation the planner inspects repository instructions (including nested rules),
Makefiles, package scripts, project configuration and GitHub workflows. `discovery.json` records
sources, repository-backed argv and effective branch policy. The write-once `plan.json` includes
that discovery and classifies type-check, lint/format, tests and build; composite validation targets
are included. Every catalog entry must be included. An absent category needs an evidence-based N/A
reason; tests cannot be absent. Unsupported checks or conflicting instructions are explicit
blockers. Commands execute as validated argv, never unrestricted generated shell strings.
Documented/workflow `python3 -m unittest discover` entrypoints are supported when their fixed
discovery flags point to existing repository test files. Unknown flags, shell expressions, traversal
and missing test files are rejected rather than inferred. Nested commands use a fixed
`env -C <relative-directory>` cwd wrapper (GNU env required). Dependencies must be available in both
implementation and independent review worktrees.

CI expectations combine accessible branch protection/effective rulesets and applicable GitHub
workflows. Static matrices (including include/exclude) and local reusable jobs are expanded;
branch/path filters are evaluated against the planned paths and then the actual PR diff.
Policy-required checks stay required even if a workflow is filtered out. Empty expectations or
missing/pending registration cannot pass. Expected jobs must succeed; app-bound identities are
verified through check runs at the reviewed SHA. `ci-evidence.json` records expectations, rollup and
check-run evidence. Changed base commits, CI configuration, policy or plan invalidate evidence and
require a new run.

Discovery fails closed for unavailable or ambiguous policy APIs. A narrowly verified exception
records proven feature absence: an unprotected private personal repository with verified
administrator access, where both effective-rules and protection APIs explicitly report that the
feature requires GitHub Pro. This is not a permission-error fallback; workflow-derived expected CI
must still be nonempty, register and succeed. Discovery also blocks dynamic matrices/names, remote
or cyclic reusable workflows, conditional/allowed-failure jobs, advanced glob patterns, PR activity
filters that cannot guarantee publication/repair CI, organization-required workflows, and diffs over
GitHub's 300-file path-filter limit. These are limitations, not requests for repository-specific
replacement inputs or permission to skip CI. `telegram-delivery.json` records the API-confirmed
outcome without chat/token values.

Repairs use the agent TODO tool, not task-ledger files. A maximum of two full attempts prevents an
unbounded inference loop. CI waiting is bounded. Follow-up issues for unresolved high/critical
blockers are deduplicated and never substitute for passing merge gates.

Persistent layout below `workspace_root`:

```text
repos/<owner>/<repo>/
worktrees/<owner>/<repo>/issue-<number>/
reviews/<owner>/<repo>/issue-<number>-<child-run>/
leases/<owner>/<repo>/owner.json
```

Failed issue worktrees are preserved. Normal exit releases the owned lease; a crash-stale lease
fails closed. Inspect its recorded run and confirm that run is inactive before manual recovery.
Never remove another active run's lease.

On an ephemeral runner, published work resumes from its remote branch/PR. Uncommitted eligible
source is captured as a patch/archive for manual recovery; the workflow does not push unvalidated
commits just to preserve them. Recovery rejects symlink traversal and withholds artifacts when known
credential content or common token/key patterns are detected. Detection and artifact upload are not
exhaustive guarantees after severe process or machine loss.

## Safety and evidence scope

This executes trusted project code and agent edits with host privileges and automatic tool
permission approval. A worktree is not a security sandbox. Use isolated workers for untrusted
repositories. Fork PRs, ambiguous linked PRs, conflicting worktree ownership, changed PR
heads/bases, failing CI, and blocking reviews fail closed. Custom workspace OpenCode configuration
is not overwritten.

Collection checks format/lint surrounding files, lint the workflow YAML and declared embedded
Python, and perform native Dagu validation. They do not execute workflows or replace
agent-orchestrated behavioral verification. Local acceptance on the approved private test repository
exercised this canonical workflow with discovered unittest validation, a published investigation
plan, implementation and publication, a separate independent review worktree, expected app-bound
GitHub CI at the current head/base, and API-confirmed Telegram delivery. No project validation or
check-name inputs were supplied.

Initial acceptance kept automatic merging disabled. After explicit operator authorization, the
canonical runtime re-ran validation and the current head/base/CI gates, merged the same
independently reviewed PR, verified issue closure, removed the issue worktree, and confirmed the
merged Telegram outcome. The default is now `auto_merge=true`; unapproved acceptance tests must
still explicitly set it to `false`.

The independent review explicitly reported a transient GitHub API failure rather than claiming CI
passed; the subsequent deterministic CI gate independently obtained and verified successful
check-run evidence. Dynamic/unsupported discovery cases remain fail-closed, and a future behavior
change needs a fresh local acceptance run. GitHub Actions is an optional deployment target, not the
primary acceptance host.
