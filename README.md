# Awesome Agent Workflows

Run a workflow from the repository root with locally installed Dagu, OpenCode,
and authenticated GitHub CLI:

```sh
make validate
make run WORKFLOW=workflows/latest-issue-resolution.yml
make run WORKFLOW=workflows/issue-resolution.yml DAGU_FLAGS='--params issue_id=42'
```

`issue-resolution` resolves one given open issue. `latest-issue-resolution` is a
thin wrapper that picks the newest open issue and runs `issue-resolution` on it;
both run manually, without a schedule, in the target
checkout (this repository by default). The wrapper finds `issue-resolution.yml`
next to itself, so start it by file path (Dagu does not follow symlinks for sub-DAGs).
`issue-resolution` creates a sibling worktree named
`<checkout>-issue-<number>` on branch `issue/<number>`. Before fixing, a planning
step investigates the issue and publishes an `Implementation plan` issue comment
with background and goals, scope and constraints, a KISS approach, detailed tasks
for a junior fixer, risks, acceptance criteria, a Definition of Done, automated
validation commands, and a final manual E2E acceptance checklist. The fixing step
checks the plan against the code, runs automated checks followed by real-system
manual E2E acceptance without mocks, and records evidence, checklist results,
and deviations. Unmet criteria or missing test prerequisites block completion.
Plan, implementation, and CI issue comments carry hidden
`<!-- issue-resolution:plan -->`, `<!-- issue-resolution:implementation -->`, and
`<!-- issue-resolution:ci -->` markers; PR review comments use
`<!-- issue-resolution:review -->`. Downstream agents read raw comment bodies to
find these handoffs and check them against the current code and PR head.
The workflow removes the worktree and branch after
verifying the PR was merged. The checkout's parent directory
must be writable. Run it from the checkout you want to target.

To work on a GitHub repository instead, pass `repo`. The workflow first clones it
with `gh` (private repos work with your login) into the per-run Dagu work
directory and runs there (both workflows accept `repo`):

```sh
make run WORKFLOW=workflows/latest-issue-resolution.yml DAGU_FLAGS='--params repo=owner/name'
```

`multi-repo-prompt` runs any prompt in a fresh worktree of each listed repo, up to
two at a time. `repos` holds one `owner/name` per line; each repo is handled by
`repo-prompt`, which clones it into `~/.cache/repo-task/<owner>/<name>` if missing,
fetches, adds a worktree on `branch` off the default branch, runs the prompt with
OpenCode, and removes the worktree and local branch afterwards (success or
failure). Dagu runs no handlers on cancel, so a cancelled run leaves its worktree
until the next run on that repo and branch removes it first. Publish anything worth keeping (commit, push, PR) in the prompt.
The prompt is a plain Dagu param; `multi-repo-prompt` escapes quotes and backslashes
before handing it to `repo-prompt` (Dagu does not), so any prompt text survives intact. Start it by file path so the sibling
`repo-prompt.yml` is found (Dagu does not follow symlinks for sub-DAGs):

```sh
dagu start workflows/multi-repo-prompt.yml --params 'repos="owner/a
owner/b" prompt="Update all dependencies to latest and open a PR." branch=chore/update-deps'
```

Agent steps use OpenCode with the model configured in the workflow and normal
permission checks. Planning uses `github-copilot/gpt-6.1-sol`; implementation,
PR publication, CI repair, review, and merging use `openai/gpt-6-luna`.
Authenticate both model providers locally before running.
Prompts state their purpose, inputs, instructions, and output
after a brief worktree context. Markdown publication uses temporary UTF-8 files
with `gh --body-file`, not inline shell arguments. Agent timeouts are 1 hour for
planning and review, 4 hours for implementation, 2 hours for CI repair, and
15 minutes for PR publication and merging. Failed runs retain unfinished
worktrees for recovery. The enclosing runner must allow the required runtime;
the six agent-step limits total 8.5 hours before other steps or retries.
