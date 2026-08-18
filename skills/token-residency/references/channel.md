# CHANNEL — dispatch prompts and returns

Laws: the orchestrator pays until session end. Prompts cite WARM/COLD
artifacts by path — never inline what a path can carry. Returns are
schema'd and capped: status, deltas, decisions, NOTES-as-claims; bulk
output goes to disk, the return carries pointer + summary.

Exemplar (a capped return):

    STATUS: done. Edited 3 files (paths below). In-boundary decision:
    kept v1 naming — reopen if the API renames. NOTES: tests not run,
    no runner in repo. Full diff filed: artifacts/diff-041.txt

Anti-pattern: pasting file contents into a prompt the agent could
read from disk, or returning a full log the caller must scroll past.
