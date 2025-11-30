#!/usr/bin/env python3
import os
import sys
import json
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.actions import export_dataframe_to_s3_stub, export_dataframe_to_s3
import pandas as pd


def test_export_stub(tmp_path):
    df = pd.DataFrame({'id': [1, 2], 'value': [10, 20]})
    p = export_dataframe_to_s3_stub(df, 'test_export')
    assert os.path.exists(p)


def test_export_boto3_local(tmp_path):
    # If boto3 is not configured (no bucket) the function should fall back to stub.
    df = pd.DataFrame({'id': [1, 2], 'value': [10, 20]})
    path = export_dataframe_to_s3(df, 'test_export_fallback')
    assert path is not None
    # If it returns s3://, the call used boto3; else local path returned
    assert path.startswith('s3://') or os.path.exists(path)


if __name__ == '__main__':
    test_export_stub(None)
    test_export_boto3_local(None)
    print('Action S3 tests passed')
