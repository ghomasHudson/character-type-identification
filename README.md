# Character-type Identification
This repository contains the character type identification dataset.

For more details, see the paper [TBD](https://TBD).

## Files

- documents.csv - contains document metadata from `document_id, set, script_url, script_file_size, script_word_count, script_start, script_end, wiki_url, wiki_title`.
- summaries.csv - contains wikipedia summaries in the format  `document_id, set, summary`.
- character_labels.csv - contains the character type annotations in the format `document_id, set, character_name, character_type`
- download_scripts.py - downloads the full scripts.

## Using the Dataset

Due to licensing issues, the full scripts aren't included in this repository. They can be downloaded to `/path/to/repo/tmp` by running:
```python
pip install -r requirements.txt
python download_scripts.py
```

Alternatively, the dataset can be conveniently loaded using [huggingface/datasets](https://github.com/huggingface/datasets):
```python
import datasets
ds = datasets.load_dataset("character_type_id")
print(ds["train"][0])
>> {"document_id": "00001", "summary":{"title": "Name of Movie (film)", "text": "The movie begins..."},...
```


## Citation

```
@article{characterTypeID,
author = {TBD},
title = {TBD},
journal = {TBD},
url = {https://TBD},
year = {2021},
pages = {TBD},
}
```
