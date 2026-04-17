# FailBench

LLM research project that is a dataset and benchmark for testing several failure modes of frontier LLMs. 

questions.json file contains questions that test failure mechanisms of LLMs; each entry in the json contains: question_id, Prompt, and Category. If an image is used in a prompt, then the json entry will contain an image_file_path entry. If a txt file is used, then the json entry wll contain a txt_file_path entry.

The src folder contains the src code that runs the questions.json file against several LLMs. The benchmark functions are in benchmark.py. main.py calls the benchmark functions with the LLM specified from user input.

## Setup

```bash
cd FailBench
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
```

## Run the benchmarks
Ensure that you have a .env file that specifies the needed API keys:

OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, DASHSCOPE_API_KEY

(DASHSCOPE_API_KEY is for Qwen)

Then, run the following:
```bash
cd src
python3 main.py --llm [llm] --output [file location] --model [model] --benchmark [benchmark file]
```
LLMs supported as of now are chatgpt, gemini, claude, and qwen. The output flag is optional and only specify it if you do not want to save benchmark outputs in the default directory. 

The model flag specifies an API name for a model under the selected LLM. There are default models:

ChatGPT: gpt-5.4\
Gemini: gemini-3-flash-preview\
Claude: claude-sonnet-4-6\
Qwen: qwen-vl-plus

Ensure to reference API documentations if you wish to change the models (and ensure use the API names).

The benchmark file is the file you would like to use to test the selected llm. As of now, there is questions.json and questions_mc.json in the repo. questions.json is the baseline questions to test the LLMs one with natural language as the ground truth for most of them. questions_mc.json changes these baseline questions to an mc format.

Also ensure you have a FailBench/Answers folder to store the output of the benchmarks. If you want to store the answers elsewhere, be sure to add an argument for the --output flag.

## References

Inspiration for the Nonsense questions came from: [Benchmark for Nonsense Questions](https://petergpt.github.io/bullshit-benchmark/viewer/index.v2.html)

Technique for Improving Spatial/Image Analysis at inference-time: https://github.com/AntResearchNLP/ViLaSR
