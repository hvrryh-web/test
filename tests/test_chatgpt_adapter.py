#!/usr/bin/env python3
import os
import sys
import json
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools')))
import chatgpt_adapter as cga


def test_chatgpt_adapter_dry_run(tmp_path):
    # Ensure the script runs without network when using dry-run
    script = os.path.join(os.path.dirname(__file__), '..', 'tools', 'chatgpt_adapter.py')
    res = subprocess.run([sys.executable, script, '--dry-run', '--count', '1'], capture_output=True, text=True)
    # Should have exit code 0 on success
    assert res.returncode == 0
    # It should print JSON that includes 'task_id' and 'description'
    stdout = res.stdout.strip()
    assert 'task_id' in stdout and 'description' in stdout
    # Validate JSON and schema
    parsed = json.loads(stdout)
    assert isinstance(parsed, dict) or isinstance(parsed, list)
    if isinstance(parsed, dict):
        assert cga.validate_task_dict(parsed)
    else:
        for obj in parsed:
            assert cga.validate_task_dict(obj)


if __name__ == '__main__':
    test_chatgpt_adapter_dry_run(None)
    print('chatgpt_adapter dry-run test OK')
