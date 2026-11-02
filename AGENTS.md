# awesome-agent-workflows agent guidelines

## Introduction

This is a repository collecting valuable [DAGU](https://docs.dagu.sh) based agentic workflows.

## Guidelines

- Keep the structure of `README.md` - only add or update information in `README.md` if it fits into its structure
- Keep workflows self-contained, simple, portable and human readable - good example:
  ```yaml
    ...
    - id: merge_and_notify
      depends: [review_pr]
      action: harness.run
      with:
        prompt: |
          Work only in ${params.worktree_path} on ${params.branch}.
          Merge remotely; do not switch branches, use --delete-branch, or remove the worktree.
          Check GitHub issue #${params.issue_id} and its linked PR #${env.PR_ID} and its PR comments. Raise non-duplicate GitHub
          issues for unresolved high-priority review findings, failing CI, or merge blockers.
          Merge when required checks pass and no blocking findings remain.
  
    - id: worktree_head
      depends: [merge_and_notify]
      action: exec
      with:
        command: git
        args: [rev-parse, HEAD]
      output: WORKTREE_HEAD
    ...
  ```
- Always check DAGU latest best-practices before adding features or workflows

## Testing

In order to test workflows feel free to create dummy issues/PRs etc. under tbrandenburg/playground.
Before running billable inference perform DAGU validation and, where supported,
a workflow-specific dry-run.

After any repository change, running `make validate` is mandatory. This target
checks every `.yml` and `.yaml` workflow in `/workflows` using Dagu, continues
checking the remaining files after an error, and returns a
nonzero status if a workflow fails. Fix or explicitly report failures before
claiming completion; never skip a workflow or suppress errors to pass the gate.
