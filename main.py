import os
import concurrent.futures
from dotenv import load_dotenv
from core import init_client, get_article_text, split_text, analyze_text_part, combine_analyses, extract_company_name

# --- Load API key ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ API key not found in .env file.")

# --- Initialize OpenAI client ---
init_client(api_key)

if __name__ == "__main__":
    num_companies = int(input("How many companies do you want to analyze? (1-3): ").strip())

    for i in range(num_companies):
        user_input = input(f"Paste an article URL or text for company #{i+1}:\n").strip()

        if user_input.startswith("http"):
            text = get_article_text(user_input)
        else:
            text = user_input

        parts = split_text(text)
        print(f"📄 Text split into {len(parts)} part(s). Processing...")

        analyses = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(analyze_text_part, parts))
            analyses.extend(results)

        company_name = extract_company_name(text)
        final_analysis = combine_analyses(analyses)

        print(f"\n=== Analysis of company {company_name} ===\n")
        print(final_analysis)
