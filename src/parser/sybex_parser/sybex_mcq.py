import re
from tqdm import tqdm
import requests
import json

from . import sybex_md_parser

def sybex_to_mcq(file_path):
    """
    Processes a Sybex Markdown file to generate multiple-choice questions (MCQs) 
    and save them to a JSON file.

    Args:
        file_path (str): Path to the input Sybex Markdown file.
        output_file_path (str): Path to the output JSON file.

    Returns:
        None
    """
    # Generate MCQs from content
    mcq_from_content = sybex_md_parser.sections_to_mcq(file_path)

    # Generate MCQs from existing MCQs
    mcq_from_mcq = sybex_md_parser.mcq_to_mcq(file_path)

    # Combine results
    res = mcq_from_content + mcq_from_mcq

    return res

# if __name__ == "__main__":
#     # Assuming `sybex_to_mcq` is already defined and generates the required MCQs
#     SYBEX_MD_PATH = "/home1/data/vule/vcs/data/sybex_md_parser.md"  # Replace with the actual path to your PDF file
#     OUTPUT_PATH = "test.json"

#     # Generate the MCQs
#     res = sybex_to_mcq(SYBEX_MD_PATH)

#     # Write the results to a JSON file
#     with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
#         json.dump(res, file, ensure_ascii=False, indent=4)

#     print(f"MCQs have been successfully written to {OUTPUT_PATH}")