# Logging & Monitoring

This project includes basic logging and monitoring capabilities for the agent harness.

Logging:
- Structured JSON logs are produced via `agent/logging_config.py` using `python-json-logger`. Logs are written to the file specified in `agent_config.json` (default `agent/agent.log`) and to the console.
- You can forward logs to an HTTP endpoint by setting the `LOG_HTTP_DEST` environment variable to an endpoint (the agent will do a best-effort POST of JSON-log entries).

Metrics:
- A Prometheus metrics server is started by the agent harness by default on port `8000` (or override `metrics_port` in `agent_config.json`). This exposes basic counters:
  - `agent_tasks_processed_total` — number of tasks processed
  - `agent_tasks_errors_total` — number of task errors
- To collect metrics:
  - Configure Prometheus to scrape `http://<agent-host>:8000/`.

Operational tips:
- Rotate log files with logrotate or use aggregated logging (e.g., Logstash, Splunk, or CloudWatch).
- Prefer a custom logging backend or a central logging endpoint for production.
- For high availability, scale the harness into multiple VMs or use a queue with worker processes.
