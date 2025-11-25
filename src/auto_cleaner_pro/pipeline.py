import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import typer
import pandas as pd

from .cleaning import load_csv_auto, clean_dataframe

app = typer.Typer(add_completion=False)
logger = logging.getLogger(__name__)


def _load_config(path: Optional[Path]) -> Optional[Dict[str, Any]]:
    if path is None:
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise typer.Exit(f"Failed to read config file {path}: {e}")


@app.command()
def run(
    input_path: Path = typer.Argument(..., help="Input CSV file"),
    output_path: Path = typer.Argument(..., help="Where cleaned CSV will be written"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Optional JSON config file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not write output files"),
    report_only: bool = typer.Option(False, "--report-only", help="Write only JSON report"),
):
    """Run the auto-cleaner pipeline."""

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info(f"Loading: {input_path}")

    cfg = _load_config(config)

    try:
        df, meta = load_csv_auto(str(input_path))
    except Exception as e:
        raise typer.Exit(f"Failed to load CSV: {e}")

    logger.info(
        f"Detected: encoding={meta.get('encoding')}, "
        f"delimiter={meta.get('delimiter')}, "
        f"header_promoted={meta.get('header_promoted')}"
    )

    cleaned, report = clean_dataframe(df, config=cfg)
    combined = {"meta": meta, "report": report}

    logger.info(f"Rows before: {meta['shape'][0]}, after: {report['shape_after'][0]}")
    logger.info(f"Columns before: {len(report['columns_before'])}, after: {len(report['columns_after'])}")

    if dry_run:
        print(json.dumps(combined, indent=2, default=str))
        raise typer.Exit()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path = output_path.with_suffix(output_path.suffix + ".report.json")

    if not report_only:
        try:
            cleaned.to_csv(output_path, index=False)
            logger.info(f"Wrote cleaned CSV: {output_path}")
        except Exception as e:
            raise typer.Exit(f"Could not write cleaned CSV: {e}")

    try:
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2, default=str)
        logger.info(f"Wrote report: {report_path}")
    except Exception as e:
        raise typer.Exit(f"Could not write report: {e}")

    print(json.dumps(combined, indent=2, default=str))
