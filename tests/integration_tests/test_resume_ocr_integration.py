import pytest
from src.resume_ocr.resume_ocr import ResumeOCR
import os
import numpy as np

pytestmark = pytest.mark.integration

dataPath = 'data/pdf_resumes'

@pytest.fixture
def resume_ocr():
    return ResumeOCR()

def get_random_pdf_path():
    pdfFilePaths = [f for f in os.listdir(dataPath) if f.endswith(".pdf")]
    assert len(pdfFilePaths) > 0, "No PDF files found in data/pdf_resumes"
    randomIndex = np.random.randint(0, len(pdfFilePaths))
    return os.path.join(dataPath, pdfFilePaths[randomIndex])


@pytest.mark.flaky(max_runs=3, min_passes=1)
def test_end_to_end_resume_ocr_path(resume_ocr):
    pdfPath = get_random_pdf_path()
    resume_ocr.setInputs(pdfPath=pdfPath)
    extractedText = resume_ocr.extractText()

    assert isinstance(extractedText, str), "Extracted text should be a string"
    assert len(extractedText.strip()) > 0, f"Empty text extracted from {pdfPath}"

@pytest.mark.flaky(max_runs=3, min_passes=1)
def test_end_to_end_resume_ocr_bytes(resume_ocr):
    pdfPath = get_random_pdf_path()
    with open(pdfPath, "rb") as f:
        pdfBytes = f.read()

    resume_ocr.setInputs(pdfBytes=pdfBytes)
    extractedText = resume_ocr.extractText()

    assert isinstance(extractedText, str), "Extracted text should be a string"
    assert len(extractedText.strip()) > 0, f"Empty text extracted from bytes of {pdfPath}"