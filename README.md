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

[Checks / Validate](/.github/workflows/checks.yml) runs `make validate` on pushes
(including merges), pull requests, and merge queues. It uses Ubuntu 24.04's
[preinstalled GNU Make](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md)
and downloads the [official Dagu 2.25.1 release](https://github.com/dagucloud/dagu/releases/tag/v2.25.1),
verifying its SHA-256 checksum. No service installation, inference, or workflow
execution is needed.

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
