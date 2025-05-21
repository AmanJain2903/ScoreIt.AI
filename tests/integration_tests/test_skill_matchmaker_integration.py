import pytest
import pandas as pd
from src.skill_matchmaker.technical_skill_matching import TechnicalSkillMatching
from src.skill_matchmaker.soft_skill_matching import SoftSkillMatching
from src.skill_matchmaker import config
from src.utils import model_load
config = config.Config()

pytestmark = pytest.mark.integration

technicalSkillDataPath = 'data/technical_skills_dataset.csv'
softSkillDataPath = 'data/soft_skills_dataset.csv'

@pytest.fixture
def technical_skill_matchmaker():
    return TechnicalSkillMatching()

@pytest.fixture
def soft_skill_matchmaker():
    return SoftSkillMatching()

def test_technical_skill_matchmaker_end_to_end(technical_skill_matchmaker):
    dataset = pd.read_csv(technicalSkillDataPath)
    if dataset.empty:
        raise ValueError("Dataset is empty. Please check the data path.")
    # Check if the dataset has the required columns
    required_columns = ['resume_skills', 'jd_skills']
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    for randomIndex in range(10):
        resume_skill = dataset['resume_skills'].iloc[randomIndex]
        job_skill = dataset['jd_skills'].iloc[randomIndex]
        # Check if the inputs are valid
        if not isinstance(resume_skill, str) or not isinstance(job_skill, str):
            raise ValueError("Resume skill and job skill must be strings.")
        # Set inputs
        technical_skill_matchmaker.setInputs(resumeSkill=resume_skill, jobSkill=job_skill)
        # Make match
        output = technical_skill_matchmaker.makeMatch()
        # Check the output
        assert isinstance(output, float)
        assert 0 <= output <= 1

def test_soft_skill_matchmaker_end_to_end(soft_skill_matchmaker):
    dataset = pd.read_csv(softSkillDataPath)
    if dataset.empty:
        raise ValueError("Dataset is empty. Please check the data path.")
    # Check if the dataset has the required columns
    required_columns = ['resume_skills', 'jd_skills']
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    for randomIndex in range(len(dataset)):
        resume_skill = dataset['resume_skills'].iloc[randomIndex]
        job_skill = dataset['jd_skills'].iloc[randomIndex]
        # Check if the inputs are valid
        if not isinstance(resume_skill, str) or not isinstance(job_skill, str):
            raise ValueError("Resume skill and job skill must be strings.")
        # Set inputs
        soft_skill_matchmaker.setInputs(resumeSkill=resume_skill, jobSkill=job_skill)
        # Make match
        output = soft_skill_matchmaker.makeMatch()
        # Check the output
        assert isinstance(output, float)
        assert 0 <= output <= 1