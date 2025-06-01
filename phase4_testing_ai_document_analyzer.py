
import unittest
import time
import io
from app import app
from extractor import extract_text_from_pdf, extract_text_from_docx, extract_text_from_image
from nlp import analyze_sentiment_vader, summarize_text

class TestTextExtraction(unittest.TestCase):
    def test_pdf_extraction(self):
        text = extract_text_from_pdf("documents/Resume_Tejesh.pdf")
        self.assertTrue("Musaib" in text)

    def test_docx_extraction(self):
        text = extract_text_from_docx("documents/sample.docx")
        self.assertGreater(len(text), 50)

    def test_image_extraction(self):
        text = extract_text_from_image("documents/sample_image.png")
        self.assertIsInstance(text, str)

class TestNLPModule(unittest.TestCase):
    def test_sentiment(self):
        result = analyze_sentiment_vader("I am very happy with this product!")
        self.assertEqual(result['sentiment'], "positive")

    def test_summary(self):
        long_text = "This is a long sample text. " * 100
        summary = summarize_text(long_text[:1000])
        self.assertIsInstance(summary, str)

class TestWebInterface(unittest.TestCase):
    def test_file_upload_and_analyze(self):
        tester = app.test_client()
        with open("documents/Resume_Musaib.pdf", 'rb') as file:
            data = {
                'file': (io.BytesIO(file.read()), "Resume_Musaib.pdf"),
                'keywords': 'project, deadline'
            }
            response = tester.post('/analyze', content_type='multipart/form-data', data=data)
            self.assertIn(b"Analysis Results", response.data)

    def test_multiple_uploads(self):
        tester = app.test_client()
        for _ in range(5):
            with open("documents/Resume_Musaib.pdf", 'rb') as file:
                response = tester.post('/analyze', content_type='multipart/form-data', data={
                    'file': (io.BytesIO(file.read()), "Resume_Musaib.pdf"),
                    'keywords': 'AI, deadline'
                })
                self.assertEqual(response.status_code, 200)

class TestPerformance(unittest.TestCase):
    def test_processing_time(self):
        start = time.time()
        text = extract_text_from_pdf("documents/Resume_Musaib.pdf")
        duration = time.time() - start
        self.assertLess(duration, 5)

if __name__ == '__main__':
    unittest.main()
