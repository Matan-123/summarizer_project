# Competitive Analysis Summarizer

A Streamlit-based tool that analyzes company articles in Hebrew or English using the OpenAI API.  
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
- Fast processing with parallel execution
- Clean and interactive Streamlit interface

## Technologies
- Python
- Streamlit
- OpenAI API
- newspaper3k
- python-dotenv

## How to Run Locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
