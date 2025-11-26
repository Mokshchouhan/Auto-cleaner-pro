from pathlib import Path
import json
import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys

sys.path.insert(0, str(Path.cwd() / "src"))
from auto_cleaner_pro.cleaning import load_csv_auto, clean_dataframe
st.set_page_config(page_title="Auto Cleaner Pro", layout="wide")
st.title("Auto Cleaner Pro — CSV Cleaner")
st.markdown(
    "Upload a CSV or pick an example, press **Clean**, inspect results, and download cleaned CSV + report."
)
st.sidebar.header("Input")
uploaded = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
use_example = st.sidebar.checkbox("Use example CSV (test_messy)", value=False)
st.sidebar.markdown("---")
st.sidebar.header("Options")
dry_run = st.sidebar.checkbox("Dry run (no files written)", value=False)
report_only = st.sidebar.checkbox("Report only (don't write cleaned CSV)", value=False)
example_path = Path("examples") / "test_messy.csv"
input_source = None
input_bytes = None

if uploaded is not None:
    input_source = "uploaded"
    input_bytes = uploaded.read()
elif use_example:
    if example_path.exists():
        input_source = "example"
        input_bytes = example_path.read_bytes()
    else:
        st.sidebar.error("Example file not found in examples/test_messy.csv")

if st.button("Clean"):

    if input_source is None:
        st.warning("Choose a file (upload) or enable the example checkbox in the sidebar.")
    else:
        st.info("Running cleaning pipeline...")

        tmp_dir = Path(".streamlit_tmp")
        tmp_dir.mkdir(exist_ok=True)
        tmp_file = tmp_dir / "uploaded.csv"
        tmp_file.write_bytes(input_bytes)

        df_raw, meta = load_csv_auto(str(tmp_file))

        cleaned_df, report = clean_dataframe(df_raw)

        st.subheader("Detected file metadata")
        st.json(meta)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Raw (head)")
            st.dataframe(df_raw.head(200))  
        with col2:
            st.subheader("Cleaned (head)")
            st.dataframe(cleaned_df.head(200))

        st.subheader("Dtype report (cleaned)")
        dtypes = {k: str(v) for k, v in cleaned_df.dtypes.items()}
        st.json(dtypes)

        st.subheader("Missingness heatmap")
        try:
            mask = cleaned_df.isna()
            fig, ax = plt.subplots(figsize=(8, max(3, len(cleaned_df) * 0.15)))
            ax.imshow(mask.T, aspect="auto", interpolation="nearest")
            ax.set_yticks(range(len(mask.columns)))
            ax.set_yticklabels(mask.columns)
            ax.set_xlabel("rows")
            st.pyplot(fig)
        except Exception as e:
            st.write("Could not render missingness heatmap:", e)

        csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
        json_bytes = json.dumps({"meta": meta, "report": report}, default=str, indent=2).encode("utf-8")

        st.download_button("Download cleaned CSV", data=csv_bytes, file_name="cleaned.csv", mime="text/csv")
        st.download_button("Download report JSON", data=json_bytes, file_name="report.json", mime="application/json")

        if not dry_run and not report_only:
            out_csv = Path("examples") / "ui_cleaned.csv"
            out_report = Path("examples") / "ui_cleaned.report.json"
            out_csv.write_bytes(csv_bytes)
            out_report.write_bytes(json_bytes)
            st.success(f"Wrote cleaned CSV: {out_csv} and report: {out_report}")

        elif not dry_run and report_only:
            out_report = Path("examples") / "ui_cleaned.report.json"
            out_report.write_bytes(json_bytes)
            st.success(f"Wrote report: {out_report}")

st.markdown("---")
