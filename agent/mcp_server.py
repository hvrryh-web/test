#!/usr/bin/env python3
"""
Minimal MCP (Model Context Protocol) server that accepts tasks through a REST API.
Usage: python -m agent.mcp_server

Endpoints:
- POST /tasks: Accepts task payload and writes to resources/tasks.xlsx or invokes agent processor.
- GET /health: Health check

Security: Simple token-based header 'X-AGENT-TOKEN' or uses VAULT for token lookup.
"""

from __future__ import annotations

import json
import os
import logging
from flask import Flask, request, jsonify
from pathlib import Path

from .vault_client import VaultClient

app = Flask(__name__)
logger = logging.getLogger(__name__)

def load_config(path=None):
    env_cfg = os.getenv('AGENT_CONFIG_PATH')
    cfg_path = path or env_cfg or os.path.join(os.path.dirname(__file__), 'agent_config.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/tasks', methods=['POST'])
def add_task():
    cfg = load_config()
    token = request.headers.get('X-AGENT-TOKEN')

    # Token check: simple header or Vault-backed token check
    api_token = os.environ.get('AGENT_API_TOKEN') or cfg.get('api_token')
    if not api_token:
        # Try vault
        try:
            vcfg = cfg.get('vault') or {}
            vc = VaultClient(vault_addr=vcfg.get('addr'))
            api_token = vc.get_secret_value(vcfg.get('secrets_path'), 'agent_api_token')
        except Exception:
            api_token = None

    if api_token and token != api_token:
        return jsonify({'error': 'unauthorized'}), 401

    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'invalid payload'}), 400
    # Expected payload: {task_id, description, status, due_date}
    resources_dir = cfg.get('data_dir') or os.path.join(os.path.dirname(__file__), '..', 'resources')
    tasks_file = cfg.get('tasks_file') or 'sample_tasks.xlsx'

    tasks_path = Path(resources_dir) / tasks_file
    # Ensure resources dir exists so writing tasks works when using test-local resources
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    # If tasks file exists, append a new row; else create new excel
    try:
        import pandas as pd
        if tasks_path.exists():
            df = pd.read_excel(tasks_path)
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        else:
            df = pd.DataFrame([data])
        df.to_excel(tasks_path, index=False)
    except Exception as e:
        logger.exception('Failed to write task: %s', e)
        return jsonify({'error': 'failed'}), 500

    return jsonify({'ok': True})


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cfg = load_config()
    host = cfg.get('api_host', '0.0.0.0')
    port = cfg.get('api_port', 8080)
    # Allow run within docker/host
    app.run(host=host, port=port)
