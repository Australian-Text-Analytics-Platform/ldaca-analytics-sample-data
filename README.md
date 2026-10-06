# Wordflow sample data

`catalogue.json` lists the sample projects and their data files, descriptions,
byte sizes, and SHA-256 checksums. Collection READMEs retain provenance and
citation information.

The samples deliberately use the common formats researchers receive data in, so
they also show what the Data Loader can read:

- Queensland election: CSV files of 2,380 tweets and 133 candidate records.
- Honi Soit: a ZIP archive of 100 UTF-8 text articles.
- Reddit and the RAPID-CDL Hansard samples: Parquet tables.

Keep each collection in the format it was provided in. Don't convert a sample to
suit one Wordflow backend; the backend should load the format instead.

Wordflow v0.7 downloads the selected files into the user's folder. Wordflow v0.8
creates remote DuckDB views over the Parquet files; it cannot import the CSV or
ZIP samples until its sample import loads other formats (ldaca-wordflow#315).
Resolve `main` to a commit SHA, then use that SHA in both catalogue and data URLs
for a stable snapshot.

The historical `demo_snapshots/` bundles are separate from the sample data catalogue
and retain their original formats.
