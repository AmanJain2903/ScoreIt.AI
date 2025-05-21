import pytest
import pandas as pd
from src.designation_matchmaker.designation_matching import DesignationMatching
from src.designation_matchmaker import config
from src.utils import model_load
config = config.Config()

pytestmark = pytest.mark.integration

designationDataPath = 'data/designation_dataset.csv'

@pytest.fixture
def designation_matchmaker():
    return DesignationMatching()

def test_designation_matchmaker_end_to_end(designation_matchmaker):
    dataset = pd.read_csv(designationDataPath)
    if dataset.empty:
        raise ValueError("Dataset is empty. Please check the data path.")
    # Check if the dataset has the required columns
    required_columns = ["resume_title", "jd_title"]
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    for randomIndex in range(10):
        resume_designation = dataset["resume_title"].iloc[randomIndex]
        job_designation = dataset["jd_title"].iloc[randomIndex]
        # Check if the inputs are valid
        if not isinstance(resume_designation, str) or not isinstance(job_designation, str):
            raise ValueError("Resume designation and job designation must be strings.")
        # Set inputs
        designation_matchmaker.setInputs(resume_designation, job_designation)
        # Make match
        output = designation_matchmaker.makeMatch()
        # Check the output
        assert isinstance(output, float)
        assert 0 <= output <= 1