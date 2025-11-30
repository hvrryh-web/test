"""
Agent task helper functions used by `agent_runner.py`.
This file adds some reusable actions for tasks.
"""
from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class SummaryResult:
    column: str
    mean: float
    sum: float
    count: int


def summarize_data(file_path: str, sheet_name: str | None = None) -> List[SummaryResult]:
    # If sheet_name is None, pandas returns a dict of DataFrames; read the default sheet instead
    if sheet_name is None:
        df = pd.read_excel(file_path)
    else:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    results = []
    numeric_columns = df.select_dtypes(include=["number"]).columns
    for col in numeric_columns:
        column_data = df[col].dropna()
        results.append(SummaryResult(column=col, mean=float(column_data.mean()), sum=float(column_data.sum()), count=int(len(column_data))))
    return results


def write_summary(output_path: str, results: List[SummaryResult]):
    import logging
    df = pd.DataFrame([r.__dict__ for r in results])
    df.to_excel(output_path, index=False)
    logging.getLogger(__name__).info('Wrote summary to %s', output_path)

