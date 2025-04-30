import pytest
import pandas as pd
from src.tools_matchmaker.tools_matching import ToolMatching
from src.tools_matchmaker import config
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
    required_columns = ['resume_tools', 'jd_tools']
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    for randomIndex in range(len(dataset)):
        resume_tool = dataset['resume_tools'].iloc[randomIndex]
        job_tool = dataset['jd_tools'].iloc[randomIndex]
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