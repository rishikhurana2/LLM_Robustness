import mimetypes
import json
import base64

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


def extract_claude_text(response) -> str:
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()