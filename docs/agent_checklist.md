# Agent Setup Quick Checklist

Before connecting a ChatGPT agent to this VM:

- [ ] Generate the sample resources: `python resources/generate_sample_xlsx.py`
- [ ] Ensure you or the agent has credentials and keys to connect to the VM (via `vagrant ssh` or SSH key)
- [ ] If using a CI or remote agent service, upload the VM SSH key to the agent service and ensure network access
- [ ] Do not check real secrets into the repository; use `resources/credentials_template.xlsx` as a template
- [ ] Start the agent service if you want automated processing: `systemctl enable --now agent-harness` (inside VM)
- [ ] Monitor logs: `/home/vagrant/workspace/agent/agent.log`

