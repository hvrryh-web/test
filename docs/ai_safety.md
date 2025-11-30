# AI Agent Safety Guidelines

This document provides a set of guidelines and best practices for operating AI agents in the VM environment.

Key principles:
- Principle of least privilege: The agent should only get the minimum privileges required to perform tasks. Avoid granting root access.
- Policy enforcement: Use `security/agent_policy.yaml` to define whitelisted commands and scripts; enforce these via `agent/executor.py`.
- Secrets management: Never store secrets in code or plain text. Use HashiCorp Vault for secret storage and fetch with `agent/vault_client.py`.
- Audit logging: Enable structured logging and export logs to a secure centralized logging endpoint. Keep logs write-only to minimize tampering.
- Network controls: Use private networks, firewalls, and VPC rules to limit external exposure.
- Approval workflows: Use human approvals for high-risk operations (e.g., delete, production writes) and require multi-person oversight.
- Safe execution: Specialist operations should run inside isolated containers (Docker/Podman) using minimal base images and a seccomp/cgroups profile to limit system calls and resource usage.
- Monitoring: Capture metrics and alerts for anomalous behavior, long-running tasks, or repeated failures.

Recommended Additional Safety Tools:
- Vault Agent or Vault Tokens for secret injection
- Container runtime (Docker/Podman) for task sandboxing
- Centralized logging and SIEM for real-time alerting
- Static policy enforcement in a gate process for deployed tasks

See `docs/sandbox.md` for sandbox and policy usage details and `security/agent_policy.yaml` for an example policy.
