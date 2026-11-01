# Contributing

## Workflow contract

1. Put executable Dagu definitions under `workflows/` and their guide under `docs/`.
2. Include required child DAGs, prompts, and runtime glue in the workflow YAML.
3. Parameterize deployment paths, target repositories, and other operator choices.
4. Never bundle secrets, auth exports, private run logs, or machine-specific state.
5. State tool/version requirements and the execution/security boundary explicitly.
6. Prefer native Dagu actions; use embedded glue only where it adds necessary semantics.
7. Bound retries, inference, waits, and repair loops. Preserve failed work safely.
8. Keep mutations explicit. Do not force-push/reset or discard another workflow's work.
9. Add high-signal tests against the deployable artifact, not a parallel implementation.
10. Validate with real tools and report the limits of end-to-end coverage.

## Pull requests

Describe the problem, workflow inputs/outputs, safety decisions, validation commands,
and evidence. Include the workflow guide and tests in the same change. Do not
publish secrets or private task data to demonstrate correctness.

New model routes need authentication/catalog checks and a readiness contract;
model-name registration alone is not proof of access or suitability.
