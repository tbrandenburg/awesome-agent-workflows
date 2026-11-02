# Awesome Agent Workflows

## Validation

Requires Dagu on `PATH`. After changes, run the mandatory check:

```sh
make validate
```

The target validates the `.yml` and `.yaml` files in `/workflows`, attempts the
remaining files after a failure, and exits nonzero if a check fails.
Override `DAGU` to select the binary, or `DAGU_FLAGS` for options such as
`--dagu-home /path/to/check-home`.

## Workflows

- [Latest issue resolution](/workflows/latest-issue-resolution.yml): sequential
  issue-to-PR resolution in a dedicated local repository clone. Captures the latest
  open issue number and its first linked PR number as Dagu output variables, stopping
  if either is missing. Requires `dagu`, authenticated `gh`, Git, and OpenCode.
  ID lookups execute `gh` directly without a shell; empty results fail the step.
  The original hourly schedule and destructive checkout cleanup are retained.

  ```sh
  dagu start workflows/latest-issue-resolution.yml -- project_dir=/path/to/dedicated/clone
  ```
