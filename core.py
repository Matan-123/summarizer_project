import time
from newspaper import Article
from openai import OpenAI

client = None  # אתחול המאוחר של ה-API מתבצע ב-main או ב-streamlit

MAX_TOKENS = 3500

def init_client(api_key):
    global client
    client = OpenAI(api_key=api_key)

def get_article_text(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def split_text(text, max_length=MAX_TOKENS):
    parts = []
    start = 0
    while start < len(text):
        end = start + max_length
        if end < len(text):
            end = text.rfind(' ', start, end)
            if end == -1:
                end = start + max_length
        parts.append(text[start:end].strip())
        start = end
    return parts

def analyze_text_part(text_part):
    prompt = f"""
You are a strategic business analyst. The following text may be in Hebrew or English.
Regardless of the input language, produce the analysis in English.

Important rules:
- Base your analysis only on the information provided.
- Do not guess or assume.
- If information is missing, write: "Not specified".

Provide the competitive analysis with sections:
1. Company Overview
2. Unique Selling Points (USP)
3. Target Market & Customers
4. Strategic Positioning
5. Potential Risks / Challenges

Text:
{text_part}
"""
    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert business consultant who never guesses and only works with given data."},
            {"role": "user", "content": prompt}
        ]
    )
    elapsed = time.time() - start_time
    print(f"✅ Finished processing part in {elapsed:.2f} seconds")
    return response.choices[0].message.content.strip()

def combine_analyses(analyses):
    combined = "\n\n---\n\n".join(analyses)
    final_prompt = f"""
Here are several partial competitive analyses of the same company.

Merge them into one complete competitive analysis with these sections:
1. Company Overview
2. Unique Selling Points (USP)
3. Target Market & Customers
4. Strategic Positioning
5. Potential Risks / Challenges

Rules:
- Base the final analysis only on the provided partial analyses.
- If a section is missing info, write: "Not specified".
- Do not guess beyond provided content.

Partial Analyses:
{combined}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert business consultant who never guesses and only uses given data."},
            {"role": "user", "content": final_prompt}
        ]
    )
    return response.choices[0].message.content.strip()
