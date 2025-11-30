# ChatGPT / OpenAI Integration

This document explains how to use a minimal ChatGPT adapter to generate tasks and post them to the MCP server (`agent.mcp_server`).

## Overview
- The `tools/chatgpt_adapter.py` script demonstrates a simple adapter: it can call the OpenAI ChatCompletion API to produce one or more tasks, then POST each task to the MCP `/tasks` endpoint.
- The script supports both a `dry-run` mode (no OpenAI or network calls) and a full mode using OpenAI and the REST endpoint.

## Agent tokens & authentication
- The MCP server requires `X-AGENT-TOKEN` in headers to accept tasks (by default configured as `AGENT_API_TOKEN` in `agent/agent_config.json` or environment variable `AGENT_API_TOKEN`).
- For local testing, set `AGENT_API_TOKEN` in your environment and start the MCP server locally:

```bash
# In PowerShell examples
$env:AGENT_API_TOKEN='changeme'
python -m agent.mcp_server
```

## OpenAI API keys and Vault
- Use environment variable `OPENAI_API_KEY` or store it in Vault. The script reads `OPENAI_API_KEY` from environment and falls back to dry-run if not present.
- To use the Vault path, add keys to the Vault and update `agent_config.json` `vault.secrets_path` and run the Vault dev container with `docker-compose` for local tests.

## Run the sample adapter
- Dry-run mode (safe):

```bash
python tools/chatgpt_adapter.py --dry-run --count 2
```

- Full online run (requires `openai` package and `OPENAI_API_KEY`):

```bash
pip install -r requirements.txt
$env:OPENAI_API_KEY='sk-...'
$env:AGENT_API_TOKEN='changeme'
python tools/chatgpt_adapter.py --count 2 --host http://localhost --port 8080
```

## Security & policy
- This script demonstrates how a ChatGPT agent can post tasks to the MCP server. The server enforces token-based authentication; in production, always validate tokens and use TLS.
- This repository keeps agent side effects (S3, email) as safe stubs; do not add external network side effects unless you have proper access controls and secrets in Vault.

## What to add for production
- Rotate API tokens and use TLS/HTTPS for MCP communication.
- Add a Vault-backed secrets retrieval flow for `OPENAI_API_KEY` or other keys.
- Add a robust OpenAI prompt/response validation step that enforces an exact JSON schema (e.g., JSON schema validation step) before posting tasks.

If you'd like, I can add a Vault-backed API-key fetch example and a schema validation step.
