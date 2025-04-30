import pytest
import pandas as pd
from src.certification_matchmaker.certification_matching import CertificationMatching
from src.certification_matchmaker import config
config = config.Config()

pytestmark = pytest.mark.integration

certificationDataPath = 'data/certification_dataset.csv'

@pytest.fixture
def certification_matchmaker():
    return CertificationMatching()

def test_certification_matchmaker_end_to_end(certification_matchmaker):
    dataset = pd.read_csv(certificationDataPath)
    if dataset.empty:
        raise ValueError("Dataset is empty. Please check the data path.")
    # Check if the dataset has the required columns
    required_columns = ["resume_certs", "jd_certs"]
    for col in required_columns:
        if col not in dataset.columns:
            raise ValueError(f"Column '{col}' not found in the dataset.")
    for randomIndex in range(len(dataset)):
        resume_certification = dataset["resume_certs"].iloc[randomIndex]
        job_certification = dataset["jd_certs"].iloc[randomIndex]
        # Check if the inputs are valid
        if not isinstance(resume_certification, str) or not isinstance(job_certification, str):
            raise ValueError("Resume certification and job certification must be strings.")
        # Set inputs
        certification_matchmaker.setInputs(resume_certification, job_certification)
        # Make match
        output = certification_matchmaker.makeMatch()
        # Check the output
        assert isinstance(output, float)
        assert 0 <= output <= 1