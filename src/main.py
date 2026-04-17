import argparse
from benchmark import (
    benchmark_openai,
    benchmark_gemini,
    benchmark_claude,
    benchmark_qwen
)

def main():
    parser = argparse.ArgumentParser(
        description="Run benchmark for a specified LLM."
    )

    parser.add_argument(
        "--llm",
        required=True,
        type=lambda s: s.strip().lower(),
        choices=["chatgpt", "gemini", "claude", "qwen"],
        help="Which LLM to benchmark: chatgpt, gemini, claude, or qwen"
    )

    parser.add_argument(
        "--model",
        default=None,
        help="Choose the model to use for your selected LLM"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON file path"
    )

    parser.add_argument(
        "--benchmark",
        default="../Questions/questions-mc.json",
        help="Input JSON file to benchmark the model. Default is questions.json.",
    )

    args = parser.parse_args()

    benchmark_map = {
        "chatgpt": benchmark_openai,
        "gemini": benchmark_gemini,
        "claude": benchmark_claude,
        "qwen": benchmark_qwen,
    }

    benchmark_fn = benchmark_map[args.llm]
    model        = args.model
    input_file   = args.benchmark
    output_file  = args.output

    benchmark_fn(output_file=output_file, model=model, questions_json_file=input_file)


if __name__ == "__main__":
    main()