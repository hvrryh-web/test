#!/usr/bin/env python3
"""
Quick test to validate reading a generated Excel file and processing tasks.
"""
import os
import subprocess
import sys

import pandas as pd

THIS_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath(os.path.join(THIS_DIR, ".."))
RESOURCES_DIR = os.path.join(PROJECT_DIR, "resources")


def test_generate_and_process(tmp_path):
    # Generate sample Excel files
    gen_script = os.path.join(RESOURCES_DIR, "generate_sample_xlsx.py")
    subprocess.run([sys.executable, gen_script], check=True)

    # Run the agent harness as module to ensure package imports work
    agent_script = ['-m', 'agent.agent_runner']
    cfg_path = os.path.join(PROJECT_DIR, "agent", "agent_config.json")
    subprocess.run([sys.executable] + agent_script + ["--process-tasks"], check=True)

    # Verify we created *.updated file
    tasks_path = os.path.join(RESOURCES_DIR, "sample_tasks.xlsx.updated")
    assert os.path.exists(tasks_path), "Updated tasks file not found"

    df = pd.read_excel(tasks_path)
    assert not df.empty
    assert "status" in df.columns
    # Verify summary file exists and includes summary columns
    summary_path = os.path.join(RESOURCES_DIR, "summary.xlsx")
    assert os.path.exists(summary_path), "Summary file not found"
    sum_df = pd.read_excel(summary_path)
    assert set(["column", "mean", "sum", "count"]).issubset(set(sum_df.columns))
    # Verify a DB query result was exported
    exports_dir = os.path.join(PROJECT_DIR, "exports")
    db_query_csv = os.path.join(exports_dir, "db_query_T998.csv")
    assert os.path.exists(db_query_csv), "DB query CSV not found"
    # Verify export CSV stub
    export_csv_found = any(f.startswith('export_T997') for f in os.listdir(exports_dir))
    assert export_csv_found, "Export CSV not found"
    # Verify email stub file
    email_files = [f for f in os.listdir(exports_dir) if f.startswith('email_')]
    assert len(email_files) >= 1, "Email stub not written"


if __name__ == "__main__":
    test_generate_and_process(os.getcwd())
    print("Test completed")
