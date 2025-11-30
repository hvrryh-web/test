#!/usr/bin/env python3
import os
import sys
import json
import importlib.util

# Ensure tools can be imported
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TOOLS_DIR = os.path.join(PROJECT_DIR, 'tools')
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import chatgpt_adapter as cga
import importlib
import types
import pytest


def import_openai_or_skip(monkeypatch, fake_resp=None):
    # Ensure openai module exists for tests and support monkeypatch of ChatCompletion
    try:
        import openai
    except Exception:
        pytest.skip('openai not installed; skip integration test')
    # Patch openai to respond with a fake payload
    if fake_resp is not None:
        class DummyChoice:
            def __init__(self, content):
                self.message = types.SimpleNamespace(content=content)

        class DummyResp:
            def __init__(self, content):
                self.choices = [DummyChoice(content)]

        def fake_create(*args, **kwargs):
            return DummyResp(fake_resp)

        monkeypatch.setattr(openai.ChatCompletion, 'create', fake_create)
    return openai


def test_validate_good_task():
    good = {
        'task_id': 'T001',
        'description': 'Summarize sample_data.xlsx',
        'status': 'pending',
        'due_date': '2025-12-01'
    }
    assert cga.validate_task_dict(good)


def test_validate_bad_task():
    bad = {
        # missing description
        'task_id': 'T002',
        'status': 'pending',
        'due_date': '2025-12-01'
    }
    assert not cga.validate_task_dict(bad)


def test_validate_bad_status_and_date():
    invalid = {
        'task_id': 'T003',
        'description': 'Summarize sample_data.xlsx',
        'status': 'running',  # invalid status
        'due_date': '2025-13-01'  # invalid month
    }
    assert not cga.validate_task_dict(invalid)


def test_generate_tasks_with_openai_from_vault(monkeypatch, tmp_path):
    # Skip if openai is not installed
    try:
        import openai
    except Exception:
        pytest.skip('openai not installed; skipping OpenAI integration test')

    # Setup monkeypatch for VaultClient.get_secret_value
    class DummyVault:
        def get_secret_value(self, path, key, default=None):
            if key in ('OPENAI_API_KEY', 'openai_api_key'):
                return 'fake-openai-key'
            return None

    monkeypatch.setattr('agent.vault_client.VaultClient', lambda *args, **kwargs: DummyVault())

    # Fake openai response: a JSON list with a single valid task
    fake_payload = json.dumps([{"task_id": "T_VAULT_001", "description": "Summarize sample_data.xlsx", "status": "pending", "due_date": "2025-12-01"}])
    # Monkeypatch openai.ChatCompletion.create
    class DummyChoice:
        def __init__(self, content):
            self.message = types.SimpleNamespace(content=content)

    class DummyResp:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]

    def fake_create(*args, **kwargs):
        return DummyResp(fake_payload)

    monkeypatch.setattr(openai.ChatCompletion, 'create', fake_create)

    # Call the adapter function (should not raise)
    tasks = cga.generate_tasks_with_openai(1)
    assert len(tasks) == 1
    assert tasks[0].task_id == 'T_VAULT_001'


if __name__ == '__main__':
    test_validate_good_task()
    test_validate_bad_task()
    print('Schema validation tests OK')
