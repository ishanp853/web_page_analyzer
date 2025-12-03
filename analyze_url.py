from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import regex as re
import ollama

app = FastAPI()


# ---------------------
# CLEAN HTML
# ---------------------
def clean_html(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", "", html)
    html = re.sub(r"<style[\s\S]*?</style>", "", html)
    html = re.sub(r"<!--.*?-->", "", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()


# ---------------------
# FETCH LIVE URL
# ---------------------
def fetch_page(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch URL")

    return response.text


# ---------------------
# ANALYZE WITH LLAMA
# ---------------------
def analyze_with_llama(cleaned_html: str) -> str:

    prompt = f"""
You are an expert Conversion Rate Optimization (CRO) and landing page analyst.

You will receive the raw HTML of ANY webpage (SaaS, eCommerce, blog, tools, agencies, documentation pages, mixed layouts, etc). 

Your tasks:
1. Understand the page’s purpose, offer/value, target audience, and conversion goal.
2. Identify ONLY meaningful, high-impact conversion elements that could be A/B tested.

Return ONLY valid JSON:

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

HTML:
{cleaned_html}
"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


# ---------------------
# FASTAPI ENDPOINT
# ---------------------
@app.get("/analyze")
def analyze(url: str):
    """
    Example:
    /analyze?url=https://example.com
    """

    try:
        raw_html = fetch_page(url)
        cleaned = clean_html(raw_html)
        result = analyze_with_llama(cleaned)
        return JSONResponse(content={"result": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
