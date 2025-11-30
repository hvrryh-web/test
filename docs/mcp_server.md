# MCP Server (REST API) for Tasks

The MCP server accepts tasks using a simple REST API and is a recommended path for programmatic integrations into the agent VM.

Endpoints
- GET /health — returns {"status": "ok"}
- POST /tasks — accepts a JSON payload of a task with required fields: `task_id`, `description`, `status`, and `due_date`.
  - Example input:
  ```json
  {
    "task_id": "T100",
    "description": "Sample task via API",
    "status": "pending",
    "due_date": "2025-12-31"
  }
  ```

Security
- Provide an `X-AGENT-TOKEN` header with the value configured in `agent/agent_config.json` (or provided through Vault at `vault/secrets` path with key `agent_api_token`).
- Alternatively, configure ACLs in your infrastructure or run the MCP server behind a secure endpoint.

How it works
- The server writes the task to the tasks spreadsheet under `cfg.data_dir` and `cfg.tasks_file`.
- Optionally, post-processing of the tasks is triggered by the agent's `agent_runner` in watch mode.

Notes
- Use secure token management: the API token should be provided via Vault rather than being checked into the repo.
- For production, secure communications with TLS & invalidate tokens regularly.
