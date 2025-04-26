import pytest
from src.resume_extractor_agent.resume_agent import ResumeAgent
import os

pytestmark = pytest.mark.integration

@pytest.fixture
def resume_agent():
    api_key = os.getenv("OPENROUTER_API_KEY")

    return ResumeAgent(
        apiKey=api_key,
        modelName=None,
        systemPrompt=None
    )

def test_resume_agent_end_to_end(resume_agent):
    input_text = "Software engineer with 5 years of experience in Python, AWS, and Machine Learning. MS in Computer Science."

    resume_agent.setUserPrompt(input_text)
    output = resume_agent.getJsonOutput()

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
    # assert output["TECHNICAL_SKILL"] == "Python, AWS, Machine Learning"
    # assert output["COMPANY_NAME"] == ""
    # assert output["TOOL"] == ""
    # assert output["EDUCATION"] == "MS in Computer Science"
    # assert output["EXPERIENCE"] == "5 years"
    # assert output["DESIGNATION"] == "Software engineer"
    # assert output["LOCATION"] == ""
    # assert output["LANGUAGE"] == ""
    # assert output["SOFT_SKILL"] == ""
    # assert output["PAY"] == ""
    # assert output["CERTIFICATION"] == ""