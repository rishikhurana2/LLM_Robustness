import os
from dotenv import load_dotenv
import json
from pathlib import Path
import concurrent.futures

from helpers import (
    get_questions,
    encode_image_as_data_url,
    encode_image_for_claude,
    extract_claude_text
)

def benchmark_openai(output_file=None, model=None):
    if output_file is None:
        output_file = "../Answers/GPT_test.json"
    if model is None:
        model = "gpt-5.4"

    from openai import OpenAI

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    json_questions = get_questions()

    results = []

    for question in json_questions:
        qid = question["question_id"]
        prompt = question["Prompt"]
        category = question["Category"]

        image_file_path = None
        txt_file_path = None

        if "image_file_path" in question and question["image_file_path"]:
            image_file_path = "../" + question["image_file_path"]

        if "txt_file_path" in question and question["txt_file_path"]:
            txt_file_path = "../" + question["txt_file_path"]

        try:
            if image_file_path is None and txt_file_path is None:
                response = client.responses.create(
                    model=model,
                    input=prompt
                )
            else:
                content = []

                if txt_file_path is not None:
                    with open(txt_file_path, "r", encoding="utf-8") as f:
                        file_txt = f.read()
                    content.append({
                        "type": "input_text",
                        "text": file_txt
                    })

                content.append({
                    "type": "input_text",
                    "text": prompt
                })

                if image_file_path is not None:
                    data_url = encode_image_as_data_url(image_file_path)
                    content.append({
                        "type": "input_image",
                        "image_url": data_url
                    })

                response = client.responses.create(
                    model=model,
                    input=[{"role": "user", "content": content}]
                )

            completion = response.output_text

            result = {
                "question_id": qid,
                "LLM": "ChatGPT",
                "Model": model,
                "Prompt": prompt,
                "Completion": completion,
                "Correct": None,
                "Category": category
            }

            if "image_file_path" in question:
                result["image_file_path"] = question["image_file_path"]
            if "txt_file_path" in question:
                result["txt_file_path"] = question["txt_file_path"]

            results.append(result)

        except Exception as e:
            error_result = {
                "question_id": qid,
                "LLM": "ChatGPT",
                "Model": model,
                "Prompt": prompt,
                "Completion": f"ERROR: {str(e)}",
                "Correct": None,
                "Category": category
            }

            if "image_file_path" in question:
                error_result["image_file_path"] = question["image_file_path"]
            if "txt_file_path" in question:
                error_result["txt_file_path"] = question["txt_file_path"]

            results.append(error_result)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        print(f"Finished question {qid}")

    print(f"Saved results to {output_file}")

# Needed parallelizing because it was too slow
def benchmark_gemini(output_file=None, model=None):
    if output_file is None:
        output_file = "../Answers/Gemini.json"
    if model is None:
        model = "gemini-3-flash-preview"

    from google import genai

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    json_questions = get_questions()

    def process_single_question_gemini(question):
        qid = question["question_id"]
        prompt = question["Prompt"]
        category = question["Category"]

        image_file_path = None
        txt_file_path = None

        if "image_file_path" in question and question["image_file_path"]:
            image_file_path = "../" + question["image_file_path"]

        if "txt_file_path" in question and question["txt_file_path"]:
            txt_file_path = "../" + question["txt_file_path"]

        uploaded_files = []

        try:
            contents = []

            # Keep the structure similar to your OpenAI version:
            # optional txt file, then prompt, then optional image
            if txt_file_path is not None:
                txt_file = client.files.upload(file=Path(txt_file_path))
                uploaded_files.append(txt_file)
                contents.append(txt_file)

            contents.append(prompt)

            if image_file_path is not None:
                image_file = client.files.upload(file=Path(image_file_path))
                uploaded_files.append(image_file)
                contents.append(image_file)

            response = client.models.generate_content(
                model=model,
                contents=contents,
            )

            completion = response.text

            result = {
                "question_id": qid,
                "LLM": "Gemini",
                "Model": model,
                "Prompt": prompt,
                "Completion": completion,
                "Correct": None,
                "Category": category,
            }

            if "image_file_path" in question:
                result["image_file_path"] = question["image_file_path"]

            if "txt_file_path" in question:
                result["txt_file_path"] = question["txt_file_path"]

        except Exception as e:
            result = {
                "question_id": qid,
                "LLM": "Gemini",
                "Model": model,
                "Prompt": prompt,
                "Completion": f"ERROR: {str(e)}",
                "Correct": None,
                "Category": category,
            }

            if "image_file_path" in question:
                result["image_file_path"] = question["image_file_path"]

            if "txt_file_path" in question:
                result["txt_file_path"] = question["txt_file_path"]
            
        finally:
            # Optional cleanup so uploaded files don't pile up in Gemini Files API
            for f in uploaded_files:
                try:
                    client.files.delete(name=f.name)
                except Exception:
                    pass
            
        return result
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks to the thread pool
        future_to_question = {
            executor.submit(process_single_question_gemini, q): q 
            for q in json_questions
        }
        
        # As each thread finishes, grab the result
        for future in concurrent.futures.as_completed(future_to_question):
            result = future.result()
            if result:
                results.append(result)
                print(f"Finished question {result['question_id']}")
                
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"Saved results to {output_file}")
    

def benchmark_claude(output_file=None, model=None):
    if output_file is None:
        output_file = "../Answers/Claude.json"
    if model is None:
        model = "claude-sonnet-4-6"

    import anthropic

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    json_questions = get_questions()
    results = []

    for question in json_questions:
        qid = question["question_id"]
        prompt = question["Prompt"]
        category = question["Category"]

        image_file_path = None
        txt_file_path = None

        if "image_file_path" in question and question["image_file_path"]:
            image_file_path = "../" + question["image_file_path"]

        if "txt_file_path" in question and question["txt_file_path"]:
            txt_file_path = "../" + question["txt_file_path"]

        try:
            content = []

            # Put long context first
            if txt_file_path is not None:
                with open(txt_file_path, "r", encoding="utf-8") as f:
                    file_txt = f.read()
                content.append({
                    "type": "text",
                    "text": file_txt
                })

            # Anthropic recommends image before the text question when possible
            if image_file_path is not None:
                content.append(encode_image_for_claude(image_file_path))

            content.append({
                "type": "text",
                "text": prompt
            })

            response = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": content if content else prompt
                    }
                ],
            )

            completion = extract_claude_text(response)

            result = {
                "question_id": qid,
                "LLM": "Claude",
                "Model": model,
                "Prompt": prompt,
                "Completion": completion,
                "Correct": None,
                "Category": category
            }

            if "image_file_path" in question:
                result["image_file_path"] = question["image_file_path"]
            if "txt_file_path" in question:
                result["txt_file_path"] = question["txt_file_path"]

            results.append(result)

        except Exception as e:
            error_result = {
                "question_id": qid,
                "LLM": "Claude",
                "Model": model,
                "Prompt": prompt,
                "Completion": f"ERROR: {str(e)}",
                "Correct": None,
                "Category": category
            }

            if "image_file_path" in question:
                error_result["image_file_path"] = question["image_file_path"]
            if "txt_file_path" in question:
                error_result["txt_file_path"] = question["txt_file_path"]

            results.append(error_result)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        print(f"Finished question {qid}")

    print(f"Saved results to {output_file}")

def benchmark_qwen(output_file="../Answers/Qwen.json"):
    pass