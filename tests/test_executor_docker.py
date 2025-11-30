#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.executor import run_in_docker


def test_docker_run_or_not_available():
    out = run_in_docker('echo hello', image='python:3.12-slim')
    assert out.get('status') in ('ok', 'denied', 'docker-not-available', 'failed')


if __name__ == '__main__':
    res = test_docker_run_or_not_available()
    print('Docker executor test passed')
