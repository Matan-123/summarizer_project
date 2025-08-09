import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from core import (
    init_client, get_article_text, split_text, analyze_text_part,
    combine_analyses, extract_company_name
)
from openai import OpenAI

# --- Load API key ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found in .env file.")
    st.stop()

# --- Initialize client ---
init_client(api_key)

# --- Show loading on startup ---
if "app_loaded" not in st.session_state:
    # Create a centered loading display
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 50vh;">
        <div style="text-align: center;">
            <h1 style="font-size: 3rem; margin-bottom: 2rem;">🚀</h1>
            <h2 style="font-size: 2rem; color: #2E86C1; margin-bottom: 1rem;">Loading Competitor Analysis Tool</h2>
            <div style="font-size: 1.5rem; color: #666;">Please wait...</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    import time
    time.sleep(3)  # Simulate loading time
    
    st.session_state.app_loaded = True
    st.rerun()  # Refresh the page to show the actual app

# --- Files for storing user data ---
INSIGHTS_FILE = "insights.csv"
ANALYSIS_HISTORY_FILE = "analysis_history.csv"
COMPARE_HISTORY_FILE = "compare_history.csv"

# --- Load existing insights ---
if os.path.exists(INSIGHTS_FILE):
    insights_df = pd.read_csv(INSIGHTS_FILE)
else:
    insights_df = pd.DataFrame(columns=["Company", "Improve", "Keep"])

# --- Load persistent history ---
if os.path.exists(ANALYSIS_HISTORY_FILE):
    df_hist = pd.read_csv(ANALYSIS_HISTORY_FILE)
    loaded_analysis_history = {
        row["Company"]: {
            "analysis": row["Analysis"],
            "summary": row.get("Summary", "")
        } for _, row in df_hist.iterrows()
    }
else:
    loaded_analysis_history = {}

if os.path.exists(COMPARE_HISTORY_FILE):
    df_comp = pd.read_csv(COMPARE_HISTORY_FILE)
    loaded_compare_history = dict(zip(df_comp["Comparison"], df_comp["Result"]))
else:
    loaded_compare_history = {}

# --- Initialize state ---
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = loaded_analysis_history
if "compare_history" not in st.session_state:
    st.session_state.compare_history = loaded_compare_history
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_summary" not in st.session_state:
    st.session_state.analysis_summary = None
if "current_company" not in st.session_state:
    st.session_state.current_company = None
if "expanded_history_item" not in st.session_state:
    st.session_state.expanded_history_item = None
if "expanded_compare_item" not in st.session_state:
    st.session_state.expanded_compare_item = None
if "comparison_in_progress" not in st.session_state:
    st.session_state.comparison_in_progress = False
if "comparison_completed" not in st.session_state:
    st.session_state.comparison_completed = False

# --- Save insights ---
def save_insights_to_csv(company_name, improvement, keep):
    global insights_df
    insights_df = insights_df[insights_df["Company"] != company_name]
    new_row = {"Company": company_name, "Improve": improvement, "Keep": keep}
    insights_df = pd.concat([insights_df, pd.DataFrame([new_row])], ignore_index=True)
    insights_df.to_csv(INSIGHTS_FILE, index=False)

# --- Save functions for history ---
def save_analysis_history():
    pd.DataFrame(
        [{
            "Company": c,
            "Analysis": v["analysis"],
            "Summary": v["summary"]
        } for c, v in st.session_state.analysis_history.items()]
    ).to_csv(ANALYSIS_HISTORY_FILE, index=False)

def save_compare_history():
    pd.DataFrame(
        [{"Comparison": c, "Result": r} for c, r in st.session_state.compare_history.items()]
    ).to_csv(COMPARE_HISTORY_FILE, index=False)

# --- Helper for CSV feedback classification ---
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
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# --- Helper for translating company names to English ---
def translate_company_name_to_english(company_name):
    """Translate company name to English if it's not already in English."""
    if not company_name:
        return company_name
    
    # Check if the name contains non-English characters
    if any(ord(char) > 127 for char in company_name):
        prompt = f"""
Translate this company name to English. Return only the English name, nothing else.

Company name: {company_name}

Rules:
- If it's already in English, return it as is
- If it's in another language, translate it to English
- Keep proper capitalization
- Return only the company name, no explanations
"""
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except:
            return company_name
    
    return company_name

# --- Sidebar Navigation ---
nav_items = [
    ("home", "Home"),
    ("analysis", "🏢 Competitor Articles Analysis"),
    ("compare", "📊 Compare Two Companies"),
    ("history", "📜 View Analysis History"),
    ("compare_history", "📜 View Company Comparison History"),
    ("insights", "📌 Improvement & Preservation Notes"),
    ("feedback", "💬 Feedback CSV Analysis")
]

for key, label in nav_items:
    if st.sidebar.button(label, key=f"nav_{key}"):
        st.session_state.current_page = key
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

# --- Home ---
if st.session_state.current_page == "home":
    st.markdown("<h2 style='text-align: center; color: #2E86C1;'>Welcome to the Competitor Analysis Tool</h2>", unsafe_allow_html=True)
    st.markdown("""
    This AI-powered tool helps you analyze competitors, compare companies, track history, manage improvement ideas, and categorize customer feedback.

    ---

    ### 🏢 Company Analysis
    Paste a company article or link. The AI will:
    - Detect the company name
    - Analyze the content for:
      * Target market
      * Strengths
      * Weaknesses
      * Main products or services
      * Key competitive insights
    - **Provides a concise summary of the analysis.**
    - **You can also write and save Improvement Notes and Preservation Notes for each company.**

    ---

    ### 📊 Compare Companies
    Paste two articles or links. The AI will:
    - Detect both company names
    - Compare them based on:
      * Target market
      * Strengths
      * Weaknesses
      * Main products or services
    - **Provides one final summary paragraph comparing both companies.**

    ---

    ### 📜 Analysis History
    Review all past single company analyses.

    ### 📜 Company Comparison History
    Review all past company comparisons.

    ### 📌 Improvement & Preservation Notes
    Save and manage insights for each company.

    ### 💬 Feedback CSV Analysis
    Classify feedback into Bug, Feature Request, User Interface, or Other.
    """)

# --- Company Analysis Page ---
if st.session_state.current_page == "analysis":
    st.header("🏢 Company Analysis")
    company_input = st.text_area("Paste article text OR URL for the competitor")

    if st.button("Identify Company"):
        with st.spinner("🔍 Identifying company, please wait..."):
            detected_name = extract_company_name(company_input)
            st.session_state["detected_name"] = detected_name
            st.session_state["company_input_saved"] = company_input
    
    # Show detected company name if available
    if "detected_name" in st.session_state:
        st.info(f"✅ **Detected Company:** {st.session_state['detected_name']}")

    if "detected_name" in st.session_state and st.button("Analyze Company"):
        company_name = st.session_state["detected_name"]
        st.session_state.current_company = company_name

        input_text_or_url = st.session_state.get("company_input_saved", "")
        with st.spinner("Analyzing company, please wait..."):
            text = get_article_text(input_text_or_url) if input_text_or_url.startswith("http") else input_text_or_url

            if not text:
                st.error("Could not retrieve text for the company. Please provide a longer article or a valid URL.")
            else:
                parts = split_text(text)
                analyses = [analyze_text_part(p) for p in parts]
                analysis_text_only = combine_analyses(analyses)

                summary_prompt = f"Summarize the following competitive analysis into one concise paragraph:\n\n{analysis_text_only}"
                client = OpenAI(api_key=api_key)
                summary_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": summary_prompt}],
                    temperature=0
                )
                company_summary = summary_response.choices[0].message.content.strip()

                st.session_state.analysis_result = analysis_text_only
                st.session_state.analysis_summary = company_summary
                st.session_state.analysis_history[company_name] = {
                    "analysis": analysis_text_only,
                    "summary": company_summary
                }
                save_analysis_history()

    if st.session_state.analysis_result and st.session_state.current_company:
        company_name = st.session_state.current_company
        # Ensure company name is in English for display
        english_company_name = translate_company_name_to_english(company_name)
        st.subheader(f"📌 Analysis of company {english_company_name}")
        st.write(st.session_state.analysis_result)
        st.markdown(f"**Company Summary:** {st.session_state.analysis_summary}")

        existing_improve = st.session_state.get(f"{company_name}_improvement", "")
        existing_keep = st.session_state.get(f"{company_name}_keep", "")

        if company_name in insights_df["Company"].values:
            existing = insights_df[insights_df["Company"] == company_name].iloc[0]
            existing_improve = existing["Improve"]
            existing_keep = existing["Keep"]

        st.subheader("📈 How can I improve compared to this competitor?")
        improve_text = st.text_area("Edit Improvement Notes", value=existing_improve)

        st.subheader("🏆 What should I keep doing because I’m better?")
        keep_text = st.text_area("Edit Preservation Notes", value=existing_keep)

        if st.button("Save My Insights"):
            save_insights_to_csv(company_name, improve_text, keep_text)
            st.success("✅ Your insights have been saved.")


# --- Compare Two Companies Page ---
if st.session_state.current_page == "compare":
    st.header("📊 Compare Two Companies")
    col1, col2 = st.columns(2)
    with col1:
        input1 = st.text_area("Company 1 article or URL")
        if st.button("Identify Company 1"):
            with st.spinner("🔍 Identifying Company 1, please wait..."):
                detected1 = extract_company_name(input1)
                st.session_state["detected_name1"] = detected1
                st.session_state["company_input1_saved"] = input1
                # Reset comparison flags when starting fresh
                st.session_state["comparison_in_progress"] = False
                st.session_state["comparison_completed"] = False
        
        # Show detected company 1 name if available (but not during comparison)
        if "detected_name1" in st.session_state and not st.session_state.get("comparison_in_progress", False):
            st.info(f"✅ **Company 1:** {st.session_state['detected_name1']}")
            
    with col2:
        input2 = st.text_area("Company 2 article or URL")
        if st.button("Identify Company 2"):
            with st.spinner("🔍 Identifying Company 2, please wait..."):
                detected2 = extract_company_name(input2)
                st.session_state["detected_name2"] = detected2
                st.session_state["company_input2_saved"] = input2
                # Reset comparison flags when starting fresh
                st.session_state["comparison_in_progress"] = False
                st.session_state["comparison_completed"] = False
        
        # Show detected company 2 name if available (but not during comparison)
        if "detected_name2" in st.session_state and not st.session_state.get("comparison_in_progress", False):
            st.info(f"✅ **Company 2:** {st.session_state['detected_name2']}")

    # Show comparison button when both companies are identified
    if "detected_name1" in st.session_state and "detected_name2" in st.session_state:
        if not st.session_state.get("comparison_in_progress", False):
            if st.button("Compare"):
                # Set flag to prevent duplicate display during comparison
                st.session_state["comparison_in_progress"] = True
                st.session_state["comparison_completed"] = False
                st.rerun()  # Force rerun to start comparison
            
        # Show comparison result if comparison is in progress
        if st.session_state.get("comparison_in_progress", False) and not st.session_state.get("comparison_completed", False):
            # Show company names during comparison (only once)
            st.info(f"🔄 **Comparing:** {st.session_state['detected_name1']} vs {st.session_state['detected_name2']}")
            
            with st.spinner("Comparing companies, please wait..."):
                name1 = st.session_state["detected_name1"]
                name2 = st.session_state["detected_name2"]

                text1_input = st.session_state.get("company_input1_saved", "")
                text2_input = st.session_state.get("company_input2_saved", "")

                text1 = get_article_text(text1_input) if text1_input.startswith("http") else text1_input
                text2 = get_article_text(text2_input) if text2_input.startswith("http") else text2_input

                analysis1 = combine_analyses([analyze_text_part(p) for p in split_text(text1)])
                analysis2 = combine_analyses([analyze_text_part(p) for p in split_text(text2)])

                compare_prompt = f"""
Compare these two companies based only on their analyses:

Company 1 ({name1}):
{analysis1}

Company 2 ({name2}):
{analysis2}

Focus on:
1. Target Market
2. Strengths
3. Weaknesses
4. Main Services or Products
5. Provide one final summary paragraph comparing both companies.
"""
                client = OpenAI(api_key=api_key)
                compare_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": compare_prompt}],
                    temperature=0
                )
                comparison_result = compare_response.choices[0].message.content.strip()
                st.write(comparison_result)

                st.session_state.compare_history[f"{name1} vs {name2}"] = comparison_result
                st.session_state["comparison_result"] = comparison_result
                save_compare_history()
                
                # Mark comparison as completed
                st.session_state["comparison_completed"] = True
                st.session_state["comparison_in_progress"] = False
        
        # Show final result after comparison is completed
        elif st.session_state.get("comparison_completed", False):
            st.success("✅ **Comparison completed!**")
            st.write(st.session_state.get("comparison_result", ""))

# --- Analysis History Page ---
if st.session_state.current_page == "history":
    st.header("📜 Analysis History")
    if st.session_state.analysis_history:
        for company, data in st.session_state.analysis_history.items():
            if st.button(company):
                if st.session_state.expanded_history_item == company:
                    st.session_state.expanded_history_item = None
                else:
                    st.session_state.expanded_history_item = company
            if st.session_state.expanded_history_item == company:
                st.subheader("Full Analysis")
                st.write(data["analysis"])
                st.subheader("Summary")
                st.write(data["summary"])
    else:
        st.info("No previous analyses found.")

# --- Comparison History Page ---
if st.session_state.current_page == "compare_history":
    st.header("📜 Company Comparison History")
    if st.session_state.compare_history:
        for comp, result in st.session_state.compare_history.items():
            if st.button(comp):
                if st.session_state.expanded_compare_item == comp:
                    st.session_state.expanded_compare_item = None
                else:
                    st.session_state.expanded_compare_item = comp
            if st.session_state.expanded_compare_item == comp:
                st.write(result)
    else:
        st.info("No previous comparisons found.")

# --- Improvement & Preservation Notes Page ---
if st.session_state.current_page == "insights":
    st.header("📌 Improvement & Preservation Notes")
    if not insights_df.empty:
        company_list = insights_df["Company"].tolist()
        selected_company = st.selectbox("Select a company to edit or delete", company_list)

        if selected_company:
            current_data = insights_df[insights_df["Company"] == selected_company].iloc[0]
            edit_improve = st.text_area("✏️ Edit 'Improve'", value=current_data["Improve"])
            edit_keep = st.text_area("✏️ Edit 'Keep'", value=current_data["Keep"])

            if st.button("💾 Save Changes"):
                save_insights_to_csv(selected_company, edit_improve, edit_keep)
                st.success(f"✅ Notes for {selected_company} have been updated.")
                st.rerun()

            if st.button("🗑 Delete This Entry"):
                updated_df = insights_df[insights_df["Company"] != selected_company]
                updated_df.to_csv(INSIGHTS_FILE, index=False)
                st.success(f"✅ Notes for {selected_company} have been deleted.")
                st.rerun()
    else:
        st.info("No saved improvement or preservation notes found.")

# --- Feedback CSV Analysis Page ---
if st.session_state.current_page == "feedback":
    st.header("💬 Feedback CSV Analysis")
    uploaded_file = st.file_uploader("Upload a CSV file with 'feedback' column", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if "feedback" not in df.columns:
            st.error("The CSV must contain a 'feedback' column.")
        else:
            if st.button("Classify Feedback"):
                with st.spinner("Classifying feedback, please wait..."):
                    df["category"] = df["feedback"].apply(classify_feedback)
                    st.dataframe(df)
                    st.download_button(
                        "📥 Download Classified CSV",
                        df.to_csv(index=False).encode("utf-8"),
                        "classified_feedback.csv",
                        "text/csv"
                    )
