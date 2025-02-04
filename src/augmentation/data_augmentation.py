import random
import json
import re
import csv
import pandas as pd

def load_data(input_file):
    """ Load data from a JSON file. """
    with open(input_file, 'r') as file:
        data = json.load(file)
    return data

def swap_answers(data):
    """
    Augments the given data by shuffling the choices and updating answers accordingly.
    If the choices contain words like "both", "all", or "none", the record will be skipped.
    """
    skip_keywords = ["both", "all", "none", "neither"]  # List of keywords to identify records to skip

    for item in data:
        question, choices, answers, reasoning = item
        
        # Check if any of the skip keywords are in the choices
        if any(keyword in choices.lower() for keyword in skip_keywords):
            continue  # Skip this record if any skip keyword is found
        
        # Parse choices into a list of (letter, content) tuples
        choices_list = re.split(r'([A-H]\. )', choices)[1:]
        try:
            parsed_choices = [
                (choices_list[i].strip('. '), choices_list[i + 1].strip())
                for i in range(0, len(choices_list), 2)
            ]
        except Exception as e:
            print(f"Error parsing choices: {choices_list}, Error: {e}")
            continue  # Skip this record if error occurs
        
        # Shuffle letters while keeping content unchanged
        letters = [choice[0] for choice in parsed_choices]
        shuffled_letters = random.sample(letters, len(letters))
        new_choices = sorted(
            zip(shuffled_letters, [choice[1] for choice in parsed_choices]),
            key=lambda x: x[0]
        )
        
        # Generate the updated choices string
        updated_choices = '\n'.join([f"{letter}. {content}" for letter, content in new_choices])
        
        # Parse and map answers to updated choices
        answers_list = re.split(r'([A-H]\. )', answers)[1:]
        try:
            parsed_answers = [
                (answers_list[i].strip('. '), answers_list[i + 1].strip())
                for i in range(0, len(answers_list), 2)
            ]
        except Exception as e:
            print(f"Error parsing answers: {answers_list}, Error: {e}")
            continue  # Skip this record if error occurs
        
        updated_answers = ' '.join(
            [f"{letter}. {content}" for letter, content in new_choices if content in [ans[1] for ans in parsed_answers]]
        )
        
        # Update the item with the new choices and answers
        item[1] = updated_choices
        item[2] = updated_answers
    
    return data

def augment_data(data, n_augmentations=5):
    """
    Augments the given dataset n_augmentations times and removes duplicates.
    Filters out lists containing empty elements or where the first element contains "Choices:".
    """
    augmented_set = set()
    for _ in range(n_augmentations):
        augmented_data = swap_answers(data)
        for item in augmented_data:
            # Lọc các list con có phần tử rỗng
            if any(element == "" for element in item):
                continue
            # Xóa list con nếu phần tử đầu tiên chứa "Choices:"
            if item[0].startswith("Choices:"):
                continue
            augmented_set.add(tuple(item))
            
    # Convert set back to a list of lists
    return [list(item) for item in augmented_set]

def save_data(data, output_path, file_format):
    """Save data to a file in JSON or CSV format."""
    if file_format == 'json':
        with open(output_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data has been saved to JSON at: {output_path}")
    elif file_format == 'csv':
        with open(output_path, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['question', 'choices', 'answer', 'reasoning'])
            writer.writerows(data)
        print(f"Data has been successfully converted to CSV at: {output_path}")
    else:
        raise ValueError("Invalid file format. Choose 'json' or 'csv'.")


def b1_data_processed(file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file, encoding='ISO-8859-1')

    # Filter rows where _is_correct == 1
    filtered_df = df[df['_is_correct'] == 1]

    # Extract relevant columns
    questions = filtered_df['question']
    choices = filtered_df['question']
    llm_answers = filtered_df['llm_answer']
    ground_truths = filtered_df['ground_truth']

    result = []

    for question, llm_answer, ground_truth in zip(questions, llm_answers, ground_truths):
        # Split question into question and choices
        if "\nA. " in question:
            question_text, choices = question.split("\nA. ", 1)
            choices = "A. " + choices
        else:
            question_text = question
            choices = ""

        # Use ground_truth for answer and llm_answer for reasoning
        answer_letter = ground_truth.strip()
        answer_map = {choice.split(". ", 1)[0]: choice.split(". ", 1)[1] for choice in choices.split("\n") if ". " in choice}
        answer = f"{answer_letter}. {answer_map.get(answer_letter, '')}" if answer_letter in answer_map else ground_truth

        # Remove standalone uppercase letters A-G followed by specific punctuation or standing alone
        reasoning_cleaned = re.sub(r"\b[A-G][,.:()]*\b", "", llm_answer)

        # Append the parsed result to the list
        result.append([question_text.strip(), choices.strip(), answer.strip(), reasoning_cleaned.strip()])

    return result

def main():
    # File paths
    INPUT_FILE = './data/final_combined_result.json'
    B1_PATH = "./data/B1_a.csv"
    OUTPUT_CSV_PATH = './data/final_aug_mcq.csv'
    
    # Load the input data
    md_data = load_data(INPUT_FILE)

    # # Perform data augmentation
    b1_data = b1_data_processed(B1_PATH)

    b1_augment_data = augment_data(b1_data, n_augmentations=10)
    augmented_data = augment_data(md_data, n_augmentations=10)
    
    final_data = b1_augment_data + augmented_data
    # Generate a list of augmented data and filter out sublists containing empty elements
    print(f"Number of unique augmented items: {len(final_data)}")

    # Convert the augmented data to CSV
    save_data(final_data, OUTPUT_CSV_PATH, 'csv')

if __name__ == "__main__":
    main()
