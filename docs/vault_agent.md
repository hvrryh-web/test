# Vault Agent & Dynamic Credential Retrieval

This project includes a minimal Vault client to fetch secrets; use Vault Agent or the recommended Vault tooling for production.

Getting started with Vault dev:

```
vault server -dev -dev-root-token-id="root"
```

To store AWS keys in Vault:

```
vault kv put secret/data/myapp aws_access_key_id=AKIA... aws_secret_access_key=... aws_session_token=... agent_api_token=changeme
```

The agent's code uses `agent/vault_client.py` to retrieve secrets (via KV v2), and `agent/actions.py` uses it to find credentials for boto3. The `VAULT_SECRETS_PATH` environment variable can point to a different path.

Security note: prefer AppRole or IAM-based authentication when running on cloud VMs instead of sharing high-privilege root tokens.
