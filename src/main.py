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

    args = parser.parse_args()

    benchmark_map = {
        "chatgpt": benchmark_openai,
        "gemini": benchmark_gemini,
        "claude": benchmark_claude,
        "qwen": benchmark_qwen,
    }

    benchmark_fn = benchmark_map[args.llm]
    model        = args.model
    output_file  = args.output

    if output_file:
        benchmark_fn(output_file=output_file, model=model)
    else:
        benchmark_fn()


if __name__ == "__main__":
    main()