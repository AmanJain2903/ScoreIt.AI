import pytest
import pandas as pd
from src.education_matchmaker.education_matching import EducationMatching
from src.education_matchmaker import config
from src.utils import model_load
config = config.Config()

pytestmark = pytest.mark.integration

dataPath = 'data/education_dataset.csv'

@pytest.fixture
def education_matchmaker():
    return EducationMatching()

def test_education_matchmaker_end_to_end(education_matchmaker):
    dataset = pd.read_csv(dataPath)
    if dataset.empty:
        raise ValueError("Dataset is empty. Please check the data path.")
    # Check if the dataset has the required columns
    required_columns = ['resume_edu', 'jd_edu']
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    for i in range(10):
        resume_education = dataset['resume_edu'].iloc[i]
        job_education = dataset['jd_edu'].iloc[i]

        # Check if the inputs are valid
        if not isinstance(resume_education, str) or not isinstance(job_education, str):
            raise ValueError("Resume education and job education must be strings.")

        # Set inputs
        education_matchmaker.setInputs(resumeEducation=resume_education, jobEducation=job_education)

        # Make match
        output = education_matchmaker.makeMatch()

        # Check the output
        assert isinstance(output, float)
        assert 0 <= output <= 1