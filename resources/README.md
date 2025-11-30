# Resources

This folder contains data, templates and tools used by the agent harness.

- `generate_sample_xlsx.py` — Generates `sample_tasks.xlsx`, `sample_data.xlsx` and `credentials_template.xlsx`.
- `sample_tasks.xlsx` — Generated tasks spreadsheet used by the agent harness (the agent writes to `sample_tasks.xlsx.updated`).
- `sample_data.xlsx` — Simple numeric dataset used in examples.
- `credentials_template.xlsx` — A template for storing credentials, do NOT store real secrets in this repository.

Run the generator script to create the sample files:

```
python generate_sample_xlsx.py
```
