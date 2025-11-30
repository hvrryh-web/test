# Excel Resources

This repository includes scripts and templates for Excel-based resources your AI agent can use during tasks.

- `resources/generate_sample_xlsx.py` - Create `sample_tasks.xlsx` and `sample_data.xlsx` in `resources/`.
- `resources/sample_tasks.xlsx` (generated) - A spreadsheet of tasks for the agent: columns `task_id`, `description`, `status`, `due_date`.
- `resources/sample_data.xlsx` (generated) - Sample dataset the agent may process.

Agent code uses `pandas` and `openpyxl` to read and write Excel files. If the agent needs to update tasks, the harness writes to an updated file: `sample_tasks.xlsx.updated` to avoid overwriting the original.

Agent design tips:
- When reading sensitive credentials from spreadsheets, prefer to keep them in a separate `credentials.xlsx` and use encryption or OS-level secrets.
- For large datasets, prefer CSV or Parquet for speed and streaming support.
