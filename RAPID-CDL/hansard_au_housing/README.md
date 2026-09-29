# Australian Federal Parliament: housing paragraphs

Every paragraph of the Australian Federal Parliament's proceedings (Hansard) that talks about
**housing**, from 1998 to 2026: housing itself, homelessness, home ownership, first home
buyers, house prices, mortgages, negative gearing, dwellings and renting. Each paragraph comes
with the sitting date and chamber and the debate title. A second file adds the paragraph
before and after each one, so each mention can be read in context. Speaker details are a
separate table to join.

The sample is derived from the RAPID-CDL database of the proceedings:

> Hames, S., & Alpert, E. (2026). *Proceedings of Australian Federal Parliament: An Analytical
> Database* (Version 2026-09-21) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22868754

Please cite the source dataset when you use this sample.

## Files

| File | Rows | Description |
|---|---|---|
| `Hansard_AU_housing_metadata.parquet` | 76,312 | Paragraphs about housing, with sitting and debate details |
| `Hansard_AU_housing_context_metadata.parquet` | 161,724 | The same paragraphs plus the paragraph before and after each one |
| `speaker_detail.parquet` | 865 | Speaker details from the source, unchanged, to join on `speaker_detail_id` |

The 76,312 paragraphs come from 3,245 sitting days and 22,805 debates: 46,992 from the House
of Representatives and 29,320 from the Senate, about 8.5 million words in all. Most are
speeches (63,647), followed by answers (9,049), questions (3,213) and petitions (254).

| Years | Paragraphs |
|---|---|
| 1996 (three sitting days) | 8 |
| 1998 to 2002 | 6,374 |
| 2003 to 2007 | 8,221 |
| 2008 to 2012 | 14,539 |
| 2013 to 2017 | 9,338 |
| 2018 to 2022 | 11,064 |
| 2023 to 8 September 2026 | 26,768 |

These are raw counts. The number of sitting days and paragraphs recorded varies from year to
year, so compare years as a share of all paragraphs in the source when that matters.

## The source dataset

*Proceedings of Australian Federal Parliament: An Analytical Database* is a collection of four
Parquet tables created from the official XML/SGML transcripts of the proceedings, published by
the Parliamentary Library. It holds the text recorded in the proceedings, the speaker's details
at the time they were speaking (where available), the procedural context, and when and where
they were speaking. Version 2026-09-21 covers 3,300 sitting days from 30 May 1996 to
8 September 2026 (House 1,775, Senate 1,525) and 6,911,269 paragraphs. Coverage is continuous
from 2 March 1998; before that it holds only three sitting days in 1996 and none in 1997.

| Source table | Contents |
|---|---|
| `paragraph` | The non-heading text of each transcript: speeches, questions and answers, petitions, motions and more |
| `debate_title` | The procedural headings each paragraph sits under |
| `speaker_detail` | Each speaker's name, gender and party for the period the record covers |
| `session` | Each sitting day's date and chamber, with links to ParlInfo and the PDF transcript |

- Zenodo record: https://zenodo.org/records/22868754
- Version DOI: [10.5281/zenodo.22868754](https://doi.org/10.5281/zenodo.22868754); all versions: [10.5281/zenodo.22868753](https://doi.org/10.5281/zenodo.22868753)
- Source code: https://github.com/rapid-community-data-lab/australian_federal_parliament, archived at [10.5281/zenodo.18946434](https://doi.org/10.5281/zenodo.18946434)
- Creators: Samuel Hames and Elizabeth Alpert, The University of Queensland

The dataset was prepared by the Reusable and Accessible Public Interest Documents project
(RAPID-CDL). RAPID-CDL is a co-investment partnership with the Australian Research Data Commons
(ARDC) through the HASS and Indigenous Research Data Commons
([10.3565/y37z-4y53](https://doi.org/10.3565/y37z-4y53)). The ARDC is enabled by the Australian
Government's National Collaborative Research Infrastructure Strategy (NCRIS).

## How this sample was made

`scripts/build_hansard_au_samples.py` in this repository (theme `housing`) rebuilds both files
from the Zenodo version 2026-09-21 files `paragraph.parquet`, `session.parquet`,
`debate_title.parquet` and `speaker_detail.parquet`, and checks their MD5 checksums against the
record first. The GST sample in `RAPID-CDL/hansard_au_gst` is made the same way.

### 1. Find housing paragraphs

A paragraph is kept when its `text` matches any of these terms, ignoring case. `\b` marks a
word boundary. A paragraph can match several terms.

| Term | Pattern | Paragraphs |
|---|---|---|
| housing | `\bhousing\b` | 47,076 |
| mortgage, mortgages | `\bmortgages?\b` | 11,360 |
| homeless, homelessness | `\bhomeless\w*` | 10,452 |
| first home (buyers, owners, grant, super saver) | `\bfirst[\s-]home\b` | 6,425 |
| home owner, homeowner, home ownership | `\bhome[\s-]?owner\w*` | 6,399 |
| rent assistance, rental stress, rent increases and similar | `\brent(?:al)?\s+(?:assistance\|stress\|increases?\|crisis\|affordability\|relief\|freeze\|caps?)\b` | 5,213 |
| negative gearing | `\bnegative(?:ly)?[\s-]+gear\w*` | 3,451 |
| rental housing, rental market, rental properties and similar | `\brental\s+(?:housing\|homes?\|market\|propert\w+\|accommodation\|vacanc\w+\|dwellings?\|sector)\b` | 2,756 |
| dwelling, dwellings | `\bdwellings?\b` | 2,717 |
| house, home or property prices | `\b(?:house\|home\|property)\s+prices?\b` | 2,415 |
| renter, renters | `\brenters?\b` | 2,358 |
| residential tenancy | `\bresidential\s+tenanc\w+` | 55 |

The full pattern is these terms joined with `|`, as listed in the build script.

Some words were left out or narrowed because most of their uses are not about housing:

- **house** on its own: "the House" and "this House" are the chamber.
- **rent**, **rental** and **tenant** on their own: many uses are the petroleum resource rent
  tax, rent seeking, or office and airport tenancies. Only the rent phrases above are kept.
- **mortgaged** and **mortgaging**: often figurative ("mortgaging our children's future"), so
  only the nouns *mortgage* and *mortgages* count.
- **dwelling on** and **dwelling upon** (87 paragraphs): the verb, as in "dwelling on the past".
  They are not counted as mentions.

Matching is by words, so a paragraph about housing that uses none of these terms is not
included, and a match is not always about homes (for example the housing of prisoners on
remand, or of asylum seekers in detention).

### 2. Add the paragraphs either side (context file only)

For each housing paragraph, the paragraphs with the same `session_id` and `debate_id` and a
`sequence_number` one lower or one higher are added. In the source, `session_id`, `debate_id`
and `sequence_number` together identify each paragraph, and sequence numbers have no gaps
inside a debate, so these are always the adjacent paragraphs. A paragraph at the start or end
of a debate has only one neighbour. Each paragraph appears once, even when it is next to two
mentions. This adds 85,412 paragraphs, in 39,543 passages.

### 3. Join the sitting and debate details

- `session` joins on `session_id`. Every paragraph has a sitting date and chamber.
- `debate_title` joins on `debate_id`. Every paragraph has a debate.

Speaker details are not joined; see [Speaker details](#speaker-details).

Text is unchanged from the source. Rows are sorted by `session_id`, `debate_id` and
`sequence_number`, so each passage reads in order.

## Speaker details

Speaker details are kept in their own table, `speaker_detail.parquet`, copied unchanged from
the source (865 rows). Join it to either file on `speaker_detail_id` to add the speaker's name,
gender and party.

- In Wordflow: open **Data Builder**, then **Join**. Add the Hansard file first and
  `speaker_detail.parquet` second, choose `speaker_detail_id` for both, and keep the join type
  **Left** (the default) so paragraphs without speaker details are kept.
- In Python with Polars:

  ```python
  import polars as pl

  paragraphs = pl.read_parquet("Hansard_AU_housing_metadata.parquet")
  speakers = pl.read_parquet("speaker_detail.parquet")
  with_speakers = paragraphs.join(speakers, on="speaker_detail_id", how="left")
  ```

A `speaker_detail_id` is one record of a person's details for a period, not a person: when a
detail such as party changes, the person gets a new record. 743 people have 865 records. To
group by person, use `phid` in `speaker_detail.parquet`, which always equals the paragraph's
`speaker_id` when there is a match.

| Column in `speaker_detail.parquet` | Description |
|---|---|
| `speaker_detail_id` | Identifier of this record |
| `phid` | The Parliamentary Library's identifier for the parliamentarian |
| `given_name`, `family_name` | As in the Parliamentary Handbook |
| `gender` | As in the Parliamentary Handbook |
| `party` | Party membership for this period |
| `valid_from`, `valid_to` | The period this record covers (the end date is exclusive) |

## Columns

From the source `paragraph` table (see the source README for full definitions):

| Column | Description |
|---|---|
| `para_id` | Paragraph identifier |
| `session_id` | Sitting day |
| `date` | Date of the sitting (from `session`). The date is nominal: it is the day the sitting started, and sittings can run into the next day |
| `chamber` | `House` or `Senate` (from `session`) |
| `sequence_number` | Position of the paragraph in the day's transcript |
| `speaker_id` | The transcript's speaker identifier, usually the Parliamentary Handbook ID; may also be a role ID |
| `speaker_detail_id` | The speaker's record at the time of this sitting; joins to `speaker_detail.parquet` |
| `debate_id` | The debate heading the paragraph sits under |
| `procedural_unit_number` | Identifier of the procedural unit |
| `procedural_unit_type` | speech, question, answer, petition or motionnospeech |
| `text` | The text recorded in Hansard for the speaker |

Added from `debate_title`:

| Column | Description |
|---|---|
| `debate_no` | Order of the debate on the day |
| `debate_title` | All enclosing headings, one per line (for example `BILLS`, the bill's name, `Second Reading`) |

Context file only:

| Column | Description |
|---|---|
| `housing_match` | `true` for a paragraph about housing, `false` for a paragraph before or after one |
| `passage_id` | Numbers each run of consecutive paragraphs; neighbouring mentions share one passage |

## Things to know

- **Links to the transcripts.** The ParlInfo and PDF links for each sitting are in the
  source's `session.parquet`, which joins on `session_id`.
- **Paragraphs without speaker details.** 795 housing paragraphs (4,326 rows in the context
  file) have no `speaker_detail_id`, so they have no match in `speaker_detail.parquet`. Most
  (724) have the `speaker_id` `10000`, probably the chair; a few have another non-member ID or
  none.
- **Empty debate titles.** Some debates have an empty title in the source (243 rows in the
  context file).
- **Debates are not a unit for counting.** As the source notes, debates can be adjourned and
  resumed, so one debate can have several `debate_id` values.
- **Quotation marks are part of the text.** The 54 texts in the context file that start and
  end with a quotation mark quote a motion, a letter or a report; they are kept as they are.

## Licence

The source transcripts are published by the Parliamentary Library of the Australian Federal
Parliament under a [CC BY-NC-ND licence](https://www.aph.gov.au/Help/Disclaimer_Privacy_Copyright#c),
and the RAPID-CDL dataset is published under
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). The same terms apply
to this sample: attribute the source, and do not use it commercially.
