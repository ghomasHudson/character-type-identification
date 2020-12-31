# coding=utf-8
# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Identifying character archetypes from movie scripts"""

from __future__ import absolute_import, division, print_function

import csv
import os

import datasets


_CITATION = """\
"""

_DESCRIPTION = """\
The character types identification dataset consists of movie
scripts annotated with character archetypes (Hero, Villain, Mentor, etc.).
"""

_URLS = {
    "full_text": "https://storage.googleapis.com/huggingface-nlp/datasets/narrative_qa/narrativeqa_full_text.zip",
    "repo": "https://github.com/ghomasHudson/character-type-identification/archive/master.zip",
}


class CharacterTypeID(datasets.GeneratorBasedBuilder):
    """Character Type Identification"""

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            citation=_CITATION,
            features=datasets.Features(
                {
                    "document": {
                        "id": datasets.Value("string"),
                        "url": datasets.Value("string"),
                        "file_size": datasets.Value("int32"),
                        "word_count": datasets.Value("int32"),
                        "start": datasets.Value("string"),
                        "end": datasets.Value("string"),
                        "summary": {
                            "text": datasets.Value("string"),
                            "url": datasets.Value("string"),
                            "title": datasets.Value("string"),
                        },
                        "text": datasets.Value("string"),
                    },
                    "character_name": datasets.Value("string"),
                    "character_type": datasets.ClassLabel(names=[
                        "Hero",
                        "Villain/Antagonist",
                        "Spouse/Partner/Lover of Hero",
                        "Spouse/Partner/Lover of Villain",
                        "Sidekick of Hero",
                        "Sidekick of Villain",
                        "Supporting role character of Hero",
                        "Supporting role character of Villain",
                        "Mentor",
                        "No Applicable Type"
                    ])
                }
            ),
            homepage="https://github.com/ghomasHudson/character-type-identification",
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""

        dl_dir = dl_manager.download_and_extract(_URLS)
        dl_dir["repo"] = os.path.join(dl_dir["repo"], "character-type-identification-master")

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"repo_dir": dl_dir["repo"], "full_text_dir": dl_dir["full_text"], "split": "train"},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"repo_dir": dl_dir["repo"], "full_text_dir": dl_dir["full_text"], "split": "test"},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={"repo_dir": dl_dir["repo"], "full_text_dir": dl_dir["full_text"], "split": "valid"},
            ),
        ]

    def _generate_examples(self, repo_dir, full_text_dir, split):
        """Yields examples."""
        documents = {}
        with open(os.path.join(repo_dir, "documents.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["set"] != split:
                    continue
                documents[row["document_id"]] = row

        summaries = {}
        with open(os.path.join(repo_dir, "summaries.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["set"] != split:
                    continue
                summaries[row["document_id"]] = row

        with open(os.path.join(repo_dir, "character_labels.csv"), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for id_, row in enumerate(reader):
                if row["set"] != split:
                    continue
                document_id = row["document_id"]
                document = documents[document_id]
                summary = summaries[document_id]
                full_text = open(os.path.join(full_text_dir, document_id + ".content"), encoding="latin-1").read()
                res = {
                    "document": {
                        "id": document["document_id"],
                        "url": document["script_url"],
                        "file_size": document["script_file_size"],
                        "word_count": document["script_word_count"],
                        "start": document["script_start"],
                        "end": document["script_end"],
                        "summary": {
                            "text": summary["summary"],
                            "url": document["wiki_url"],
                            "title": document["wiki_title"],
                        },
                        "text": full_text,
                    },
                    "character_name": row["character_name"],
                    "character_type": row["character_type"]
                }
                yield id_, res
