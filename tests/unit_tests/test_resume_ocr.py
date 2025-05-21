import pytest
from unittest.mock import patch, MagicMock
from src.resume_ocr.resume_ocr import ResumeOCR

pytestmark = pytest.mark.unit

@pytest.fixture
def resume_ocr():
    return ResumeOCR()

@pytest.fixture
def mock_fitz_doc():
    mock_page = MagicMock()
    mock_page.get_text.return_value = "sample extracted text"

    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [mock_page]
    return mock_doc

def test_initialization_success(resume_ocr):
    assert resume_ocr.pdfPath is None
    assert resume_ocr.pdfBytes is None
    assert resume_ocr.resumeText == ""

def test_setInputs_path_success(resume_ocr):
    resume_ocr.setInputs(pdfPath="sample.pdf")
    assert resume_ocr.pdfPath == "sample.pdf"
    assert resume_ocr.pdfBytes is None

def test_setInputs_bytes_success(resume_ocr):
    resume_ocr.setInputs(pdfBytes=b"sample bytes")
    assert resume_ocr.pdfPath is None
    assert resume_ocr.pdfBytes == b"sample bytes"

def test_setInputs_both_fail(resume_ocr):
    with pytest.raises(ValueError):
        resume_ocr.setInputs(pdfPath="sample.pdf", pdfBytes=b"bytes")

def test_setInputs_none_fail(resume_ocr):
    with pytest.raises(ValueError):
        resume_ocr.setInputs()

def test_setInputs_invalid_type_path_fail(resume_ocr):
    with pytest.raises(TypeError):
        resume_ocr.setInputs(pdfPath=123)

def test_setInputs_invalid_type_bytes_fail(resume_ocr):
    with pytest.raises(TypeError):
        resume_ocr.setInputs(pdfBytes="not bytes")

@patch("src.resume_ocr.resume_ocr.fitz.open")
def test_extractText_pdfPath_success(mock_fitz_open, resume_ocr, mock_fitz_doc):
    mock_fitz_open.return_value.__enter__.return_value = mock_fitz_doc
    resume_ocr.setInputs(pdfPath="sample.pdf")
    result = resume_ocr.extractText()

    assert result == "sample extracted text"
    assert resume_ocr.resumeText == result
    mock_fitz_open.assert_called_once_with("sample.pdf")

@patch("src.resume_ocr.resume_ocr.fitz.open")
def test_extractText_pdfBytes_success(mock_fitz_open, resume_ocr, mock_fitz_doc):
    mock_fitz_open.return_value.__enter__.return_value = mock_fitz_doc
    resume_ocr.setInputs(pdfBytes=b"sample bytes")
    result = resume_ocr.extractText()

    assert result == "sample extracted text"
    assert resume_ocr.resumeText == result
    mock_fitz_open.assert_called_once_with(stream=b"sample bytes", filetype="pdf")

def test_extractText_no_inputs_fail(resume_ocr):
    with pytest.raises(ValueError):
        resume_ocr.extractText()

def test_extractText_already_extracted(resume_ocr):
    resume_ocr.resumeText = "already extracted"
    result = resume_ocr.extractText()
    assert result == "already extracted"

def test_resetOCR_success(resume_ocr):
    resume_ocr.setInputs(pdfPath="sample.pdf")
    resume_ocr.resumeText = "text"
    resume_ocr.resetOCR()
    assert resume_ocr.pdfPath is None
    assert resume_ocr.pdfBytes is None
    assert resume_ocr.resumeText == ""