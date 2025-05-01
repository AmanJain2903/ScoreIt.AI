import pytest
from src.matchmaker_engine.matching_engine import MatchingEngine
import os
import pandas as pd
import numpy as np

pytestmark = pytest.mark.integration

descriptionDatasetPath = "data/job_description_dataset.csv"
resumeDatasetPath = "data/resume_dataset.csv"

@pytest.fixture
def matchmaker_engine():
    engine = MatchingEngine()
    return engine

def test_end_to_end_matchmaker(matchmaker_engine):
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
    