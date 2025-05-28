from flask import Flask, request, render_template, jsonify, send_file, session
from werkzeug.utils import secure_filename
from analyzer import extract_text, analyze_text, answer_question
import os
import json
import csv
import io
import time
import re
from fpdf import FPDF
from dotenv import load_dotenv
import logging
import logging.handlers

# Ensure logs directory exists
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(os.path.join(logs_dir, 'app.log'), maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'files' not in request.files:
        logger.error("No files provided in request")
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    custom_keywords_input = request.form.get('custom_keywords', '')
    custom_keywords = [kw.strip() for kw in re.split(r'[,\s]+', custom_keywords_input) if kw.strip()]
    results = []
    session['analysis_results'] = []  # Initialize session storage

    for i, file in enumerate(files):
        if file.filename == '':
            continue
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        timestamp = str(int(time.time() * 1000))
        output_filename = f'result_{i}_{timestamp}'

        try:
            file.save(file_path)
            if os.path.getsize(file_path) > app.config['MAX_CONTENT_LENGTH']:
                logger.error(f"File {filename} too large")
                return jsonify({'error': f"File {filename} too large. Maximum size is 10MB."}), 400

            file_type = os.path.splitext(filename)[1].lower()
            text = extract_text(file_path, file_type)
            analysis = analyze_text(text, custom_keywords)
            result = {
                'text': text,
                'keywords': analysis['keywords'],
                'entities': analysis['entities'],
                'sentiment': analysis['sentiment'],
                'summary': analysis['summary'],
                'language': analysis['language'],
                'custom_keywords': analysis['custom_keywords'],
                'output_filename': output_filename
            }
            results.append(result)
            session['analysis_results'].append(result)

            # Save as text file
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_filename}.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"File: {filename}\n")
                f.write("Extracted Text:\n")
                f.write(text + "\n\n")
                f.write(f"Language: {analysis['language']}\n")
                f.write(f"Sentiment: {analysis['sentiment']['label']} (Score: {analysis['sentiment']['score']})\n")
                f.write(f"Summary: {analysis['summary']}\n\n")
                f.write("Keywords:\n")
                for kw in analysis['keywords']:
                    f.write(f"{kw['text']} (Relevance: {kw['relevance']})\n")
                f.write("\nEntities:\n")
                for ent in analysis['entities']:
                    f.write(f"{ent['text']} - {ent['type']} (Relevance: {ent['relevance']})\n")
                f.write("\nCustom Keywords:\n")
                for kw in analysis['custom_keywords']:
                    f.write(f"{kw['text']} (Relevance: {kw.get('relevance', 'N/A')})\n")

            logger.info(f"Processed file {filename} successfully")
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}", exc_info=True)
            results.append({"error": f"Error processing {filename}: {str(e)}"})
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    return jsonify(results)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    text = data.get('text')
    question = data.get('question')
    if not text or not question:
        logger.error("Missing text or question in /ask request")
        return jsonify({"error": "Text and question are required"}), 400
    try:
        answer = answer_question(text, question)  # Fixed: Use question, not text
        logger.info(f"Answered question: {question} -> {answer}")
        return jsonify({"answer": answer})
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/download-txt')
def download_txt():
    index = int(request.args.get('index', '0'))
    try:
        analysis_results = session.get('analysis_results', [])
        if not analysis_results or index < 0 or index >= len(analysis_results):
            logger.error(f"Invalid index {index} for download-txt")
            return jsonify({"error": "No result available for download."}), 404
        output_filename = analysis_results[index]['output_filename']
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_filename}.txt")
        if os.path.exists(result_path):
            logger.info(f"Downloading TXT for index {index}")
            return send_file(result_path, as_attachment=True, download_name=f'analysis_result_{index}.txt')
        logger.error(f"TXT file not found: {result_path}")
        return jsonify({"error": "No result available for download."}), 404
    except Exception as e:
        logger.error(f"Error downloading TXT: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed downloading file."}), 500

@app.route('/download-json')
def download_json():
    index = int(request.args.get('index', '0'))
    try:
        analysis_results = session.get('analysis_results', [])
        if not analysis_results or index < 0 or index >= len(analysis_results):
            logger.error(f"Invalid index {index} for download-json")
            return jsonify({"error": "No result available for download."}), 404
        result = analysis_results[index]
        json_data = {
            "file": result['output_filename'],
            "text": result['text'],
            "language": result['language'],
            "sentiment": result['sentiment'],
            "summary": result['summary'],
            "keywords": result['keywords'],
            "entities": result['entities'],
            "custom_keywords": result['custom_keywords']
        }
        logger.info(f"Downloading JSON for index {index}")
        return send_file(
            io.BytesIO(json.dumps(json_data, indent=2).encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'analysis_result_{index}.json'
        )
    except Exception as e:
        logger.error(f"Error downloading JSON: {str(e)}", exc_info=True)
        return jsonify({"error": "Error downloading JSON file."}), 500

@app.route('/download-csv')
def download_csv():
    index = int(request.args.get('index', '0'))
    try:
        analysis_results = session.get('analysis_results', [])
        if not analysis_results or index < 0 or index >= len(analysis_results):
            logger.error(f"Invalid index {index} for download-csv")
            return jsonify({"error": "No result available for download."}), 404
        result = analysis_results[index]
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(["Type", "Text", "Relevance", "Entity Type"])
        for kw in result['keywords']:
            writer.writerow(["Keyword", kw['text'], kw['relevance'], ""])
        for ent in result['entities']:
            writer.writerow(["Entity", ent['text'], ent['relevance'], ent['type']])
        for kw in result['custom_keywords']:
            writer.writerow(["Custom Keyword", kw['text'], kw.get('relevance', 'N/A'), ""])
        output.seek(0)
        logger.info(f"Downloading CSV for index {index}")
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'analysis_result_{index}.csv'
        )
    except Exception as e:
        logger.error(f"Error downloading CSV: {str(e)}", exc_info=True)
        return jsonify({"error": "Error downloading file."}), 500

@app.route('/download-pdf')
def download_pdf():
    index = int(request.args.get('index', '0'))
    pdf_path = None
    try:
        analysis_results = session.get('analysis_results', [])
        if not analysis_results or index < 0 or index >= len(analysis_results):
            logger.error(f"Invalid index {index} for download-pdf")
            return jsonify({"error": "No result available for download."}), 404
        result = analysis_results[index]

        # Sanitize text to avoid encoding issues
        def sanitize_text(text):
            if not isinstance(text, str):
                text = str(text)
            return text.encode('utf-8', errors='replace').decode('utf-8').replace('\ufffd', '')

        # Verify font file
        font_path = 'DejaVuSans.ttf'
        if not os.path.exists(font_path):
            logger.error(f"Font file {font_path} not found")
            return jsonify({"error": "Font file missing. Please add DejaVuSans.ttf to project root."}), 500

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', '', 16)
        pdf.cell(0, 10, "AI Document Analysis Report", ln=True, align='C')
        pdf.set_font('DejaVu', '', 12)
        pdf.ln(10)

        # File
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 8, "File", ln=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 8, sanitize_text(result['output_filename']))
        pdf.ln(5)

        # Language
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 8, "Language", ln=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 8, sanitize_text(result['language']))
        pdf.ln(5)

        # Sentiment
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 8, "Sentiment", ln=True)
        pdf.set_font('DejaVu', '', 12)
        sentiment = result['sentiment']
        sentiment_text = f"{sanitize_text(sentiment['label'])} (Score: {sanitize_text(sentiment['score'])})" if isinstance(sentiment, dict) else sanitize_text(sentiment)
        pdf.multi_cell(0, 8, sentiment_text)
        pdf.ln(5)

        # Summary
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 8, "Summary", ln=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 8, sanitize_text(result['summary']))
        pdf.ln(5)

        # Extracted Text (limited to 1000 chars)
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 8, "Extracted Text", ln=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 8, sanitize_text(result['text'][:1000]))
        pdf.ln(5)

        # Keywords
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 8, "Keywords", ln=True)
        pdf.set_font('DejaVu', '', 12)
        for kw in result['keywords']:
            pdf.multi_cell(0, 8, f"- {sanitize_text(kw['text'])} (Relevance: {sanitize_text(kw['relevance'])})")
        pdf.ln(5)

        # Entities
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 8, "Entities", ln=True)
        pdf.set_font('DejaVu', '', 12)
        for ent in result['entities']:
            pdf.multi_cell(0, 8, f"- {sanitize_text(ent['text'])} ({sanitize_text(ent['type'])}, Relevance: {sanitize_text(ent['relevance'])})")
        pdf.ln(5)

        # Custom Keywords
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 8, "Custom Keywords", ln=True)
        pdf.set_font('DejaVu', '', 12)
        for kw in result['custom_keywords']:
            pdf.multi_cell(0, 8, f"- {sanitize_text(kw['text'])} (Relevance: {sanitize_text(kw.get('relevance', 'N/A'))})")
        pdf.ln(5)

        pdf_filename = f"{result['output_filename']}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        pdf.output(pdf_path)

        logger.info(f"Generated PDF: {pdf_path}")
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'analysis_result_{index}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        logger.error(f"Error generating PDF for index {index}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error generating PDF: {str(e)}"}), 500
    finally:
        if pdf_path and os.path.exists(pdf_path):
            try:
                time.sleep(1)  # Ensure file is released
                os.remove(pdf_path)
                logger.info(f"Cleaned up PDF: {pdf_path}")
            except Exception as e:
                logger.error(f"Failed to clean up PDF {pdf_path}: {str(e)}", exc_info=True)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)