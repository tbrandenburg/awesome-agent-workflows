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
- When authoring, validating, or operating DAGU workflows, consider using the
  `dagu` skill for its current workflow-specific guidance.
- In case of changes: Do not make it more complicated, but try it simpler and smarter and in a state-of-the-art way - actively pursue elegant solutions instead of highly sophisticated and specific solutions - robustness and reliability through simplicity

## Privacy and repository portability

- Keep tracked documentation and workflows generic. Do not add personal names,
  account handles, email addresses, private repository names or URLs, local
  workspace/home paths, or other identifying details.
- Prefer parameters, environment variables, and placeholders over embedding
  repository-specific values. Keep operational examples portable; include
  server paths only when needed to explain the configured DAGU instance.
- Exception: the testing guidance may name `tbrandenburg/playground` as the
  designated repository for temporary test issues or pull requests.

## DAGU server registration and sub-workflows

- Keep each workflow's canonical YAML in this repository's `workflows/` directory.
- Register workflows in the shared server by symlinking each repository YAML
  into `/var/lib/dagu/dags/` (or the configured DAG directory). Use an absolute
  target so the server reads the canonical repository copy:
  ```sh
  repo_path=/absolute/path/to/repository
  dagu_dags_dir=/var/lib/dagu/dags
  name=example.yml
  test ! -e "$dagu_dags_dir/$name" && test ! -L "$dagu_dags_dir/$name"
  ln -s "$repo_path/workflows/$name" "$dagu_dags_dir/$name"
  ```
- If a workflow calls a sub-DAG, register that child YAML too, and ensure the
  `dag:` reference matches its server-visible DAG name. Edit only the repository
  copy; do not maintain a second independent YAML under the server DAG directory.
- Before creating a link, inspect the destination. Never overwrite an existing
  file or symlink without preserving it. Verify the link target with
  `readlink -f`, then use Dagu MCP `dagu_read` targets `dags` and `dag_spec` to
  confirm registration and inspect the loaded definition.
- A local Dagu CLI may point at a different DAG directory than the shared
  server. Check the CLI context/configuration before using `dagu ls` as evidence
  about the MCP-connected instance.
- Do not assume a valid YAML file or a registered parent proves that a
  symlinked sub-DAG resolves. Test the child call on the target server with a
  controlled, harmless input. If the parent skips the child because there is
  no eligible input, the sub-DAG call remains untested.
- Dagu server behavior can vary by configuration/version. Record observed
  results as evidence for the tested instance, not as a universal guarantee.

## Multi-repository worktree runs

- Choose only repositories the user authorized and use a read-only prompt for
  smoke tests (for example, report repository, branch, HEAD, default branch, and
  worktree path; explicitly forbid file changes, commits, pushes, and PRs).
- Before running, inspect the workflow's clone/cache paths and check for an
  existing worktree or local branch with the requested branch name. Use a
  unique temporary branch; do not let stale-worktree cleanup remove unrelated
  user work.
- Verify each child run's `ensure_clone`, `default_branch`, `worktree`,
  `run_prompt`, and exit-handler results. After completion, inspect each clone
  to confirm the temporary worktree and branch were removed and no files were
  changed.

## Testing

For workflow tests, use `tbrandenburg/playground` for temporary issues or pull
requests and clean them up after testing.
Before running billable inference perform DAGU validation and, where supported,
a workflow-specific dry-run.

After any repository change, running `make validate` is mandatory. This target
checks every `.yml` and `.yaml` workflow in `/workflows` using Dagu, continues
checking the remaining files after an error, and returns a
nonzero status if a workflow fails. Fix or explicitly report failures before
claiming completion; never skip a workflow or suppress errors to pass the gate.
