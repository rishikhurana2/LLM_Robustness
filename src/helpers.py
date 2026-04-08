import mimetypes
import json
import base64
import re
import os
from dotenv import load_dotenv

def get_questions():
    with open("../questions.json", "r", encoding="utf-8") as f:
        return json.load(f)


def encode_image_as_data_url(image_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{b64}"

# helper function to encode image for claude (returns a json)
def encode_image_for_claude(image_path: str) -> dict:
    mime_type, _ = mimetypes.guess_type(image_path)

    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if mime_type not in allowed_types:
        raise ValueError(f"Unsupported image type for Claude: {mime_type}")

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": mime_type,
            "data": image_b64,
        },
    }

# Below are helper functions used for grading the LLMs

def extract_claude_text(response) -> str:
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()

def normalize_text(s):
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def extract_boolean(s):
    s = normalize_text(s)
    if s == "true":
        return True
    if s == "false":
        return False
    return None

# Function that grades LLM responses
def grade_completion(ground_truth, completion, prompt, judge_model="gpt-5.4"):
    """
    Uses GPT-5.4 to decide whether `completion` should count as correct
    under the provided ground truth.

    Returns:
        (correct, judge_reason)
        where correct is True/False/None
    """
    from openai import OpenAI

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    judge_prompt = f"""
        You are grading an LLM answer against a ground truth answer.

        Task:
        Decide whether the model completion should be marked correct under the ground truth.

        Important grading rules:
        - Be semantically accurate, not surface-form strict.
        - If the completion is meaningfully equivalent to the ground truth, mark correct=true.
        - If the compleition is not meaningfully equivalent to the ground truth, mark correct=false.
        - Do not give partial credit. Output only correct=true or correct=false.

        Return STRICT JSON with exactly these keys:
        {{
            "correct": true,
            "reason": "brief explanation"
        }}

        Question:
        {prompt}

        Ground truth:
        {ground_truth}

        Model completion:
        {completion}
    """.strip()

    try:
        response = client.responses.create(
            model=judge_model,
            input=judge_prompt
        )

        raw = response.output_text.strip()

        parsed = json.loads(raw)
        correct = parsed.get("correct", None)
        reason = parsed.get("reason", "")

        if isinstance(correct, bool):
            return correct, reason

        return None, f"Judge returned non-boolean correct field: {raw}"

    except Exception as e:
        return None, f"Judge error: {str(e)}"
