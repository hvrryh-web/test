# Sandbox & Policy Enforcement

The agent harness includes a basic sandbox and policy enforcement mechanism to limit actions executed by the agent.

Key points:
- `security/agent_policy.yaml` contains allow/deny rules for read/write operations, allowed commands, and a whitelist of scripts.
- `agent/executor.py` loads the policy and validates commands before executing them.
- The executor sets resource limits (CPU, memory) using Python's `resource` module to prevent runaway processes.
- For safety, the executor only runs commands that match the policy's `allowed_actions` and refuses commands listed under `prohibited_actions`.

Implementation notes:
- The sandbox enforces only a minimal level of policy — for production, consider using OS-level containers, user namespaces, or lightweight VMs.
- All external commands are run through `run_safe_command()` (caller must provide a pre-validated command string).
- Add scripts to the `whitelisted_scripts` list to allow them to run via `run_safe_script()`.

Security recommendations:
- Review and maintain the policy file to control allowed commands (keep minimal).
- Use signed and vetted scripts only.
- For production, enforce policy in a kernel-level sandbox (cgroups, seccomp, containers), or use ephemeral worker VMs.
