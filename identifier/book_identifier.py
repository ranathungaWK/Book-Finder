import os
import json
import re
import google.generativeai as genai
import google.api_core.exceptions as api_exceptions
from dotenv import load_dotenv

load_dotenv()

genai_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=genai_api_key)

model = genai.GenerativeModel("gemini-2.5-pro")


def identify(ocr_predictions):
    """
    Identify books based on OCR predictions from book spines.
    Returns a Python list of dicts, ready for jsonify().
    """

    prompt = f"""
You are given OCR predictions extracted from book spines:

OCR: {ocr_predictions}

Your task:
1. Infer the correct book titles and authors.
2. For each book, return a JSON object with:
   - "title"
   - "author"
   - "description" 

STRICT OUTPUT RULES:
- Respond ONLY with valid JSON.
- No markdown, no commentary, no code fences.
- If descriptions are requested, ALWAYS include a meaningful description.
- If nothing matches, return [].
Descriptions MUST be present when requested.
"""

    # ----------------------------
    # MODEL CALL
    # ----------------------------
    try:
        response = model.generate_content(prompt)
        text_output = response.text.strip()
    except api_exceptions.ResourceExhausted as e:
        # Quota exceeded
        retry_seconds = None
        m = re.search(r"retry in\s*([0-9]+(?:\.[0-9]+)?)s", str(e))
        if m:
            retry_seconds = float(m.group(1))

        return {
            "error": "quota_exceeded",
            "message": str(e),
            "retry_after_seconds": retry_seconds,
        }

    except Exception as e:
        return {
            "error": "model_call_failed",
            "message": str(e)
        }

    def extract_json(s: str):
        """Extract first JSON array or object from text."""
        if not s:
            return None

        
        s = re.sub(r"```json|```", "", s, flags=re.IGNORECASE)

       
        start_match = re.search(r"[\[{]", s)
        if not start_match:
            return None

        start = start_match.start()
        open_char = s[start]
        close_char = ']' if open_char == '[' else '}'

        end = s.rfind(close_char)
        if end == -1:
            return None

        candidate = s[start:end + 1]
        try:
            return json.loads(candidate)
        except:
            return None

    parsed = extract_json(text_output)

    if parsed is None:
        return {
            "error": "could_not_parse_model_output",
            "raw_text": text_output
        }

    
    if isinstance(parsed, dict):
        items = [parsed]
    elif isinstance(parsed, list):
        items = parsed
    else:
        items = []
    

    return items
