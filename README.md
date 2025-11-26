# auto-cleaner-pro

<p align="left">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" />
  <img src="https://img.shields.io/github/license/Mokshchouhan/Auto-cleaner-pro" />
  <img src="https://img.shields.io/github/repo-size/Mokshchouhan/Auto-cleaner-pro" />
  <img src="https://img.shields.io/github/stars/Mokshchouhan/Auto-cleaner-pro?style=social" />
  <img src="https://github.com/Mokshchouhan/Auto-cleaner-pro/actions/workflows/ci.yml/badge.svg" alt="CI" />
</p>


**auto-cleaner-pro** — a general-purpose, robust, reusable CSV cleaning pipeline that works with *any* CSV file.  
This project provides a safe default pipeline to detect CSV format, normalize column names, infer and cast data types, and produce a human + machine readable report.

---

## 🚀 Features
- Automatic **encoding detection** (chardet)
- Automatic **delimiter detection** (csv.Sniffer)
- **Header detection & promotion** (turns first row into header if needed)
- Column name cleaning (`Name` → `name`, `AGE (Years)` → `age_years`)
- Smart **dtype inference**:
  - boolean (`yes/no`, `true/false`, `0/1`)
  - numbers (int, float)
  - dates (ISO, dd/mm/YYYY, long format, etc.)
- Generates both:
  - Cleaned CSV
  - JSON report with detailed info
- Command-line interface (`acp`)
- Notebook-friendly API

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

2. Install dependencies
pip install -r requirements.txt

3. Install Auto Cleaner Pro in editable mode

This makes the acp command available:

pip install -e .


You can now run:

acp --help

🧼 CLI Usage
Basic usage
acp input.csv output.csv

With a config file
acp input.csv output.csv --config my_config.json

Dry run (no files written)
acp input.csv output.csv --dry-run

Report only
acp input.csv output.csv --report-only

📝 Example

Input file: examples/test_messy.csv

acp examples/test_messy.csv examples/cleaned.csv


Output:

Loading: examples/test_messy.csv
Detected: encoding=ascii, delimiter=,, header_promoted=True
Rows before: 4, after: 4
Columns before: 4, after: 4
Wrote cleaned CSV: examples/cleaned.csv
Wrote report: examples/cleaned.csv.report.json


Cleaned CSV example:

name	age_years	joined_at	active
Alice	30	2020-01-05	True
Bob	25	2021-01-06	False
Charlie	NaN	2022-03-03	True
Daisy	42	NaT	False
📘 Python API Usage (in code or notebooks)
from auto_cleaner_pro.cleaning import load_csv_auto, clean_dataframe

df, meta = load_csv_auto("examples/test_messy.csv")
cleaned, report = clean_dataframe(df)

print(report)
print(cleaned.head())


In Jupyter Notebook, add this before imports:

import sys, os
sys.path.append(os.path.abspath(".."))  # or the project root path

📂 Project Structure
auto-cleaner-pro/
│
├── src/auto_cleaner_pro/
│   ├── cleaning.py       # core cleaning logic
│   ├── pipeline.py       # CLI entry point
│
├── tools/                # test helpers / scripts
├── tests/                # pytest test suite
├── examples/             # sample data
├── notebooks/            # Jupyter notebooks
│
├── pyproject.toml        # package metadata + entry point
├── requirements.txt
├── README.md

🧪 Testing

Run all tests:

pytest -q

🤝 Contributing

Pull requests are welcome.
For major changes, please open an issue first to discuss.