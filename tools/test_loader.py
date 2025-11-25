import sys
from pathlib import Path

# make sure our local src package is importable
sys.path.insert(0, str(Path.cwd() / 'src'))

from auto_cleaner_pro.cleaning import load_csv_auto

# create a small example CSV (mixed simple data)
example_path = Path('examples/test_sample.csv')
example_path.parent.mkdir(parents=True, exist_ok=True)
example_path.write_text('Name, Age, Note\nAlice,30,hello\nBob,25,world\n', encoding='utf-8')

df, meta = load_csv_auto(str(example_path))
print('META:', meta)
print('\\nHEAD:')
print(df.head().to_string(index=False))
