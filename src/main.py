import json
import re

import parser

def save_to_json(data, file_path):
    """
    Save data to a JSON file.

    Args:
        data (any): Data to save.
        file_path (str): Path to the output JSON file.

    Returns:
        None
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Data saved to: {file_path}")

def process_json_files(file_paths):
    """
    Processes a list of JSON files, concatenates their content, 
    and updates the reasoning part by removing standalone uppercase letters.

    Args:
    - file_paths (list): List of file paths to JSON files to be processed.

    Returns:
    - list: A list of combined data from all files with updated reasoning texts.
    """

    def remove_standalone_uppercase(text):
        """
        Removes standalone uppercase letters from the reasoning text.

        Args:
        - text (str): The reasoning text to be processed.

        Returns:
        - str: The updated reasoning text without standalone uppercase letters.
        """
        return re.sub(r'\b[A-Z]\b', '', text)

    result = []  # Initialize an empty list to store the combined results
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                if isinstance(data, list):
                    # Process each entry in the list
                    for entry in data:
                        if len(entry) > 3:  # Ensure there's a reasoning part
                            entry[-1] = remove_standalone_uppercase(entry[-1])  # Update reasoning
                        result.append(entry)  # Add the entry to the result list
                else:
                    print(f"Warning: The file {file_path} does not contain a list.")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    
    return result
    
if __name__ == "__main__":
    CEH_MD_PATH = "./data/ceh.md"
    CEH_V10_MD_PATH = "./data/ceh_v10.md"
    SYBEX_MD_PATH = "./data/sybex_md_parser.md"

    JSON_CEH_PATH = "./data/ceh_processed.json"
    JSON_CEH_V10_PATH = "./data/ceh_v10_processed.json"
    JSON_SYBEX_PATH = "./data/sybex_processed.json"
    
    OUTPUT_FILE = "./data/final_combined_result.json" # output 
    
    sybex_mcq = parser.sybex_to_mcq(SYBEX_MD_PATH)
    print("Done sybex parser!")
    ceh_mcq = parser.ceh_to_mcq(CEH_MD_PATH)
    print("Done ceh parser!")
    cehv10_mcq = parser.cehv10_to_mcq(CEH_V10_MD_PATH)
    print("Done ceh_v10 parser!")

    # Save each final dataset (Question, Choices, Answers, Reasoning) extracted from original PDF files
    save_to_json(ceh_mcq, JSON_CEH_PATH)
    save_to_json(cehv10_mcq, JSON_CEH_V10_PATH)
    save_to_json(sybex_mcq, JSON_SYBEX_PATH)

    # List of file paths to be processed
    file_paths = [
        JSON_CEH_PATH,
        JSON_CEH_V10_PATH,
        JSON_SYBEX_PATH
    ]

    # Process the files and get the result
    processed_data = process_json_files(file_paths)
    print(f"\nNumber of processed entries: {len(processed_data)}")

    # final mcq from 3 PDF files
    
    with open(OUTPUT_FILE, 'w') as file:
        json.dump(processed_data, file, indent=4)

    print(f"Processed final data that has been saved to {OUTPUT_FILE}")
    