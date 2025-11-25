from pathlib import Path
import sys

# ensure local src/ is importable
sys.path.insert(0, str(Path.cwd() / "src"))

# Import the run function directly
from auto_cleaner_pro.pipeline import run as pipeline_run

# Prepare arguments
input_path = Path("examples/test_messy.csv")
output_path = Path("examples/cleaned_from_cli.csv")
config_path = None  # or Path("path/to/config.json")

# Call the pipeline runner directly (bypass Typer CLI parsing)
pipeline_run(input_path=input_path, output_path=output_path, config=config_path, dry_run=False, report_only=False)
