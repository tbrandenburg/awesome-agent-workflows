# Awesome Agent Workflows

- [Latest issue resolution](/workflows/latest-issue-resolution.yml): sequential
  issue-to-PR resolution in a dedicated local repository clone. Captures the latest
  open issue number and its first linked PR number as Dagu output variables, stopping
  if either is missing. Requires `dagu`, authenticated `gh`, Git, and OpenCode.
  The original hourly schedule and destructive checkout cleanup are retained.

  ```sh
  dagu start workflows/latest-issue-resolution.yml -- project_dir=/path/to/dedicated/clone
  ```
