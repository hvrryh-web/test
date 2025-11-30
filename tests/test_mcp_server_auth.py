#!/usr/bin/env python3
import json
import os
import tempfile
import shutil
import sys

# Ensure repo root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import mcp_server as server


def test_mcp_post_authorized(tmp_path):
    cfg_file = tmp_path / 'agent_config.json'
    cfg = {
        'data_dir': str(tmp_path),
        'tasks_file': 'sample_tasks.xlsx',
        'api_token': 'testtoken',
    }
    cfg_file.write_text(json.dumps(cfg))

    os.environ['AGENT_CONFIG_PATH'] = str(cfg_file)

    # Create a test payload
    payload = {'task_id': 'T1000', 'description': 'Sample add', 'status': 'pending', 'due_date': '2025-01-01'}
    client = server.app.test_client()
    headers = {'X-AGENT-TOKEN': 'testtoken'}

    response = client.post('/tasks', json=payload, headers=headers)
    assert response.status_code == 200

    # The server should have written the tasks file
    tasks_path = tmp_path / 'sample_tasks.xlsx'
    assert tasks_path.exists()


def test_mcp_post_unauthorized(tmp_path):
    cfg_file = tmp_path / 'agent_config.json'
    cfg = {
        'data_dir': str(tmp_path),
        'tasks_file': 'sample_tasks.xlsx',
        'api_token': 'testtoken',
    }
    cfg_file.write_text(json.dumps(cfg))
    os.environ['AGENT_CONFIG_PATH'] = str(cfg_file)

    payload = {'task_id': 'T1001', 'description': 'Sample add', 'status': 'pending', 'due_date': '2025-01-01'}
    client = server.app.test_client()
    headers = {'X-AGENT-TOKEN': 'wrongtoken'}

    response = client.post('/tasks', json=payload, headers=headers)
    assert response.status_code == 401


if __name__ == '__main__':
    print('Run pytest to execute tests')
