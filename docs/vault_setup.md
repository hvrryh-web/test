# HashiCorp Vault Setup (Demo)

This document explains how to use HashiCorp Vault for storing secrets for the agent. For production, use hardened Vault and policies.

Steps (demo environment):

1. Install & run Vault locally (dev mode):
```
vault server -dev -dev-root-token-id="root"
```
2. Set environment variables for the agent to connect to Vault (on host or VM):
```
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root
```
3. Store secrets into Vault (KV v2):
```
vault kv put secret/data/myapp aws_access_key=AKIA... aws_secret_key=... smtp_user=smtp@example.com smtp_pass=secret
```
4. Read secrets in the agent harness:
- The agent uses `agent/vault_client.py` to fetch secrets. Sample usage:
```
from agent.vault_client import VaultClient
client = VaultClient()
aws_key = client.get_secret_value('secret/data/myapp', 'aws_access_key')
```
5. Agent fallback: if Vault is not set up or reachable, the agent falls back to the environment variables (for example `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `SMTP_USER`). This behavior is implemented in `agent/vault_client.py`.

Security tips:
- Do not commit tokens or sensitive credential files to the repository.
- Configure Vault policies limiting read access for the agent's role.
- Use Vault Agent or dynamic authentication for improved security in production.
