import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0, str(Path.cwd() / "src"))

from auto_cleaner_pro.cleaning import load_csv_auto, clean_dataframe, clean_column_name


def test_load_and_header_promotion():
    p = Path("examples/test_messy.csv")
    assert p.exists(), "examples/test_messy.csv must exist for tests"
    df, meta = load_csv_auto(str(p))
    assert isinstance(meta, dict)
    assert "header_promoted" in meta
    assert meta["header_promoted"] is True
    assert df.shape[0] == 4


def test_clean_column_names_and_clean_dataframe():
    assert clean_column_name(" AGE (Years) ") == "age_years"
    assert clean_column_name(" 123start") == "_123start"
    p = Path("examples/test_messy.csv")
    df, meta = load_csv_auto(str(p))
    cleaned, report = clean_dataframe(df)
    assert all(isinstance(c, str) for c in report["columns_after"])
    assert "age_years" in report["dtypes"]
    assert "active" in report["dtypes"]