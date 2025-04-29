import pytest
import pandas as pd
from src.designation_matchmaker.designation_matching import DesignationMatching
from src.designation_matchmaker import config
import numpy as np
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
    required_columns = ['ResumeDesignations', 'JDDesignations']
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    randomIndex = np.random.randint(0, len(dataset))
    resume_designation = dataset['ResumeDesignations'].iloc[randomIndex]
    job_designation = dataset['JDDesignations'].iloc[randomIndex]
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