# Observability and Monitoring

This repository includes example components for observability:

- Prometheus config: `monitoring/prometheus.yml` — scrape agent's metrics endpoint and Vault's metrics
- Fluentd config: `monitoring/fluent.conf` — example forwarding to STDOUT
- The agent exposes Prometheus metrics via `metrics_server.py` on port specified in `agent_config.json` (default 8000)

How to run:
- If using Docker Compose: `docker compose up -d prometheus fluentd agent vault`
- Configure your Prometheus server to point to the agent's metrics endpoint if deployed in a different cluster.

Tips for production:
- Add Grafana or other dashboards to visualize metrics
- Use Fluentd/Logstash to send logs to a central data store (e.g., Elasticsearch, Splunk, CloudWatch)
- Ensure secure credentials for endpoints and use Vault for secrets
