import re

def mcq_to_mcq(md_file_path):
    """
    Process all sections and answers in the Markdown file to generate a list of results.

    Args:
        md_file_path (str): Path to the Markdown file.

    Returns:
        list: A list of tuples in the format (question, options, answer, explanation).
    """
    def extract_mcq_sections(md_file_path):
        """Extract specific sections from the Markdown file."""
        with open(md_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        pattern = r"(## Assessment Test.*?)(?=##)|(## Review Questions.*?)(?=<!-- image -->)"
        
        sections = re.findall(pattern, content, re.DOTALL)

        return [section[0] or section[1] for section in sections]

    def extract_answers(md_file_path):
        """Extract answers from specific sections of the Markdown file."""
        with open(md_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        pattern = r"(## Answers to Assessment Test.*?)(?=<!-- image -->)|(## Answers to Review Questions.*?)(?=## Index)"
        answers = re.findall(pattern, content, re.DOTALL)
        answers = [answer[0] or answer[1] for answer in answers]

        return [answers[0]] + re.split(r"(?=^## Chapter)", answers[1], flags=re.MULTILINE)[1:]

    def normalization(section):
        """Normalize a text section by removing unnecessary content and formatting it."""
        cleaned_section = re.sub(r"^(## \d+|\d+).*\n?", "", section, flags=re.MULTILINE)
        cleaned_section = re.sub(r"\n\n+", "\n", cleaned_section)
        cleaned_section = re.sub(r"^- ", "", cleaned_section, flags=re.MULTILINE)

        filtered_lines = [line for line in cleaned_section.split('\n') if re.match(r"^\d+\.\s|^[A-Z]\.\s", line)]
        return '\n'.join(filtered_lines)

    def split_questions(input_text):
        """Split a text section into individual questions."""
        questions = re.split(r'^\d+\. ', input_text, flags=re.MULTILINE)
        questions = [q.strip() for q in questions if q.strip()]
        return [(q[:q.find('A. ')].strip(), q[q.find('A. '):]) for q in questions]

    def extract_ground_truth_and_reasoning(input_text):
        """Extract ground truth answers and reasoning from a text section."""
        matches = re.findall(r'(\d+)\.\s([A-Z])\.\s(.*?)(?:\n|$)', input_text, flags=re.MULTILINE)
        return [(match[1], match[2].strip()) for match in matches]

    def map_answers_to_choices(questions, answers):
        """Map answers to their corresponding choices and reasoning."""
        mapped_results = []
        for i, (ground_truth, reasoning) in enumerate(answers):
            question_choices = questions[i][1]
            choice_match = re.search(rf'{ground_truth}\.\s.*?(?=\n|$)', question_choices)
            if choice_match:
                choice_text = choice_match.group(0).strip()
                mapped_results.append((choice_text, reasoning))
            else:
                mapped_results.append((ground_truth, reasoning))
        return mapped_results

    def format_result(questions, updated_res):
        """Format the final result as a list of tuples."""
        return [(q, opts, ans, expl) for (q, opts), (ans, expl) in zip(questions, updated_res)]

    # Main processing pipeline
    sections = [normalization(section) for section in extract_mcq_sections(md_file_path)]
    answers = [normalization(answer) for answer in extract_answers(md_file_path)]

    all_results = []

    for section, answer in zip(sections, answers):
        questions = split_questions(section)
        res = extract_ground_truth_and_reasoning(answer)
        updated_res = map_answers_to_choices(questions, res)
        all_results.extend(format_result(questions, updated_res))

    mcq_list = [list(mcq) for mcq in all_results]
    return mcq_list

# if __name__ == "__main__":
#     md_file_path = "sybex_md_parser.md"  
#     res = mcq_to_mcq(md_file_path) 
#     print(res[0])
#     print(len(res))