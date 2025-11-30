#!/usr/bin/env python3
"""
High-level actions the agent can perform. These are safe operations designed to be idempotent and auditable.
"""
import os
import json
import sqlite3
import time
import logging
import tempfile
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from .vault_client import get_credential
from .executor import run_safe_command

logger = logging.getLogger(__name__)
RESOURCES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
EXPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'exports'))

def export_dataframe_to_s3(df: pd.DataFrame, export_name: str, bucket: Optional[str] = None, prefix: Optional[str] = None) -> Optional[str]:
    """Export to S3 using boto3 if credentials are present, else fallback to local stub.
    Returns the path/URL of the export.
    """
    try:
        import boto3
        # Attempt to dynamically obtain AWS credentials from Vault
        from .vault_client import get_aws_credentials
        aws_creds = get_aws_credentials(os.environ.get('VAULT_SECRETS_PATH', 'secret/data/myapp'))
        session_params = {}
        if aws_creds:
            session_params = aws_creds
        # Else boto3 uses environment or instance credentials
        s3 = boto3.client('s3', **session_params)
        # Attempt to fetch AWS creds from Vault
        from .vault_client import get_aws_credentials
        aws_creds = get_aws_credentials(os.environ.get('VAULT_SECRETS_PATH', 'secret/data/myapp'))
        session_params = {}
        if aws_creds:
            session_params = aws_creds
        elif os.environ.get('AWS_ACCESS_KEY_ID'):
            session_params = {}
        s3 = boto3.client('s3', **session_params)
        # Try to source AWS credentials from Vault if available
        from .vault_client import VaultClient
        client = VaultClient()
        aws_key = client.get_secret_value(os.environ.get('VAULT_SECRETS_PATH', 'secret/data/myapp'), 'aws_access_key')
        aws_secret = client.get_secret_value(os.environ.get('VAULT_SECRETS_PATH', 'secret/data/myapp'), 'aws_secret_key')
        session_params = {}
        if aws_key and aws_secret:
            session_params['aws_access_key_id'] = aws_key
            session_params['aws_secret_access_key'] = aws_secret
        s3 = boto3.client('s3', **session_params)
        local_tmp = os.path.join(tempfile.gettempdir(), f'{export_name}.csv')
        df.to_csv(local_tmp, index=False)
        if not bucket:
            bucket = os.environ.get('S3_BUCKET')
        key = f"{(prefix + '/') if prefix else ''}{export_name}.csv"
        s3.upload_file(local_tmp, bucket, key)
        return f's3://{bucket}/{key}'
    except Exception:
        return export_dataframe_to_s3_stub(df, export_name)

os.makedirs(EXPORTS_DIR, exist_ok=True)


@dataclass
class DBQueryResult:
    columns: List[str]
    rows: List[List]


def db_query(query: str, db_path: Optional[str] = None) -> DBQueryResult:
    # Use a local SQLite DB for demonstration; in production, use connection details from Vault
    if not db_path:
        db_path = os.path.join(RESOURCES_DIR, 'sample.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(query)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    conn.close()
    return DBQueryResult(columns=cols, rows=rows)


def ensure_sample_db():
    db_path = os.path.join(RESOURCES_DIR, 'sample.db')
    if os.path.exists(db_path):
        return db_path
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('CREATE TABLE sample (id INTEGER PRIMARY KEY, value INTEGER, note TEXT)')
    cur.executemany('INSERT INTO sample (id, value, note) VALUES (?, ?, ?)', [(i, i*10, f'Row {i}') for i in range(1, 11)])
    conn.commit()
    conn.close()
    return db_path


def export_dataframe_to_s3_stub(df: pd.DataFrame, export_name: str) -> str:
    # For safety, a 'stub' implementation writes to local 'exports' instead of real S3.
    path = os.path.join(EXPORTS_DIR, f'{export_name}.csv')
    df.to_csv(path, index=False)
    logger.info('Exported dataframe to local exports folder as a S3 stub: %s', path)
    return path


def send_email_stub(to: str, subject: str, body: str) -> bool:
    # Do not send real emails from sample code. Instead, write to export file for auditing.
    safe_to = to.replace('@', '_').replace('/', '_') if to else 'unknown'
    path = os.path.join(EXPORTS_DIR, f'email_{safe_to}_{int(time.time())}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'to': to, 'subject': subject, 'body': body}, f, indent=2)
    logger.info('Email stub wrote message to %s', path)
    return True


def run_command_action(command: str) -> dict:
    # Validate and run command via the executor
    return run_safe_command(command)


def summarize_data(file_name: str, output_name: Optional[str] = None) -> List[dict]:
    path = os.path.join(RESOURCES_DIR, file_name)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    df = pd.read_excel(path)
    numeric_columns = df.select_dtypes(include=['number']).columns
    results = []
    for col in numeric_columns:
        column_data = df[col].dropna()
        results.append({'column': col, 'mean': float(column_data.mean()), 'sum': float(column_data.sum()), 'count': int(len(column_data))})
    if output_name:
        out_path = os.path.join(EXPORTS_DIR, output_name)
        pd.DataFrame(results).to_excel(out_path, index=False)
    return results
