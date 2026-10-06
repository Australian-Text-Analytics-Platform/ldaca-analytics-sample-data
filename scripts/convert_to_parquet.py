"""Rebuild the Queensland election Parquet tables from the last CSV revision. Requires pyarrow==23.0.1.

Honi Soit stays a ZIP of text files: it demonstrates archive loading in the Data Loader.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '17fce77'


def original(path):
    return subprocess.check_output(['git', 'show', f'{SOURCE}:{path}'], cwd=ROOT)


def write(path, table):
    pq.write_table(table, ROOT / path, compression='zstd', row_group_size=10000)
    assert pq.read_table(ROOT / path).equals(table)
    print(f'{path}: {table.num_rows} rows, {table.num_columns} columns verified')


for stem in ['qldelection2020_candidate_tweets', 'candidate_info_gender']:
    source = f'ADO/twitter/{stem}.csv'
    rows = list(csv.DictReader(io.StringIO(original(source).decode('utf-8'))))
    # IDs are exact nullable integers. Other CSV fields retain their original text,
    # including empty strings and timestamp formatting.
    fields = {key: pa.array([int(row[key]) if row[key] else None for row in rows], type=pa.int64())
              if key.endswith('_id') else pa.array([row[key] for row in rows], type=pa.string())
              for key in rows[0]}
    table = pa.table(fields)
    for before, after in zip(rows, table.to_pylist(), strict=True):
        assert before == {key: '' if value is None else str(value) for key, value in after.items()}
    write(source.replace('.csv', '.parquet'), table)

catalogue_path = ROOT / 'catalogue.json'
catalogue = json.loads(catalogue_path.read_text())
for collection in catalogue['collections']:
    for entry in collection['files']:
        entry['path'] = entry['path'].replace('.csv', '.parquet')
        content = (ROOT / entry['path']).read_bytes()
        # Wordflow's catalogue contract reads `size`; keep `size_bytes` for the
        # DuckDB views. Both must hold the real byte count.
        entry.update(
            size=len(content),
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
        )
    collection['total_size_bytes'] = sum(entry['size_bytes'] for entry in collection['files'])
catalogue_path.write_text(json.dumps(catalogue, indent=2) + '\n')
