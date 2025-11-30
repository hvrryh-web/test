# FAQ

Q: How does this environment help ChatGPT Agent Mode?
A: It provides a local VM runtime where the agent can safely connect and perform tasks like reading and writing Excel resources. The repository contains scripts, examples, and safe harness patterns to execute tasks.

Q: Are there any restrictions on what the agent can run?
A: The sample harness uses only local, safe operations. For safety, avoid arbitrary shell execution. If necessary, implement strict whitelisting.

Q: Where should secrets be stored?
A: Never commit secrets to the repo. Use a secure secrets manager or the agent platform's secret storage.

Q: How to enable long-running tasks?
A: Configure the `agent-harness.service` systemd unit in `scripts/provision.sh` and use `systemctl` to start or enable it.

Q: How to connect via the ChatGPT Agent Mode UI?
A: Typically add the VM's SSH details and keys to the chat agent UI when configuring resource connections; refer to provider docs for adding SSH keys.
