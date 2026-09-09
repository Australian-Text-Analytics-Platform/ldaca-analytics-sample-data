# Wordflow sample data

`catalogue.json` lists the sample projects and their data files, descriptions,
byte sizes, and SHA-256 checksums. All catalogue data files are Parquet; collection
READMEs retain provenance and citation information.

- Queensland election: 2,380 tweets and 133 candidate records.
- Honi Soit: 100 UTF-8 articles with original filenames and document text.
- Reddit: the existing four Parquet tables.

Wordflow desktop creates remote DuckDB views over these files. Resolve `main`
to a commit SHA, then use that SHA in both catalogue and data URLs for a stable
snapshot. Queries require network access until views are materialized.

The historical `demo_snapshots/` bundles are separate from the sample data catalogue
and retain their original formats.

## Reproducing the CSV and ZIP conversion

With a checkout containing Git history and uv installed:

```sh
uv run --no-project --with pyarrow==23.0.1 python scripts/convert_to_parquet.py
```

The script reads originals from revision `17fce77`, validates all converted values
against their sources and Parquet round trips, and refreshes catalogue checksums.
No source download or Python runtime is needed by Wordflow to read the Parquet data.
