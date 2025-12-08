import re
import json

content_json = """
### CMS Metadata (Strict JSON-like Field Block)

```json
{
  "Audience": ["Developer", "IT Admin"],
  "Intent": ["Learn", "Reference"],
  "Tags": ["Pricing and Payments", "Online Payment User Guide"],
  "Prerequisites": [],
}
```
"""

content_text = """
### CMS Metadata

*   **Audience**: Developer, IT Admin
*   **Intent**: Configure
*   **Tags**: [Pricing and Payments, Insight.com]
"""

def clean_meta(text):
    if not text: return "General"
    clean = re.sub(r"[{}\"\[\]]", "", text) # Remove JSON chars
    clean = re.sub(r"\*\*|__", "", clean)
    clean = re.sub(r"\n\s*", " ", clean)
    return clean.strip()

def extract_metadata(text):
    data = {"audience": "General", "intent": "Inform", "tags": "local, extraction"}

    # 1. Try JSON block
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group(1)
            # Fix trailing commas which are common in LLM JSON
            json_str = re.sub(r",\s*\}", "}", json_str)
            parsed = json.loads(json_str)

            # Map keys (case insensitive)
            for k, v in parsed.items():
                k_lower = k.lower()
                val_str = str(v)
                if isinstance(v, list):
                    val_str = ", ".join(v)

                if "audience" in k_lower: data["audience"] = val_str
                if "intent" in k_lower: data["intent"] = val_str
                if "tags" in k_lower: data["tags"] = val_str

            print("Extracted via JSON")
            return data
        except Exception as e:
            print(f"JSON extract failed: {e}")

    # 2. Fallback to Regex
    # Improved Regex to handle optional quotes and various separators
    # Key: "Value" OR Key: Value

    # Audience
    aud_match = re.search(r"(?:[-*]\s+)?[\"*]*Audience[\"*]*\s*:\s*[\"\[]*(.*?)[\"\]]*(?=\n(?:\s*[-*]|\s*\n|$|}|,))", text, re.IGNORECASE | re.DOTALL)
    if aud_match:
         data["audience"] = aud_match.group(1).strip()

    # Intent
    int_match = re.search(r"(?:[-*]\s+)?[\"*]*Intent[\"*]*\s*:\s*[\"\[]*(.*?)[\"\]]*(?=\n(?:\s*[-*]|\s*\n|$|}|,))", text, re.IGNORECASE | re.DOTALL)
    if int_match:
         data["intent"] = int_match.group(1).strip()

    # Tags
    tag_match = re.search(r"(?:[-*]\s+)?[\"*]*Tags[\"*]*\s*:\s*(\[?.*?\]?)(?=\n(?:\s*[-*]|\s*\n|$|}|,))", text, re.IGNORECASE | re.DOTALL)
    if tag_match:
         data["tags"] = tag_match.group(1).strip()

    print("Extracted via Regex")
    return data

print("--- TEXT TEST ---")
print(extract_metadata(content_text))

print("\n--- JSON TEST ---")
print(extract_metadata(content_json))
