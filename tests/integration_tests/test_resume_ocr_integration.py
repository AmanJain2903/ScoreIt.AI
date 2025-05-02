import pytest
from src.resume_ocr.resume_ocr import ResumeOCR
import os
import pandas as pd
import numpy as np

pytestmark = pytest.mark.integration

dataPath = 'data/pdf_resumes'

@pytest.fixture
def resume_ocr():
    ocr = ResumeOCR()
    return ocr

def test_end_to_end_resume_ocr_path(resume_ocr):
    pdfFilePaths = os.listdir(dataPath)
    randomIndex = np.random.randint(0, len(pdfFilePaths))
    randomFilePath = os.path.join(dataPath, pdfFilePaths[randomIndex])
    resume_ocr.setInputs(pdfPath=randomFilePath)
    extractedText = resume_ocr.extractText()
    assert isinstance(extractedText, str)
    assert len(extractedText) > 0
    resume_ocr.resetOCR()

def test_end_to_end_resume_ocr_bytes(resume_ocr):
    pdfFilePaths = os.listdir(dataPath)
    randomIndex = np.random.randint(0, len(pdfFilePaths))
    randomFilePath = os.path.join(dataPath, pdfFilePaths[randomIndex])
    with open(randomFilePath, "rb") as f:
        pdfBytes = f.read()
    resume_ocr.setInputs(pdfBytes=pdfBytes)
    extractedText = resume_ocr.extractText()
    assert isinstance(extractedText, str)
    assert len(extractedText) > 0
    resume_ocr.resetOCR()
