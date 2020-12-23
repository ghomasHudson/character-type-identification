#!/bin/env python3
'''Convert from mturk data file to dataset'''

import csv
from collections import Counter

code_to_role = {
    "N/A": "No Applicable Type",
    "H": "Hero",
    "A": "Villain/Antagonist",
    "H-L": "Spouse/Partner/Lover of Hero",
    "A-L": "Spouse/Partner/Lover of Villain",
    "H-SK": "Sidekick of Hero",
    "A-SK": "Sidekick of Villain",
    "H-SR": "Supporting role character of Hero",
    "A-SR": "Supporting role character of Villain",
    "M": "Mentor",
    # "BUS": "Power in the background",
    # "LAW": "Lawman",
}
#preds = "Batch_4279120_batch_results.Big1.csv"
preds = "Combined_Batch.csv"
metadata_file = "/home/thomas/Documents/long-document-benchmark/narrativeqa/documents.csv"

# ###########################
#   Helper Functions
# ###########################


def make_friendly(filename):
    datas = []
    hit_ids = []
    with open(filename) as f_sum:
        reader = csv.DictReader(f_sum)
        for line_no, line in enumerate(reader):
            data = {"answers": {}}

            characters = line["Input.characters"].split("'' ''")
            for i in range(min(len(characters), 9)):
                for k in code_to_role.keys():
                    k_short = k
                    if k == "N/A":
                        k_short = "na"
                    key_str = "Answer.char" + str(
                        i) + k_short + ".Character " + str(i) + " " + k
                    if line[key_str] == "true":
                        data["answers"][characters[i]] = code_to_role[k]

            keys_to_pass = {"Answer.seenMovie.Seen movie": "seenMovie"}
            data["approved"] = line["Approve"] == "x"
            data["rejected"] = line["Reject"] == "x"
            for k in keys_to_pass:
                data[keys_to_pass[k]] = line[k]
            for k in line.keys():
                if k is None:
                    pass
                elif "." not in k and " " not in k:
                    data[k] = line[k]
                elif " " not in k and "." in k:
                    data[k.split(".")[1]] = line[k]

            hit_ids.append(data["HITId"])
            datas.append(data)
    return datas


def most_common(lst):
    """Return most common element in list"""
    data = Counter(lst)
    return data.most_common(1)[0][0]


def majority_vote(preds):
    """Reduces multiple of predictions using majority vote"""
    output = []

    # Bin by movie title
    title_map = {}
    for pred in preds:
        title_map[pred["title"]] = title_map.get(pred["title"], []) + [pred]

    # Majority vote
    majority_votes = {}
    proportion_matching_majority = {}
    confusion_matrix = {}
    for title in title_map:
        majority_votes[title] = {}
        proportion_matching_majority[title] = {}
        for movie in title_map[title]:
            for character in movie["answers"]:
                majority_votes[title][character] = majority_votes[title].get(
                    character, []) + [movie["answers"][character]]

        # Pick most frequent item
        for character in majority_votes[title]:
            most_common_element = most_common(majority_votes[title][character])
            number_matching_majority = len([
                e for e in majority_votes[title][character]
                if e == most_common_element
            ])
            proportion_matching = number_matching_majority / len(
                majority_votes[title][character])
            proportion_matching_majority[title][
                character] = proportion_matching
            if most_common_element not in confusion_matrix.keys():
                confusion_matrix[most_common_element] = Counter()
            for vote in majority_votes[title][character]:
                confusion_matrix[most_common_element].update([vote])
            majority_votes[title][character] = most_common_element

        # Put other data back in
        full_detail = title_map[title][0]
        full_detail["answers"] = majority_votes[title]
        output.append(full_detail)
    return output


# ###########################
#   Main code
# ###########################

if __name__ == "__main__":

    # Load metadata_file
    metadatas = {}
    with open(metadata_file) as f:
        reader = csv.DictReader(f)
        for line in reader:
            metadatas[line["wiki_url"]] = line

    preds = make_friendly(preds)
    preds = majority_vote(preds)

    doc_writer = csv.DictWriter(open("documents.csv", 'w'), [
        "document_id", "set", "script_url", "script_file_size",
        "script_word_count", "script_start", "script_end", "wiki_url",
        "wiki_title"
    ])
    doc_writer.writeheader()
    summary_writer = csv.DictWriter(open("summaries.csv", 'w'),
                                    ["document_id", "set", "summary"])
    summary_writer.writeheader()
    labels_writer = csv.DictWriter(
        open("character_labels.csv",
             'w'), ["document_id", "set", "character_name", "character_type"])
    labels_writer.writeheader()

    for pred in preds:
        meta = metadatas[pred["wiki_url"]]
        doc_id = meta["document_id"]
        set_name = meta["set"]
        summary = pred["summary"].replace("<b>", "").replace("</b>", "")
        summary = summary.replace("<br>", "\n")

        document_line = {
            "document_id": doc_id,
            "set": set_name,
            "script_url": meta["story_url"],
            "script_file_size": 0,
            "script_start": meta["story_start"],
            "script_end": meta["story_end"],
            "wiki_url": pred["wiki_url"],
            "wiki_title": meta["wiki_title"]
        }
        doc_writer.writerow(document_line)
        summary_line = {
            "document_id": doc_id,
            "set": set_name,
            "summary": summary
        }
        summary_writer.writerow(summary_line)
        for answer in pred["answers"]:
            character_line = {
                "document_id": doc_id,
                "set": set_name,
                "character_name": answer,
                "character_type": pred["answers"][answer]
            }
            labels_writer.writerow(character_line)
