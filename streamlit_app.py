import streamlit as st
import concurrent.futures
from dotenv import load_dotenv
import os
from core import init_client, get_article_text, split_text, analyze_text_part, combine_analyses

# טעינת מפתח
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ API key not found in .env file.")
    st.stop()

init_client(api_key)

st.title("Competitive Analysis Summarizer")
st.write("Paste a URL or article text below to get a detailed competitive analysis.")

user_input = st.text_area("Enter article URL or text:", height=200)

if st.button("Analyze"):
    if not user_input.strip():
        st.warning("Please enter article URL or text to analyze.")
    else:
        with st.spinner("Fetching and analyzing..."):
            try:
                if user_input.startswith("http"):
                    text = get_article_text(user_input)
                else:
                    text = user_input

                parts = split_text(text)
                analyses = []

                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    results = list(executor.map(analyze_text_part, parts))
                    analyses.extend(results)

                final_analysis = combine_analyses(analyses)

                st.subheader("Final Competitive Analysis")
                st.text(final_analysis)

            except Exception as e:
                st.error(f"Error: {e}")
