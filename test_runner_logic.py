import re
import json

def extract_meta(enriched_output):
    # Updated Metadata Extraction (Hybrid: JSON -> Regex)
    audience = "General"
    intent = "Inform"
    tags_list = "[local, extraction]"

    # Strategy 1: Attempt to find and parse a JSON block
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", enriched_output, re.DOTALL)
    json_success = False

    if json_match:
        try:
            json_str = json_match.group(1)
            # Fix trailing commas common in LLM output
            json_str = re.sub(r",\s*\}", "}", json_str)
            parsed_data = json.loads(json_str)

            # Helper to stringify lists
            def fmt_val(v):
                if isinstance(v, list): return ", ".join(str(x) for x in v)
                return str(v).strip()

            # Case-insensitive key lookup
            lookup = {k.lower(): v for k, v in parsed_data.items()}

            if "audience" in lookup: audience = fmt_val(lookup["audience"])
            if "intent" in lookup: intent = fmt_val(lookup["intent"])

            if "tags" in lookup:
                raw_tags = fmt_val(lookup["tags"])
                tags_list = f"[{raw_tags}]"

            json_success = True
            print("  -> Extracted metadata via JSON block")
        except Exception as e:
            print(f"  -> Warning: Failed to parse JSON metadata block: {e}")

    # Strategy 2: Fallback to Regex if JSON failed or not found
    if not json_success:
        print("  -> Attempting metadata extraction via Regex...")
        # Regex handles: * Key: Value  OR  "Key": "Value"  OR  Key: [Value]

        def extract_field(key_name, text):
            # Matches: (bullet?) (quote?)Key(quote?): (whitespace) (quote/bracket?) Value (quote/bracket?) (newline/comma/end)
            # Using .format() to avoid f-string curly brace conflicts
            pattern = r"(?:[-*]\s+)?[\"*]*{}[\"*]*\s*:\s*[\"\[]*(.*?)[\"\]]*(?=\n(?:\s*[-*]|\s*\n|$|\}}\s*,))".format(key_name)
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else None

        aud_val = extract_field("Audience", enriched_output)
        int_val = extract_field("Intent", enriched_output)
        tag_val = extract_field("Tags", enriched_output)

        def clean_meta_text(text):
            if not text: return None
            # Remove quotes, brackets if greedy match caught them
            text = re.sub(r"[{}\"\[\]]", "", text)
            text = re.sub(r"\*\*|__", "", text)
            return text.strip()

        if aud_val: audience = clean_meta_text(aud_val) or "General"
        if int_val: intent = clean_meta_text(int_val) or "Inform"

        if tag_val:
            raw_t = clean_meta_text(tag_val)
            if raw_t: tags_list = f"[{raw_t}]"

    return {"audience": audience, "intent": intent, "tags": tags_list}

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

print("--- TEXT OUTPUT ---")
print(extract_meta(content_text))
print("\n--- JSON OUTPUT ---")
print(extract_meta(content_json))
