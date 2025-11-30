#!/usr/bin/env python3
"""
Configure structured JSON logging and optional HTTP sink.
"""
import logging
import os
from pythonjsonlogger import jsonlogger


def configure_logging(log_file: str = None, level: str = 'INFO'):
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if log_file:
        # Ensure the directory exists for the log file
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception:
                pass
        try:
            fh = logging.FileHandler(log_file)
        except Exception:
            # Fallback to workspace-local log path
            local_log = os.path.join(os.getcwd(), 'agent', 'agent.log')
            os.makedirs(os.path.dirname(local_log), exist_ok=True)
            fh = logging.FileHandler(local_log)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # Optional: HTTP destination via environment variable
    http_url = os.environ.get('LOG_HTTP_DEST')
    if http_url:
        try:
            import requests

            class HTTPHandler(logging.Handler):
                def emit(self, record):
                    payload = formatter.format(record)
                    try:
                        requests.post(http_url, json={'log': payload}, timeout=1)
                    except Exception:
                        pass

            hh = HTTPHandler()
            hh.setLevel(getattr(logging, level.upper(), logging.INFO))
            logger.addHandler(hh)
        except Exception:
            pass
