import pytest
import pandas as pd
from src.tools_matchmaker.tools_matching import ToolMatching
from src.tools_matchmaker import config
import numpy as np
config = config.Config()

pytestmark = pytest.mark.integration

toolDataPath = 'data/tools_dataset.csv'

@pytest.fixture
def tool_matchmaker():
    return ToolMatching()

def test_tool_matchmaker_end_to_end(tool_matchmaker):
    dataset = pd.read_csv(toolDataPath)
    if dataset.empty:
        raise ValueError("Dataset is empty. Please check the data path.")
    # Check if the dataset has the required columns
    required_columns = ['ResumeTools', 'JobTools']
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    randomIndex = np.random.randint(0, len(dataset))
    resume_tool = dataset['ResumeTools'].iloc[randomIndex]
    job_tool = dataset['JobTools'].iloc[randomIndex]
    # Check if the inputs are valid
    if not isinstance(resume_tool, str) or not isinstance(job_tool, str):
        raise ValueError("Resume tool and job tool must be strings.")
    # Set inputs
    tool_matchmaker.setInputs(resume_tool, job_tool)
    # Make match
    output = tool_matchmaker.makeMatch()
    # Check the output
    assert isinstance(output, float)
    assert 0 <= output <= 1