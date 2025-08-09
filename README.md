# 🧠 Competitor Analysis Tool (Streamlit + OpenAI)

An AI-powered web application that enables businesses and individuals to analyze competitors through articles or URLs. Built with **Streamlit**, **OpenAI API**, and **Python**, this app extracts meaningful insights, summarizes company strategies, and compares companies side-by-side.

---

## 🚀 Features

### 🏢 Single Company Analysis
- Paste a competitor's article text or URL.
- Automatically detects the company name.
- Extracts and analyzes:
  - Target Market
  - Strengths & Weaknesses
  - Main Products or Services
  - Competitive Positioning
- Provides a concise **English summary** of the analysis.
- Lets you **save notes** for:
  - Improvements you can make
  - Practices you should keep

### 📊 Compare Companies
- Input two articles or URLs.
- Extracts and compares both companies across:
  - Target Market
  - Strengths
  - Weaknesses
  - Main Services/Products
- Generates a side-by-side comparison + final summary.

### 📜 History
- Automatically stores:
  - Past company analyses
  - Company comparisons
- Results are persistent across sessions.

### 🧠 Insights
- Save & manage:
  - “Improvement Notes”
  - “Preservation Notes”
- Fully editable and deletable.

### 💬 CSV Feedback Categorization
- Upload a `.csv` file with a `feedback` column.
- Automatically categorizes user feedback into:
  - Bug
  - Feature Request
  - User Interface
  - Other

---

## 📦 Tech Stack

- **Python 3.10+**
- **Streamlit**
- **OpenAI API (GPT-4o)**
- **Newspaper3k**, **Trafilatura** – for article parsing
- **Pandas**, **BeautifulSoup**, **lxml**, **Feedparser**
- **Dotenv** for local `.env` API key management

---

## 🛠 Setup Instructions

# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/summarizer_project.git
cd summarizer_project

# 2. Install dependencies (Python 3.10+ required)
pip install -r requirements.txt

# 3. Set your API token (create a .env file in the root)
# .env content:
# OPENAI_API_KEY=your_api_token_here

# 4. Run the app
streamlit run app.py





