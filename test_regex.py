import re

content = """
### CMS Metadata

*   **Audience**: Developer, IT Admin
*   **Intent**: Configure
*   **Tags**: [Pricing and Payments, Insight.com]
*   **Prerequisites**: Account Login (for account holders)
*   **Synthetic Queries**:
    1. How do I pay my invoice using an existing Insight account?
    2. What's the process to make a payment as a guest without logging in?
    3. Can multiple invoices be paid at once on Insight.com?

### Q&A
"""

def clean_meta(text):
    if not text: return "General"
    clean = re.sub(r"\*\*|__", "", text)
    clean = re.sub(r"\n\s*", " ", clean)
    return clean.strip()

def run_test(regex_pattern, name):
    print(f"Testing {name} regex: {regex_pattern}")
    audience_match = re.search(r"(?:[-*] )?\**Audience\**:\s*(.*?)(?=\n(?:[-*] |\n|$))", content, re.IGNORECASE | re.DOTALL)
    intent_match = re.search(r"(?:[-*] )?\**Intent\**:\s*(.*?)(?=\n(?:[-*] |\n|$))", content, re.IGNORECASE | re.DOTALL)
    tags_match = re.search(r"(?:[-*] )?\**Tags\**:\s*\[?(.*?)\]?(?=\n(?:[-*] |\n|$))", content, re.IGNORECASE | re.DOTALL)

    print(f"Audience: '{clean_meta(audience_match.group(1))}'" if audience_match else "Audience: None")
    print(f"Intent: '{clean_meta(intent_match.group(1))}'" if intent_match else "Intent: None")
    print(f"Tags: '{clean_meta(tags_match.group(1))}'" if tags_match else "Tags: None")
    print("-" * 20)

# Original fails on this content because of mismatching list chars
# New Proposed Regex
# Allow for * or - at start of line
# Lookahead for newline followed by * or - or another newline or end of string.
# Need to be careful about matching the lookahead correctly.

print("--- NEW REGEX TEST ---")
# Regex breakdown:
# (?:[-*]\s+)?   : Optional start bullet '- ' or '* '
# \**Tag\**:     : Key
# \s*            : Separator
# (.*?)          : Value capture
# (?=\n(?:\s*[-*]|\s*\n|$)) : Stop at newline followed by bullet, empty line, or EOF.

regex_audience = r"(?:[-*]\s+)?\**Audience\**:\s*(.*?)(?=\n(?:\s*[-*]|\s*\n|$))"
regex_intent = r"(?:[-*]\s+)?\**Intent\**:\s*(.*?)(?=\n(?:\s*[-*]|\s*\n|$))"
regex_tags = r"(?:[-*]\s+)?\**Tags\**:\s*\[?(.*?)\]?(?=\n(?:\s*[-*]|\s*\n|$))"

m_aud = re.search(regex_audience, content, re.IGNORECASE | re.DOTALL)
m_int = re.search(regex_intent, content, re.IGNORECASE | re.DOTALL)
m_tag = re.search(regex_tags, content, re.IGNORECASE | re.DOTALL)

print(f"Audience: '{clean_meta(m_aud.group(1))}'" if m_aud else "Audience: None")
print(f"Intent: '{clean_meta(m_int.group(1))}'" if m_int else "Intent: None")
print(f"Tags: '{clean_meta(m_tag.group(1))}'" if m_tag else "Tags: None")
