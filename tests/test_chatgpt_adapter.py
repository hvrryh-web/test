#!/usr/bin/env python3
import os
import sys
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_chatgpt_adapter_dry_run(tmp_path):
    # Ensure the script runs without network when using dry-run
    script = os.path.join(os.path.dirname(__file__), '..', 'tools', 'chatgpt_adapter.py')
    res = subprocess.run([sys.executable, script, '--dry-run', '--count', '1'], capture_output=True, text=True)
    # Should have exit code 0 on success
    assert res.returncode == 0
    # It should print JSON that includes 'task_id' and 'description'
    stdout = res.stdout.strip()
    assert 'task_id' in stdout and 'description' in stdout


if __name__ == '__main__':
    test_chatgpt_adapter_dry_run(None)
    print('chatgpt_adapter dry-run test OK')
