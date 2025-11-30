# Docker & Docker Compose: Running the Agent

This repo includes a Dockerfile for the agent and a `docker-compose.yml` sample that runs:

- `vault` (dev server)
- `prometheus` for metrics
- `fluentd` for logs
- `agent` container that runs `agent.agent_runner` in watch mode

Start the dev stack:

```bash
docker compose up -d --build
```

Stop the stack:

```bash
docker compose down
```

Notes:
- You can use `docker compose logs -f agent` to follow logs.
- Use `docker exec -it <container> /bin/bash` to inspect the running container.
- Seccomp profile: `security/seccomp.json` is a small example. Use a hardened profile in production.
