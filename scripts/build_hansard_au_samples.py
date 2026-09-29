"""Build themed samples from RAPID-CDL's Australian Federal Parliament database.

Source: https://doi.org/10.5281/zenodo.22868754 (version 2026-09-21). Download
paragraph.parquet, session.parquet, debate_title.parquet and speaker_detail.parquet
into one folder, then run from this repository's root:

    uv run --no-project --with polars==1.40.0 python scripts/build_hansard_au_samples.py SOURCE_DIR [THEME ...]

With no THEME, every theme is built. Each theme writes
RAPID-CDL/hansard_au_<theme>/Hansard_AU_<theme>_metadata.parquet (matching paragraphs),
Hansard_AU_<theme>_context_metadata.parquet (plus the paragraph before and after), and an
unchanged copy of speaker_detail.parquet for users to join on speaker_detail_id.
"""
import hashlib
import shutil
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
SOURCE_MD5 = {
    'paragraph.parquet': '06300f04e7a27ba6d2045be08229d6af',
    'session.parquet': 'cc15e90d3c20c57064f9d94a9ad225f4',
    'debate_title.parquet': '04a5dcd10604e84697d5c59a760c5dce',
    'speaker_detail.parquet': 'fae43b939fdb771d3d66b31ca81d3884',
}
KEYS = ['session_id', 'debate_id', 'sequence_number']

# Each theme: a case-insensitive pattern a paragraph must match, and text that looks
# like a match but is not one (it is replaced before matching; the text is unchanged).
THEMES = {
    'gst': {
        # GST, GSTs, gst, Gst; goods and services tax with service(s), and/&, any spacing
        'pattern': r'\bgsts?\b|\bgoods\s*(?:and|&)\s*services?[\s-]*tax',
        # "amon-gst" is "amongst" split across a line
        'not_a_match': r'amon-gst',
    },
    'housing': {
        # "house" alone is left out: "the House" is the chamber
        'pattern': '|'.join([
            r'\bhousing\b',
            r'\bhomeless\w*',
            r'\bhome[\s-]?owner\w*',
            r'\bfirst[\s-]home\b',
            r'\b(?:house|home|property)\s+prices?\b',
            r'\bmortgages?\b',
            r'\bnegative(?:ly)?[\s-]+gear\w*',
            r'\bdwellings?\b',
            r'\brenters?\b',
            r'\brent(?:al)?\s+(?:assistance|stress|increases?|crisis|affordability|relief|freeze|caps?)\b',
            r'\brental\s+(?:housing|homes?|market|propert\w+|accommodation|vacanc\w+|dwellings?|sector)\b',
            r'\bresidential\s+tenanc\w+',
        ]),
        # "dwelling on the past" is the verb
        'not_a_match': r'\bdwelling\s+(?:on|upon)\b',
    },
}

source = Path(sys.argv[1])
themes = sys.argv[2:] or list(THEMES)
for name, expected in SOURCE_MD5.items():
    with open(source / name, 'rb') as file:
        assert hashlib.file_digest(file, 'md5').hexdigest() == expected, f'{name} is not the 2026-09-21 release'

paragraphs = pl.scan_parquet(source / 'paragraph.parquet')
sessions = pl.read_parquet(source / 'session.parquet').select('session_id', 'date', 'chamber')
debates = pl.read_parquet(source / 'debate_title.parquet').select('debate_id', 'debate_no', debate_title='title')
assert sessions['session_id'].is_unique().all()
assert debates['debate_id'].is_unique().all()


def add_context(matched):
    # Each match with the paragraph before and after it in the same session and debate.
    # (session_id, debate_id, sequence_number) is unique and sequence numbers have no gaps
    # inside a debate, so +/- 1 is the adjacent paragraph.
    match_keys = matched.select(KEYS)
    wanted = pl.concat([match_keys.with_columns(pl.col('sequence_number') + offset) for offset in (-1, 0, 1)]).unique()
    with_context = (
        paragraphs.join(wanted.lazy(), on=KEYS, how='semi')
        .collect()
        .join(match_keys.with_columns(match=pl.lit(True)), on=KEYS, how='left')
        .with_columns(pl.col('match').fill_null(False))
        .sort(KEYS)
    )
    new_passage = (
        (pl.col('session_id') != pl.col('session_id').shift())
        | (pl.col('debate_id') != pl.col('debate_id').shift())
        | (pl.col('sequence_number') != pl.col('sequence_number').shift() + 1)
    ).fill_null(True)
    return with_context.with_columns(passage_id=new_passage.cum_sum().cast(pl.Int64))


def add_metadata(frame):
    joined = (
        frame.join(sessions, on='session_id', how='left')
        .join(debates, on='debate_id', how='left')
        .sort(KEYS)
    )
    assert joined.height == frame.height and joined['date'].null_count() == 0
    # Sitting date and chamber next to session_id
    first = ['para_id', 'session_id', 'date', 'chamber']
    return joined.select(*first, pl.exclude(first))


for theme in themes:
    rule = THEMES[theme]
    checked = pl.col('text').str.replace_all('(?i)' + rule['not_a_match'], '')
    matched = paragraphs.filter(checked.str.contains('(?i)' + rule['pattern'])).collect()
    with_context = add_context(matched).rename({'match': f'{theme}_match'})

    out = ROOT / 'RAPID-CDL' / f'hansard_au_{theme}'
    out.mkdir(parents=True, exist_ok=True)
    for name, frame in [
        (f'Hansard_AU_{theme}_metadata.parquet', add_metadata(matched)),
        (f'Hansard_AU_{theme}_context_metadata.parquet', add_metadata(with_context)),
    ]:
        frame.write_parquet(out / name, compression='zstd')
        assert pl.read_parquet(out / name).equals(frame)
        print(f'{name}: {frame.height} rows, {frame.width} columns verified')
    # Speaker details stay a separate table, copied unchanged from the source
    shutil.copyfile(source / 'speaker_detail.parquet', out / 'speaker_detail.parquet')
    with open(out / 'speaker_detail.parquet', 'rb') as file:
        assert hashlib.file_digest(file, 'md5').hexdigest() == SOURCE_MD5['speaker_detail.parquet']
