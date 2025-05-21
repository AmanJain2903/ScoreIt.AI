import pytest
from src.matchmaker_engine.matching_engine import MatchingEngine
from src.resume_ocr.resume_ocr import ResumeOCR
from src.jd_scraper.jd_scraper import JobDescriptionScraper
from src.resume_extractor_agent.resume_agent import ResumeAgent
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv()

API_NAME = "OPENROUTER_API_KEY"
MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free"

RAgent = ResumeAgent(
    apiKey=os.getenv(API_NAME),
    modelName=MODEL_NAME,
    systemPrompt=None, # Default system prompt will be used
    useDefaultModelIfNone=True,
    useDefaultSystemPromptIfNone=True
)

JDAgent = JobDescriptionAgent(
    apiKey=os.getenv(API_NAME),
    modelName=MODEL_NAME,
    systemPrompt=None, # Default system prompt will be used
    useDefaultModelIfNone=True,
    useDefaultSystemPromptIfNone=True
)

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
    RAgent.setUserPrompt(resume)
    resumeJson = RAgent.getJsonOutput()
    JDAgent.setUserPrompt(jd)
    jdJson = JDAgent.getJsonOutput()
    matchmaker_engine.resumeJson = resumeJson
    matchmaker_engine.jdJson = jdJson
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
    RAgent.setUserPrompt(resume)
    resumeJson = RAgent.getJsonOutput()
    JDAgent.setUserPrompt(jd)
    jdJson = JDAgent.getJsonOutput()
    matchmaker_engine.resumeJson = resumeJson
    matchmaker_engine.jdJson = jdJson
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
    RAgent.setUserPrompt(resume)
    resumeJson = RAgent.getJsonOutput()
    JDAgent.setUserPrompt(jd)
    jdJson = JDAgent.getJsonOutput()
    matchmaker_engine.resumeJson = resumeJson
    matchmaker_engine.jdJson = jdJson
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
    RAgent.setUserPrompt(resume)
    resumeJson = RAgent.getJsonOutput()
    JDAgent.setUserPrompt(jd)
    jdJson = JDAgent.getJsonOutput()
    matchmaker_engine.resumeJson = resumeJson
    matchmaker_engine.jdJson = jdJson
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

    