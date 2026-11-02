# Issue resolution

The [canonical YAML](/workflows/issue-resolution.yaml) is self-contained. Local Dagu is primary; the
[Actions wrapper](/.github/workflows/run-issue-resolution.yml) uses a pre-provisioned, persistent
self-hosted Linux runner.

## Flow

```text
pin repository/issue/branch/PR + acquire repository lease
  -> resolve economy/balanced once from real auth, catalog and readiness
  -> native checkout/fetch + isolated issue worktree
  -> native repeated child cycle:
       reconcile live Git/GitHub/evidence before choosing unfinished work
       -> balanced plan when useful -> economy work/validate/commit/push/PR
       -> independent pinned-source economy review
       -> same readiness policy against fresh observations -> optional guarded merge
       -> wait without agents / correct / reconcile evidence / truthful handoff
  -> verify merge and issue closure -> preserve unknown files during cleanup
  -> truthful Telegram outcome -> release owned lease
```

`reconcile_loop` uses installed Dagu 2.25.1's native `repeat_policy: until` on `dag.run`. Its
condition is checked after each child, with 30 seconds between cycles, at most 120 child cycles, and
a two-hour overall timeout. Waiting is not a repair attempt: queued/running CI or unknown
mergeability invokes neither worker nor reviewer. Six inference-bearing cycles bound correction and
evidence repair; exhaustion produces a human handoff. Observations have two native retries at
five-second intervals and five-minute deadlines. Persistent observation/provider/process errors stop
the run and are reported as infrastructure errors, not invented engineering findings.

Agents discover repository conventions, commands and applicable CI. There is no command catalog,
Actions/path/matrix interpreter, frozen plan, narrative JSON schema, custom launcher or materialized
prompt collection. There is no agent-maintained phase/status file. Dagu owns context, identities,
budgets and observations; agents own engineering judgment and Markdown evidence. One worker resumes
unfinished implementation, validation or publication rather than handing work to a publication-only
agent. It can adapt the plan without a replan token. Existing published revisions go directly to
independent review unless local tracked changes or unpublished commits need reconciliation.
Preparation exposes its existing context artifact through native file-output capture, rather than
printing a second control record for downstream steps to parse.

The review report ends with a small fenced JSON decision (revision, verdict/reason and expected CI),
not a narrative schema. Dagu extracts this locally; a missing derived control file is regenerated
without an agent. Malformed decisions return to the same reviewer using prior evidence, not to
implementation. A misplaced untracked `review.md` is moved from review scratch to the reports
directory. Other unknown/generated files are preserved. Tracked mutation or changed review HEAD
fails review integrity; scratch cleanliness alone does not. Tracked `review.md` documents and
symlinks are not reclassified as misplaced reports. PR bodies use Markdown `--body-file` publication
rather than shell-escaped newline strings; a missing closing link returns to publication
reconciliation without authorizing a merge.

### Responsibilities and line budget

| Responsibility              | Before                                           | Now                                                       |
| --------------------------- | ------------------------------------------------ | --------------------------------------------------------- |
| Declared root + child steps | 8 + 10                                           | 6 + 8                                                     |
| Agent roles                 | investigate, implement, publish, correct, review | balanced plan, economy worker, independent economy review |
| Agent phase protocol        | six `task.status` tokens and translations        | none; observed Git/GitHub facts and native sequencing     |
| Readiness policy            | separate observation and final-merge predicates  | one inline observer reused before work, review and merge  |

The formatted canonical YAML is **499 lines**, down from **594**: a net reduction of **95**. This
meets the hard limit, but not the aspirational 400–450 range. `make validate` rejects 500 or more
lines after the formatting check, counting child DAGs, prompts, code and comments together.

Remaining inline glue pins identities and leases, selects authenticated models, safely delivers
Telegram/relinquishes the lease, manages Git review scratch, extracts the review decision, and
compares fresh GitHub observations with repository-backed CI expectations. Native Dagu owns
sequencing, repetition and retries. Runtime complexity was not moved into scripts or external
prompts.

## Local deployment

Install Dagu 2.25.1, OpenCode V2, Python 3.12+, Bash, Git, jq and GitHub CLI. Configure
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
using real auth metadata, catalog and bounded readiness calls. Known auth/model/quota unavailability
allows the next candidate; network/timeouts/unexpected failures do not silently downgrade. Economy
and balanced stay pinned; premium is neither probed nor used. Planning uses balanced; other agents
use economy in separate native OpenCode contexts. Availability can change after readiness: a later
provider quota failure stops that run as an infrastructure error. A new run can choose the next
usable candidate through the same ordered readiness checks; there is no in-run model downgrade or
provider-configuration rewrite.

Run artifacts include model-selection attempts, `context.json`, Markdown plans/work/review, locally
derived `review.json`, GitHub snapshots and `telegram.json`. Each child has its own native agent
transcript artifacts. Plans are published to the issue; independent review is published to the
pinned PR and reruns actual validation in a detached worktree.

Agents record numeric `workflowDatabaseId` values/check names using relevant configuration and
GitHub APIs, letting GitHub expand matrices/reusable jobs. Empty/missing CI is not passing;
genuinely absent CI requires explicit evidence. Changed head/base requires fresh review. Real CI
failures/conflicts/findings return to the same worker. Persistently missing expectations return to
evidence reconciliation after nine observations; contradictory CI-absence claims return immediately
to review. No caller-supplied validation command or required-check list can override discovery.

`handoff` is a successful automation outcome, not a claim that the issue is resolved. It covers
manual merging (`auto_merge=false`), approval/draft/rule obstacles and justified human intervention.
The reviewer may confirm `no_change` with validation evidence and no PR. A closed issue is reported
as external completion; this does not assert that this run implemented or merged it. No-change and
handoff do not automatically close an issue or delete its worktree.

Persistent worktrees retain committed and uncommitted source on failure. There is no automatic
reset/stash/force-push or source-export framework. Stale leases fail closed: inspect `owner.json`
and confirm its run is inactive before recovery. Resume the same issue/linked PR without discarding
work. Only verified merge/issue closure permits cleanup, and generated/unknown files retain the
worktree rather than being force-removed. Review scratch with generated files is retained in native
artifacts for inspection. The optional wrapper therefore requires persistent self-hosted storage,
not ephemeral hosted runners. Private targets require a private workflow-host repository; masking is
not privacy.

A newly started run reconciles a single linked PR, local changes/commits and discussion before
choosing work or review. A push without a PR, or an unfinished dirty worktree, goes to the same
worker. The reviewer recovers prior evidence from discussion when needed. A final stale head/base
returns to the bounded loop: revision changes invalidate review and CI evidence rather than
immediately abandoning the issue. Preserve failed run artifacts; do not remove an active lease.

## Original prompt mapping

- `ghar-issue-investigate.md`: evidence/history, 5 Whys, scoped actionable planning, issue
  publication.
- `prp-issue-fix.md`: plan accuracy, conventions, implementation, real validation and deviations.
- `commit-push.md`: safe cohesive staging, useful commit context, normal push and linked PR.
- `resolve-ci-errors.md`: diagnose, plan, fix, validate/push in the existing worker; no task ledger
  or mandatory TODO tool. Dagu owns repetition.
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

### Local acceptance (2026-11-02)

Disposable [issue #239](https://github.com/tbrandenburg/playground/issues/239) and
[PR #240](https://github.com/tbrandenburg/playground/pull/240) exercised implementation/publication,
interruption immediately after PR creation, resume, independent review and a successful
`auto_merge=false` handoff. A real GitHub CI rerun produced **nine agent-free waiting cycles**.
Malformed PR-body newlines were repaired without another implementation commit.

A deliberate implementation regression then failed **2/29 tests**, locally and in real GitHub
[run 41406119152](https://github.com/tbrandenburg/playground/actions/runs/41406119152). The worker
diagnosed actual failed logs, restored the implementation and passed **29 tests** without changing
the test blob. Fresh independent review and corrected-head
[CI run 41406381061](https://github.com/tbrandenburg/playground/actions/runs/41406381061) passed;
Dagu merged the PR, verified issue closure and confirmed Telegram delivery. The temporary CI delay
was absent from the final workflow diff. Generated files retained the issue worktree safely.

Fresh [issue #241](https://github.com/tbrandenburg/playground/issues/241) and
[PR #242](https://github.com/tbrandenburg/playground/pull/242) proceeded through balanced planning,
implementation/publication, **33 passing tests** and real
[CI run 41407962024](https://github.com/tbrandenburg/playground/actions/runs/41407962024). The gate
rejected a workflow-name/ID discrepancy despite green checks. Provider quotas interrupted evidence
repair; the next run selected configured candidates in their existing order and resumed independent
review without invoking a worker. Numeric workflow evidence and fresh independent validation then
passed; Dagu merged PR #242, verified issue #241 closed and confirmed Telegram delivery (receipt
`8822`). The resumed merge used GitHub Copilot economy/balanced models after explicit OpenAI quota
failures, without changing provider configuration or reimplementing code.

[Issue #243](https://github.com/tbrandenburg/playground/issues/243) then exercised the final YAML's
native context-file capture and complete no-change path. Planning, the worker and separate review
confirmed **33 tests**, an unchanged head/base, no repository edits or commits and no PR. The run
succeeded with `no_change` and Telegram receipt `8823`, leaving the issue open as designed. The
operator subsequently closed this disposable verification issue and removed its clean worktree.

Disposable probes used the canonical observer/integrity blocks with real GitHub/Git data. They
accepted current evidence and rejected stale head/base, malformed reports, missing expected checks
and contradictory CI absence; missing derived control files were regenerated locally. Both
inference-budget boundaries handed off. Misplaced review reports were recovered, unknown scratch
output was preserved, and tracked source mutation was rejected. Native observer failures retried
three times, recorded infrastructure errors and satisfied the parent's stop condition with zero
agents. A process-local unreachable proxy exercised real GitHub CLI connection failure without
changing shared networking or services. Private probes/evidence remain outside this checkout.
Additional probes verified that tracked `review.md` files and report symlinks are preserved, native
context-file outputs decode correctly, and the actual Makefile budget accepts 499 but rejects 500
lines.

Failures found during development included unsupported prior-output working directories, literal
PR-body newline escapes, failed-child repetition, provider quotas and workflow-name/ID mismatch.
Parameter-only working directories, publication reconciliation, a native child failure handler,
explicit quota recognition and numeric-ID instructions address these findings.

Owned issue worktrees #239 and #243 were removed only after verifying inactive leases, pinned
branches/heads, ownership and contents; two known generated Python cache files were removed from
#239 first. The canonical merge path removed #241's clean worktree. Failed-run transcripts and
review scratch remain available as private recovery evidence; pre-existing worktrees were not
cleaned or reset.

Unexercised paths include a genuinely CI-free merge, actual required-human approval, an empty
open-issue queue, a real last-millisecond remote-base change and an Actions dispatch. Stale base
evidence was rejected by disposable probes, not by moving a shared base branch. Conservative
ambiguity/access failures and stale leases still require operator inspection; unknown review scratch
is retained rather than classified or force-deleted.
