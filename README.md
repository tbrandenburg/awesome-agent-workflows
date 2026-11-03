# Awesome Agent Workflows

Run a workflow from the repository root
with locally installed Dagu, OpenCode, and authenticated GitHub CLI:

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

Agent steps use OpenCode with `github-copilot/gpt-6.1-sol` and automatic permission
approval for unattended execution. Authenticate that provider locally before running.
Each step uses a private OpenCode process rather than an existing background service.
