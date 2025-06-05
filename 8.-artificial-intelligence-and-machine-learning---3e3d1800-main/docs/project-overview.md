# AI Document Analyzer: Project Overview

## Project Summary

The **AI Document Analyzer** is a web-based application designed to automate the analysis of unstructured documents, including PDFs, DOCX files, text files, and images. Leveraging natural language processing (NLP), the tool extracts text, performs sentiment analysis, identifies keywords and entities, generates summaries, and answers user-defined questions. The project aims to streamline document processing for applications such as resume screening, report analysis, and information extraction, reducing manual effort and enhancing insights.

---

## Objectives

- Develop a robust system to process multiple document formats (PDF, DOCX, TXT, images) with high text extraction accuracy (>95%).
- Implement NLP-driven features: sentiment analysis, keyword and entity extraction, text summarization, and question answering.
- Provide a user-friendly web interface for document upload, analysis, result visualization, and output downloads (TXT, JSON, CSV, PDF).
- Ensure reliability through cloud-based (IBM Watson NLU) and local NLP processing fallbacks.
- Address usability and performance, targeting analysis response times under 5 seconds and handling files up to 10MB.

---

## Key Features

- **Text Extraction**: Supports PDFs (`pdfplumber`, `PyMuPDF`), DOCX (`python-docx`), TXT, and images (`pytesseract` with OpenCV preprocessing).
- **Sentiment Analysis**: Uses IBM Watson NLU and `vaderSentiment` to determine document tone (Positive, Neutral, Negative) with confidence scores.
- **Keyword and Entity Extraction**: Identifies relevant keywords and entities (e.g., names, phone numbers) using Watson NLU and regex-based local methods.
- **Summarization**: Generates concise summaries using the BART model from Hugging Face Transformers.
- **Question Answering**: Answers user questions (e.g., “What is the phone number?”) using RoBERTa and regex patterns.
- **Web Interface**: Built with Flask and Tailwind CSS, featuring file upload, custom keyword input, result display, and Chart.js visualizations.
- **Output Formats**: Allows downloading analysis results as TXT, JSON, CSV, or PDF, with robust PDF generation using `FPDF`.

---

## Technology Stack

- **Backend**: Python 3.8+, Flask, IBM Watson NLU, `vaderSentiment`, `transformers` (Hugging Face).
- **Text Extraction**: `pdfplumber`, `PyMuPDF`, `python-docx`, `pytesseract`, OpenCV.
- **Frontend**: HTML, Tailwind CSS, Chart.js.
- **Environment**: `.env` for API credentials, Tesseract-OCR for image processing.
- **Logging**: Custom logging to `logs/analyzer.log` and `logs/app.log`.

---

## Project Phases

1. **Research**  
   Defined project scope, evaluated NLP tools, and assessed feasibility. Deliverables included a project proposal and technology stack report.

2. **Design**  
   Created system architecture, data flow diagrams, and UI wireframes. Established modular workflows for text extraction and NLP analysis.

3. **Development**  
   Implemented the prototype with text extraction, NLP modules, and web interface. Addressed multi-format support and API integration.

4. **Testing**  
   Validated functionality, fixed issues (e.g., neutral sentiment scores, PDF download errors), and conducted user acceptance testing.

5. **Deployment**  
   Operationalized the application on a cloud server, configured monitoring, and provided user training.

---

## Key Challenges and Resolutions

- **Neutral Sentiment Scores**: Calibrated `vaderSentiment` thresholds and ensured sufficient input text for IBM Watson to improve score accuracy.
- **PDF Download Errors**: Sanitized text inputs and verified font availability (`DejaVuSans.ttf`) for reliable PDF generation.
- **Summary Generation**: Limited input text to 1000 characters for the BART model to prevent errors.
- **Multi-Format Support**: Integrated multiple libraries (`pdfplumber`, `PyMuPDF`, `pytesseract`) to handle diverse document types.

---

## Test Case

**Primary Test Document**: `Resum.pdf`

| Feature              | Outcome                                            |
|----------------------|----------------------------------------------------|
| Text Extraction      | Name: *Mohammed *, Phone: *+91-123456789*   |
| Sentiment Analysis   | Positive (0.3) using Watson and Vader              |
| Keywords/Entities    | "project", "python",  Mohammed (Person)"    |
| Summary              | Generated concise summary of the resume’s content  |
| Question Answering   | Correctly answered: "What is the phone number?"    |

---

## Repository Structure

Root/
├── app.py
├── analyzer.py
├── .env
├── DejaVuSans.ttf
├── static/
│ ├── uploads/ # Temporary file uploads
│ └── outputs/ # Analysis result downloads
├── templates/
│ └── index.html # Web interface
├── logs/
│ ├── analyzer.log
│ └── app.log
└── documents/
└── Resume.pdf # Test file


---

## Future Enhancements

- Support additional file formats (e.g., PPTX, XLSX).
- Enhance NLP models with fine-tuning for domain-specific documents.
- Implement user authentication and cloud storage for analysis history.
- Optimize performance for larger documents (>10MB) using asynchronous processing.

---

## Conclusion

The **AI Document Analyzer** delivers a powerful, user-friendly solution for automated document analysis, combining advanced NLP with a robust web interface. The project’s phased approach ensured systematic development, testing, and deployment, addressing challenges and meeting objectives. Documentation for each phase is provided to support ongoing maintenance and future enhancements.
