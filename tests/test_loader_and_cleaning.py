import sys
from pathlib import Path

import pandas as pd
import pytest

# Ensure local src/ is importable during tests
sys.path.insert(0, str(Path.cwd() / "src"))

from auto_cleaner_pro.cleaning import load_csv_auto, clean_dataframe, clean_column_name


def test_load_and_header_promotion():
    # examples/test_messy.csv was created earlier in examples/
    p = Path("examples/test_messy.csv")
    assert p.exists(), "examples/test_messy.csv must exist for tests"

    df, meta = load_csv_auto(str(p))
    # We expect header promotion to have happened on that sample
    assert isinstance(meta, dict)
    assert "header_promoted" in meta
    # header_promoted should be True for our test_messy sample
    assert meta["header_promoted"] is True

    # basic sanity of dataframe shape (4 rows in examples/test_messy.csv after header)
    assert df.shape[0] == 4


def test_clean_column_names_and_clean_dataframe():
    # quick unit-test for name cleaning
    assert clean_column_name(" AGE (Years) ") == "age_years"
    assert clean_column_name(" 123start") == "_123start"
    # run a full cleaning on the sample and inspect results
    p = Path("examples/test_messy.csv")
    df, meta = load_csv_auto(str(p))
    cleaned, report = clean_dataframe(df)
    # check cleaned columns are normalized and present in report
    assert all(isinstance(c, str) for c in report["columns_after"])
    # age column should be cast to numeric in the sample
    assert "age_years" in report["dtypes"]
    assert "active" in report["dtypes"]