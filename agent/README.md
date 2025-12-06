# Agent Harness

This small Python harness shows a pattern for reading tasks from Excel and processing them in a safe manner.

Main features:
- `agent_runner.py` reads `resources/sample_tasks.xlsx`, processes each task with a simple rule, and writes `sample_tasks.xlsx.updated`.
- The agent runs under the `agent` user inside the VM or under the current user locally.

How to run locally:

```
./scripts/bootstrap_local.sh
source .venv/bin/activate
python resources/generate_sample_xlsx.py
python -m agent.agent_runner --process-tasks
```

How to run in VM:

```
vagrant up
vagrant ssh
# inside VM
source /home/agent/venv/bin/activate
python /home/vagrant/workspace/resources/generate_sample_xlsx.py
python /home/vagrant/workspace/agent/agent_runner.py --process-tasks
```
