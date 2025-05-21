import pytest
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
import os
import pandas as pd
import numpy as np

pytestmark = pytest.mark.integration

dataPath = 'data/job_description_dataset.csv'

@pytest.fixture
def jd_agent():
    api_key = os.getenv("OPENROUTER_API_KEY")

    return JobDescriptionAgent(
        apiKey=api_key,
        modelName=None,
        systemPrompt=None,
        useDefaultModelIfNone=True,
        useDefaultSystemPromptIfNone=True,
    )

def test_jd_agent_end_to_end(jd_agent):
    dataset = pd.read_csv(dataPath)
    randomIndex = np.random.randint(0, len(dataset))
    description = dataset['Description'].iloc[randomIndex]
    
    while pd.isna(description) or len(description) < 0 or not isinstance(description, str):
        randomIndex = np.random.randint(0, len(dataset))
        description = dataset['Description'].iloc[randomIndex]

    jd_agent.setUserPrompt(description)
    output = jd_agent.getJsonOutput()

    assert isinstance(output, dict)
    expected_keys = [
    "TECHNICAL_SKILL",
    "COMPANY_NAME",
    "TOOL",
    "EDUCATION",
    "EXPERIENCE",
    "DESIGNATION",
    "LOCATION",
    "LANGUAGE",
    "SOFT_SKILL",
    "PAY",
    "CERTIFICATION"
    ]
    for key in expected_keys:
        assert key in output
        assert isinstance(output[key], str)
    
    # Strict check for the output
    # assert output["TECHNICAL_SKILL"] == "Python, TensorFlow, cloud computing"
    # assert output["COMPANY_NAME"] == ""
    # assert output["TOOL"] == ""
    # assert output["EDUCATION"] == "Bachelor's degree"
    # assert output["EXPERIENCE"] == ""
    # assert output["DESIGNATION"] == "Data Scientist"
    # assert output["LOCATION"] == ""
    # assert output["LANGUAGE"] == ""
    # assert output["SOFT_SKILL"] == ""
    # assert output["PAY"] == ""
    # assert output["CERTIFICATION"] == ""