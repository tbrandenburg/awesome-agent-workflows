# Awesome Agent Workflows

Run a workflow from the repository root with locally installed Dagu, OpenCode,
and authenticated GitHub CLI:

```sh
make validate
make run WORKFLOW=workflows/latest-issue-resolution.yml
```

The latest issue resolution workflow handles the newest open issue in the target
checkout (this repository by default). It creates a sibling worktree named
`<checkout>-issue-<number>` on branch `issue/<number>`. Before fixing, a planning
step investigates the issue and publishes an `Implementation plan` issue comment
with implementation tasks, validation commands, and acceptance criteria. The
fixing step reads that comment, checks it against the code, and documents any
necessary deviations. Plan, implementation, and CI issue comments carry hidden
`<!-- issue-resolution:plan -->`, `<!-- issue-resolution:implementation -->`, and
`<!-- issue-resolution:ci -->` markers; PR review comments use
`<!-- issue-resolution:review -->`. Downstream agents read raw comment bodies to
find these handoffs and check them against the current code and PR head.
The workflow removes the worktree and branch after
verifying the PR was merged. The checkout's parent directory
must be writable. Run it from the checkout you want to target.

To work on a GitHub repository instead, pass `repo`. The workflow first clones it
with `gh` (private repos work with your login) into the per-run Dagu work
directory and runs there:

```sh
make run WORKFLOW=workflows/latest-issue-resolution.yml DAGU_FLAGS='--params repo=owner/name'
```

Agent steps use OpenCode with the model configured in the workflow and normal
permission checks. Authenticate that provider locally before running.
