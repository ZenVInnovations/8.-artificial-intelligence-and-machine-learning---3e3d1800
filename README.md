# AI Document Analyzer

## Overview

The **AI Document Analyzer** is a web-based application that automates the analysis of unstructured documents (PDFs, DOCX, TXT, images) using natural language processing (NLP). It extracts text, performs sentiment analysis, identifies keywords and entities, generates summaries, and answers user questions—streamlining tasks like resume screening and report analysis.

Built with **Flask**, **IBM Watson NLU**, and **Hugging Face Transformers**, the tool offers a user-friendly interface with result visualization and multiple output formats (TXT, JSON, CSV, PDF).

---

## Features

- **Multi-Format Text Extraction**: Processes PDFs, DOCX, TXT, and images using `pdfplumber`, `PyMuPDF`, `python-docx`, and `pytesseract`.
- **Sentiment Analysis**: Determines document tone (Positive, Neutral, Negative) via IBM Watson NLU and `vaderSentiment`.
- **Keyword & Entity Extraction**: Identifies key terms and entities (e.g., names, phone numbers) using Watson NLU and regex-based fallbacks.
- **Summarization**: Generates concise summaries using the BART model.
- **Question Answering**: Answers queries (e.g., “What is the phone number?”) using RoBERTa and regex patterns.
- **Web Interface**: Responsive UI with file upload, custom keyword input, Chart.js visualizations, and download options.
- **Robust Error Handling**: Manages API failures, file size limits (10MB), and temporary file cleanup.

---

## Project Structure

 ├── docs/
│ ├── project_overview.md
│ ├── Phase1_Research_Documentation.pdf
│ ├── Phase2_Design_Documentation.pdf
│ ├── Phase3_Development_Documentation.pdf
│ ├── Phase4_Testing_Documentation.pdf
│ └── Phase5_Deployment_Documentation.pdf
├── static/
│ ├── uploads/
│ ├── outputs/
│ └── favicon.ico
├── templates/
│ └── index.html
├── logs/
│ ├── analyzer.log
│ └── app.log
├── documents/
│ └── Resume.pdf
├── analyzer.py
├── app.py
├── .env
└── DejaVuSans.ttf


---

## Prerequisites

- Python 3.8+
- Tesseract-OCR (`C:\Program Files\Tesseract-OCR\tesseract.exe`)
- IBM Watson NLU API credentials

---

## Dependencies

Install from `requirements.txt` or manually:

```bash
pip install flask==3.0.3 werkzeug==3.0.4 fpdf==1.7.2 python-dotenv==1.0.1 \
pdfplumber==0.11.4 PyMuPDF==1.24.11 python-docx==1.1.2 pytesseract==0.3.13 \
opencv-python==4.10.0.84 pillow==10.4.0 langdetect==1.0.9 ibm-watson==8.0.0 \
vaderSentiment==3.3.2 transformers==4.44.2 torch==2.4.1

git clone https://github.com/ZenVInnovations/8.-artificial-intelligence-and-machine-learning---3e3d1800.git
cd 8.-artificial-intelligence-and-machine-learning---3e3d1800

python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate  # macOS/Linux
WATSON_API_KEY=U0eUK2PyFxFAMoeH7kouJsbaSJZ-D02wYa5jTSZ9tRGI
WATSON_SERVICE_URL=https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/ef9739eb-ebab-4cef-a42c-b13561a34afc
python app.py
