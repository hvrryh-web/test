# ChatGPT Agent VM Environment

This workspace provides a minimal environment for a ChatGPT agent to connect to a VM and process tasks, including sample Excel resources.

- ## Key components
- Vagrantfile and a provisioning script to bootstrap an Ubuntu VM
- A Python agent harness that reads/writes Excel files and processes tasks
- Sample resources (Excel generator) and tests
- Documentation in `docs/` for setup and security
- Vault integration via `agent/vault_client.py` and `docs/vault_setup.md`
- A sandboxed command executor `agent/executor.py` and policy file `security/agent_policy.yaml`
- Monitoring via Prometheus metrics and structured logging
- Dockerized agent via `Dockerfile` and `docker-compose.yml` for dev/observation
- MCP server endpoint in `agent/mcp_server.py` for REST-based task ingestion

See `docs/agent_setup.md`, `docs/excel_resources.md`, and `docs/vm_connection.md` for details.

## Quick start (local)

1. Bootstrap local Python environment:

```bash
./scripts/bootstrap_local.sh
source .venv/bin/activate
```
2. Generate sample Excel files and run the agent:

```bash
python resources/generate_sample_xlsx.py
# If you run locally, override the config to point to the workspace resources:
export AGENT_CONFIG_PATH=$(pwd)/agent/agent_config.json
python -m agent.agent_runner --process-tasks

4. Use the ChatGPT adapter to post tasks to MCP (optional):

```bash
# Dry run (no OpenAI):
python tools/chatgpt_adapter.py --dry-run --count 1

# Full run (requires OPENAI_API_KEY and AGENT_API_TOKEN):
export OPENAI_API_KEY=sk-...
export AGENT_API_TOKEN=changeme
python tools/chatgpt_adapter.py --count 1 --host http://localhost --port 8080
```
```
3. Run tests:

```bash
./scripts/run_tests.sh
```

## Notes

- If you plan to run on a VM, `vagrant up` will provision the VM and install dependencies.
- For security, never check in real credentials; use the `resources/credentials_template.xlsx` as a template and keep real secrets in a secure store.
- For security, never check in real credentials; use Vault (HashiCorp Vault) or environment variables for secrets. See `docs/vault_setup.md` for a quick guide.
