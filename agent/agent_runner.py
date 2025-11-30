#!/usr/bin/env python3
"""
Simple agent harness that reads tasks from an Excel spreadsheet and executes sample actions.
This is a minimal, safe harness to show the agent how to interact with local resources.

Usage:
  python agent_runner.py --process-tasks
  python agent_runner.py --watch

"""

import argparse
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List

import pandas as pd

# Make sure relative imports work even when invoked as a script
if __package__ is None:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    __package__ = 'agent'

from . import tasks as agent_tasks
from . import actions as agent_actions
from . import executor as agent_executor
from . import logging_config
<<<<<<< Updated upstream
from .metrics_server import start_metrics
=======
from .metrics_server import start_metrics, TASK_COUNTER, TASK_ERRORS
>>>>>>> Stashed changes
from .vault_client import VaultClient

CONFIG_PATH = os.getenv("AGENT_CONFIG_PATH") or os.path.join(os.path.dirname(__file__), "agent_config.json")


@dataclass
class Task:
    task_id: str
    description: str
    status: str
    due_date: datetime | None = None


def load_config(path: str = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_tasks(file_path: str) -> List[Task]:
    df = pd.read_excel(file_path)
    tasks: List[Task] = []
    for _, row in df.iterrows():
        due = None
        if not pd.isna(row.get("due_date")):
            try:
                due = pd.to_datetime(row["due_date"]) if not pd.isna(row["due_date"]) else None
            except Exception:
                due = None

        tasks.append(
            Task(
                task_id=str(row.get("task_id")),
                description=str(row.get("description")),
                status=str(row.get("status")) if not pd.isna(row.get("status")) else "pending",
                due_date=due,
            )
        )
    return tasks


def process_task(task: Task) -> str:
    """
    Mock processing logic. Replace with actual task execution steps the agent must perform.
    For security, the harness runs only safe, local actions.

    Returns updated status.
    """
    # Safe sample action: mark the task as completed if description contains 'sample'
    desc = task.description.lower() if task.description else ""
    if "sample" in desc:
        return "completed"
    # If the task indicates summarize, run a sample summarize
    if "summarize" in desc:
        try:
            # Look up the sample data path relative to the config; the runner manages the file paths
            # This is a safe demonstration; in a real agent, validate the paths carefully
            data_path = os.path.join(os.path.dirname(__file__), "..", "resources", "sample_data.xlsx")
            data_path = os.path.abspath(data_path)
            results = agent_tasks.summarize_data(data_path)
            out_path = os.path.join(os.path.dirname(__file__), "..", "resources", "summary.xlsx")
            agent_tasks.write_summary(out_path, results)
            return "completed"
        except Exception:
            return "failed"
    # Extended actions: db_query, export, s3_export, email, run_command
    try:
        if "db_query:" in desc:
            query = task.description.split(':', 1)[1].strip()
            db_path = agent_actions.ensure_sample_db()
            res = agent_actions.db_query(query, db_path)
            df = pd.DataFrame(res.rows, columns=res.columns)
            outdir = os.path.join(os.path.dirname(__file__), "..", "exports")
            os.makedirs(outdir, exist_ok=True)
            outpath = os.path.join(outdir, f"db_query_{task.task_id}.csv")
            df.to_csv(outpath, index=False)
            return "completed"
        if "export_parquet" in desc or "export_csv" in desc:
            file_name = 'sample_data.xlsx'
            df = pd.read_excel(os.path.join(os.path.dirname(__file__), '..', 'resources', file_name))
            outpath = agent_actions.export_dataframe_to_s3_stub(df, f'export_{task.task_id}')
            return "completed"
        if "send_email" in desc:
            parts = task.description.split(':', 1)[1]
            params = dict([p.split('=') for p in parts.split(';') if '=' in p])
            to = params.get('to')
            subject = params.get('subject', 'No Subject')
            body = params.get('body', '')
            # Validate email action via policy
            out = agent_actions.send_email_stub(to, subject, body)
            return 'completed' if out else 'failed'
        if "run_command:" in desc:
            cmd = task.description.split(':', 1)[1].strip()
            out = agent_executor.run_safe_command(cmd)
            logging.info('Command output: %s', out)
            return 'completed' if out.get('status') == 'ok' else 'failed'
    except Exception as e:
        logging.exception('Failed to process task %s: %s', task.task_id, e)
        return 'failed'

    return 'in-progress'


def write_tasks(file_path: str, tasks: List[Task]):
    df = pd.DataFrame(
        [{
            "task_id": t.task_id,
            "description": t.description,
            "status": t.status,
            "due_date": t.due_date,
        } for t in tasks]
    )
    # Save to a new file to avoid accidental overwrite
    backup_path = file_path + ".updated"
    df.to_excel(backup_path, index=False)
    logging.info("Wrote updated tasks to %s", backup_path)


def process_tasks_file(config):
    tasks_path = os.path.join(config["data_dir"], config["tasks_file"])
    logging.info("Reading tasks from %s", tasks_path)
    tasks = read_tasks(tasks_path)

    for t in tasks:
        new_status = process_task(t)
<<<<<<< Updated upstream
=======
        try:
            TASK_COUNTER.inc()
            if new_status == 'failed':
                TASK_ERRORS.inc()
        except Exception:
            pass
>>>>>>> Stashed changes
        logging.info("Task %s: %s -> %s", t.task_id, t.status, new_status)
        t.status = new_status

    write_tasks(tasks_path, tasks)


def run_watch(config):
    tasks_path = os.path.join(config["data_dir"], config["tasks_file"])
    logging.info("Watching tasks file: %s", tasks_path)
    last_mod = None
    while True:
        try:
            mod = os.path.getmtime(tasks_path)
            if last_mod is None or mod > last_mod:
                logging.info("Detected change. Processing tasks...")
                process_tasks_file(config)
                last_mod = mod
        except Exception as e:
            logging.error("Error monitoring tasks: %s", e)
        time.sleep(5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--process-tasks", action="store_true")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()

    cfg = load_config()

    log_file = cfg.get("log_file") or os.path.join(os.path.dirname(__file__), "agent.log")
    log_file = os.getenv("AGENT_LOG_FILE") or log_file
    logging_config.configure_logging(log_file, level=cfg.get('log_level', 'INFO'))

    # Start metrics server for monitoring
    start_metrics(cfg.get('metrics_port', 8000))
    # Vault: optional fetch of secret keys for configuration (do not log secret values)
    try:
        vault_cfg = cfg.get('vault') or {}
        vc = VaultClient(vault_addr=vault_cfg.get('addr'))
        secrets_path = vault_cfg.get('secrets_path')
        if secrets_path:
            data = vc.get_raw_secret(secrets_path)
            logging.info('Vault secrets keys available: %s', list(data.keys()))
    except Exception:
        logging.info('Vault not configured or unreachable; using environment fallbacks')

    if args.process_tasks:
        process_tasks_file(cfg)
    elif args.watch:
        run_watch(cfg)
    else:
        print("No action specified. Use --process-tasks or --watch")


if __name__ == "__main__":
    main()
