import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path.cwd() / 'src'))
from auto_cleaner_pro.cleaning import load_csv_auto, clean_dataframe

# Create a messy CSV with weird column names and mixed types

example_path = Path('examples/test_messy.csv')
example_path.parent.mkdir(parents=True, exist_ok=True)
csv_text = '''  Name , AGE (Years), joined_at , Active?
Alice , 30 , 2020-01-05 , yes
Bob,25,01/06/2021,No
Charlie, , March 3 2022,TRUE
Daisy, 42, , false
'''
example_path.write_text(csv_text, encoding='utf-8')

df, meta = load_csv_auto(str(example_path))
print('--- LOAD META ---')
print(meta)
print('\\n--- RAW DF ---')
print(df.to_string(index=False))

cleaned, report = clean_dataframe(df)
print('\\n--- CLEANED DF ---')
print(cleaned.to_string(index=False))
print('\\n--- REPORT ---')
import json
print(json.dumps(report, indent=2))
