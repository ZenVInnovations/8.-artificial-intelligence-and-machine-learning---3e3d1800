# phase5_deployment_ai_document_analyzer.py

import os
from flask import Flask, request, render_template_string, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
import logging
from dotenv import load_dotenv

# Load environment variables (e.g., IBM Watson API keys)
load_dotenv()

# Setup Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simple index page template
index_html = """
<!doctype html>
<html>
<head><title>AI Document Analyzer - Upload</title></head>
<body>
  <h1>Upload Document for Analysis</h1>
  <form method="POST" action="/upload" enctype="multipart/form-data">
    <input type="file" name="file" required />
    <input type="submit" value="Analyze" />
  </form>
</body>
</html>
"""

# Simple results page template
results_html = """
<!doctype html>
<html>
<head><title>Analysis Results</title></head>
<body>
  <h1>Document Analysis Results</h1>
  <p><strong>Sentiment:</strong> {{ analysis.sentiment }}</p>
  <p><strong>Keywords:</strong> {{ analysis.keywords | join(', ') }}</p>
  <p><strong>Summary:</strong> {{ analysis.summary }}</p>
  <p><strong>Entities:</strong> {{ analysis.entities | join(', ') }}</p>
  <a href="/download-txt">Download Results as TXT</a><br><br>
  <a href="/">Analyze Another Document</a>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(index_html)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logging.error("No file part in request")
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        logging.error("No selected file")
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join('static/uploads', filename)
        file.save(upload_path)
        logging.info(f"File saved at {upload_path}")
        print(f"[OUTPUT] File saved at {upload_path}")

        session['uploaded_file'] = upload_path
        
        # Placeholder for text extraction
        extracted_text = "This is the extracted text from the uploaded document."
        print(f"[OUTPUT] Extracted Text: {extracted_text}")

        # Placeholder for NLP analysis results
        analysis_results = {
            'sentiment': 'Positive',
            'keywords': ['project', 'deadline', 'team'],
            'summary': 'This document outlines the project timeline and key deadlines.',
            'entities': ['Tejesh', 'AI Document Analyzer', 'Deadline']
        }
        print("[OUTPUT] Analysis Results:")
        print(f" Sentiment: {analysis_results['sentiment']}")
        print(f" Keywords: {analysis_results['keywords']}")
        print(f" Summary: {analysis_results['summary']}")
        print(f" Entities: {analysis_results['entities']}")

        session['analysis_results'] = analysis_results
        return redirect(url_for('results'))
    else:
        logging.error("Unsupported file format")
        return "Unsupported file format", 400

@app.route('/results')
def results():
    analysis = session.get('analysis_results', None)
    if not analysis:
        return redirect(url_for('index'))
    return render_template_string(results_html, analysis=analysis)

@app.route('/download-txt')
def download_txt():
    analysis = session.get('analysis_results', None)
    if not analysis:
        return redirect(url_for('index'))
    output_path = 'static/outputs/analysis_result.txt'
    with open(output_path, 'w') as f:
        f.write("Sentiment: {}\n".format(analysis['sentiment']))
        f.write("Keywords: {}\n".format(', '.join(analysis['keywords'])))
        f.write("Summary: {}\n".format(analysis['summary']))
        f.write("Entities: {}\n".format(', '.join(analysis['entities'])))
    logging.info(f"TXT file created at {output_path}")
    print(f"[OUTPUT] TXT file created at {output_path}")
    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/outputs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    print("Starting AI Document Analyzer Deployment Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)


"""
=== Expected Console Output on File Upload and Analysis ===

Starting AI Document Analyzer Deployment Server...
[OUTPUT] File saved at static/uploads/Resume_Tejesh.pdf
[OUTPUT] Extracted Text: This is the extracted text from the uploaded document.
[OUTPUT] Analysis Results:
 Sentiment: Positive
 Keywords: ['project', 'deadline', 'team']
 Summary: This document outlines the project timeline and key deadlines.
 Entities: ['Tejesh', 'AI Document Analyzer', 'Deadline']
[OUTPUT] TXT file created at static/outputs/analysis_result.txt


=== Contents of static/outputs/analysis_result.txt ===

Sentiment: Positive
Keywords: project, deadline, team
Summary: This document outlines the project timeline and key deadlines.
Entities: Tejesh, AI Document Analyzer, Deadline

"""
