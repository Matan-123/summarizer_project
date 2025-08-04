import time
from urllib.parse import urlparse
from openai import OpenAI
from newspaper import Article
import re

client = None

def init_client(api_key):
    """Initialize the OpenAI client with the provided API key."""
    global client
    client = OpenAI(api_key=api_key)

def get_article_text(url):
    """Fetch and return the main text content from a given article URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        print(f"❌ Failed to fetch article: {e}")
        return ""

def split_text(text, max_length=3000):
    """Split text into smaller parts for processing."""
    words = text.split()
    parts = []
    current_part = []

    for word in words:
        current_part.append(word)
        if len(" ".join(current_part)) > max_length:
            parts.append(" ".join(current_part))
            current_part = []

    if current_part:
        parts.append(" ".join(current_part))

    return parts

def extract_company_name(text_or_url):
    """Extract company name from text or URL using the model."""
    if text_or_url.startswith("http"):
        domain = urlparse(text_or_url).netloc
        domain = domain.replace("www.", "")

        news_domains = [
            "ynet.co.il", "haaretz.co.il", "globes.co.il",
            "calcalist.co.il", "themarker.com", "mako.co.il",
            "bizportal.co.il", "walla.co.il", "maariv.co.il"
        ]

        # אם האתר הוא אתר חדשות – נזהה מהתוכן
        if domain in news_domains:
            article_text = get_article_text(text_or_url)
            return _ask_gpt_for_company_name(article_text)
        else:
            # אתר חברה – נוודא פיצול מילים נכון
            clean_name = domain.split(".")[0]
            return _split_camel_case_or_concat(clean_name)

    # אם קיבלנו טקסט – נבקש מהמודל לזהות את שם החברה
    return _ask_gpt_for_company_name(text_or_url)

def _ask_gpt_for_company_name(text):
    """Ask GPT to extract a clean company name."""
    prompt = f"""
From the following text, extract ONLY the company name.

Rules:
- No location.
- No legal entity suffix (Ltd, Inc, etc.).
- Only in English (translate if needed).
- Keep correct spacing between words (e.g., "Profit Gym" not "profitgym").
- Capitalize each word correctly.
- Do not merge or remove spaces between words.

Text:
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    name = response.choices[0].message.content.strip()
    return _split_camel_case_or_concat(name)

def _split_camel_case_or_concat(name):
    """Ensure proper spacing for camel case or concatenated names."""
    # הוספת רווח לפני אותיות גדולות
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
    # אם אין רווחים – נהפוך לכתיבה עם אות ראשונה גדולה
    if " " not in spaced:
        spaced = spaced.capitalize()
    return spaced.strip()

def analyze_text_part(part):
    """Analyze a single part of text using the OpenAI API."""
    prompt = f"""
You are a top-tier business consultant.  
Analyze the company described in the provided text and produce a **detailed competitive analysis**.

Your response must have these sections:

1. **Company Overview**
2. **Unique Selling Points (USP)**
3. **Target Market & Customers**
4. **Strategic Positioning**
5. **Potential Risks / Challenges**

Rules:
- Only use the provided information from the text.
- If information for a section is missing, write: "Not specified".
- NEVER guess or invent details not supported by the text.
- Write in English.

Text:
{part}
"""
    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert business consultant who strictly uses only provided data."},
            {"role": "user", "content": prompt}
        ]
    )
    elapsed = time.time() - start_time
    print(f"✅ Finished processing part in {elapsed:.2f} seconds")
    return response.choices[0].message.content.strip()

def combine_analyses(analyses):
    """Merge multiple partial analyses into one final competitive analysis."""
    combined = "\n\n---\n\n".join(analyses)
    final_prompt = f"""
Merge the following partial competitive analyses into one complete competitive analysis.

Sections:
1. Company Overview
2. Unique Selling Points (USP)
3. Target Market & Customers
4. Strategic Positioning
5. Potential Risks / Challenges

Rules:
- Use only provided information.
- No guessing or adding details.
- If missing info, write: "Not specified".
- Write in English.

Partial Analyses:
{combined}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert business consultant who strictly uses only provided data."},
            {"role": "user", "content": final_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def generate_company_summary(analysis_text):
    """Generate a one-paragraph summary."""
    summary_prompt = f"""
Summarize the following competitive analysis into one concise paragraph in English.

Text:
{analysis_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()
