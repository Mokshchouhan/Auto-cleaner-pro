import sys
from pathlib import Path
import json
import pandas as pd

sys.path.insert(0, str(Path.cwd() / 'src'))
from auto_cleaner_pro.cleaning import load_csv_auto, clean_dataframe
p = Path('examples/test_dates_mixed.csv')
p.parent.mkdir(parents=True, exist_ok=True)
lines = [
    'date_col',
    '2020-01-05',
    '01/06/2021',
    'March 3 2022',
    '06/07/23',
]
p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('--- RUN without config ---')
df, meta = load_csv_auto(str(p))
print('META:', meta)
cleaned, report = clean_dataframe(df)
print('DTYPES:', report['dtypes'])
print(cleaned.to_string(index=False))

print('\n--- RUN with config (explicit formats) ---')
config = { 'date_formats': ['%Y-%m-%d', '%d/%m/%Y', '%B %d %Y', '%d/%m/%y'] }
df2, meta2 = load_csv_auto(str(p))
cleaned2, report2 = clean_dataframe(df2, config=config)
print('META:', meta2)
print('DTYPES:', report2['dtypes'])
print(cleaned2.to_string(index=False))
