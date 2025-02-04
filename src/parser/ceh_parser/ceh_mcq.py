import re
import json
from tqdm import tqdm

def read_markdown_file(md_path):
    """Read the content of the Markdown file."""
    with open(md_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_to_json(output_path, data):
    """Write the list of question and answer pairs to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def extract_chapters(content, section_patterns):
    """Extract chapters from Markdown content based on specific section headings."""
    sections = []

    # Loop through the section patterns to extract chapters from the start until the last section
    for i in range(len(section_patterns) - 1):
        # Create regex pattern to match content between two consecutive section headings
        pattern = rf"({re.escape(section_patterns[i])})(.*?)(?={re.escape(section_patterns[i + 1])})"
        
        # Search for the pattern in the content
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Append the matched title and content (keeping the section heading)
            sections.append(match.group(1).strip() + "\n" + match.group(2).strip())

    # Handle the last chapter (from the last section to the next specific heading or the end of the content)
    last_pattern = rf"({re.escape(section_patterns[-1])})(.*?)(?=(## Tool, Sites, and References|## About the Online Content)|$)"
    last_match = re.search(last_pattern, content, re.DOTALL)
    
    if last_match:
        # Append the last section with its heading and content
        sections.append(last_match.group(1).strip() + "\n" + last_match.group(2).strip())

    # Extract the review section from "## Getting Started: Essential Knowledge" to before "## About the Online Content"
    review_pattern = r"## Getting Started: Essential Knowledge\n\nThis chapter includes questions from the following topics:(.*?)## About the Online Content"
    review_match = re.search(review_pattern, content, re.DOTALL)
    
    if review_match:
        # Append the review section with its heading and content at the end
        sections.append("## Getting Started: Essential Knowledge\n\nThis chapter includes questions from the following topics:" + "\n" + review_match.group(1).strip())

    return sections

def normalize_section(section):
    """
    Normalize a section by removing unwanted lines based on specific criteria.
    
    Args:
        section (str): The input section text.
    
    Returns:
        str: The normalized section text.
    """
    # Remove lines containing non-ASCII characters
    section = re.sub(r'^.*[^\x00-\x7F]+.*\n?', '', section, flags=re.MULTILINE)
    
    # Remove lines containing "<!-- image -->", "Figure", or "Table"
    section = re.sub(r"^(.*(<!-- image -->|Figure|Table).*\n?)", "", section, flags=re.MULTILINE)
    
    # Remove lines that begin or end with the "|" character
    section = re.sub(r"(^\|.*?\n?|.*?\|$\n?)", "", section, flags=re.MULTILINE)
    
    # Replace lines starting with "- " with an empty string
    section = re.sub(r"^- ", "", section, flags=re.MULTILINE)
    
    # Remove extra blank lines, leaving only one blank line between sections
    section = re.sub(r"(\n\s*){2,}", "\n\n", section).strip()
    
    return section.strip()

def extract_questions_and_answers(section):
    """Extract the Question and Answer sections from a chapter."""
    
    # Regular expression pattern to match the content starting from "## Question" to the next "##" or end of the section
    question_pattern = r"(## Question.*?)(?=##|\Z)"
    
    # Regular expression pattern to match the content starting from "## Answer" to the end of the section
    answer_pattern = r"(## Answer.*?)(?=\Z)"
    
    # Search for the "Question" section using the defined pattern
    question = re.search(question_pattern, section, re.DOTALL)
    
    # Search for the "Answer" section using the defined pattern
    answer = re.search(answer_pattern, section, re.DOTALL)
    
    # If a question is found, extract and strip its content, otherwise return None
    question_text = question.group(0).strip() if question else None
    
    # If an answer is found, extract and strip its content, otherwise return None
    answer_text = answer.group(0).strip() if answer else None

    # Return the extracted question and answer text
    return question_text, answer_text


def process_and_extract(data_samples):
    """
    Process and extract structured data for a list of data samples.

    Args:
        data_samples (list): A list of data samples, where each sample contains question and answer data.

    Returns:
        list: A list of structured data dictionaries for all samples.
    """
    def process_qna(data):
        """
        Process a single data sample into question and answer dictionaries.

        Args:
            data (tuple): A tuple containing question data and answer data.

        Returns:
            tuple: Two dictionaries, one for questions and one for answers.
        """
        questions_data = data[0]
        answers_data = data[1]

        # Extract questions using regex
        questions = re.findall(r'\n(\d+)\.\s+(.*?)(?=\n\d+\.\s)', questions_data, re.DOTALL)
        answers = re.findall(r'\n(\d+)\.\s+(.*?)(?=\n\d+\.\s)', answers_data, re.DOTALL)

        question_choices = {}
        answers_reasoning = {}

        # Populate question choices dictionary
        for key, question in questions:
            question_choices[int(key)] = question.strip()

        # Populate answers reasoning dictionary
        for key, answer in answers:
            answers_reasoning[int(key)] = answer.strip()

        return question_choices, answers_reasoning

    def map_answers_to_choices(answers, choices):
        """
        Map answers to corresponding choices.

        Args:
            answers (list): A list of answer keys (e.g., ['A', 'B']).
            choices (list): A list of choice strings.

        Returns:
            str: A string containing the matched choices.
        """
        mapped_answers = []
        for answer in answers:
            answer_choice = [choice for choice in choices if choice.startswith(f"{answer}")]
            mapped_answers.extend(answer_choice)
        return "\n".join(mapped_answers)

    def extract_qna(question_choices, answers_reasoning):
        """
        Extract structured Q&A data from processed dictionaries.

        Args:
            question_choices (dict): A dictionary of question keys and their text.
            answers_reasoning (dict): A dictionary of answer keys and their reasoning text.

        Returns:
            list: A list of structured data dictionaries.
        """
        result = []

        for key in question_choices:
            # Skip if the key does not exist in answers_reasoning
            if key not in answers_reasoning:
                continue

            question = question_choices[key]
            answer_and_reasoning = answers_reasoning[key]

            # Extract question text (before choices)
            question_text = re.split(r'\n', question)[0].strip()
            question_text = re.sub(r'(.*?)(A\..*)', r'\1', question_text).strip()

            # Extract choices
            choices = re.findall(r'[A-G]\..*?(?=\n|$)', question)
            choices_text = "\n".join(choices)

            # Extract answers and reasoning
            # Split the answer and reasoning at the first period
            if "." in answer_and_reasoning:
                answer_part, reasoning_part = re.split(r'\.', answer_and_reasoning, 1)
            else:
                answer_part, reasoning_part = answer_and_reasoning, ""

            # Split answers by ','
            answers = [answer.strip() for answer in answer_part.split(',') if answer.strip()]

            # Map full content of each answer
            mapped_answers_text = map_answers_to_choices(answers, choices)

            # Reasoning 
            reasoning = reasoning_part.strip()

            # Append structured result
            result.append([
                question_text,
                choices_text,
                mapped_answers_text,
                reasoning
            ])

        return result

    # Assuming 'data_samples' is a list of tuples with questions and answers, e.g. [(questions_data, answers_data), ...]
    structured_data = []
    for data in tqdm(data_samples, desc="Processing CEH", unit="sample"):
        question_choices, answers_reasoning = process_qna(data)
        structured_data.extend(extract_qna(question_choices, answers_reasoning))

    return structured_data

def ceh_to_mcq(md_path):
    """
    Processes a CEH Markdown file to extract chapters, clean them, generate multiple-choice questions (MCQs), 
    and save the results to a JSON file.

    Args:
        md_path (str): Path to the input Markdown file.
        output_path (str): Path to the output JSON file.

    Returns:
        None
    """
    # Read the Markdown file
    ceh_content = read_markdown_file(md_path)

    section_patterns = [
    "## Getting Started: Essential Knowledge",
    "## Reconnaissance: Information Gathering for the Ethical Hacker",
    "## Scanning and Enumeration",
    "## Sniffing and Evasion",
    "## Attacking a System",
    "## Web-Based Hacking: Servers and Applications",
    "## Wireless Network Hacking",
    "## Mobile Communications and the IoT",
    "## Security in Cloud Computing",
    "## Trojans and Other Attacks",
    "## Cryptography 101",
    "## Low Tech: Social Engineering and Physical Security",
    "## The Pen Test: Putting It All Together",
    ]
    
    # Extract chapters based on section patterns
    chapter_extracted = extract_chapters(ceh_content, section_patterns)

    # Normalize the extracted chapters
    chapters_normed = [normalize_section(chapter) for chapter in chapter_extracted]  # len=14

    # Exclude the review chapter and process the remaining chapters
    rest_chapters = chapters_normed[:-1]  # Exclude the last review chapter
    
    # Remove font-error chapterschapters
    rest_chapters_qna = [
        extract_questions_and_answers(chapter)
        for chapter in rest_chapters
        if "1. " in chapter  # Ensure chapters contain questions
    ]
    
    result = process_and_extract(rest_chapters_qna)
    return result

# # Save the result to the output JSON file
# write_to_json(output_path, result)
# print(f"Processed MCQs saved to: {output_path}")


