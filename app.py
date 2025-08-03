import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import openai

# --- Load API key ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Helper functions ---
def summarize_article(article_text):
    prompt = f"Summarize the following article into exactly 3 main bullet points:\n\n{article_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def classify_feedback(feedback_text):
    prompt = f"""
    Classify the following user feedback into one of these categories:
    1. Bug
    2. Feature Request
    3. User Interface
    4. Other

    Feedback: {feedback_text}

    Reply with only the category name.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# --- Streamlit UI ---
st.title("🔍 Competitor & Feedback Analysis Tool (OpenAI API)")

menu = st.sidebar.selectbox("Select Action", ["🏢 Competitor Articles Analysis", "💬 Feedback CSV Analysis"])

if menu == "🏢 Competitor Articles Analysis":
    st.header("🏢 Competitor Articles Analysis")
    article_text = st.text_area("Paste the article text here")
    if st.button("Summarize Article"):
        if article_text.strip():
            summary = summarize_article(article_text)
            st.subheader("📌 Summary (3 bullet points):")
            st.write(summary)
        else:
            st.warning("Please paste some article text before summarizing.")

elif menu == "💬 Feedback CSV Analysis":
    st.header("💬 Feedback CSV Analysis")
    uploaded_file = st.file_uploader("Upload a CSV file with a column named 'feedback'", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if "feedback" not in df.columns:
            st.error("The CSV file must contain a 'feedback' column.")
        else:
            if st.button("Classify Feedback"):
                df["category"] = df["feedback"].apply(classify_feedback)
                st.dataframe(df)
                st.download_button(
                    "📥 Download Classified Feedback CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    "classified_feedback.csv",
                    "text/csv"
                )

