import requests
import re

def llm_section_to_mcq(section_content):
    LLM_API = "" # Endpoint API của LLM (input: question, context | output: answer)
    
    """
    Processes a section of content to generate multiple-choice questions (MCQs) along with their answers and reasoning.

    Args:
        section_content (str): The content of a section from which MCQs will be generated.

    Returns:
        list: A list of tuples where each tuple contains:
            - question (str): The MCQ question.
            - choices (str): The answer choices in the format:
                A. [Choice A]
                B. [Choice B]
                C. [Choice C]
                D. [Choice D]
            - answer (str): The correct answer, clearly specified.
            - reasoning (str): Detailed reasoning explaining why the correct answer is valid and why the other options are incorrect.
    """
    def aug_mcq_from_section(context, llm_api=LLM_API):
        """
        Sends the context to an API for generating up to 3 MCQs following a strict format.

        Args:
            context (str): The context from which MCQs will be generated.

        Returns:
            str: A formatted string containing the MCQs, their choices, answers, and reasoning.
        """
        prompt = """Your task is to create up to 3 high-quality multiple-choice questions (MCQs) based on the information provided context. 
        
**You must strictly adhere to the following format:**
```
Question: 
[Create a clear, concise question based on the context.]  
Choices:  
A. [Option A]  
B. [Option B]  
C. [Option C]  
D. [Option D]  
Answers: [Specify the correct answer, e.g., "A", "B", etc.]  
Reasoning: [Provide a logical reason of why the selected answer is correct.]
```

**Note:**
- Only use information provided in the context. Do not introduce new details or assumptions.
- Do not alter or reinterpret the context in any way.
- Ensure all questions and choices are directly supported by the context.
- Focus solely on generating MCQs in the required format. Do not include any explanations, commentary, or additional text outside the specified format."""
        
        payload = {
            "questions": [prompt],
            "contexts": [context],
        }
        response = requests.post(llm_api, json=payload).json()
        res = response['result'][0].strip()  # Extract result and clean extra spaces
        res = res.replace("**", "")  # Remove emphasis formatting (**)

        # Normalize format for specific sections
        replace_dict = {
            r"^Question.*": "Question:",
        }

        for pattern, replacement in replace_dict.items():
            res = re.sub(pattern, replacement, res, flags=re.MULTILINE)
        return res

    def extract_mcq_data(data):
        """
        Extracts structured MCQ data (question, choices, answer, reasoning) from formatted text.

        Args:
            data (str): The input text containing questions, choices, answers, and reasonings.

        Returns:
            list: A list of tuples where each tuple contains:
                - question (str): The MCQ question.
                - choices (str): The answer choices.
                - answer (str): The correct answer.
                - reasoning (str): Explanation of the correct and incorrect answers.
        """
        # Regex patterns to extract components
        question_pattern = r"Question:\s*(.*?)\nChoices:"  # Question pattern
        choices_pattern = r"Choices:\s*(.*?)\nAnswers:"  # Choices pattern
        answer_pattern = r"Answers:\s*(.*?)\nReasoning:"  # Answer pattern
        reasoning_pattern = r"Reasoning:\s*(.*?)(?:\nQuestion|$)"  # Reasoning pattern

        # Extract components using re.findall
        questions = re.findall(question_pattern, data, re.DOTALL)
        choices = re.findall(choices_pattern, data, re.DOTALL)
        answers = re.findall(answer_pattern, data, re.DOTALL)
        reasonings = re.findall(reasoning_pattern, data, re.DOTALL)

        # Combine extracted data into structured list
        structured_data = [
            (q.strip(), c.strip(), a.strip(), r.strip())
            for q, c, a, r in zip(questions, choices, answers, reasonings)
        ]

        return structured_data
    
    def map_mcq_choices_to_answer(mcq_data):
        """
        Maps the content of the choices to the answer using the answer's letter.

        Args:
            mcq_data (list): A list of tuples containing:
                - question (str): The MCQ question.
                - choices (str): The answer choices (formatted as A., B., etc.).
                - answer (str): The correct answer letter.
                - reasoning (str): Explanation of the correct and incorrect answers.

        Returns:
            list: A list of tuples where each tuple contains:
                - question (str): The MCQ question.
                - choices (str): The answer choices.
                - mapped_answer (str): The content of the correct answer.
                - reasoning (str): Explanation of the correct answer.
        """
        mapped_results = []

        for question, choices, answer_letter, reasoning in mcq_data:
            # Parse choices into a dictionary
            choice_lines = choices.split("\n")
            choice_dict = {
                line.split(". ")[0]: line.split(". ", 1)[1]
                for line in choice_lines if ". " in line
            }

            # Map the answer letter to the corresponding choice content
            mapped_answer = f"{answer_letter}. {choice_dict.get(answer_letter, '').strip()}"

            # Append the mapped result
            mapped_results.append((question, choices, mapped_answer, reasoning))

        return mapped_results

    mcq_from_llm = aug_mcq_from_section(section_content, LLM_API)  # Generate MCQ text
    structured_data = extract_mcq_data(mcq_from_llm)  # Extract structured MCQ data (question, choices, answers, reasoning)
    mcq_data = map_mcq_choices_to_answer(structured_data)
    return mcq_data
