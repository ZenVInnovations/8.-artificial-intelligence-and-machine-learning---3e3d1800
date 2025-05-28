# project-template
AI Document Analyzer

Overview
The AI Document Analyzer is a web-based application that automates the analysis of unstructured documents (PDFs, DOCX, TXT, images) using natural language processing (NLP). It extracts text, performs sentiment analysis, identifies keywords and entities, generates summaries, and answers user questions, streamlining tasks like resume screening and report analysis. Built with Flask, IBM Watson NLU, and Hugging Face Transformers, the tool offers a user-friendly interface with result visualization and multiple output formats (TXT, JSON, CSV, PDF).
Features

Multi-Format Text Extraction: Processes PDFs, DOCX, TXT, and images using pdfplumber, PyMuPDF, python-docx, and pytesseract.
Sentiment Analysis: Determines document tone (Positive, Neutral, Negative) via IBM Watson NLU and vaderSentiment.
Keyword & Entity Extraction: Identifies key terms and entities (e.g., names, phone numbers) with Watson NLU and regex-based fallbacks.
Summarization: Generates concise summaries using the BART model.
Question Answering: Answers queries (e.g., “What is the phone number?”) using RoBERTa and regex patterns.
Web Interface: Responsive UI with file upload, custom keyword input, Chart.js visualizations, and download options.
Robust Error Handling: Manages API failures, file size limits (10MB), and temporary file cleanup.

Project Structure
├── docs/                   # Documentation files
│   ├── project_overview.md
│   ├── Phase1_Research_Documentation.pdf
│   ├── Phase2_Design_Documentation.pdf
│   ├── Phase3_Development_Documentation.pdf
│   ├── Phase4_Testing_Documentation.pdf
│   └── Phase5_Deployment_Documentation.pdf
├── static/                 # Static assets
│   ├── uploads/           # Temporary uploaded files
│   ├── outputs/           # Generated analysis files
│   └── favicon.ico
├── templates/              # HTML templates
│   └── index.html
├── logs/                   # Log files
│   ├── analyzer.log
│   └── app.log
├── documents/              # Test documents
│   └── Resume.pdf
├── analyzer.py             # NLP and text extraction logic
├── app.py                  # Flask application
├── .env                    # Environment variables
└── DejaVuSans.ttf          # Font for PDF generation

Prerequisites

Python 3.8+
Tesseract-OCR (C:\Program Files\Tesseract-OCR\tesseract.exe)
IBM Watson NLU API credentials
Dependencies (see requirements.txt or install manually)

Installation

Clone the Repository:
git clone https://github.com/ZenVInnovations/8.-artificial-intelligence-and-machine-learning---3e3d1800.git
cd 8.-artificial-intelligence-and-machine-learning---3e3d1800


Set Up Virtual Environment:
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux


Install Dependencies:
pip install flask==3.0.3 werkzeug==3.0.4 fpdf==1.7.2 python-dotenv==1.0.1 pdfplumber==0.11.4 PyMuPDF==1.24.11 python-docx==1.1.2 pytesseract==0.3.13 opencv-python==4.10.0.84 pillow==10.4.0 langdetect==1.0.9 ibm-watson==8.0.0 vaderSentiment==3.3.2 transformers==4.44.2 torch==2.4.1


Configure Environment:

Create a .env file in the root directory:WATSON_API_KEY=U0eUK2PyFxFAMoeH7kouJsbaSJZ-D02wYa5jTSZ9tRGI
WATSON_SERVICE_URL=https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/ef9739eb-ebab-4cef-a42c-b13561a34afc




Download Font:

Place DejaVuSans.ttf in the root directory (download from DejaVu Fonts).



Usage

Run the Application:
python app.py


Access at http://localhost:5000.


Analyze a Document:

Upload a file (e.g., documents/Resume.pdf) via the web interface.
Enter custom keywords (e.g., “project, deadline”).
View results, including sentiment, keywords, entities, summary, and a keyword relevance chart.
Download results as TXT, JSON, CSV, or PDF.


Ask Questions:

Enter a question (e.g., “What is the phone number?”) to get answers based on the document content.



Example

Test File: Resume.pdf
Keywords: “project, deadline”
Results:
Sentiment: Positive (Score: 0.3)
Keywords: “project” (Relevance: 0.85), “python” (Relevance: 0.75)
Entities: “Mohammed” (Person, Relevance: 0.95), “+91-7795888591” (Phone, Relevance: 0.95)
Summary: “Mohammed  is a Computer Science student with project experience.”
Question: “What is the phone number?” → Answer: “+91-123456789”



Documentation
Detailed documentation is available in the docs/ folder:

Project Overview
Phase 1: Research
Phase 2: Design
Phase 3: Development
Phase 4: Testing
Phase 5: Deployment

Issues Addressed

Neutral Sentiment Scores: Adjusted vaderSentiment thresholds and ensured sufficient input text for IBM Watson.
PDF Download Errors: Implemented text sanitization and verified DejaVuSans.ttf availability.
Summary Errors: Limited input text to 1000 characters for BART model stability.

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/new-feature).
Commit changes (git commit -m "Add new feature").
Push to the branch (git push origin feature/new-feature).
Open a Pull Request.

License
This project is licensed under the MIT License. See LICENSE for details.
Contact
For issues or inquiries, please open a GitHub issue or contact the repository owner.
