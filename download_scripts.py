#!/bin/env python3
'''Downloads movie scripts from documents.csv'''

import os
import csv
import logging

from bs4 import BeautifulSoup
import requests

repo_base = os.path.dirname(__file__)
movie_scripts_path = os.path.join(repo_base, "tmp")
os.mkdir(movie_scripts_path)

with open(os.path.join(repo_base, "documents.csv")) as doc_metadata_file:
    reader = csv.DictReader(doc_metadata_file)


    out_doc = open(os.path.join(repo_base, "documents_new.csv"), 'w')
    out_writer = csv.DictWriter(out_doc,fieldnames=reader.fieldnames)
    out_writer.writeheader()
    for line in reader:

        # Download script
        r = requests.get(line["script_url"])

        # Use contents of longest <pre> tag if exists
        soup = BeautifulSoup(r.text, "html.parser")
        script_text = ""
        for pre_tag in soup.find_all("pre"):
            if len(pre_tag.text) > len(script_text):
                script_text = pre_tag.text
        if script_text == "":
            script_text = r.text

        # Save to file
        doc_path = os.path.join(movie_scripts_path,
                                line["document_id"] + ".txt")
        with open(doc_path, 'w') as f_out:
            f_out.write(script_text)

        dl_size = os.stat(doc_path).st_size
        if int(line["script_file_size"]) != 0:
            # Verify file size
            if dl_size != line["script_file_size"]:
                percent_diff = (dl_size / int(line["script_file_size"])) / int(
                    line["script_file_size"]) * 100
                logging.warning(doc_path + " differs by " + str(percent_diff) +
                                "%")
        else:
            # Write file size and word count
            line["script_file_size"] = dl_size
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(script_text)
            line["script_word_count"] = len(doc)
            out_writer.writerow(line)
