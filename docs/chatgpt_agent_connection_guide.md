# ChatGPT Agent Mode — VM Connection Guide

If you're using ChatGPT Agent Mode (or any remote agent connection), the typical steps for the agent to connect to the VM are:

1. Provide the VM connection details or an SSH key to the service that will make the agent connection. This often includes:
   - Host: the public or private address the agent can access
   - Port: typically 22
   - Username: for example, `agent` in this repo's VM
   - SSH private key (or a certificate) securely configured in the agent UI

2. Confirm that the agent's environment has network access to the VM. If the agent runs on cloud infrastructure, ensure relevant firewall rules and IP allowlisting are configured.

3. Ensure the `agent` user on the VM has the right permissions and that the agent will run only pre-approved actions. Avoid granting blanket root privileges unless required for a specific task.

4. Confirm the agent has a workspace mounted and that the agent user can read/write to the workspace. This repository mounts the host workspace into `/home/vagrant/workspace`.

5. If the agent should run a long-running process, configure a systemd service or a supervisor process. This repo includes `agent-harness.service` for a basic example.

Security reminder:
- Never share secret keys in repository source; provide them via the Agent Mode UI or a secret manager.
- Prefer ephemeral SSH keys or certificates where supported.
- For production, configure a bastion host or jumpbox rather than exposing the VM publicly.
