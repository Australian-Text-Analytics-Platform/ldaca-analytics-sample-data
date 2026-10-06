# Wordflow sample data

`catalogue.json` lists the sample projects and their data files, descriptions,
byte sizes, and SHA-256 checksums. Collection READMEs retain provenance and
citation information.

- Queensland election: 2,380 tweets and 133 candidate records.
- Honi Soit: a ZIP archive of 100 UTF-8 text articles. It stays a ZIP so the
  sample shows the Data Loader reading an archive of documents.
- Reddit: the existing four Parquet tables.

Wordflow v0.7 downloads the selected files into the user's folder. Wordflow v0.8
creates remote DuckDB views over the Parquet files; it cannot read the Honi Soit
ZIP until it loads archives again (ldaca-wordflow#315). Resolve `main` to a
commit SHA, then use that SHA in both catalogue and data URLs for a stable
snapshot. Queries require network access until views are materialized.

The historical `demo_snapshots/` bundles are separate from the sample data catalogue
and retain their original formats.

## Reproducing the CSV conversion

With a checkout containing Git history and uv installed:

```sh
uv run --no-project --with pyarrow==23.0.1 python scripts/convert_to_parquet.py
```

The script reads the Queensland election CSVs from revision `17fce77`, validates
all converted values against their sources and Parquet round trips, and refreshes
catalogue checksums.
No source download or Python runtime is needed by Wordflow to read the Parquet data.
