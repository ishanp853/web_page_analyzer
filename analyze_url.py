import requests
from bs4 import BeautifulSoup
import ollama
import re


# ----------------------------------
# CLEAN HTML
# ----------------------------------
def clean_html(html):
    html = re.sub(r"<script[\s\S]*?</script>", "", html)
    html = re.sub(r"<style[\s\S]*?</style>", "", html)
    html = re.sub(r"<!--.*?-->", "", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()


# ----------------------------------
# FETCH LIVE URL HTML
# ----------------------------------
def fetch_page(url):
    print(f"[+] Fetching URL: {url}")

    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    return response.text


# ----------------------------------
# ANALYZE HTML USING LLAMA 3.1 8B
# ----------------------------------
def analyze_with_llama(cleaned_html):

    prompt = f"""
You are an expert Conversion Rate Optimization (CRO) and landing page analyst.

You will receive the raw HTML of ANY webpage (SaaS, eCommerce, blog, tools, agencies, documentation pages, mixed layouts, etc).

Your tasks:

1. Understand the page’s purpose, offer/value, target audience, and conversion goal.
2. Identify ONLY meaningful, high-impact conversion elements that could be A/B tested.
3. Ignore noise:
   - scripts, comments, hidden divs
   - boilerplate text, lorem ipsum
   - legal footers (unless containing trust signals)

You MUST return ONLY a single valid JSON object using EXACTLY this schema:

{{
  "page_summary": "",
  "primary_goal": "",
  "elements": [
    {{
      "id": "el_1",                 
      "type": "",               
      "text": "",               
      "html_tag": "",          
      "selector_hint": "",      
      "section": "",            
      "order_on_page": 1,      
      "above_the_fold": false,    
      "testability_score": 1, 
      "notes": ""               
    }}
  ]
}}

Rules:
- Output MUST be valid JSON only (no explanation text).
- Include only CRO-relevant elements.
- "id" values MUST be sequential: el_1, el_2, el_3...
- Estimate above_the_fold using DOM depth + typical desktop viewport.
- Keep JSON short, clean, and meaningful.
- If the page lacks certain element types, skip them.

HTML:
{cleaned_html}
"""

    print("[+] Sending HTML to LLaMA model...")

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]



# ----------------------------------
# MAIN EXECUTION
# ----------------------------------
if __name__ == "__main__":
    url = input("Enter URL to analyze: ")

    html = fetch_page(url)
    cleaned_html = clean_html(html)
    result = analyze_with_llama(cleaned_html)

    print("\n===== ANALYSIS RESULT =====\n")
    print(result)

    # Save result
    with open("result.json", "w", encoding="utf8") as f:
        f.write(result)

    print("\n[✔] Saved output to result.json")
