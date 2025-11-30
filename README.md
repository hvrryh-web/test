# ChatGPT Agent VM Environment

This workspace provides a minimal environment for a ChatGPT agent to connect to a VM and process tasks, including sample Excel resources.

Key components:
- Vagrantfile and a provisioning script to bootstrap an Ubuntu VM
- A Python agent harness that reads/writes Excel files and processes tasks
- Sample resources (Excel generator) and tests
- Documentation in `docs/` for setup and security

See `docs/agent_setup.md`, `docs/excel_resources.md`, and `docs/vm_connection.md` for details.

## Quick start (local)
1. Bootstrap local Python environment:
```
./scripts/bootstrap_local.sh
source .venv/bin/activate
```
2. Generate sample Excel files and run the agent:
```
python resources/generate_sample_xlsx.py
python agent/agent_runner.py --process-tasks
```
3. Run tests:
```
./scripts/run_tests.sh
```

## Notes
- If you plan to run on a VM, `vagrant up` will provision the VM and install dependencies.
- For security, never check in real credentials; use the `resources/credentials_template.xlsx` as a template and keep real secrets in a secure store.
 - For security, never check in real credentials; use Vault (HashiCorp Vault) or environment variables for secrets. See `docs/vault_setup.md` for a quick guide.
