# auto-cleaner-pro

**auto-cleaner-pro** — a general-purpose, robust, reusable CSV cleaning pipeline that works with *any* CSV file.  
This project provides a safe default pipeline to detect CSV format, normalize column names, infer and cast data types, and produce a human + machine readable report.

---

## Quick links
- CLI runner: `python -m auto_cleaner_pro.pipeline run <input.csv> <output.csv>`
- Dev helper: `python tools/run_pipeline.py` (calls the pipeline on `examples/test_messy.csv`)
- Tests & tools: `tools/` and `tests/`

---

## Goals
- Work with *any* CSV (unknown delimiter, encoding, header/no-header, messy column names).
- Provide deterministic, repeatable cleaning with a JSON report.
- Allow user customization (date formats, future config options).
- Lightweight and beginner-friendly — easy to extend.

---

## Installation (developer workflow)

1. Create & activate your Conda or venv environment (example with Conda):
```bash
conda create -n auto-cleaner-pro-env python=3.11 -y
conda activate auto-cleaner-pro-env
