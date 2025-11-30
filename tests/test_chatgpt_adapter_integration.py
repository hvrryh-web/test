#!/usr/bin/env python3
import os
import sys
import time
import json
import subprocess
import socket
import requests
import types
import pytest

# Ensure project and tools are importable
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TOOLS_DIR = os.path.join(PROJECT_DIR, 'tools')
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import chatgpt_adapter as cga
from agent import mcp_server as server


def get_free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    addr, port = s.getsockname()
    s.close()
    return port


@pytest.mark.skipif(os.environ.get('RUN_INTEGRATION_TESTS', 'false').lower() != 'true', reason='Integration tests disabled')
def test_adapter_posts_to_live_mcp_with_vault(monkeypatch, tmp_path):
    # Write temp agent config that points to local resources and Vault
    port = get_free_port()
    cfg = {
        'data_dir': str(tmp_path),
        'tasks_file': 'sample_tasks.xlsx',
        'api_token': 'testtoken',
        'api_port': port,
        'vault': {'addr': os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200'), 'secrets_path': 'secret/data/testapp'}
    }
    cfg_file = tmp_path / 'agent_config.json'
    with open(cfg_file, 'w', encoding='utf-8') as f:
        json.dump(cfg, f)
    os.environ['AGENT_CONFIG_PATH'] = str(cfg_file)

    # Write secret to Vault dev
    vault_addr = cfg['vault']['addr']
    vault_token = os.environ.get('VAULT_TOKEN', 'root')
    secret_path = cfg['vault']['secrets_path']
    secrete_url = f"{vault_addr}/v1/{secret_path}"
    # Data path for KV v2 is {mount}/data/{path}
    payload = {'data': {'OPENAI_API_KEY': 'fake-openai-key'}}
    resp = requests.post(secrete_url, headers={'X-Vault-Token': vault_token}, json=payload)
    assert resp.ok, f"Failed to write secret to Vault: {resp.status_code} {resp.text}"

    # Start MCP server in background on free port (already passed in config)
    env = os.environ.copy()
    env['AGENT_CONFIG_PATH'] = str(cfg_file)
    env['AGENT_API_TOKEN'] = cfg['api_token']
    # run server as process
    proc = subprocess.Popen([sys.executable, '-m', 'agent.mcp_server'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for server to start
    base = 'http://127.0.0.1'
    # Poll for health endpoint
    health_ok = False
    for _ in range(20):
        try:
            r = requests.get(f'http://127.0.0.1:{port}/health', timeout=1)
            if r.ok:
                health_ok = True
                break
        except Exception:
            time.sleep(0.5)
    assert health_ok, 'MCP server did not start'

    # Monkeypatch openai chat completion to return a valid response
    fake_payload = json.dumps([{"task_id": "T_INT_001", "description": "Summarize sample_data.xlsx", "status": "pending", "due_date": "2025-12-01"}])
    try:
        import openai
        class DummyChoice:
            def __init__(self, content):
                self.message = types.SimpleNamespace(content=content)
        class DummyResp:
            def __init__(self, content):
                self.choices = [DummyChoice(content)]
        def fake_create(*args, **kwargs):
            return DummyResp(fake_payload)
        monkeypatch.setattr(openai.ChatCompletion, 'create', fake_create)
    except Exception:
        pytest.skip('openai package not installed; skip integration test')

    # Generate tasks and post them
    tasks = cga.generate_tasks_with_openai(1)
    assert len(tasks) == 1

    resp = cga.post_task_to_mcp('http://127.0.0.1', 8080, cfg['api_token'], tasks[0])
    assert resp.ok

    # Verify the task file exists
    tasks_path = tmp_path / cfg['tasks_file']
    assert tasks_path.exists()

    proc.terminate()
    proc.wait(timeout=5)


if __name__ == '__main__':
    print('Integration test should be run by CI with RUN_INTEGRATION_TESTS=true')
