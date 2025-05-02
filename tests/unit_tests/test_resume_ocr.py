import pytest
from unittest.mock import patch, MagicMock
from src.resume_ocr.resume_ocr import ResumeOCR
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def resume_ocr():
    ocr = ResumeOCR()
    return ocr

@pytest.fixture
def tesseract_mock():
    with patch("pytesseract.image_to_string") as mock:
        yield mock
        mock.return_value = "sample text"

def test_initialization_success(resume_ocr):
    assert resume_ocr.pdfPath is None
    assert resume_ocr.pdfBytes is None
    assert isinstance(resume_ocr.resumeText, str)
    assert resume_ocr.resumeText == ""

def test_setInputs_path_success(resume_ocr):
    pdfPath = "sample.pdf"
    resume_ocr.setInputs(pdfPath=pdfPath)
    assert resume_ocr.pdfPath == pdfPath
    assert resume_ocr.pdfBytes is None
    assert resume_ocr.resumeText == ""

def test_setInputs_bytes_success(resume_ocr):
    pdfBytes = b"sample bytes"
    resume_ocr.setInputs(pdfBytes=pdfBytes)
    assert resume_ocr.pdfPath is None
    assert resume_ocr.pdfBytes == pdfBytes
    assert resume_ocr.resumeText == ""

def test_setInputs_both_fail(resume_ocr):
    pdfPath = "sample.pdf"
    pdfBytes = b"sample bytes"
    with pytest.raises(ValueError, match="Only one of pdfPath or pdfBytes should be provided."):
        resume_ocr.setInputs(pdfPath=pdfPath, pdfBytes=pdfBytes)

def test_setInputs_none_fail(resume_ocr):
    with pytest.raises(ValueError, match="Either pdfPath or pdfBytes must be provided."):
        resume_ocr.setInputs()

def test_setInputs_invalid_type_path_fail(resume_ocr):
    pdfPath = 12345
    with pytest.raises(TypeError, match="pdfPath must be a string."):
        resume_ocr.setInputs(pdfPath=pdfPath)

def test_setInputs_invalid_type_bytes_fail(resume_ocr):
    pdfBytes = "not bytes"
    with pytest.raises(TypeError, match="pdfBytes must be bytes."):
        resume_ocr.setInputs(pdfBytes=pdfBytes)
    
def test_extractText_pdfPath_success(resume_ocr, tesseract_mock):
    pdfPath = "sample.pdf"
    resume_ocr.setInputs(pdfPath=pdfPath)
    tesseract_mock.return_value = "extracted text"
    
    with patch("src.resume_ocr.resume_ocr.convert_from_path") as mock_convert:
        mock_convert.return_value = [MagicMock()]
        result = resume_ocr.extractText()
    
    assert result == "extracted text"
    assert resume_ocr.resumeText == "extracted text"
    mock_convert.assert_called_once_with(pdfPath)
    tesseract_mock.assert_called_once()

def test_extractText_pdfBytes_success(resume_ocr, tesseract_mock):
    pdfBytes = b"sample bytes"
    resume_ocr.setInputs(pdfBytes=pdfBytes)
    tesseract_mock.return_value = "extracted text"
    
    with patch("src.resume_ocr.resume_ocr.convert_from_bytes") as mock_convert:
        mock_convert.return_value = [MagicMock()]
        result = resume_ocr.extractText()
    
    assert result == "extracted text"
    assert resume_ocr.resumeText == "extracted text"
    mock_convert.assert_called_once_with(pdfBytes)
    tesseract_mock.assert_called_once()

def test_extractText_no_inputs_fail(resume_ocr):
    with pytest.raises(ValueError, match="pdfPath or pdfBytes must be set before extracting text."):
        resume_ocr.extractText()

def test_extractText_already_extracted(resume_ocr, tesseract_mock):
    resume_ocr.resumeText = "already extracted text"
    result = resume_ocr.extractText()
    
    assert result == "already extracted text"
    tesseract_mock.assert_not_called()

def test_resetOCR_success(resume_ocr):
    pdfPath = "sample.pdf"
    pdfBytes = b"sample bytes"
    resume_ocr.setInputs(pdfPath=pdfPath)
    
    resume_ocr.resetOCR()
    
    assert resume_ocr.pdfPath is None
    assert resume_ocr.pdfBytes is None
    assert resume_ocr.resumeText == ""



