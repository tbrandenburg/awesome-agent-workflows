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
9. Prioritize formatting, linting, and native validation of the deployable artifacts and embedded
   code. Do not add a behavioral test framework or a parallel workflow implementation by default;
   see [repository boundaries](/AGENTS.md#repository-boundary).
10. For behavior changes, the agent runs the canonical workflow locally with disposable inputs,
    verifies actual outputs and side effects, and reports the remaining limitations. Keep temporary
    harnesses and private run evidence outside the tracked repository.

## Pull requests

Describe the problem, workflow inputs/outputs, safety decisions, validation commands, and evidence.
Include the workflow guide and applicable formatting/lint configuration in the same change;
checked-in behavioral tests are not required by default. Do not publish secrets or private task data
to demonstrate correctness.

New model routes need authentication/catalog checks and a readiness contract; model-name
registration alone is not proof of access or suitability.
