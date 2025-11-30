# Agent Setup Guide

This environment is intended to support a ChatGPT AI agent running inside a VM (via Vagrant). It provides a simple, safe harness for the agent to perform local tasks and access sample Excel resources.

Steps:

1. Install Vagrant and VirtualBox (or an alternate provider supported by Vagrant).
2. Bring up the VM:
   - vagrant up
   - vagrant ssh
3. Once inside the VM, activate the Python environment (if provisioning configured it):
   - source /home/agent/venv/bin/activate
4. Generate sample Excel resources (if not present):
   - cd /home/vagrant/workspace/resources
   - python3 generate_sample_xlsx.py
5. Run the agent harness manually or via the system service:
   - python -m agent.agent_runner --process-tasks
   - systemctl start agent-harness  # if service is enabled
   - Or use Docker Compose to run the agent inside containers:
     - docker compose up -d --build

Notes:
- The VM has an 'agent' user with passwordless sudo for ease of use for the agent harness. This is for demonstration only; for production, use stricter access controls.
- The sync folder binds the project to `/home/vagrant/workspace` so changes on the host are visible to the VM.
