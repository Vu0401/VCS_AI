# VCS Passport

Please read this README thoroughly before proceeding with any installation.
If you only need to run tests, skip to section `## 3. Test Execution Guide`.
Thank you!

# Task

The `Certified Ethical Hacker (CEH)` is an international cybersecurity certification issued by EC-Council, designed to assess professionals' ability to identify and fix vulnerabilities in computer systems.

You will be provided with:

Set A: CEH-related knowledge materials
Set B1: CEH exam questions
Your task is to fine-tune the (Llama-3.2-1B model)[https://huggingface.co/meta-llama/Llama-3.2-1B] using the provided materials to achieve higher accuracy.

# Instruction

## 1. Folder Structure

 + `/Tài_liệu_hướng_dẫn.pdf`: Instructions on running the code, including detailed input and output descriptions for each main file.

 + `/Tài_liệu_mô tả_phương_pháp.pdf`: Detailed explanation of the entire problem-solving process.

 + `/scr/`: Contains the main source code for processing input data.

 + `/train_test/train.ipynb`: Notebook for training the model.

 + `/train_test/infer.ipynb`: Notebook for testing the model.

 + `/lora_model.zip`: Pre-trained LoRA model.


## 2. Environment Setup for Running `scr` on `conda` (For Running the Parser)

### NOTE: You can check the final output at data/final_aug_mcq.csv without running the code.

If you want to run it, follow these steps:

 + Step 1 Create the environment: 
	`conda create --name vcs python=3.11 -y`

 + Step 2 Activate the environment: 
	`conda activate vcs`

 + Step 3 Install required libraries:
	`pip install -r requirements.txt`

 + Step 4 Verify the environment: 
	`python --version`
	`pip list`

 + Step 5 Configure LLM Endpoint (Important):
	Open the file `llm/llama_content_to_mcq.py` and replace the endpoint URL in the variable:
	`LLM_API = "http://12.3....."`
	
 + Step 6 Run the main scripts:
	`cd ../scr` # Navigate to the scr folder
	`python main.py`
	`python augmentation/data_augmentation.py`
	
	The main output file is `final_aug_mcq.csv` (located at `data/final_aug_mcq.csv`).

 + Step 7 Remove the environment (after testing):
	`conda remove --name vcs --all`


## 3. Test Execution Guide (For Running Tests Only)

 + Step 1 Upload the notebook to Kaggle:
	`/train_test/infer.ipynb`

 + Step 2 Upload the model to the notebook:
	Navigate to `Upload` -> `New dataset` -> Upload  `/lora_model.zip` 

 + Step 3 Upload the test CSV file:
	Navigate to `Upload` -> `New dataset` -> Upload the test file (must match the structure of `B1.csv`)

 + Step 4 Modify the file paths as needed:
	Update the configuration at the beginning of the notebook.

 + Step 5 Run the notebook:
	Output will be located at `/kaggle/working/output.xlsx` (equivalent to `./train_test/output.xlsx`)


## 4. Training Execution Guide (For Running Training Only)

 + Step 1 Upload the training notebook to Kaggle:
	`/train_test/train.ipynb`

 + Step 2 Upload the training dataset to the notebook:
	Navigate to `Upload` -> `New dataset` -> `Upload final_aug_mcq.csv` (must match the structure of `final_aug_mcq.csv`).

 + Step 3 Modify the file paths as needed:
	Update the configuration at the beginning of the notebook.

 + Step 4 Run the notebook:
	Output will be located at `/kaggle/working/lora_model` (equivalent to `./train_test/lora_model.zip`).




















