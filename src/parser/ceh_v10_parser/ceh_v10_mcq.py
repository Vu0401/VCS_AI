import requests
import re
from tqdm import tqdm
import json
import sys
import os

from .ceh_v10_md_parser import get_all_sections

sys.path.append(os.getcwd())
from llm.llama_content_to_mcq import llm_section_to_mcq

def process_sections(md_path):
    """
    Processes sections from a markdown file to generate multiple-choice questions (MCQs) using LLaMA.

    Args:
        md_path (str): The path to the markdown file containing sections to be processed.

    Returns:
        list: A list of dictionaries or tuples (depending on the output of `llm_section_to_mcq`), where each record contains:
            - question (str): The MCQ question.
            - choices (str): The answer choices in the format:
                A. [Choice A]
                B. [Choice B]
                C. [Choice C]
                D. [Choice D]
            - answer (str): The correct answer, clearly specified.
            - reasoning (str): Detailed reasoning explaining the correct answer and why other options are incorrect.

    Process:
        1. Extracts all sections from the markdown file using `get_all_sections`.
        2. Iterates over the sections with a progress bar using `tqdm`.
        3. Generates MCQs for each section by calling `llm_section_to_mcq`.
        4. Filters results to include only those sections that generate at least one MCQ.
        5. Aggregates the results into a single list and returns it.

    Notes:
        - The `get_all_sections` function must return a list of section content from the given markdown file.
        - The `llm_section_to_mcq` function is expected to process a single section and return a list of MCQs.
        - If no MCQs are generated for a section, that section is skipped.
    """
    # sections = [get_all_sections(md_path)[0]]  # 1
    sections = get_all_sections(md_path)  # 910
    result = []
    
    # Duyệt qua từng phần tử của sections với tqdm để hiển thị tiến trình
    for section in tqdm(sections, desc="Processing CEH_V10", unit="section"):
        res = llm_section_to_mcq(section)
        if len(res) >= 1:  # Kiểm tra điều kiện có ít nhất 1 record (question, choices, answer, reasoning)
            result.extend(res)  # Nếu đúng, thêm kết quả vào list
        else:
            continue
    return result

def cehv10_to_mcq(md_path):
    """
    Processes a CEH v10 Markdown file to generate multiple-choice questions (MCQs) 
    and saves the result to a JSON file.

    Args:
        md_path (str): Path to the input Markdown file.
        output_path (str): Path to the output JSON file.

    Returns:
        None
    """
    # Process sections to generate MCQs
    result = process_sections(md_path)
    return result

