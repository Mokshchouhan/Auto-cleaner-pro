import io
import csv
import re
from typing import Tuple, Dict, Any, Optional, List

import chardet
import pandas as pd
from dateutil import parser as dateutil_parser


def detect_encoding(path: str, n_bytes: int = 65536) -> str:
    """Read the first 
    _bytes of a file and use chardet to guess encoding."""
    with open(path, "rb") as f:
        raw = f.read(n_bytes)
    guess = chardet.detect(raw)
    return guess.get("encoding", "utf-8")


def detect_delimiter(sample_text: str, fallback: str = ",") -> str:
    
    common_delimiters = {",", ";", "\t", "|", ":"}

    try:
        dialect = csv.Sniffer().sniff(sample_text)
        d = dialect.delimiter

        # accept only real CSV delimiters
        if d in common_delimiters:
            return d
        else:
            return fallback
    except Exception:
        return fallback


def _has_header(sample_text: str) -> bool:
    """Heuristic: ask csv.Sniffer if a header exists (may be wrong on small samples)."""
    try:
        return csv.Sniffer().has_header(sample_text)
    except Exception:
        return True  # assume header by default


def _looks_like_header_row(series: pd.Series) -> bool:
    """Simple heuristic: return True when the row values contain many alphabetic tokens (likely header)."""
    count_letters = sum(1 for v in series.astype(str).str.strip() if re.search(r"[A-Za-z]", v))
    count_nonempty = sum(1 for v in series.astype(str).str.strip() if v != "")
    if count_nonempty == 0:
        return False
    return count_letters >= max(1, count_nonempty // 2)


def load_csv_auto(path: str, sample_bytes: int = 65536, **read_csv_kwargs) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    # Load any CSV file with automatic detection.
    encoding = detect_encoding(path, n_bytes=sample_bytes)

    with open(path, "rb") as f:
        sample_raw = f.read(sample_bytes)
    try:
        sample_text = sample_raw.decode(encoding, errors="replace")
    except Exception:
        sample_text = sample_raw.decode("utf-8", errors="replace")

    delimiter = detect_delimiter(sample_text)
    header_detected = _has_header(sample_text)

    read_opts = dict(encoding=encoding, sep=delimiter)
    read_opts.update(read_csv_kwargs)

    try:
        header = 0 if header_detected else None
        df = pd.read_csv(path, header=header, **read_opts)
    except Exception:
        try:
            df = pd.read_csv(path, header=header, encoding=encoding, sep=",", engine="python", **read_csv_kwargs)
        except Exception:
            df = pd.read_csv(path, header=None, encoding=encoding, engine="python", **read_csv_kwargs)
            df.columns = [f"column_{i}" for i in range(df.shape[1])]

    header_promoted = False
    if header_detected is False:
        try:
            first_row = df.iloc[0]
            if _looks_like_header_row(first_row):
                new_cols = [str(x).strip() for x in first_row.tolist()]
                df = df.iloc[1:].reset_index(drop=True)
                df.columns = new_cols
                header_promoted = True
        except Exception:
            header_promoted = False

    meta = {
        "encoding": encoding,
        "delimiter": delimiter,
        "header_detected": header_detected,
        "header_promoted": header_promoted,
        "shape": df.shape,
    }
    return df, meta


def clean_column_name(name: str) -> str:   
    if name is None:
        return "column"
    s = str(name).strip()
    s = s.lower()
    s = re.sub(r"[^0-9a-zA-Z\.]+", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.rstrip("_")
    if re.match(r"^[0-9]", s):
        s = "_" + s
    s = s.strip()
    if s == "":
        return "column"
    return s



def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Apply clean_column_name to all columns and ensure uniqueness by appending counters."""
    new_cols: List[str] = []
    seen: Dict[str, int] = {}
    for orig in df.columns:
        cleaned = clean_column_name(orig)
        if cleaned in seen:
            seen[cleaned] += 1
            cleaned = f"{cleaned}_{seen[cleaned]}"
        else:
            seen[cleaned] = 0
        new_cols.append(cleaned)
    df = df.copy()
    df.columns = new_cols
    return df


def _try_formats(series: pd.Series, formats: List[str]) -> Optional[pd.Series]:
    """Try each format in Formats using pandas.to_datetime(format=...) and return the best Series if one format converts a decent fraction."""
    best_series = None
    best_score = 0.0
    nonempty = series.dropna().astype(str).str.strip()
    total = len(nonempty)
    if total == 0:
        return None
    for fmt in formats:
        try:
            parsed = pd.to_datetime(nonempty, format=fmt, errors="coerce")
            success = parsed.notna().sum()
            score = success / total
            if score > best_score:
                best_score = score
                # reindex to full original series index, inserting NaT for missing values
                full_parsed = pd.Series([pd.NaT] * len(series), index=series.index, dtype="datetime64[ns]")
                full_parsed[nonempty.index] = parsed
                best_series = full_parsed
        except Exception:
            continue
    # accept if at least half parsed
    if best_score >= 0.5:
        return best_series
    return None


def _try_dateutil(series: pd.Series) -> Optional[pd.Series]:
   # Try parsing with dateutil.parser.parse using dayfirst heuristics and pick the best option.
    nonempty = series.dropna().astype(str).str.strip()
    total = len(nonempty)
    if total == 0:
        return None

    best_series = None
    best_score = 0.0
    for dayfirst in (False, True):
        parsed_list = []
        success = 0
        for v in nonempty:
            try:
                dt = dateutil_parser.parse(v, dayfirst=dayfirst)
                parsed_list.append(dt)
                success += 1
            except Exception:
                parsed_list.append(pd.NaT)
        score = success / total
        if score > best_score:
            best_score = score
            # build full Series aligned to original index
            full = pd.Series([pd.NaT] * len(series), index=series.index, dtype="datetime64[ns]")
            full[nonempty.index] = pd.to_datetime(pd.Series(parsed_list, index=nonempty.index), errors="coerce")
            best_series = full
    if best_score >= 0.5:
        return best_series
    return None


def try_cast_datetime(series: pd.Series, date_formats: Optional[List[str]] = None) -> pd.Series:
    # Attempt to parse datetimes with optional user formats and dateutil fallback.
    # 1) user-provided formats
    if date_formats:
        fmt_series = _try_formats(series, date_formats)
        if fmt_series is not None:
            return fmt_series

    # 2) try pandas generic parsing
    try:
        parsed = pd.to_datetime(series, errors="coerce")
        non_null = parsed.notna().sum()
        total = len(series.dropna())
        if total > 0 and (non_null / total) >= 0.5:
            return parsed
    except Exception:
        pass

    # 3) dateutil fallback (try dayfirst heuristics)
    du = _try_dateutil(series)
    if du is not None:
        return du

    # 4) give up and return original
    return series


# ---------------------------
# Numeric and boolean casting (unchanged)
# ---------------------------

def try_cast_numeric(series: pd.Series) -> pd.Series:
    #Attempt to convert to numeric where it makes sense; otherwise return original series.
    converted = pd.to_numeric(series, errors="coerce")
    non_null = converted.notna().sum()
    total = len(series.dropna())
    if total == 0:
        return series
    if non_null / total >= 0.5:
        return converted
    return series


def try_cast_bool(series: pd.Series) -> pd.Series:
    #Try to interpret common boolean-like strings (true/false, yes/no, 0/1)
    low = series.dropna().astype(str).str.strip().str.lower()
    if low.empty:
        return series
    true_set = {"true", "t", "yes", "y", "1", "on"}
    false_set = {"false", "f", "no", "n", "0", "off"}
    mapped = low.map(lambda s: True if s in true_set else (False if s in false_set else None))
    non_null = mapped.notna().sum()
    total = len(low)
    if total == 0:
        return series
    if non_null / total >= 0.8:
        out = mapped.reindex(series.index)
        return out.astype("boolean")
    return series


def infer_and_cast_dtypes(df: pd.DataFrame, sample_frac: float = 1.0, config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    #For each column, attempt boolean -> numeric -> datetime casting using heuristics.
    df = df.copy()
    if 0 < sample_frac < 1.0:
        sample = df.sample(frac=sample_frac, random_state=0)
    else:
        sample = df

    date_formats = None
    if config and isinstance(config, dict):
        date_formats = config.get("date_formats")

    for col in df.columns:
        try:
            series = df[col]
            # boolean
            b = try_cast_bool(sample[col])
            if not b.equals(sample[col]):
                df[col] = try_cast_bool(series)
                continue

            # numeric
            num = try_cast_numeric(sample[col])
            if not num.equals(sample[col]):
                df[col] = try_cast_numeric(series)
                continue

            # datetime (now honors config)
            dt = try_cast_datetime(sample[col], date_formats=date_formats)
            if not dt.equals(sample[col]):
                df[col] = try_cast_datetime(series, date_formats=date_formats)
                continue
        except Exception:
            continue
    return df


def clean_dataframe(df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    # Run a sequence of cleaning steps and produce a simple report.

    report: Dict[str, Any] = {}
    before_cols = list(df.columns)
    before_shape = df.shape

    df = clean_column_names(df)
    report["columns_before"] = before_cols
    report["columns_after"] = list(df.columns)

    df = infer_and_cast_dtypes(df, config=config)
    after_shape = df.shape
    report["shape_before"] = before_shape
    report["shape_after"] = after_shape

    report["dtypes"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
    return df, report