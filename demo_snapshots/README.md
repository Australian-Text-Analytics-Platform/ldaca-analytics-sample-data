# Demo snapshots

This folder hosts pre-built `.ldaca-snapshot` bundles that Wordflow can pull into a user's snapshot folder via the **Import sample content → Demo snapshots** tab. Each bundle is a full captured analysis (concordance, quotation, token frequency, Trends, or topic modelling) so users can explore a working result without running the analysis themselves.

## Layout

```
demo_snapshots/
├── catalogue.json     ← lists every published bundle
├── README.md          ← this file
└── <tool>-<title>.ldaca-snapshot   ← one per published bundle
```

The bundle filename must match the tool key prefix (the `SnapshotToolKey` constant in the frontend, e.g. `concordance-`, `token_frequencies-`, `sequential_analysis-`, `topic_modeling-`, `quotation-`) so the destination tool's Load dialog discovers it.

## Authoring a new bundle

1. In Wordflow, run the live tool against a known dataset (ideally one shipped in this same sample-data repo so the user can import data + snapshot together).
2. Click **Save** in the tool's snapshot actions; pick a stable, descriptive filename.
3. Locate the file on disk — it lives in `<user_cache>/snapshots/<filename>.ldaca-snapshot`.
4. Copy the file into this folder.
5. Append a new entry to `catalogue.json`:

```json
{
  "id": "concordance-scl-tutorial",
  "filename": "concordance-scl-tutorial.ldaca-snapshot",
  "path": "demo_snapshots/concordance-scl-tutorial.ldaca-snapshot",
  "tool": "concordance",
  "name": "Concordance — Honi Soit tutorial",
  "description": "Demo concordance run on the SCL Honi Soit corpus.",
  "size": 12345,
  "sha256": "<sha-256 of the bundle>",
  "tool_version": "v0.4.4",
  "recommended_dataset": "SCL"
}
```

The `sha256` must match the bundle exactly — the backend verifies after download and refuses to install on mismatch. Compute it with `shasum -a 256 <filename>` or equivalent.

6. Commit and push. The next time a user opens the import dialog, the demo will appear under the **Demo snapshots** tab.

## Conflict handling

If a user has a local file with the same filename but a different sha256 (their own save, or a previous demo version), the importer **skips** that entry by default and shows a conflict warning in the UI. The user can opt in to **Replace local copy and re-download** per row — the backend deletes the local file and re-downloads atomically.

## Schema reference

| Field | Required | Description |
|---|---|---|
| `id` | yes | Stable identifier used by the import API. Cannot collide across the catalogue. |
| `filename` | yes | On-disk filename inside the user's snapshot folder. Must match the tool prefix. |
| `path` | yes | Path inside this repo (`demo_snapshots/<filename>`). |
| `tool` | yes | `SnapshotToolKey` (one of `concordance`, `quotation`, `token_frequencies`, `sequential_analysis`, `topic_modeling`). |
| `name` | yes | Display label in the catalogue list. |
| `description` | yes | One-line summary. |
| `size` | yes | Bundle size in bytes. |
| `sha256` | yes | SHA-256 of the bundle for integrity verification. |
| `tool_version` | no | App version at capture time (informational). |
| `recommended_dataset` | no | Catalogue collection id to import alongside (e.g. `SCL`). |
