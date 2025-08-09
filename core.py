import time
import re
import os
from urllib.parse import urlparse
from openai import OpenAI
from newspaper import Article

client = None

def init_client(api_key):
    """Initialize the OpenAI client."""
    global client
    client = OpenAI(api_key=api_key)

def get_article_text(url):
    """Fetch article content from a URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        # Get both text and title for better company name extraction
        text = article.text.strip()
        title = article.title.strip() if article.title else ""
        
        # Combine title and text for better context
        full_content = f"Title: {title}\n\nContent: {text}"
        return full_content
    except Exception as e:
        print(f"❌ Failed to fetch article: {e}")
        return ""

def split_text(text, max_length=3000):
    """Split text into parts for analysis."""
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

from urllib.parse import urlparse
import os
from openai import OpenAI

def extract_company_name(text_or_url):
    """Extract company name from text or URL."""
    if text_or_url.startswith("http"):
        # For URLs, always extract the company name from the article content
        # rather than trying to guess from the domain
        article_text = get_article_text(text_or_url)
        if article_text:
            return _ask_gpt_for_company_name(article_text)
        else:
            # Fallback to domain extraction if article text is empty
            domain = urlparse(text_or_url).netloc.replace("www.", "").lower()
            base_name = domain.split(".")[0]
            if base_name not in ["com", "co", "ac", "org", "net", "thebrandhopper"]:
                return base_name.upper()
            return "Unknown Company"

    # If user provided text instead of a link
    return _ask_gpt_for_company_name(text_or_url)


def _ask_gpt_for_company_name(text):
    """Ask GPT to extract a company name from text."""
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    prompt = f"""
Extract the company name from the following text or content.
Return only the company name, nothing else.

Content:
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def _ask_gpt_for_company_name(text):
    """Ask GPT to extract a clean company name."""
    prompt = f"""
From the following text, extract ONLY the main company name that the article is about.

Rules:
- Extract the PRIMARY company being discussed in the article
- Ignore website names, publisher names, or other companies mentioned in passing
- No location.
- No legal entity suffix (Ltd, Inc, etc.).
- Only in English (translate if needed).
- Keep correct spacing between words (e.g., "Coca Cola" not "cocacola").
- Capitalize each word correctly.
- Do not merge or remove spaces between words.
- If the article is about Coca-Cola, return "Coca-Cola"
- If the article is about Apple, return "Apple"
- Focus on the main subject company, not the website hosting the article

Text:
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return _split_camel_case_or_concat(response.choices[0].message.content.strip())

def _split_camel_case_or_concat(name):
    """Ensure proper spacing for camel case or concatenated names."""
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
    if " " not in spaced:
        spaced = spaced.capitalize()
    return spaced.strip()

def analyze_text_part(part):
    """Analyze text part."""
    prompt = f"""
You are a top-tier business consultant.  
Analyze the company described in the provided text and produce a detailed competitive analysis.

Sections:
1. Company Overview
2. Unique Selling Points (USP)
3. Target Market & Customers
4. Strategic Positioning
5. Potential Risks / Challenges

Rules:
- Only use provided information.
- If missing info, write: "Not specified".
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
    print(f"✅ Processed part in {time.time() - start_time:.2f} sec")
    return response.choices[0].message.content.strip()

def combine_analyses(analyses):
    """Combine multiple analyses into one."""
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
- Only use provided information.
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
    """Generate one-paragraph summary."""
    prompt = f"""
Summarize the following competitive analysis into one concise paragraph in English.

Text:
{analysis_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()
