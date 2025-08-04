# Competitive Analysis Summarizer

A Streamlit-based tool that analyzes competitor company articles in Hebrew or English using the OpenAI API.  
It supports both URLs and pasted text, extracts and processes the content, and generates a structured competitive analysis:

- Company Overview
- Unique Selling Points (USP)
- Target Market & Customers
- Strategic Positioning
- Potential Risks / Challenges

## Features
- Works with Hebrew and English
- Extracts article text automatically from URLs
- Handles both short and long articles
- Generates structured competitive analysis for a single company
- Compares two companies side-by-side with **one concise summary**
- Saves analysis history and comparison history
- Allows adding and editing **Improvement** & **Preservation** notes
- Analyzes CSV feedback and categorizes into:
  - Bug
  - Feature Request
  - User Interface
  - Other
- Clean and interactive Streamlit interface

## Technologies
- Python
- Streamlit
- OpenAI API
- Pandas
- newspaper3k
- python-dotenv

## How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
