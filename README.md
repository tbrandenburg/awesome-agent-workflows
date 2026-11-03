# Awesome Agent Workflows

Run a workflow from the repository root with locally installed Dagu, OpenCode,
and authenticated GitHub CLI:

```sh
make validate
make run WORKFLOW=workflows/latest-issue-resolution.yml
```

The latest issue resolution workflow handles the newest open issue in the target
checkout (this repository by default). It creates a sibling worktree named
`<checkout>-issue-<number>` on branch `issue/<number>`, then removes the worktree
and branch after verifying the PR was merged. The checkout's parent directory
must be writable. To target another checkout:

```sh
make run WORKFLOW=workflows/latest-issue-resolution.yml DAGU_FLAGS='--params project_dir=/path/to/checkout'
```

To work on a GitHub repository instead, pass `repo`. The workflow first clones it
with `gh` (private repos work with your login) into the per-run Dagu work
directory and runs there:

```sh
make run WORKFLOW=workflows/latest-issue-resolution.yml DAGU_FLAGS='--params repo=owner/name'
```

Agent steps use OpenCode with the model configured in the workflow and normal
permission checks. Authenticate that provider locally before running.
