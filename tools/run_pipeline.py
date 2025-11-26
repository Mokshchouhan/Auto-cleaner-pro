from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / "src"))
from auto_cleaner_pro.pipeline import run as pipeline_run
input_path = Path("examples/test_messy.csv")
output_path = Path("examples/cleaned_from_cli.csv")
config_path = None  # or Path("path/to/config.json")
pipeline_run(input_path=input_path, output_path=output_path, config=config_path, dry_run=False, report_only=False)
