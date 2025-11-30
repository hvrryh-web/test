#!/usr/bin/env python3
"""
Generate sample Excel files for agent demonstration.
Run: python generate_sample_xlsx.py

It writes files to the same directory:
- sample_tasks.xlsx: a tasks spreadsheet with columns task_id, description, status, due_date
- sample_data.xlsx: a dataset spreadsheet with sample rows
"""

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent


def generate_tasks(path: Path):
    rows = []
    today = datetime.today()
    for i in range(1, 6):
        rows.append({
            "task_id": f"T{i:03}",
            "description": f"Sample task {i}: process sample data {i}",
            "status": "pending",
            "due_date": (today + timedelta(days=i)).date(),
        })
    # Add a summarize task to show an example of a more complex agent action
    rows.append({
        "task_id": "T999",
        "description": "Summarize sample_data.xlsx",
        "status": "pending",
        "due_date": (today + timedelta(days=7)).date(),
    })
    # Add db query example
    rows.append({
        "task_id": "T998",
        "description": "DB_QUERY: SELECT * FROM sample",
        "status": "pending",
        "due_date": (today + timedelta(days=3)).date(),
    })
    # Add an export CSV example
    rows.append({
        "task_id": "T997",
        "description": "EXPORT_CSV: export sample_data",
        "status": "pending",
        "due_date": (today + timedelta(days=4)).date(),
    })
    # Add send email example (stub)
    rows.append({
        "task_id": "T996",
        "description": "SEND_EMAIL:to=example@example.com;subject=Report;body=Hello",
        "status": "pending",
        "due_date": (today + timedelta(days=2)).date(),
    })
    # Parquet export task and S3 upload task (S3 will use dynamic credentials if present)
    rows.append({
        "task_id": "T995",
        "description": "EXPORT_PARQUET: sample_data",
        "status": "pending",
        "due_date": (today + timedelta(days=8)).date(),
    })
    rows.append({
        "task_id": "T994",
        "description": "S3_UPLOAD: sample_data.parquet",
        "status": "pending",
        "due_date": (today + timedelta(days=9)).date(),
    })
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)
    print(f"Wrote {path}")


def generate_data(path: Path):
    rows = []
    for i in range(1, 11):
        rows.append({
            "id": i,
            "value": i * 10,
            "note": f"Row {i} sample",
        })
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)
    # Write parquet version for export and streaming examples
    try:
        df.to_parquet(path.with_suffix('.parquet'), index=False)
        print(f"Wrote {path.with_suffix('.parquet')}")
    except Exception:
        pass
    print(f"Wrote {path}")


def generate_credentials(path: Path):
    # Template only — don't store real secrets in the repository
    rows = [
        {"name": "example_service", "api_key": "REPLACE_ME", "api_secret": "REPLACE_ME"}
    ]
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)
    print(f"Wrote {path}")


if __name__ == "__main__":
    generate_tasks(BASE_DIR / "sample_tasks.xlsx")
    generate_data(BASE_DIR / "sample_data.xlsx")
    # Instead of creating a credentials file with secrets in the repo, generate only a template
    generate_credentials(BASE_DIR / "credentials_template.xlsx")
