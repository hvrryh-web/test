# Agent Runbook / Playbook

This runbook outlines a typical sequence an AI agent uses when connected to the VM:

1. Fetch tasks
   - The agent reads `resources/sample_tasks.xlsx` to find pending tasks.
  - External agents (ChatGPT or others) can post tasks to the MCP server via `POST /tasks` at `agent.mcp_server`.
2. Validate tasks
   - Validate task content, file paths, and allowed operations based on `security/agent_policy.yaml`.
3. Execute tasks in a sandboxed or safe manner
   - For example: summarization tasks will call `agent_runner` which uses pandas and creates an output file `resources/summary.xlsx`.
4. Write results
   - Updated tasks are written to `resources/sample_tasks.xlsx.updated` and summaries are written to `resources/summary.xlsx`.
5. Cleanup and logs
   - Logs are captured at `/home/vagrant/workspace/agent/agent.log` in the VM or `agent/agent.log` locally.

Administrator actions:
- To add new tasks: add a row to `resources/sample_tasks.xlsx` with `status` set to `pending`.
- To add a new action type: extend `agent/tasks.py` with safe operations and update `agent/agent_runner.py` to call the function accordingly.
 - To create an external ChatGPT integration that generates tasks, see `tools/chatgpt_adapter.py` for an example.

Key operational notes:
- For anything requiring external network access, validate host connectivity and firewalls.
- For running heavy or long tasks, consider offloading to containers or VM workers.
- Ensure all actions are auditable.
