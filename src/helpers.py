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