#!/usr/bin/env python3
import os
import sys
import subprocess
import json

from agent.executor import run_safe_command, Policy


def test_policy_denies_unsafe_command():
    out = run_safe_command('echo hello')
    assert out.get('status') == 'denied'


def test_policy_allows_python_commands():
    # Run the generator script via the safe executor; this should be allowed by policy
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cmd = f'{sys.executable} {os.path.join(root, "resources", "generate_sample_xlsx.py")}'
    out = run_safe_command(cmd)
    assert out.get('status') in ('ok', 'failed')


if __name__ == '__main__':
    test_policy_denies_unsafe_command()
    test_policy_allows_python_commands()
    print('Executor tests passed')
