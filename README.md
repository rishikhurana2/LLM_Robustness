# FailBench

LLM research project that is a dataset and benchmark for testing several failure modes of frontier LLMs. 

questions.json file contains questions that test failure mechanisms of LLMs; each entry in the json contains: question_id, Prompt, and Category. If an image is used in a prompt, then the json entry will contain an image_file_path entry. If a txt file is used, then the json entry wll contain a txt_file_path entry.

The src folder contains the src code that runs the questions.json file against several LLMs. The benchmark functions are in benchmark.py. main.py calls the benchmark functions with the LLM specified from user input.

## Setup

```bash
cd FailBench
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the benchmarks
Ensure that you have a .env file that specifies the needed API keys:

OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, DASHSCOPE_API_KEY

(DASHSCOPE_API_KEY is for Qwen)

```bash
cd src
python3 main.py --llm [llm] --output [file location]
```
LLMs supported as of now are chatgpt, gemini, claude, and qwen. The output flag is optional and only specify it if you do not want to save benchmark outputs in the default directory.

Ensure you have a FailBench/Answers folder to store the output of the benchmarks. If you want to store the answers elsewhere, be sure to add an argument for the --output flag.
