# Queensland Election 2020 on Twitter

Following a curated dataset on Australia's Federal Election 2019, which has been published, the QUT Digital Observatory along with Professor Axel Bruns, Professor Daniel Angus, and PhD student Tegan Cohen carried out another collection of tweets from Twitter accounts officially associated with Queensland election candidates in 2020.

## Acknowledge

The `Gender` information is collected by [Sydney Corpus Lab](https://sydneycorpuslab.com)

## Citation
Axel, Bruns; Daniel, Agnus; Tegan, Cohen; QUT Digital Observatory; (2022): Queensland Election 2020 on Twitter. Queensland University of Technology. (Dataset) https://doi.org/10.25912/RDF_1665115527020

## Parquet distribution

The tweets (2,380 rows) and candidate metadata (133 rows) are distributed as
Parquet. Tweet/user ID columns use nullable 64-bit integers without floating-point
conversion. Other fields preserve the CSV text, including timestamp formatting.
