#!/usr/bin/env python3
"""
Minimal Hashicorp Vault client wrapper with fallback to environment variables.

Usage:
  client = VaultClient(vault_addr='http://127.0.0.1:8200', token='...')
  secret = client.get_secret('secret/data/myapp')

This wrapper uses requests to query Vault's KV v2 API and returns the 'data' section.
To avoid adding a full vault dependency, this is a small helper for demo use.
"""

from __future__ import annotations

import base64
import os
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class VaultClient:
    vault_addr: str = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
    token: Optional[str] = None

    def __post_init__(self):
        self.token = self.token or os.environ.get("VAULT_TOKEN")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["X-Vault-Token"] = self.token
        return headers

    def get_secret(self, path: str) -> Dict[str, Any]:
        """Get a secret from Vault's KV v2 secrets engine.

        Path example (KV v2): 'secret/data/mysecrets'
        """
        url = f"{self.vault_addr}/v1/{path}"
        resp = requests.get(url, headers=self._headers())
        if not resp.ok:
            raise RuntimeError(f"Vault GET failed: {resp.status_code} {resp.text}")
        data = resp.json()
        # For KV v2, the payload is at data.data
        if "data" in data and isinstance(data["data"], dict) and "data" in data["data"]:
            return data["data"]["data"]
        # Otherwise return the inner data
        if "data" in data:
            return data["data"]
        return data

    def get_raw_secret(self, path: str) -> Dict[str, Any]:
        return self.get_secret(path)

    def get_secret_value(self, path: str, key: str, default: Optional[str] = None) -> Optional[str]:
        try:
            payload = self.get_secret(path)
            if key in payload:
                return str(payload[key])
        except Exception:
            return default
        return default

# Quick fallback: get from env if VAULT_TOKEN missing or Vault not available
def get_credential(path: str, key: str, env_var: Optional[str] = None) -> Optional[str]:
    if env_var and os.environ.get(env_var):
        return os.environ.get(env_var)


    def get_aws_credentials(path: str, env_prefix: str = 'AWS') -> Dict[str, str] | None:
        try:
            client = VaultClient()
            data = client.get_raw_secret(path)
            # Expected keys: aws_access_key_id, aws_secret_access_key, aws_session_token (optional)
            aws_key = data.get('aws_access_key_id') or data.get('aws_access_key')
            aws_secret = data.get('aws_secret_access_key') or data.get('aws_secret_key')
            aws_token = data.get('aws_session_token')
            if aws_key and aws_secret:
                return {
                    'aws_access_key_id': aws_key,
                    'aws_secret_access_key': aws_secret,
                    'aws_session_token': aws_token,
                }
        except Exception:
            pass
        # fallback to env vars
        k = os.environ.get(f'{env_prefix}_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID')
        s = os.environ.get(f'{env_prefix}_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_ACCESS_KEY')
        t = os.environ.get(f'{env_prefix}_SESSION_TOKEN') or os.environ.get('AWS_SESSION_TOKEN')
        if k and s:
            return {
                'aws_access_key_id': k,
                'aws_secret_access_key': s,
                'aws_session_token': t,
            }
        return None
    try:
        client = VaultClient()
        return client.get_secret_value(path, key)
    except Exception:
        return os.environ.get(env_var)
