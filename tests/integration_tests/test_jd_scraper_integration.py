import pytest
from src.jd_scraper.jd_scraper import JobDescriptionScraper
import os
import pandas as pd
import numpy as np

pytestmark = pytest.mark.integration

sampleLink = "https://www.linkedin.com/jobs/view/4197961513"

def test_jd_scraper_integration():
    scraper = JobDescriptionScraper()
    scraper.setInputs(sampleLink)
    job_description = scraper.extractJobDescription()
    assert isinstance(job_description, str)
    assert len(job_description) > 0