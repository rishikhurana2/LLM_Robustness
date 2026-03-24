# FailBench

LLM research project that is a dataset and benchmark for testing several failure modes of frontier LLMs.

## Setup

```bash
cd FailBench
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the benchmarks

```bash
python3 main.py --llm [llm] --output [file location (optional)]
```
llms supported as of now are chatgpt, gemini, claude, and qwen. 

Ensure you have a FailBench/Answers folder to store the output of the benchmarks. If you want to store the answers elsewhere, be sure to add an argument for the --output flag.
