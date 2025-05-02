import pytest
from src.matchmaker_engine.matching_engine import MatchingEngine
from src.resume_ocr.resume_ocr import ResumeOCR
from src.jd_scraper.jd_scraper import JobDescriptionScraper
import os
import pandas as pd
import numpy as np

pytestmark = pytest.mark.integration

descriptionDatasetPath = "data/job_description_dataset.csv"
resumeDatasetPath = "data/resume_dataset.csv"
pdfResumePath = "data/pdf_resumes"

@pytest.fixture
def matchmaker_engine():
    engine = MatchingEngine()
    return engine

def test_end_to_end_matchmaker_text(matchmaker_engine):
    descriptionDataset = pd.read_csv(descriptionDatasetPath)
    resumeDataset = pd.read_csv(resumeDatasetPath)
    randomIndex = np.random.randint(0, len(descriptionDataset))
    resume = resumeDataset['Resume'].iloc[randomIndex]
    jd = descriptionDataset['Description'].iloc[randomIndex]

    matchmaker_engine.setInputs(resume, jd)
    report = matchmaker_engine.getMatch()

    assert isinstance(report, dict)
    expected_keys = [
    "TECHNICAL_SKILL",
    "TOOL",
    "EDUCATION",
    "EXPERIENCE",
    "DESIGNATION",
    "SOFT_SKILL",
    "CERTIFICATION"
    ]
    for key in expected_keys:
        assert key in report
        assert isinstance(report[key], float)

def test_end_to_end_matchmaker_pdf_path(matchmaker_engine):
    pdfResumeFiles = os.listdir(pdfResumePath)
    randomIndex = np.random.randint(0, len(pdfResumeFiles))
    resumePath = os.path.join(pdfResumePath, pdfResumeFiles[randomIndex])
    ocr = ResumeOCR()
    ocr.setInputs(pdfPath=resumePath)
    resume = ocr.extractText()
    descriptionDataset = pd.read_csv(descriptionDatasetPath)
    randomIndex = np.random.randint(0, len(descriptionDataset))
    jd = descriptionDataset['Description'].iloc[randomIndex]
    matchmaker_engine.setInputs(resume, jd)
    report = matchmaker_engine.getMatch()
    assert isinstance(report, dict)
    expected_keys = [
    "TECHNICAL_SKILL",
    "TOOL", 
    "EDUCATION",
    "EXPERIENCE",
    "DESIGNATION",
    "SOFT_SKILL",
    "CERTIFICATION"
    ]
    for key in expected_keys:
        assert key in report
        assert isinstance(report[key], float)

def test_end_to_end_matchmaker_pdf_bytes(matchmaker_engine):
    pdfResumeFiles = os.listdir(pdfResumePath)
    randomIndex = np.random.randint(0, len(pdfResumeFiles))
    resumePath = os.path.join(pdfResumePath, pdfResumeFiles[randomIndex])
    with open(resumePath, "rb") as f:
        resumeBytes = f.read()
    ocr = ResumeOCR()
    ocr.setInputs(pdfBytes=resumeBytes)
    resume = ocr.extractText()
    descriptionDataset = pd.read_csv(descriptionDatasetPath)
    randomIndex = np.random.randint(0, len(descriptionDataset))
    jd = descriptionDataset['Description'].iloc[randomIndex]
    matchmaker_engine.setInputs(resume, jd)
    report = matchmaker_engine.getMatch()
    assert isinstance(report, dict)
    expected_keys = [
    "TECHNICAL_SKILL",
    "TOOL", 
    "EDUCATION",
    "EXPERIENCE",
    "DESIGNATION",
    "SOFT_SKILL",
    "CERTIFICATION"
    ]
    for key in expected_keys:
        assert key in report
        assert isinstance(report[key], float)

def test_end_to_end_matchmaker_with_jd_link(matchmaker_engine):
    resumeDataset = pd.read_csv(resumeDatasetPath)
    randomIndex = np.random.randint(0, len(resumeDataset))
    resume = resumeDataset['Resume'].iloc[randomIndex]
    jdLink = "https://www.linkedin.com/jobs/view/4197961513"
    jdScraper = JobDescriptionScraper()
    jdScraper.setInputs(jdLink)
    jd = jdScraper.extractJobDescription()
    matchmaker_engine.setInputs(resume, jd)
    report = matchmaker_engine.getMatch()
    assert isinstance(report, dict)
    expected_keys = [
    "TECHNICAL_SKILL",
    "TOOL", 
    "EDUCATION",
    "EXPERIENCE",
    "DESIGNATION",
    "SOFT_SKILL",
    "CERTIFICATION"
    ]
    for key in expected_keys:
        assert key in report
        assert isinstance(report[key], float)

    