#!/usr/bin/env python3
"""
Safe executor: runs a command or a whitelisted script under resource limits and checks policy file.
"""
import os
import shlex
import subprocess
import time
import logging
import resource
from typing import Optional

import ruamel.yaml as yaml

POLICY_PATH = os.path.join(os.path.dirname(__file__), '..', 'security', 'agent_policy.yaml')

logger = logging.getLogger(__name__)


class Policy:
    def __init__(self, path: Optional[str] = None):
        self.path = path or POLICY_PATH
        self._data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                return yaml.YAML().load(f)
        return {}

    def allows_command(self, cmd: str) -> bool:
        # Basic check: exact match or substring in whitelisted commands
        allowed = self._data.get('allowed_actions', [])
        for a in allowed:
            if a.get('type') == 'run_command':
                for c in a.get('commands', []):
                    if cmd.strip() == c.strip() or c.strip() in cmd:
                        return True
        return False

    def is_script_whitelisted(self, script_path: str) -> bool:
        w = self._data.get('whitelisted_scripts', []) or []
        return any(script_path.endswith(s) for s in w)


def _limit_resources(cpu_seconds: int = 5, mem_bytes: int = 512 * 1024 * 1024):
    # preexec_fn to set resource limits
    def _lim():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    return _lim


def run_safe_command(command: str, timeout: int = 30, check_policy: bool = True) -> dict:
    policy = Policy()
    if check_policy and not policy.allows_command(command):
        logger.warning('Command not allowed by policy: %s', command)
        return {'status': 'denied', 'reason': 'policy'}

    args = shlex.split(command)
    try:
        start = time.time()
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout, preexec_fn=_limit_resources())
        duration = time.time() - start
        return {
            'status': 'ok' if proc.returncode == 0 else 'failed',
            'returncode': proc.returncode,
            'stdout': proc.stdout,
            'stderr': proc.stderr,
            'duration': duration,
        }
    except subprocess.TimeoutExpired as e:
        logger.error('Command timeout: %s', command)
        return {'status': 'timeout', 'reason': str(e)}
    except Exception as e:
        logger.exception('Command failed: %s', command)
        return {'status': 'error', 'reason': str(e)}


def run_safe_script(script_path: str, timeout: int = 30) -> dict:
    policy = Policy()
    if not policy.is_script_whitelisted(script_path):
        logger.warning('Script not whitelisted: %s', script_path)
        return {'status': 'denied', 'reason': 'script_whitelist'}
    if not os.path.exists(script_path):
        logger.warning('Script not found: %s', script_path)
        return {'status': 'file_missing'}
    return run_safe_command(f'bash {script_path}', timeout=timeout)
