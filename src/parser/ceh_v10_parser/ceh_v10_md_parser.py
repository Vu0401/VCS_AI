import re

def extract_chapters(md_path):
    """
    Extract chapters from a Markdown file based on the chapter headings.

    Args:
        md_path (str): Path to the Markdown file.

    Returns:
        list: A list of strings, each representing a chapter's content.
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {md_path} does not exist.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the file: {e}")

    # Regular expression to extract chapter content
    pattern = r"## Chapter (\d+): .*?(?=## Chapter \d+: |## References|$)"
    chapters = [match.group(0) for match in re.finditer(pattern, content, re.DOTALL)]

    return chapters

def normalization(text):
    """
    Normalize text by removing unnecessary elements and cleaning structure.

    Args:
        text (str): The input text to normalize.

    Returns:
        str: Normalized text.
    """
    # Remove image references
    text = re.sub(r"Figure \d+-\d+ .*?<!-- image -->", "", text, flags=re.DOTALL).replace("<!-- image -->", "\n")
    
    # Remove table rows and headers
    text = re.sub(r"^(\|.*|Table.*)$", "", text, flags=re.MULTILINE)
    
    # Mark section titles for splitting and process each block
    sections = text.replace("##", "@@##").split("@@")
    normalized_sections = []
    
    for section in sections:
        if "##" in section:  # Check for title block
            title, *content = section.strip().split("\n", 1)
            if not content or not content[0].strip():
                continue  # Skip if no content after title
            # Remove consecutive blank lines
            section = re.sub(r"\n{3,}", "\n\n", section)
            normalized_sections.append(section.strip())
        else:
            normalized_sections.append(section.strip())

    return "\n\n".join(normalized_sections).strip()

def extract_sections(text):
    """
    Extract sections with titles and content from the given text.

    Args:
        text (str): The input text that contains multiple sections.

    Returns:
        list: A list of sections where each section is a string containing a title and its content.
    """
    # Regular expression to match section titles and content
    pattern = r"(## .+?)(?=\n##|\Z)"  # Match "##" followed by the title and content until the next "##" or end of text
    
    # Find all matches using the regular expression
    sections = re.findall(pattern, text, re.DOTALL)
    
    return sections

def get_all_sections(md_path):
    """
    Extracts all sections with titles and content from a Markdown file.

    Args:
        md_path (str): Path to the Markdown file.

    Returns:
        list: A list of strings, each representing a section with its title and content.

    Process:
        1. Extracts chapters based on headings like "## Chapter X".
        2. Normalizes each chapter by cleaning unnecessary elements.
        3. Extracts sections based on headings like "## Section Title".
        4. Combines and returns all sections.

    """
    chapters = extract_chapters(md_path)
    normed_chapters = [normalization(chapter) for chapter in chapters]
    sections_list = [extract_sections(chapter) for chapter in normed_chapters]
    all_sections = [section.strip() for chapter in sections_list for section in chapter]
    return all_sections


# if __name__ == "__main__":
#     md_path = "CEH_v10_EC-Council_Certified_E-IP_Specialist-1.md"
#     all_sections = get_all_sections(md_path)
#     print(len(all_sections))
#     print(all_sections[0])

