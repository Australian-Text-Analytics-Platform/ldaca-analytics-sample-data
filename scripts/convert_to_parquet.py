"""Rebuild Parquet corpora from the last CSV/ZIP revision. Requires pyarrow==23.0.1."""
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

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

with zipfile.ZipFile(io.BytesIO(original('SCL/Honi_Soit.zip'))) as archive:
    rows = []
    for filename in sorted(archive.namelist()):
        path = PurePosixPath(filename)
        if path.suffix == '.txt':
            rows.append(dict(file_path=filename, base_name=path.stem, extension=path.suffix,
                             document=archive.read(filename).decode('utf-8')))
    assert len(rows) == 100
    write('SCL/Honi_Soit.parquet', pa.Table.from_pylist(rows))

catalogue_path = ROOT / 'catalogue.json'
catalogue = json.loads(catalogue_path.read_text())
for collection in catalogue['collections']:
    for entry in collection['files']:
        entry['path'] = entry['path'].replace('.csv', '.parquet').replace('.zip', '.parquet')
        content = (ROOT / entry['path']).read_bytes()
        entry.update(size_bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
    collection['total_size_bytes'] = sum(entry['size_bytes'] for entry in collection['files'])
catalogue_path.write_text(json.dumps(catalogue, indent=2) + '\n')
