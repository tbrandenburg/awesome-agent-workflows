# Issue resolution

The [canonical YAML](/workflows/issue-resolution.yaml) is self-contained. Local Dagu is primary; the
[Actions wrapper](/.github/workflows/run-issue-resolution.yml) uses a pre-provisioned, persistent
self-hosted Linux runner.

## Flow

```text
pin repository/issue/branch/PR + acquire repository lease
  -> native checkout/fetch + isolated issue worktree
  -> resolve economy/balanced once from real auth, catalog and readiness
  -> native repeated child cycle:
       investigate/plan -> implement/validate -> commit/push/PR
       OR correct actual failures -> commit/push
       -> fresh separate-worktree independent review
       -> observe GitHub: wait / fix / replan / review / ready / blocked
  -> current-head/base/CI recheck -> optional merge -> verify issue closure
  -> cleanup only after merge -> truthful Telegram outcome -> release lease
```

`correction_loop` uses installed Dagu 2.24.0's native `repeat_policy: until` on `dag.run`. Its
condition is checked after each child, with 30 seconds between cycles, at most 120 observations, and
a two-hour overall timeout. Waiting is not a repair attempt; queued/running CI or unknown
mergeability does not invoke a fixer. Exhaustion or unresolved access/approval obstacles fail
honestly and preserve work. A child failure marks the run blocked and stops repetition; observers
have 90-second step deadlines, rather than retrying broken observation for an hour.

Agents discover repository conventions, commands and applicable CI. There is no command catalog,
Actions/path/matrix interpreter, frozen plan, narrative JSON schema, custom launcher or materialized
prompt collection. Plans/reports are readable Markdown; small control outputs select the next
visible Dagu phase. Invalid assumptions allow balanced re-investigation; report-formatting problems
must not restart implementation. `task.status` contains one routing token; explanations belong in
Markdown. The observer reads its first line and blocks unknown tokens. Missing/unparseable review
control returns to independent review, not implementation.

## Local deployment

Install Dagu 2.24.0, OpenCode V2, Python 3.12+, Bash, Git, jq and GitHub CLI. Configure
GitHub/Telegram credentials and at least one usable OpenCode provider for the execution account.
Keep credentials outside the repository, preferably in a mode-0600 deployment dotenv file. Never
export stored OAuth credentials into the workflow.

Native Dagu secrets redact `GH_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` and the three
inference API keys. Unused `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` and `OPENROUTER_API_KEY` names must
exist with empty values; stored OpenCode authentication remains eligible. The Actions wrapper
defines these names through job secrets.

```bash
dagu start workflows/issue-resolution.yaml --params \
  'repository=owner/repository issue_number=123 auto_merge=false workspace_root="/absolute/path/to/workspaces" deployment_env_file="/absolute/path/to/deployment.env"'
```

`repository` is required; `issue_number=0` selects an open issue once. `base_branch` defaults to the
repository default. `auto_merge=true` is the default, but checks, independent review, approvals and
rules are never bypassed. Use `false` for manual review and unapproved acceptance-test merging.

Deployment defaults are `/var/lib/dagu/workspaces` and `/var/lib/dagu/issue-resolver.env`. Override
these for another host. Optional `git_author_name`/`git_author_email` configure the workflow
checkout's commit identity. No repository-specific validation/check inputs exist.

### Credentials

Provide `GH_TOKEN`, `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to the execution account through the
deployment dotenv file or environment. Native CLI agents receive declared inference-key secrets;
stored OpenCode authentication is read by OpenCode itself, not exported by the workflow. Git uses a
process-local `gh auth git-credential` helper with terminal prompting disabled; no global Git
configuration or credential file is rewritten.

## Models, evidence and recovery

Economy/balanced/premium definitions remain centralized in `consts`. Selection preserves their order
using real auth metadata, catalog and bounded readiness calls. Auth/model unavailability allows the
next candidate; network/timeouts/unexpected failures do not silently downgrade. Economy and balanced
stay pinned; premium is neither probed nor used. Planning uses balanced; other agents use economy in
separate native OpenCode contexts.

Run artifacts include model-selection evidence, `context.json`, `task.status`, Markdown
plans/reports, `review.json`, readiness/GitHub snapshots and `telegram.json`. Each child has its own
native agent transcript artifacts. Plans are published to the issue; independent review is published
to the pinned PR and reruns actual validation in a detached worktree.

Agents record expected workflow database IDs/check names using relevant configuration and GitHub
APIs, letting GitHub expand matrices/reusable jobs. Empty/missing CI is not passing; genuinely
absent CI requires explicit evidence. Changed head/base requires fresh review. Real CI
failures/conflicts/findings invoke TODO-tool correction, not a ledger. OpenCode versions without the
experimental TODO tool record the single task in the existing correction report instead; that
optional tool's absence is not a repair blocker.

Persistent worktrees retain committed and uncommitted source on failure. There is no automatic
reset/stash/force-push or source-export framework. Stale leases fail closed: inspect `owner.json`
and confirm its run is inactive before recovery. Resume the same issue/linked PR without discarding
work. Only verified merge/issue closure permits cleanup. The optional wrapper therefore requires
persistent self-hosted storage, not ephemeral hosted runners. Private targets require a private
workflow-host repository; masking is not privacy.

A newly started run resumes a single linked open PR at independent review, not by repeating
implementation. The reviewer recovers prior context from issue/PR discussion and checks the current
head/base. Preserve failed run artifacts for diagnosis; do not remove a lease while its owner is
active.

## Original prompt mapping

- `ghar-issue-investigate.md`: evidence/history, 5 Whys, scoped actionable planning, issue
  publication.
- `prp-issue-fix.md`: plan accuracy, conventions, implementation, real validation and deviations.
- `commit-push.md`: safe cohesive staging, useful commit context, normal push and linked PR.
- `resolve-ci-errors.md`: diagnose, plan, fix, validate/push; TODO replaces the ledger and Dagu owns
  repetition.
- `prp-review.md`: independent full-context review, actual checks, severity and actionable feedback.

The actual Sofathek `.made/workflows.yml` and issue-opened investigation trigger supply the
sequence. Latest-issue selection and shared-checkout cleanup were replaced with pinned
identity/worktrees. Unsafe rewriting, duplicate phases and oversized templates were removed;
substantive responsibilities remain directly in YAML. Sofathek files are not runtime dependencies.

## Local discovery and verification

The existing local symlink is `/var/lib/dagu/dags/issue-resolution.yaml`. External links require
`dag_discovery.symlinks: true` in the actual service config. Verify discovery with
`DAGU_HOME=/var/lib/dagu dagu ls issue-resolution`; direct CLI execution needs no scheduler. See
[AGENTS.md](/AGENTS.md#develop-and-validate) for the approved playground test policy.

Lint/schema checks do not execute workflows. Each behavior change needs fresh real local acceptance
evidence; old-version runs and unexecuted recovery paths must not be claimed.

### Latest local acceptance (2026-11-02)

Investigation, implementation, validation and PR publication executed in an earlier run of this
rewrite. The final canonical run resumed that PR after an intentionally injected regression and
succeeded: one correction using actual failed CI logs, two independent reviews, five wait-only
cycles with zero agent invocations, current-head CI and final gates passing, and confirmed Telegram
delivery. The issue worktree remained clean, the lease was released, and the PR/issue stayed open
with `auto_merge=false`. The target's 26 subprocess tests passed after repair.

Direct probes of the canonical final gate against real GitHub state accepted valid evidence and
rejected seven stale/missing/failed-evidence cases. Native child-failure stopping, active-lease
contention, closed-issue rejection, credential-helper portability and the wrapper's visibility guard
were also checked. Private transcripts and disposable probes remain outside the checkout.

Automatic merging/issue closure, a genuinely CI-free target, an empty open-issue queue, API-key-only
inference authentication and an actual Actions dispatch were not exercised. Installed OpenCode
`v2.0.28` lacks TODO support; its Markdown-report fallback was exercised instead.
