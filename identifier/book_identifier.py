# import os
# import json
# import re
# import google.generativeai as genai
# import google.api_core.exceptions as api_exceptions
# from dotenv import load_dotenv

# load_dotenv()

# genai_api_key = os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=genai_api_key)

# model = genai.GenerativeModel("gemini-1.0-pro")


# def identify(ocr_predictions):
#     """
#     Identify books based on OCR predictions from book spines.
#     Returns a Python list of dicts, ready for jsonify().
#     """

#     prompt = f"""
# You are given OCR predictions extracted from book spines:

# OCR: {ocr_predictions}

# Your task:
# 1. Infer the correct book titles and authors.
# 2. For each book, return a JSON object with:
#    - "title"
#    - "ISBN"
#    - "author"
#    - "description" 

# STRICT OUTPUT RULES:
# - Respond ONLY with valid JSON.
# - No markdown, no commentary, no code fences.
# - If descriptions are requested, ALWAYS include a meaningful description.
# - If nothing matches, return [].
# Descriptions MUST be present when requested.
# """

#     # ----------------------------
#     # MODEL CALL
#     # ----------------------------
#     try:
#         response = model.generate_content(prompt)
#         text_output = response.text.strip()
#     except api_exceptions.ResourceExhausted as e:
#         # Quota exceeded
#         retry_seconds = None
#         m = re.search(r"retry in\s*([0-9]+(?:\.[0-9]+)?)s", str(e))
#         if m:
#             retry_seconds = float(m.group(1))

#         return {
#             "error": "quota_exceeded",
#             "message": str(e),
#             "retry_after_seconds": retry_seconds,
#         }

#     except Exception as e:
#         return {
#             "error": "model_call_failed",
#             "message": str(e)
#         }

#     def extract_json(s: str):
#         """Extract first JSON array or object from text."""
#         if not s:
#             return None

        
#         s = re.sub(r"```json|```", "", s, flags=re.IGNORECASE)

       
#         start_match = re.search(r"[\[{]", s)
#         if not start_match:
#             return None

#         start = start_match.start()
#         open_char = s[start]
#         close_char = ']' if open_char == '[' else '}'

#         end = s.rfind(close_char)
#         if end == -1:
#             return None

#         candidate = s[start:end + 1]
#         try:
#             return json.loads(candidate)
#         except:
#             return None

#     parsed = extract_json(text_output)

#     if parsed is None:
#         return {
#             "error": "could_not_parse_model_output",
#             "raw_text": text_output
#         }

    
#     if isinstance(parsed, dict):
#         items = [parsed]
#     elif isinstance(parsed, list):
#         items = parsed
#     else:
#         items = []
    

#     return items
import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Book-Finder",
}


def identify(ocr_predictions):
    """
    Identify books based on OCR predictions from book spines.
    Returns a Python list of dicts, ready for jsonify().
    """

    prompt = f"""
You are given OCR predictions extracted from book spines:

OCR: {ocr_predictions}

Your task:
1. Infer the correct book titles and authors from the OCR text.
2. For each book detected, return a JSON array with objects containing:
   - "title" (string): The book title
   - "ISBN" (string): ISBN if found, otherwise "N/A"
   - "author" (string): The author name
   - "description" (string): A brief description of the book

CRITICAL OUTPUT REQUIREMENTS:
- You MUST respond with ONLY valid JSON, no other text.
- Start your response with [ and end with ]
- Do NOT use markdown code blocks (no ```json or ```)
- Do NOT include any explanatory text before or after the JSON
- Use double quotes for all strings
- If no books are found, return an empty array: []
- Example format: [{{"title": "Book Title", "ISBN": "1234567890", "author": "Author Name", "description": "Book description"}}]

Now return the JSON array:
"""

    payload = {
        "model": "openai/gpt-4o",   # or llama-3 for cheaper usage
        "max_tokens": 512,
        "temperature": 0.3,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )
    except Exception as e:
        return {
            "error": "network_error",
            "message": str(e)
        }

    # ----------------------------
    # HANDLE HTTP ERRORS
    # ----------------------------
    if response.status_code != 200:
        try:
            err = response.json()
        except:
            err = response.text

        return {
            "error": "model_call_failed",
            "status_code": response.status_code,
            "details": err
        }

    data = response.json()

    try:
        text_output = data["choices"][0]["message"]["content"].strip()
    except Exception:
        return {
            "error": "invalid_model_response",
            "raw_response": data
        }

    # ----------------------------
    # IMPROVED JSON EXTRACTION
    # ----------------------------
    def extract_json(s: str):
        """Extract JSON from text with multiple fallback strategies"""
        if not s:
            return None

        # Strategy 1: Try direct JSON parsing
        try:
            return json.loads(s.strip())
        except:
            pass

        # Strategy 2: Remove markdown code blocks
        cleaned = re.sub(r"```json\s*|```\s*", "", s, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except:
            pass

        # Strategy 3: Find JSON object/array boundaries
        start_match = re.search(r"[\[{]", cleaned)
        if start_match:
            start = start_match.start()
            open_char = cleaned[start]
            close_char = "]" if open_char == "[" else "}"
            
            # Find matching closing bracket
            depth = 0
            end = -1
            for i in range(start, len(cleaned)):
                if cleaned[i] == open_char:
                    depth += 1
                elif cleaned[i] == close_char:
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            
            if end > start:
                candidate = cleaned[start:end + 1]
                try:
                    return json.loads(candidate)
                except:
                    pass

        # Strategy 4: Try to fix common JSON issues
        # Remove leading/trailing text
        json_match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
        if json_match:
            candidate = json_match.group(1)
            try:
                return json.loads(candidate)
            except:
                # Try fixing common issues
                # Fix single quotes to double quotes
                fixed = re.sub(r"'([^']*)':", r'"\1":', candidate)
                fixed = re.sub(r":\s*'([^']*)'", r': "\1"', fixed)
                try:
                    return json.loads(fixed)
                except:
                    pass

        return None

    parsed = extract_json(text_output)

    if parsed is None:
        # Try to extract any useful information even if JSON parsing fails
        # Look for title and author patterns in the text
        fallback_result = []
        title_match = re.search(r'(?:title|book)[\s:]+["\']?([^"\'\n]+)["\']?', text_output, re.IGNORECASE)
        author_match = re.search(r'(?:author|by)[\s:]+["\']?([^"\'\n]+)["\']?', text_output, re.IGNORECASE)
        
        if title_match or author_match:
            fallback_result.append({
                "title": title_match.group(1) if title_match else "Unknown",
                "author": author_match.group(1) if author_match else "Unknown",
                "ISBN": "N/A",
                "description": "Parsed from unstructured model output"
            })
            return fallback_result
        
        return {
            "error": "could_not_parse_model_output",
            "message": "The model returned text that could not be parsed as JSON. This might be due to the model's response format.",
            "raw_text": text_output[:500],  # Limit to first 500 chars
            "suggestion": "Try again or check the OCR input quality"
        }

    if isinstance(parsed, dict):
        return [parsed]
    elif isinstance(parsed, list):
        return parsed
    else:
        return []
