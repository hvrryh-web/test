#!/usr/bin/env python3
"""
Simple Prometheus metrics server using Flask; run as a thread or separate process.
"""
from prometheus_client import start_http_server, Summary, Counter, Gauge
import logging

REQUEST_TIME = Summary('agent_request_processing_seconds', 'Time spent processing requests')
TASK_COUNTER = Counter('agent_tasks_processed_total', 'Number of tasks processed')
TASK_ERRORS = Counter('agent_tasks_errors_total', 'Number of task errors')


def start_metrics(port: int = 8000):
    try:
        start_http_server(port)
        logging.getLogger(__name__).info('Metrics server started on port %s', port)
    except Exception as e:
        logging.getLogger(__name__).exception('Failed to start metrics server: %s', e)
