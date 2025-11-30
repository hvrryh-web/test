# Sample Agent Task Workflows

These are example tasks an AI agent can be asked to perform when connected to this VM environment.

1. Task: Update task statuses from an Excel sheet
   - Steps: read `resources/sample_tasks.xlsx`, update `status` column, write out `.updated` file.

2. Task: Aggregate data from spreadsheets
   - Steps: read `resources/sample_data.xlsx`, compute summary statistics, write a `summary.xlsx` with results.

3. Task: Export CSV or Parquet files for downstream systems
   - Steps: transform data using pandas, write compressed Parquet files, and move to `exports/`.

4. Task: Respond to a task backlog via the agent harness
   - Steps: agent watches `resources/sample_tasks.xlsx` for changes and runs `agent_runner` to process new entries.

5. Task: Read a list of commands in a spreadsheet, validate them, and execute safe scripts
   - Steps: validate commands against a policy, execute only whitelisted safe scripts in a sandbox, and write results to spreadsheet.

Design guidelines:
- Keep task definitions small and idempotent.
- Avoid arbitrary code execution unless necessary; use whitelists and safe execution mechanisms.
- Use system logs and audit trails.
