# awesome-agent-workflows agent guidelines

## Introduction

This is a repository collecting valuable [DAGU](https://docs.dagu.sh) based agentic workflows.

## Guidelines

- Keep the structure of `README.md` - only add or update information in `README.md` if it fits into its structure

## Testing

In order to test workflows feel free to create dummy issues/PRs etc. under tbrandenburg/playground.
Before running billable inference perform DAGU validation and, where supported,
a workflow-specific dry-run.

After any repository change, running `make validate` is mandatory. This target
checks every `.yml` and `.yaml` workflow in `/workflows` using Dagu, continues
checking the remaining files after an error, and returns a
nonzero status if a workflow fails. Fix or explicitly report failures before
claiming completion; never skip a workflow or suppress errors to pass the gate.
