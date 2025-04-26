import pytest
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
import os

pytestmark = pytest.mark.integration

@pytest.fixture
def jd_agent():
    api_key = os.getenv("OPENROUTER_API_KEY")

    return JobDescriptionAgent(
        apiKey=api_key,
        modelName=None,
        systemPrompt=None
    )

def test_jd_agent_end_to_end(jd_agent):
    input_text = "Looking for a Data Scientist with expertise in Python, TensorFlow, and cloud computing. Bachelor's degree required."

    jd_agent.setUserPrompt(input_text)
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
    assert output["TECHNICAL_SKILL"] == "Python, TensorFlow, cloud computing"
    assert output["COMPANY_NAME"] == ""
    assert output["TOOL"] == ""
    assert output["EDUCATION"] == "Bachelor's degree"
    assert output["EXPERIENCE"] == ""
    assert output["DESIGNATION"] == "Data Scientist"
    assert output["LOCATION"] == ""
    assert output["LANGUAGE"] == ""
    assert output["SOFT_SKILL"] == ""
    assert output["PAY"] == ""
    assert output["CERTIFICATION"] == ""