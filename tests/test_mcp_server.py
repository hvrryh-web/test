#!/usr/bin/env python3
import os
import json
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import mcp_server as server


@pytest.fixture
def client(tmp_path):
    cfg_path = os.path.join(os.path.dirname(__file__), '..', 'agent', 'agent_config.json')
    # Use a local config pointing to resources
    cfg = json.load(open(cfg_path))
    cfg['data_dir'] = os.path.join(os.path.dirname(__file__), '..', 'resources')
    cfg['tasks_file'] = 'sample_tasks.xlsx'
    tmp_cfg = tmp_path / 'cfg.json'
    with open(tmp_cfg, 'w') as f:
        json.dump(cfg, f)
    os.environ['AGENT_CONFIG_PATH'] = str(tmp_cfg)
    # Compatibility: Flask's test client expects werkzeug.__version__ to exist
    try:
        import werkzeug
        if not hasattr(werkzeug, '__version__'):
            setattr(werkzeug, '__version__', '3.0.0')
    except Exception:
        pass
    server.app.config['TESTING'] = True
    with server.app.test_client() as c:
        yield c


def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200


def test_add_task(client, tmp_path):
    payload = {'task_id': 'M001', 'description': 'Test API task', 'status': 'pending', 'due_date': '2025-12-31'}
    headers = {'X-AGENT-TOKEN': 'changeme'}
    r = client.post('/tasks', json=payload, headers=headers)
    assert r.status_code == 200
    assert r.get_json().get('ok') == True
    # Ensure written
    import pandas as pd
    df = pd.read_excel(os.path.join(os.path.dirname(__file__), '..', 'resources', 'sample_tasks.xlsx'))
    assert 'M001' in df['task_id'].astype(str).values


if __name__ == '__main__':
    pytest.main(['-q'])
