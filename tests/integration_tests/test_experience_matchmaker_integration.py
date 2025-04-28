import pytest
import pandas as pd
from src.experience_matchmaker.experience_matching import ExperienceMatching
from src.experience_matchmaker import config
config = config.Config()

pytestmark = pytest.mark.integration

dataPath = 'data/experience_dataset.csv'

@pytest.fixture
def experience_matchmaker():
    return ExperienceMatching(modelName1=config.MODEL_NAME_1, modelName2=config.MODEL_NAME_2)


def test_experience_matchmaker_end_to_end(experience_matchmaker):
    dataset = pd.read_csv(dataPath)
    if dataset.empty:
        raise ValueError("Dataset is empty. Please check the data path.")
    # Check if the dataset has the required columns
    required_columns = ['ResumeExperience', 'JDExperience']
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    for i in range(len(dataset)):
        resume_experience = dataset['ResumeExperience'].iloc[i]
        job_experience = dataset['JDExperience'].iloc[i]

        # Check if the inputs are valid
        if not isinstance(resume_experience, str) or not isinstance(job_experience, str):
            raise ValueError("Resume experience and job experience must be strings.")

        # Set inputs
        experience_matchmaker.setInputs(resumeExperience=resume_experience, jobExperience=job_experience)

        # Make match
        output = experience_matchmaker.makeMatch()

        # Check the output
        assert isinstance(output, float)
        assert 0 <= output <= 1