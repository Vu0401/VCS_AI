import sys
import os
import re
import json
import requests
from tqdm import tqdm

sys.path.append(os.getcwd())
from llm.llama_content_to_mcq import llm_section_to_mcq

def sections_from_md(md_path):
    """
    Process a Markdown file to extract and normalize sections.

    Args:
        md_path (str): Path to the Markdown file.

    Returns:
        list: Processed sections with titles and content.
    """
    def read_markdown_file(md_path):
        """Read the content of the Markdown file."""
        with open(md_path, 'r', encoding='utf-8') as file:
            return file.read()

    def extract_chapters(content, section_patterns):
        """Extract chapters from Markdown content based on specific section headings."""
        sections = []
        for i in range(len(section_patterns) - 1):
            pattern = rf"{section_patterns[i]}(.*?)(?={section_patterns[i + 1]})"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                sections.append(match.group(0).strip())

        # Add the last section explicitly
        last_pattern = rf"{section_patterns[-1]}.*"
        last_match = re.search(last_pattern, content, re.DOTALL)
        if last_match:
            sections.append(last_match.group(0).strip())

        return sections[:-1]  # Remove the "## Review Questions" section

    def normalize_section(section):
        """Normalize a section by removing unwanted content."""
        patterns_to_remove = [
            r"(?i)## THE following CEH Exam TopiCs arE CovErEd in THis CHapTEr:.*?(?=##)",
            r"## Review Questions.*?$",
            r"!\[.*?\]\(.*?\)",  # Remove image tags
            r"Figure.*?<!-- image -->"  # Remove "Figure" related content
        ]
        for pattern in patterns_to_remove:
            section = re.sub(pattern, "", section, flags=re.DOTALL).strip()

        section = section.replace(
            "$ & )  W $ F S U J G J F E & U I J D B M ) B D L F S 4 U V E Z ( V J E F By Ric Messier $ P Q Q Z S J H U ¥ C Z + P I O 8 J M F Z 4 P O T * O D", ""
        )
        section = re.sub(r"(\n\s*){2,}", "\n\n", section).strip()  # Normalize newlines
        return section

    def extract_sections_from_text(text):
        """Extract sections with titles and content from text."""
        pattern = r"(## .+?)(?=\n##|\Z)"
        return re.findall(pattern, text, re.DOTALL)

    # Main processing pipeline
    section_patterns = [
        r"## Ethical Hacking",
        r"## Networking Foundations",
        r"## Security Foundations",
        r"## Footprinting and Reconnaissance",
        r"## Scanning Networks",
        r"## Enumeration",
        r"## System Hacking",
        r"## Malware",
        r"## Sniffing",
        r"## Social Engineering",
        r"## Wireless Security",
        r"## Attack and Defense",
        r"## Cryptography",
        r"## Security Architecture",
        r"## Security Architecture and Design",
        r"## Review Questions"
    ]

    content = read_markdown_file(md_path)
    chapters = extract_chapters(content, section_patterns)
    normalized_chapters = [normalize_section(chapter) for chapter in chapters]

    result = []
    for chapter in normalized_chapters:
        sections = extract_sections_from_text(chapter)
        for section in sections:
            if len(section.strip().split("\n", 1)) > 1:  # Ensure section has content
                result.append(section)

    return result

def sections_to_mcq(MD_DIR):
    # sections = [sections_from_md(MD_DIR)[0]] # try 1 section
    sections = sections_from_md(MD_DIR) # full sections
    result = []
    
    # Duyệt qua từng phần tử của sections với tqdm để hiển thị tiến trình
    for section in tqdm(sections, desc="Processing Sybex", unit="section"):
        res = llm_section_to_mcq(section)
        if len(res) >= 1:  # Kiểm tra điều kiện có ít nhất 1 record (question, choices, answer, reasoning)
            result.extend(res)  # Nếu đúng, thêm kết quả vào list
        else:
            continue
        result.extend(res)
    return result

# if __name__ == "__main__":
#     MD_DIR = "./data/sybex_md_parser.md"
#     res = sections_to_mcq(MD_DIR)
#     print(res)


