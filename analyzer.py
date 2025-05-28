import os
import re
import logging
import time
from collections import Counter
from dotenv import load_dotenv
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions, EntitiesOptions, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pdfplumber
import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
import cv2
import numpy as np
from transformers import pipeline
from langdetect import detect, LangDetectException

# Ensure logs directory exists
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, 'analyzer.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize VADER for sentiment analysis
vader_analyzer = SentimentIntensityAnalyzer()

def preprocess_image(image_path):
    """Enhance image for better OCR accuracy."""
    try:
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        img = cv2.GaussianBlur(img, (5, 5), 0)
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        return Image.fromarray(img)
    except Exception as e:
        logger.error(f"Image preprocessing failed for {image_path}: {str(e)}", exc_info=True)
        raise ValueError(f"Image preprocessing failed: {str(e)}")

def extract_text(file_path, file_type):
    """Extract text from various file types (images, PDFs, DOCX, TXT)."""
    try:
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        if file_type in ['.png', '.jpg', '.jpeg']:
            img = preprocess_image(file_path)
            text = pytesseract.image_to_string(img, config='--psm 6').strip()
        elif file_type == '.pdf':
            # Try pdfplumber first
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ''.join(page.extract_text() or '' for page in pdf.pages).strip()
            except Exception:
                # Fallback to PyMuPDF
                doc = fitz.open(file_path)
                text = ''.join(page.get_text() for page in doc).strip()
                doc.close()
        elif file_type == '.docx':
            doc = docx.Document(file_path)
            text = '\n'.join(para.text for para in doc.paragraphs if para.text).strip()
        elif file_type == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read().strip()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        logger.info(f"Extracted text from {file_path} ({len(text)} characters)")
        return text or "No text extracted."
    except Exception as e:
        logger.error(f"Text extraction failed for {file_path}: {str(e)}", exc_info=True)
        return ""

def local_keyword_extraction(text):
    """Extract keywords using frequency analysis."""
    try:
        words = re.findall(r'\b\w+\b', text.lower())
        stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with'}
        word_counts = Counter(word for word in words if word not in stop_words and len(word) > 3)
        total_count = sum(word_counts.values())
        keywords = [
            {'text': word, 'relevance': round(count / total_count, 4) if total_count else 0.5}
            for word, count in word_counts.most_common(10)
        ]
        logger.info(f"Extracted {len(keywords)} local keywords")
        return keywords
    except Exception as e:
        logger.error(f"Local keyword extraction failed: {str(e)}", exc_info=True)
        return []

def local_entity_extraction(text):
    """Extract entities using regex patterns."""
    try:
        entities = []
        # Name (e.g., Mohammed Musaib)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        for match in re.finditer(name_pattern, text):
            entities.append({'text': match.group(), 'type': 'Person', 'relevance': 0.95})

        # Phone (e.g., +91-7795888591, flexible formats)
        phone_pattern = r'\+?\d{1,4}[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
        for match in re.finditer(phone_pattern, text):
            entities.append({'text': match.group(), 'type': 'Phone', 'relevance': 0.95})

        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append({'text': match.group(), 'type': 'Email', 'relevance': 0.95})

        # Location (e.g., Bagepalli, Karnataka)
        location_pattern = r'\b[A-Z][a-z]+, [A-Z][a-z]+\b'
        for match in re.finditer(location_pattern, text):
            entities.append({'text': match.group(), 'type': 'Location', 'relevance': 0.90})

        logger.info(f"Extracted {len(entities)} local entities")
        return entities[:10]
    except Exception as e:
        logger.error(f"Local entity extraction failed: {str(e)}", exc_info=True)
        return []

def local_sentiment_analysis(text):
    """Perform sentiment analysis using VADER."""
    try:
        scores = vader_analyzer.polarity_scores(text)
        compound = scores['compound']  # Range: -1 to 1
        if compound > 0.05:
            label = 'Positive'
        elif compound < -0.05:
            label = 'Negative'
        else:
            label = 'Neutral'
        logger.info(f"Local sentiment: {label} (Score: {compound})")
        return {'label': label, 'score': compound}
    except Exception as e:
        logger.error(f"Local sentiment analysis failed: {str(e)}", exc_info=True)
        return {'label': 'Neutral', 'score': 0.0}

def summarize_text(text):
    """Generate a summary using BART."""
    try:
        if len(text.split()) < 10:
            logger.warning("Text too short for summarization")
            return "Text too short to summarize."
        
        # Lazy initialization of summarizer
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        max_length = min(len(text.split()) // 2, 150)
        min_length = min(max_length // 2, 50)
        summary = summarizer(text[:1000], max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
        logger.info("Summary generated successfully")
        return summary
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}", exc_info=True)
        return "Error generating summary."

def detect_language(text):
    """Detect the language of the text."""
    try:
        lang = detect(text)
        logger.info(f"Detected language: {lang}")
        return lang
    except LangDetectException as e:
        logger.error(f"Language detection failed: {str(e)}", exc_info=True)
        return 'en'

def extract_custom_keywords(text, custom_keywords):
    """Extract user-defined keywords with frequency-based relevance."""
    try:
        if not text or not custom_keywords:
            return []
        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)
        word_counts = Counter(words)
        results = []
        for kw in (kw.strip().lower() for kw in custom_keywords if kw.strip()):
            count = word_counts.get(kw, 0)
            relevance = min(count / total_words * 10, 1.0) if total_words else 0.0
            if count > 0:
                results.append({'text': kw, 'relevance': round(relevance, 4)})
        logger.info(f"Extracted {len(results)} custom keywords")
        return results
    except Exception as e:
        logger.error(f"Custom keyword extraction failed: {str(e)}", exc_info=True)
        return []

def analyze_text(text, custom_keywords=None):
    """Analyze text using Watson NLU or local fallback."""
    if not isinstance(text, str) or not text.strip():
        logger.warning("Empty or invalid text input")
        return {
            'keywords': [],
            'entities': [],
            'sentiment': {'label': 'Neutral', 'score': 0.0},
            'summary': "No text provided.",
            'language': 'en',
            'custom_keywords': []
        }

    if custom_keywords is None:
        custom_keywords = []

    # Sanitize text for PDF compatibility
    text = text.encode('utf-8', errors='replace').decode('utf-8')

    result = {
        'keywords': [],
        'entities': [],
        'sentiment': {'label': 'Neutral', 'score': 0.0},
        'summary': "",
        'language': detect_language(text),
        'custom_keywords': extract_custom_keywords(text, custom_keywords)
    }

    # Watson NLU with retry
    api_key = os.getenv('WATSON_API_KEY')
    service_url = os.getenv('WATSON_SERVICE_URL')
    if api_key and service_url:
        for attempt in range(3):
            try:
                authenticator = IAMAuthenticator(api_key)
                nlu = NaturalLanguageUnderstandingV1(version='2021-08-01', authenticator=authenticator)
                nlu.set_service_url(service_url)
                nlu_result = nlu.analyze(
                    text=text,
                    features=Features(
                        keywords=KeywordsOptions(limit=10),
                        entities=EntitiesOptions(limit=10),
                        sentiment=SentimentOptions()
                    ),
                    language=result['language'] if result['language'] != 'en' else None
                ).get_result()
                result['keywords'] = [{'text': k['text'], 'relevance': k['relevance']} for k in nlu_result.get('keywords', [])]
                result['entities'] = [{'text': e['text'], 'type': e['type'], 'relevance': e['relevance']} for k in nlu_result.get('entities', [])]
                result['sentiment'] = {
                    'label': nlu_result['sentiment']['document']['label'].capitalize(),
                    'score': nlu_result['sentiment']['document']['score']
                }
                logger.info("Watson NLU analysis successful")
                break
            except Exception as e:
                logger.error(f"Watson NLU attempt {attempt + 1} failed: {str(e)}", exc_info=True)
                if attempt == 2:
                    logger.warning("Max Watson NLU retries reached, using local analysis")
                    result['keywords'] = local_keyword_extraction(text)
                    result['entities'] = local_entity_extraction(text)
                    result['sentiment'] = local_sentiment_analysis(text)
                time.sleep(1)

    else:
        logger.warning("Watson API credentials missing, using local analysis")
        result['keywords'] = local_keyword_extraction(text)
        result['entities'] = local_entity_extraction(text)
        result['sentiment'] = local_sentiment_analysis(text)

    result['summary'] = summarize_text(text)
    return result

def answer_question(text, question):
    """Answer a question based on the text."""
    try:
        if not isinstance(text, str) or not text.strip() or not isinstance(question, str) or not question.strip():
            logger.warning("Invalid text or question input")
            return "Invalid input."

        # Quick regex for common questions
        if "phone" in question.lower():
            phone_pattern = r'\+?\d{1,4}[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
            match = re.search(phone_pattern, text)
            if match:
                return match.group()

        if "name" in question.lower():
            name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            match = re.search(name_pattern, text)
            if match:
                return match.group()

        # Lazy initialization of QA pipeline
        qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
        result = qa_pipeline(question=question, context=text[:1000])  # Limit context
        logger.info(f"Answered question: {question} -> {result['answer']}")
        return result['answer'].strip()
    except Exception as e:
        logger.error(f"Question answering failed: {str(e)}", exc_info=True)
        return "Unable to answer the question."

if __name__ == '__main__':
    try:
        # Test with sample file
        file_path = 'documents/Resume_Musaib.pdf'
        file_type = '.pdf'
        text = extract_text(file_path, file_type)
        logger.info(f"Extracted Text (first 100 chars): {text[:100]}...")
        analysis = analyze_text(text, custom_keywords=["project", "deadline"])
        logger.info("Analysis Results:")
        logger.info(f"Language: {analysis['language']}")
        logger.info(f"Sentiment: {analysis['sentiment']['label']} (Score: {analysis['sentiment']['score']})")
        logger.info(f"Summary: {analysis['summary']}")
        logger.info("Keywords:")
        for kw in analysis['keywords']:
            logger.info(f"  {kw['text']} (Relevance: {kw['relevance']})")
        logger.info("Entities:")
        for ent in analysis['entities']:
            logger.info(f"  {ent['text']} ({ent['type']}, Relevance: {ent['relevance']})")
        logger.info("Custom Keywords:")
        for ck in analysis['custom_keywords']:
            logger.info(f"  {ck['text']} (Relevance: {ck['relevance']})")
        questions = ["What is the name on the resume?", "What is the phone number?"]
        for q in questions:
            answer = answer_question(text, q)
            logger.info(f"Question: {q} | Answer: {answer}")
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}", exc_info=True)