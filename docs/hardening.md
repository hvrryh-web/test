# Hardening and OS-level sandboxing

This document explains how to harden the agent environment for production use.

1. Use containers: run task execution inside containers using config-defined images (or signed images from a private registry).
   - Use `agent/executor.py`'s `run_in_docker()` to execute arbitrary commands inside a limited container with `--cpus` and `--memory` limits.
   - Add the `--security-opt seccomp=<seccomp_file>` to the docker command to restrict syscalls.

2. Limit privileges
   - Avoid `--privileged` in docker run. Use user namespaces or `--user` to run containers as non-root.
   - Use a custom Docker image with minimal OS and non-root default user.

3. Use seccomp & cgroups
   - Keep `security/seccomp.json` as a minimal example. For production, create tailored profiles that block sensitive syscalls.
   - Use container runtime configs to set cgroups limits (CPU/memory) and swap parameters.

4. Keep secrets off-disk
   - Do not check secrets into the repo. Use Vault with short-lived credentials, or a cloud provider's dynamic credentials setup.
   - While running containers, use secret stores or inject via environment variables only when required.

5. Monitoring & observability
   - Keep metrics and logs exported to central systems. Use `monitoring/prometheus.yml` as template and connect to a centralized Prometheus and alerting system.
   - Use Fluentd or other log forwarder to ship logs securely and enforce write-only log storage.

6. Security scanning & CI gates
   - Run container image scanning tools and static analysis as part of your CI pipeline.
   - Use policy-as-code (OPA, Gatekeeper) to validate job/admin definitions before deployment.

