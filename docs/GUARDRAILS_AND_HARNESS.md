# Guardrails and deterministic harness

The production assistant modules enforce the following controls:

1. `TOOLS` and `TOOL_SCHEMAS` provide the allowlist.
2. `_valid_args` rejects unknown tools, missing fields, wrong JSON types, extra
   fields, invalid dates, and invalid enum values.
3. `execute_tool` enforces student-only saves and all database lookups use the
   authenticated user where ownership applies.
4. `confirm_action` creates a user-bound, exact-target, expiring single-use action;
   `approve_action` rejects unknown, cross-user, expired, and replayed IDs.
5. Retrieved records are delimited as `<retrieved_data>` and system instructions
   explicitly treat descriptions and eligibility text as untrusted.
6. Logs and API responses do not intentionally include passwords, tokens, or
   filesystem paths; resume access remains a separate authorized endpoint.
7. `MAX_ITERATIONS`, `MAX_TOOL_CALLS`, and one error-specific repair attempt bound
   model execution.
8. Tool errors, empty results, pending saves, and model failures are reported
   honestly; textual claims are not treated as database writes.

Run the harness with:

```powershell
$env:PYTHONPATH='.'; python -m backend.agent_harness
```

The 2026-11-13 synthetic run passed all 10 harness cases. This is deterministic
module evidence, not a real-Ollama transcript. Live prompt-injection and model
latency evidence remain outstanding.
