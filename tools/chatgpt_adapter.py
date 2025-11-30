#!/usr/bin/env python3
"""
Small example adapter that uses OpenAI API to generate task payloads and propose tasks to the MCP server
in this repository. This script is meant to be run outside the agent harness as a demonstration of sending
tasks from an external ChatGPT-based agent to the MCP server using the API token.

Usage example:
    export OPENAI_API_KEY=sk-...  
    export AGENT_API_TOKEN=changeme
    python tools/chatgpt_adapter.py --host http://localhost --port 8080 --count 1 --dry-run

This script is intentionally minimal; it does not validate OpenAI usage strictly. It uses env vars or Vault
if present (Vault support is optional and not required here).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass
from typing import List, Optional
import sys
from jsonschema import validate, ValidationError, FormatChecker

import requests

try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class GeneratedTask:
    task_id: str
    description: str
    status: str = 'pending'
    due_date: Optional[str] = None


DEFAULT_PROMPT = (
    "Generate a single JSON task describing a safe, local action that a Python agent can perform.\n"
    "Output must be valid JSON and contain the keys: task_id, description, status, due_date (YYYY-MM-DD).\n"
    "Examples of actions: 'Summarize sample_data.xlsx', 'DB_QUERY: SELECT * FROM sample', 'EXPORT_CSV: export sample_data'\n"
)


TASK_SCHEMA = {
    'type': 'object',
    'properties': {
        'task_id': {'type': 'string'},
        'description': {'type': 'string'},
        'status': {'type': 'string', 'enum': ['pending', 'in-progress', 'completed', 'failed']},
        'due_date': {'type': 'string', 'format': 'date'},
    },
    'required': ['task_id', 'description', 'status', 'due_date'],
}


def generate_tasks_with_openai(count: int = 1) -> List[GeneratedTask]:
    if not OPENAI_AVAILABLE:
        raise RuntimeError('openai package is not available. Install openai or run in dry-run mode')
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        # Try to fetch from Vault (optional)
        try:
            # Ensure agent package is importable
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if repo_root not in sys.path:
                sys.path.insert(0, repo_root)
            from agent.vault_client import VaultClient
            # If agent config path exists, prefer the 'vault.secrets_path' specified there
            vault_path = os.environ.get('VAULT_SECRETS_PATH')
            if not vault_path:
                config_path = os.environ.get('AGENT_CONFIG_PATH') or os.path.join(repo_root, 'agent', 'agent_config.json')
                if os.path.exists(config_path):
                    import json as _json
                    try:
                        cfg = _json.load(open(config_path, 'r', encoding='utf-8'))
                        vault_cfg = cfg.get('vault') or {}
                        vault_path = vault_cfg.get('secrets_path')
                    except Exception:
                        vault_path = None
            if not vault_path:
                vault_path = 'secret/data/myapp'
            vc = VaultClient()
            # Accept either key name variants
            key = vc.get_secret_value(vault_path, 'OPENAI_API_KEY') or vc.get_secret_value(vault_path, 'openai_api_key')
            if key:
                logger.info('OpenAI key retrieved from Vault')
        except Exception:
            key = None
    if not key:
        raise RuntimeError('OPENAI_API_KEY must be set in environment or Vault')
    openai.api_key = key

    prompt = DEFAULT_PROMPT + f"\nReturn {count} tasks as a JSON list."
    resp = openai.ChatCompletion.create(
        model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.2,
    )
    # The model output should be JSON; parse it
    text = resp.choices[0].message.content.strip()
    payload = json.loads(text)

    tasks = []
    for p in payload:
        # validate raw dict before converting
        try:
            validate(instance=p, schema=TASK_SCHEMA, format_checker=FormatChecker())
        except ValidationError as e:
            logger.warning('Skipping invalid task from OpenAI response: %s', e)
            continue
        tasks.append(GeneratedTask(
            task_id=str(p.get('task_id')),
            description=str(p.get('description')),
            status=str(p.get('status', 'pending')),
            due_date=p.get('due_date')
        ))
    return tasks


def generate_tasks_dryrun(count: int = 1) -> List[GeneratedTask]:
    # Produce minimal fixed examples for offline/dry-run
    tasks = []
    import datetime
    for i in range(count):
        tasks.append(GeneratedTask(
            task_id=f"T_CHAT_{i+1:03}",
            description='Summarize sample_data.xlsx',
            status='pending',
            due_date=(datetime.date.today()).isoformat()
        ))
    return tasks


def validate_task_dict(task_dict: dict) -> bool:
    """Validate a dict against the TASK_SCHEMA. Returns True if valid, else False."""
    try:
        validate(instance=task_dict, schema=TASK_SCHEMA, format_checker=FormatChecker())
        return True
    except ValidationError:
        return False


def post_task_to_mcp(host: str, port: int, token: Optional[str], task: GeneratedTask) -> requests.Response:
    base = host.rstrip('/')
    url = f"{base}:{port}/tasks" if str(port) not in host else f"{base}/tasks"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-AGENT-TOKEN"] = token
    payload = {
        'task_id': task.task_id,
        'description': task.description,
        'status': task.status,
        'due_date': task.due_date,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=5)
    return resp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default=os.environ.get('MCP_HOST', 'http://localhost'), help='MCP base URL (http://localhost)')
    parser.add_argument('--port', default=int(os.environ.get('MCP_PORT', 8080)), type=int)
    parser.add_argument('--count', default=1, type=int)
    parser.add_argument('--dry-run', action='store_true', help='Do not call OpenAI or the MCP server; emit tasks to stdout')
    parser.add_argument('--token', default=os.environ.get('AGENT_API_TOKEN'), help='Agent token for MCP authentication')
    args = parser.parse_args()

    if args.dry_run:
        tasks = generate_tasks_dryrun(args.count)
    else:
        if OPENAI_AVAILABLE and os.environ.get('OPENAI_API_KEY'):
            try:
                tasks = generate_tasks_with_openai(count=args.count)
            except Exception as e:
                logger.error('OpenAI generation failed: %s', e)
                tasks = generate_tasks_dryrun(args.count)
        else:
            logger.warning('openai package or OPENAI_API_KEY missing. Falling back to dry-run tasks')
            tasks = generate_tasks_dryrun(args.count)

    for t in tasks:
        logger.info('Task: %s - %s', t.task_id, t.description)
        if args.dry_run:
            print(json.dumps(t.__dict__, indent=2))
        else:
            try:
                resp = post_task_to_mcp(args.host, args.port, args.token, t)
                if resp.ok:
                    logger.info('Posted task %s: %s', t.task_id, resp.text)
                else:
                    logger.error('MCP POST failed [%s] %s', resp.status_code, resp.text)
            except Exception as e:
                logger.exception('Failed to post task: %s', e)


if __name__ == '__main__':
    main()
