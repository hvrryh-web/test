# Security Guide for Agent-in-VM Environment

This environment is designed for demonstration and local automation. For production, consider secure gating and stricter controls.

- Users
  - The VM user `agent` is created for running the agent harness. Avoid storing sensitive secrets in plaintext in the workspace.
- Access control
  - Use SSH key-based access and keep keys secure. Rotate keys when needed.
- Secrets & credentials
  - Do NOT embed credentials in spreadsheets or in checked-in config files. Use OS secret managers (HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager) or encrypted files.
  - This repository includes a small Vault client wrapper `agent/vault_client.py` which fetches secrets from a KV v2 engine by default, and falls back to environment variables if no Vault token is present (for development convenience only).
- Network exposure
  - Vagrant sets up a private network by default. Avoid exposing the agent service to the public internet unless protected.
- Logging & auditing
  - Agent logs are stored at `/home/vagrant/workspace/agent/agent.log`. Consider central logging and log rotation.
- Systemd service
  - If you enable the systemd service, make sure you set up appropriate process monitoring and resource caps.
  - The `agent/executor.py` enforces a policy defined in `security/agent_policy.yaml`. This is a minimal enforcement mechanism. For real-world use, prefer hardened sandbox/containment using containers or VMs.

Typical run policies:
- Only accept file changes from trusted sources in the shared workspace.
- Keep container or VM images up-to-date with security patches.

